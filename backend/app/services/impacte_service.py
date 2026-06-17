from datetime import date
from statistics import mean, pstdev

from app.models.registre_impacte import RegistreImpacte, RegistreImpacteCreate
from app.repositories.indicador_impacte_repository import IndicadorImpacteRepository
from app.repositories.registre_impacte_repository import RegistreImpacteRepository
from app.repositories.programa_participant_repository import ProgramaParticipantRepository
from app.services.analisi_service import AnalisiService


class ImpacteService:
    """
    Servei responsable de validar si la formació ha tingut un impacte real,
    diferenciant-ho explícitament del seguiment de compliment d'un pla d'acció.

    Mentre AnalisiService respon a la pregunta "el participant ha fet el que
    el pla deia?" (compliment de KPI respecte a un valor objectiu intern),
    aquest servei respon a la pregunta "el participant ha canviat respecte
    a ell mateix, i aquest canvi es pot atribuir a la formació?" (delta
    pre/post sobre un indicador de negoci, amb comparació respecte a un
    grup no format i correlació amb el compliment del pla).
    """

    def __init__(self):
        self.indicador_repository = IndicadorImpacteRepository()
        self.registre_repository = RegistreImpacteRepository()
        self.participant_repository = ProgramaParticipantRepository()
        self.analisi_service = AnalisiService()

    # ------------------------------------------------------------------
    # CRUD bàsic d'indicadors i registres
    # ------------------------------------------------------------------

    def get_indicadors_programa(self, idPrograma: int):
        return self.indicador_repository.get_by_programa(idPrograma)

    def create_indicador(self, indicador):
        from app.models.indicador_impacte import IndicadorImpacte

        nou_indicador = IndicadorImpacte(
            idIndicadorImpacte=self.indicador_repository.next_id(),
            **indicador.model_dump()
        )

        return self.indicador_repository.create(nou_indicador)

    def create_registre_impacte(self, registre: RegistreImpacteCreate):
        indicador = self.indicador_repository.get_by_id(registre.idIndicadorImpacte)

        if indicador is None:
            return None

        nou_registre = RegistreImpacte(
            idRegistreImpacte=self.registre_repository.next_id(),
            dataRegistre=date.today().isoformat(),
            **registre.model_dump()
        )

        return self.registre_repository.create(nou_registre)

    def get_registres_indicador(self, idIndicadorImpacte: int):
        return self.registre_repository.get_by_indicador(idIndicadorImpacte)

    # ------------------------------------------------------------------
    # NIVELL 1 — Delta pre/post per participant i per indicador
    # ------------------------------------------------------------------

    def _valor_moment(
        self,
        idIndicadorImpacte: int,
        idUsuari: int,
        moment: str
    ) -> float | None:
        registres = [
            registre
            for registre in self.registre_repository.get_by_indicador_and_usuari(
                idIndicadorImpacte, idUsuari
            )
            if registre.moment == moment
        ]

        if not registres:
            return None

        # Si hi ha diversos registres per al mateix moment, ens quedem
        # amb el més recent (permet rectificacions sense perdre traçabilitat).
        ultim = sorted(registres, key=lambda r: r.dataRegistre)[-1]

        return ultim.valor

    def get_delta_impacte_usuari(
        self,
        idIndicadorImpacte: int,
        idUsuari: int
    ) -> dict | None:
        indicador = self.indicador_repository.get_by_id(idIndicadorImpacte)

        if indicador is None:
            return None

        valor_pre = self._valor_moment(idIndicadorImpacte, idUsuari, "pre")
        valor_post = self._valor_moment(idIndicadorImpacte, idUsuari, "post")

        if valor_pre is None or valor_post is None:
            return {
                "idIndicadorImpacte": idIndicadorImpacte,
                "idUsuari": idUsuari,
                "valorPre": valor_pre,
                "valorPost": valor_post,
                "delta": None,
                "deltaPercentual": None,
                "disponible": False,
                "motiu": "Falta el valor 'pre' o 'post' per calcular el delta."
            }

        delta = valor_post - valor_pre

        # Si l'indicador és "menor_millor" (p. ex. temps de resolució),
        # una millora real és una REDUCCIÓ del valor, així que invertim el signe
        # perquè un delta positiu signifiqui sempre "millora" de cara a l'usuari.
        delta_normalitzat = (
            -delta if indicador.orientacio == "menor_millor" else delta
        )

        delta_percentual = (
            round((delta_normalitzat / abs(valor_pre)) * 100, 2)
            if valor_pre != 0
            else None
        )

        return {
            "idIndicadorImpacte": idIndicadorImpacte,
            "idUsuari": idUsuari,
            "valorPre": valor_pre,
            "valorPost": valor_post,
            "delta": round(delta_normalitzat, 2),
            "deltaPercentual": delta_percentual,
            "disponible": True,
            "millora": delta_normalitzat > 0
        }

    def get_deltes_programa(self, idIndicadorImpacte: int, idPrograma: int) -> list[dict]:
        participants = self.participant_repository.get_by_programa(idPrograma)

        deltes = []

        for participant in participants:
            delta = self.get_delta_impacte_usuari(idIndicadorImpacte, participant.idUsuari)

            if delta is not None:
                deltes.append(delta)

        return deltes

    # ------------------------------------------------------------------
    # NIVELL 2 — Comparació entre grup format i grup de control
    # ------------------------------------------------------------------

    def comparar_grups(
        self,
        idIndicadorImpacteFormat: int,
        idProgramaFormat: int,
        idIndicadorImpacteControl: int | None = None,
        idProgramaControl: int | None = None
    ) -> dict:
        """
        Compara l'evolució de l'indicador entre els participants d'un
        programa de formació (grup format) i, opcionalment, els
        participants d'un altre programa o segment (grup de control).

        S'admeten dos identificadors d'indicador diferents (un per grup)
        perquè, a la pràctica, el mateix concepte de negoci (p. ex. "temps
        de resolució d'incidències") sol registrar-se com un indicador
        independent per a cada programa. Si el grup de control utilitza
        el mateix indicador que el grup format, n'hi ha prou amb indicar
        idIndicadorImpacteFormat i deixar idIndicadorImpacteControl a None.

        Una millora del grup format que NO s'observa (o és molt menor)
        en el grup de control és l'evidència mínima per atribuir el canvi
        a la formació i no a factors externs (estacionalitat, mercat, etc.).
        """
        idIndicadorImpacteControl = (
            idIndicadorImpacteControl
            if idIndicadorImpacteControl is not None
            else idIndicadorImpacteFormat
        )

        deltes_format = self.get_deltes_programa(idIndicadorImpacteFormat, idProgramaFormat)
        valors_format = [
            d["delta"] for d in deltes_format if d.get("disponible")
        ]

        resultat = {
            "idIndicadorImpacteFormat": idIndicadorImpacteFormat,
            "grupFormat": {
                "idPrograma": idProgramaFormat,
                "nParticipants": len(valors_format),
                "deltaMitja": round(mean(valors_format), 2) if valors_format else None,
                "desviacioEstandard": (
                    round(pstdev(valors_format), 2) if len(valors_format) > 1 else None
                )
            },
            "grupControl": None,
            "diferenciaEntreGrups": None,
            "conclusio": None
        }

        if idProgramaControl is not None:
            deltes_control = self.get_deltes_programa(
                idIndicadorImpacteControl, idProgramaControl
            )
            valors_control = [
                d["delta"] for d in deltes_control if d.get("disponible")
            ]

            resultat["idIndicadorImpacteControl"] = idIndicadorImpacteControl
            resultat["grupControl"] = {
                "idPrograma": idProgramaControl,
                "nParticipants": len(valors_control),
                "deltaMitja": round(mean(valors_control), 2) if valors_control else None,
                "desviacioEstandard": (
                    round(pstdev(valors_control), 2) if len(valors_control) > 1 else None
                )
            }

            if valors_format and valors_control:
                diferencia = round(mean(valors_format) - mean(valors_control), 2)
                resultat["diferenciaEntreGrups"] = diferencia
                resultat["conclusio"] = self._interpretar_diferencia(
                    diferencia, len(valors_format), len(valors_control)
                )
            else:
                resultat["conclusio"] = (
                    "No hi ha prou dades disponibles en un dels dos grups "
                    "(falten valors 'pre' o 'post') per calcular la comparació."
                )

        if resultat["conclusio"] is None and valors_format:
            resultat["conclusio"] = (
                "No hi ha grup de control definit. Aquesta dada només mostra "
                "l'evolució del grup format i NO permet atribuir el canvi a la "
                "formació, ja que podria deure's a altres factors externs."
            )

        return resultat

    def _interpretar_diferencia(
        self,
        diferencia: float,
        n_format: int,
        n_control: int
    ) -> str:
        mostra_petita = n_format < 5 or n_control < 5
        avis_mostra = (
            " Atenció: la mida de la mostra és petita, per la qual cosa "
            "aquesta conclusió s'ha d'interpretar amb molta cautela."
            if mostra_petita else ""
        )

        if diferencia > 0:
            return (
                f"El grup format millora de mitjana {diferencia} punts més que "
                f"el grup de control. Això és un indici (no una prova causal) "
                f"de que la formació hi pot haver contribuït.{avis_mostra}"
            )

        if diferencia < 0:
            return (
                f"El grup format millora de mitjana {abs(diferencia)} punts MENYS "
                f"que el grup de control. Això suggereix que la millora observada "
                f"podria no ser atribuïble a la formació.{avis_mostra}"
            )

        return (
            "No s'observa diferència entre el grup format i el grup de control. "
            f"No hi ha evidència de que la formació hagi tingut impacte "
            f"diferencial.{avis_mostra}"
        )

    # ------------------------------------------------------------------
    # NIVELL 3 — Correlació entre compliment del pla i delta d'impacte
    # ------------------------------------------------------------------

    def correlacio_progres_impacte(
        self,
        idIndicadorImpacte: int,
        idPrograma: int
    ) -> dict:
        """
        Calcula la correlació de Pearson entre:
          - el progrés del pla d'acció de cada participant (% de compliment
            de KPI calculat per AnalisiService), i
          - el delta normalitzat de l'indicador d'impacte del mateix participant.

        Una correlació positiva i alta suggereix que el disseny del pla
        d'acció (objectius, accions i KPI) és un bon proxy del canvi real.
        Una correlació baixa o nul·la és evidència de que complir el pla
        NO garanteix que la formació hagi tingut impacte, és a dir, que
        el seguiment intern i l'eficàcia real es poden estar desacoblant.
        """
        participants = self.participant_repository.get_by_programa(idPrograma)

        parells = []

        for participant in participants:
            progres = self.analisi_service._calcular_progres_participant(
                idPrograma, participant.idUsuari
            )

            delta = self.get_delta_impacte_usuari(
                idIndicadorImpacte, participant.idUsuari
            )

            if delta is not None and delta.get("disponible"):
                parells.append({
                    "idUsuari": participant.idUsuari,
                    "progresPla": progres,
                    "deltaImpacte": delta["delta"]
                })

        n = len(parells)

        resultat = {
            "idIndicadorImpacte": idIndicadorImpacte,
            "idPrograma": idPrograma,
            "nParticipants": n,
            "dades": parells,
            "coeficientPearson": None,
            "interpretacio": None
        }

        if n < 3:
            resultat["interpretacio"] = (
                "Calen com a mínim 3 participants amb dades completes "
                "(progrés del pla i delta pre/post de l'indicador) per "
                "calcular una correlació amb un mínim de sentit. "
                f"Actualment només hi ha {n}."
            )
            return resultat

        progres_vals = [p["progresPla"] for p in parells]
        delta_vals = [p["deltaImpacte"] for p in parells]

        r = self._pearson(progres_vals, delta_vals)
        resultat["coeficientPearson"] = r
        resultat["interpretacio"] = self._interpretar_correlacio(r, n)

        return resultat

    def _pearson(self, x: list[float], y: list[float]) -> float | None:
        n = len(x)

        mitjana_x = mean(x)
        mitjana_y = mean(y)

        numerador = sum(
            (x[i] - mitjana_x) * (y[i] - mitjana_y) for i in range(n)
        )

        suma_quadrats_x = sum((valor - mitjana_x) ** 2 for valor in x)
        suma_quadrats_y = sum((valor - mitjana_y) ** 2 for valor in y)

        denominador = (suma_quadrats_x * suma_quadrats_y) ** 0.5

        if denominador == 0:
            return None

        return round(numerador / denominador, 3)

    def _interpretar_correlacio(self, r: float | None, n: int) -> str:
        avis_mostra = (
            f" Amb una mostra de només {n} participants, aquest resultat "
            "és merament orientatiu i no es pot generalitzar."
        )

        if r is None:
            return (
                "No s'ha pogut calcular la correlació (variància nul·la "
                "en alguna de les dues variables)." + avis_mostra
            )

        magnitud = abs(r)

        if magnitud >= 0.7:
            força = "forta"
        elif magnitud >= 0.4:
            força = "moderada"
        elif magnitud >= 0.2:
            força = "feble"
        else:
            força = "pràcticament inexistent"

        sentit = "positiva" if r >= 0 else "negativa"

        missatge = (
            f"Correlació {força} i {sentit} (r={r}) entre el compliment del "
            f"pla d'acció i la millora de l'indicador d'impacte."
        )

        if magnitud < 0.2:
            missatge += (
                " Això suggereix que complir el pla d'acció NO garanteix "
                "una millora real de l'indicador de negoci: el seguiment "
                "intern (KPI del pla) i l'eficàcia real de la formació "
                "es podrien estar desacoblant."
            )
        elif r < 0:
            missatge += (
                " Un coeficient negatiu és un senyal d'alerta: els "
                "participants que més compleixen el pla NO són els que "
                "més milloren en l'indicador real. Caldria revisar si els "
                "KPI del pla són un bon proxy de l'objectiu formatiu."
            )

        return missatge + avis_mostra