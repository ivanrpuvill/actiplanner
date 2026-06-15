from app.repositories.programa_participant_repository import ProgramaParticipantRepository
from app.repositories.objectiu_pla_repository import ObjectiuPlaRepository
from app.repositories.pla_accio_repository import PlaAccioRepository
from app.repositories.accio_repository import AccioRepository
from app.repositories.kpi_repository import KPIRepository
from app.repositories.registre_kpi_repository import RegistreKPIRepository


class AnalisiService:
    def __init__(self):
        self.participant_repository = ProgramaParticipantRepository()
        self.pla_repository = PlaAccioRepository()
        self.objectiu_repository = ObjectiuPlaRepository()
        self.accio_repository = AccioRepository()
        self.kpi_repository = KPIRepository()
        self.registre_kpi_repository = RegistreKPIRepository()

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

                if progres < 40:
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

    def get_participants_amb_desviacio(self, idPrograma: int) -> list[dict]:
        participants = self.participant_repository.get_by_programa(idPrograma)
        desviacions = []

        for participant in participants:
            progres = self._calcular_progres_participant(
                idPrograma,
                participant.idUsuari
            )

            if progres < 40:
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
                    ultim_registre = max(
                        registres,
                        key=lambda registre: registre.dataRegistre
                    )
                    assoliment = self._calcular_assoliment_kpi(
                        kpi,
                        ultim_registre.valor
                    )

                    valors.append(assoliment)

        return self._mitjana(valors)

    def _mitjana(self, valors: list[float]) -> float:
        if not valors:
            return 0

        return round(sum(valors) / len(valors), 2)

    def _calcular_estat(self, progres: float) -> str:
        if progres >= 80:
            return "assolit"

        if progres >= 40:
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