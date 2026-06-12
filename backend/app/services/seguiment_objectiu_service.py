from app.repositories.seguiment_objectiu_repository import SeguimentObjectiuRepository
from app.repositories.accio_repository import AccioRepository
from app.repositories.kpi_repository import KPIRepository
from app.repositories.registre_kpi_repository import RegistreKPIRepository


class SeguimentObjectiuService:
    def __init__(self):
        self.seguiment_repository = SeguimentObjectiuRepository()
        self.accio_repository = AccioRepository()
        self.kpi_repository = KPIRepository()
        self.registre_kpi_repository = RegistreKPIRepository()

    def get_seguiments_objectiu(self, idObjectiu: int):
        return self.seguiment_repository.get_by_objectiu(idObjectiu)

    def get_seguiments_usuari(self, idUsuari: int):
        return self.seguiment_repository.get_by_usuari(idUsuari)

    def get_seguiments_programa_usuari(
        self,
        idPrograma: int,
        idUsuari: int
    ):
        return self.seguiment_repository.get_by_programa_usuari(
            idPrograma,
            idUsuari
        )

    def calcular_progres_objectiu_usuari(
        self,
        idObjectiu: int,
        idUsuari: int
    ) -> float:
        seguiment = self.seguiment_repository.get_by_objectiu_usuari(
            idObjectiu,
            idUsuari
        )

        if seguiment is None:
            return 0

        accions = self.accio_repository.get_by_objectiu(idObjectiu)
        valors_kpi = []

        for accio in accions:
            kpis = self.kpi_repository.get_by_accio(accio.idAccio)

            for kpi in kpis:
                registres = self.registre_kpi_repository.get_by_kpi_and_usuari(
                    kpi.idKPI,
                    idUsuari
                )

                valor_kpi = self._calcular_valor_kpi_usuari(kpi, idUsuari)

                valors_kpi.append(valor_kpi)

        if not valors_kpi:
            return 0

        return round(sum(valors_kpi) / len(valors_kpi), 2)

    def get_detall_seguiment_objectiu_usuari(
        self,
        idObjectiu: int,
        idUsuari: int
    ):
        seguiment = self.seguiment_repository.get_by_objectiu_usuari(
            idObjectiu,
            idUsuari
        )

        if seguiment is None:
            return None

        progres = self.calcular_progres_objectiu_usuari(
            idObjectiu,
            idUsuari
        )

        return {
            "idSeguiment": seguiment.idSeguiment,
            "idObjectiu": seguiment.idObjectiu,
            "idPrograma": seguiment.idPrograma,
            "idUsuari": seguiment.idUsuari,
            "progresCalculat": progres,
            "estatCalculat": self._calcular_estat(progres)
        }

    def _calcular_estat(self, progres: float) -> str:
        if progres >= 80:
            return "assolit"
        if progres >= 40:
            return "en_progres"
        return "pendent"

    def _calcular_valor_kpi_usuari(
        self,
        kpi,
        idUsuari
    ):
        registres = self.registre_kpi_repository.get_by_kpi_and_usuari(
            kpi.idKPI,
            idUsuari
        )

        if not registres:
            return 0

        if getattr(kpi, "tipusCalcul", "acumulat") == "mitjana":
            return round(
                sum(r.valor for r in registres) / len(registres),
                2
            )

        return round(
            sum(r.valor for r in registres),
            2
        )