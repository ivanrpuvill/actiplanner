from app.repositories.programa_participant_repository import ProgramaParticipantRepository
from app.repositories.objectiu_pla_repository import ObjectiuPlaRepository
from app.repositories.pla_accio_repository import PlaAccioRepository
from app.repositories.accio_repository import AccioRepository
from app.repositories.kpi_repository import KPIRepository
from app.repositories.registre_kpi_repository import RegistreKPIRepository
from app.repositories.usuari_repository import UsuariRepository


class AnalisiService:
    def __init__(self):
        self.participant_repository = ProgramaParticipantRepository()
        self.pla_repository = PlaAccioRepository()
        self.objectiu_repository = ObjectiuPlaRepository()
        self.accio_repository = AccioRepository()
        self.kpi_repository = KPIRepository()
        self.registre_kpi_repository = RegistreKPIRepository()
        self.usuari_repository = UsuariRepository()

    def get_analisi_programa(self, idPrograma: int) -> dict:
        participants = self.participant_repository.get_by_programa(idPrograma)

        resultats_participants = []

        for participant in participants:
            progres = self._calcular_progres_participant(
                idPrograma,
                participant.idUsuari
            )

            resultats_participants.append({
                "idUsuari": participant.idUsuari,
                "progres": progres,
                "estat": self._calcular_estat(progres)
            })

        progres_mitja = self._mitjana([
            participant["progres"]
            for participant in resultats_participants
        ])

        return {
            "idPrograma": idPrograma,
            "nombreParticipants": len(participants),
            "progresMitjaPrograma": progres_mitja,
            "estatPrograma": self._calcular_estat(progres_mitja),
            "participants": resultats_participants
        }

    def get_objectius_risc(self, idPrograma: int) -> list[dict]:
        objectius_risc = []

        plans = self.pla_repository.get_by_programa(idPrograma)

        for pla in plans:
            objectius = self.objectiu_repository.get_by_pla(pla.idPla)

            for objectiu in objectius:
                progres = self._calcular_progres_objectiu_programa(
                    idPrograma,
                    objectiu.idObjectiu
                )

                if progres < 20:
                    objectius_risc.append({
                        "idPla": pla.idPla,
                        "idObjectiu": objectiu.idObjectiu,
                        "descripcio": objectiu.descripcio,
                        "progres": progres,
                        "estat": self._calcular_estat(progres)
                    })

        return objectius_risc

    def get_participants_destacats(self, idPrograma: int) -> list[dict]:
        participants = self.participant_repository.get_by_programa(idPrograma)
        destacats = []

        for participant in participants:
            progres = self._calcular_progres_participant(
                idPrograma,
                participant.idUsuari
            )

            if progres >= 80:
                destacats.append({
                    "idUsuari": participant.idUsuari,
                    "progres": progres,
                    "estat": "destacat"
                })

        return destacats

    def get_ranquing_programa(self, idPrograma: int) -> list[dict]:
        """
        Retorna TOTS els participants del programa ordenats per progrés
        descendent, amb posició i nom inclosos.

        A diferència de get_participants_destacats (que només retorna qui
        supera el llindar del 80%, i per tant sovint queda buit o amb un
        únic element en programes amb pocs participants), aquest mètode
        sempre retorna el rànquing complet: és el que cal fer servir per
        a qualsevol pantalla de gamificació o rànquing, ja que un rànquing
        amb 0 o 1 posicions no compleix la seva funció comparativa.
        """
        participants = self.participant_repository.get_by_programa(idPrograma)
        ranquing = []

        for participant in participants:
            progres = self._calcular_progres_participant(
                idPrograma,
                participant.idUsuari
            )

            usuari = self.usuari_repository.get_by_id(participant.idUsuari)
            nom = f"{usuari.nom} {usuari.cognoms}".strip() if usuari else f"Usuari {participant.idUsuari}"

            ranquing.append({
                "idUsuari": participant.idUsuari,
                "nom": nom,
                "progres": progres,
                "estat": self._calcular_estat(progres),
                "destacat": progres >= 80
            })

        ranquing.sort(key=lambda item: item["progres"], reverse=True)

        for index, item in enumerate(ranquing):
            item["posicio"] = index + 1

        return ranquing

    def get_participants_amb_desviacio(self, idPrograma: int) -> list[dict]:
        participants = self.participant_repository.get_by_programa(idPrograma)
        desviacions = []

        for participant in participants:
            progres = self._calcular_progres_participant(
                idPrograma,
                participant.idUsuari
            )

            if progres < 20:
                desviacions.append({
                    "idUsuari": participant.idUsuari,
                    "progres": progres,
                    "estat": "desviacio"
                })

        return desviacions

    def _calcular_progres_participant(
        self,
        idPrograma: int,
        idUsuari: int
    ) -> float:
        plans = self.pla_repository.get_by_programa(idPrograma)
        progressos = []

        for pla in plans:
            objectius = self.objectiu_repository.get_by_pla(pla.idPla)

            for objectiu in objectius:
                progres = self._calcular_progres_objectiu_usuari(
                    objectiu.idObjectiu,
                    idUsuari
                )
                progressos.append(progres)

        return self._mitjana(progressos)

    def _calcular_progres_objectiu_programa(
        self,
        idPrograma: int,
        idObjectiu: int
    ) -> float:
        participants = self.participant_repository.get_by_programa(idPrograma)
        progressos = []

        for participant in participants:
            progres = self._calcular_progres_objectiu_usuari(
                idObjectiu,
                participant.idUsuari
            )
            progressos.append(progres)

        return self._mitjana(progressos)

    def _calcular_progres_objectiu_usuari(
        self,
        idObjectiu: int,
        idUsuari: int
    ) -> float:
        accions = self.accio_repository.get_by_objectiu(idObjectiu)
        valors = []

        for accio in accions:
            kpis = self.kpi_repository.get_by_accio(accio.idAccio)

            for kpi in kpis:
                registres = self.registre_kpi_repository.get_by_kpi_and_usuari(
                    kpi.idKPI,
                    idUsuari
                )

                if registres:
                    valor_agregat = self._agregar_registres_kpi(kpi, registres)
                    assoliment = self._calcular_assoliment_kpi(
                        kpi,
                        valor_agregat
                    )

                    valors.append(assoliment)

        return self._mitjana(valors)

    def _agregar_registres_kpi(self, kpi, registres) -> float:
        """
        Agrega els registres d'un KPI segons el seu tipusCalcul:
          - acumulat: suma tots els valors registrats (p. ex. nombre de
            reunions fetes al llarg del període).
          - mitjana: mitjana de tots els valors registrats (p. ex. una
            puntuació recollida en diversos moments).
          - ultim: només el valor del registre més recent (p. ex. un
            indicador d'estat puntual, com una certificació obtinguda).
        """
        tipus_calcul = getattr(kpi, "tipusCalcul", "acumulat")

        if tipus_calcul == "mitjana":
            return self._mitjana([registre.valor for registre in registres])

        if tipus_calcul == "ultim":
            ultim_registre = max(
                registres,
                key=lambda registre: registre.dataRegistre
            )
            return ultim_registre.valor

        return sum(registre.valor for registre in registres)

    def _mitjana(self, valors: list[float]) -> float:
        if not valors:
            return 0

        return round(sum(valors) / len(valors), 2)

    def _calcular_estat(self, progres: float) -> str:
        """
        Estat agregat (objectiu, pla, participant, programa). El llindar
        d'assoliment es manté al 80% perquè, en agregar diversos KPI
        heterogenis mitjançant una mitjana, exigir el 100% faria que
        gairebé cap objectiu compost arribés mai a "assolit" tot i tenir
        un rendiment molt alt en tots els seus components.
        """
        if progres >= 80:
            return "assolit"

        if progres >= 20:
            return "en_progres"

        return "pendent"

    def _calcular_estat_kpi(self, assoliment: float) -> str:
        """
        Estat d'un KPI individual. A diferència de l'estat agregat,
        aquí "assolit" exigeix haver arribat (o superat) el 100% del
        valorObjectiu del propi KPI, ja que en aquest nivell hi ha un
        únic valor de referència clar i verificable.
        """
        if assoliment >= 100:
            return "assolit"

        if assoliment >= 20:
            return "en_progres"

        return "pendent"

    def _calcular_assoliment_kpi(self, kpi, valor_actual: float) -> float:
        tipus = getattr(kpi, "tipus", "numeric")
        orientacio = getattr(kpi, "orientacio", "major_millor")

        if tipus == "boolea":
            return 100 if valor_actual >= 1 else 0

        if tipus == "percentatge":
            objectiu = getattr(kpi, "valorObjectiu", 100) or 100
            if objectiu == 0:
                return 0

            assoliment = (valor_actual / objectiu) * 100
            return max(0, min(100, round(assoliment, 2)))

        minim = getattr(kpi, "valorMinim", 0) or 0
        objectiu = getattr(kpi, "valorObjectiu", None)
        maxim = getattr(kpi, "valorMaxim", None)

        referencia = objectiu if objectiu is not None else maxim

        if referencia is None or referencia == minim:
            return 0

        if orientacio == "menor_millor":
            assoliment = ((referencia - valor_actual) / (referencia - minim)) * 100
        else:
            assoliment = ((valor_actual - minim) / (referencia - minim)) * 100

        return max(0, min(100, round(assoliment, 2)))