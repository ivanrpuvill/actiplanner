from app.repositories.kpi_repository import KPIRepository
from app.repositories.registre_kpi_repository import RegistreKPIRepository


class KPIService:
    def __init__(self):
        self.kpi_repository = KPIRepository()
        self.registre_kpi_repository = RegistreKPIRepository()

    def get_kpi(self, idKPI: int):
        return self.kpi_repository.get_by_id(idKPI)

    def get_registres_kpi(self, idKPI: int):
        return self.registre_kpi_repository.get_by_kpi(idKPI)

    def get_registres_kpi_usuari(self, idKPI: int, idUsuari: int):
        return self.registre_kpi_repository.get_by_kpi_and_usuari(idKPI, idUsuari)

    def get_evolucio_kpi(self, idKPI: int):
        registres = self.registre_kpi_repository.get_by_kpi(idKPI)

        registres_ordenats = sorted(
            registres,
            key=lambda registre: registre.dataRegistre
        )

        return [
            {
                "idRegistre": registre.idRegistre,
                "idKPI": registre.idKPI,
                "idPrograma": registre.idPrograma,
                "idUsuari": registre.idUsuari,
                "valor": registre.valor,
                "dataRegistre": registre.dataRegistre
            }
            for registre in registres_ordenats
        ]