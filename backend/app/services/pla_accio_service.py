from app.repositories.pla_accio_repository import PlaAccioRepository
from app.repositories.objectiu_pla_repository import ObjectiuPlaRepository
from app.repositories.accio_repository import AccioRepository
from app.repositories.kpi_repository import KPIRepository
from app.repositories.registre_kpi_repository import RegistreKPIRepository


class PlaAccioService:
    def __init__(self):
        self.pla_repository = PlaAccioRepository()
        self.objectiu_repository = ObjectiuPlaRepository()
        self.accio_repository = AccioRepository()
        self.kpi_repository = KPIRepository()
        self.registre_kpi_repository = RegistreKPIRepository()

    def get_pla_detallat(self, idPla: int) -> dict | None:
        pla = self.pla_repository.get_by_id(idPla)

        if pla is None:
            return None

        objectius = self.objectiu_repository.get_by_pla(idPla)
        objectius_detallats = []
        progres_objectius = []

        for objectiu in objectius:
            accions = self.accio_repository.get_by_objectiu(objectiu.idObjectiu)
            accions_detallades = []
            valors_accions = []

            for accio in accions:
                kpis = self.kpi_repository.get_by_accio(accio.idAccio)
                kpis_detallats = []
                valors_kpi = []

                for kpi in kpis:
                    ultim_registre = self.registre_kpi_repository.get_ultim_by_kpi(kpi.idKPI)
                    ultim_valor = ultim_registre.valor if ultim_registre else 0

                    valors_kpi.append(ultim_valor)

                    kpis_detallats.append({
                        "idKPI": kpi.idKPI,
                        "nom": kpi.nom,
                        "descripcio": kpi.descripcio,
                        "periodicitat": kpi.periodicitat,
                        "ultimValor": ultim_valor,
                        "dataUltimRegistre": ultim_registre.dataRegistre if ultim_registre else None
                    })

                progres_accio = self._calcular_mitjana(valors_kpi)
                valors_accions.append(progres_accio)

                accions_detallades.append({
                    "idAccio": accio.idAccio,
                    "titol": accio.titol,
                    "descripcio": accio.descripcio,
                    "dataInici": accio.dataInici,
                    "dataFi": accio.dataFi,
                    "progresAccio": progres_accio,
                    "estatAccio": self._calcular_estat(progres_accio),
                    "kpis": kpis_detallats
                })

            progres_objectiu = self._calcular_mitjana(valors_accions)
            progres_objectius.append(progres_objectiu)

            objectius_detallats.append({
                "idObjectiu": objectiu.idObjectiu,
                "descripcio": objectiu.descripcio,
                "valor": objectiu.valor,
                "progresObjectiu": progres_objectiu,
                "estatObjectiu": self._calcular_estat(progres_objectiu),
                "accions": accions_detallades
            })

        progres_pla = self._calcular_mitjana(progres_objectius)

        return {
            "idPla": pla.idPla,
            "idPrograma": pla.idPrograma,
            "titol": pla.titol,
            "dataCreacio": pla.dataCreacio,
            "actiu": pla.actiu,
            "progresPla": progres_pla,
            "estatPla": self._calcular_estat(progres_pla),
            "objectius": objectius_detallats
        }

    def _calcular_mitjana(self, valors: list[float]) -> float:
        if not valors:
            return 0

        return round(sum(valors) / len(valors), 2)

    def _calcular_estat(self, progres: float) -> str:
        if progres >= 80:
            return "assolit"
        if progres >= 40:
            return "en_progres"
        return "pendent"