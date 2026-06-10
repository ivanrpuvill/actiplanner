from app.repositories.programa_formacio_repository import ProgramaFormacioRepository
from app.repositories.pla_accio_repository import PlaAccioRepository
from app.repositories.objectiu_pla_repository import ObjectiuPlaRepository
from app.repositories.accio_repository import AccioRepository


class PlaAccioService:
    def __init__(self):
        self.programa_repository = ProgramaFormacioRepository()
        self.pla_repository = PlaAccioRepository()
        self.objectiu_repository = ObjectiuPlaRepository()
        self.accio_repository = AccioRepository()

    def get_programes_empresa(self, idEmpresa: int) -> list:
        return self.programa_repository.get_by_empresa(idEmpresa)

    def get_plans_programa(self, idPrograma: int) -> list:
        programa = self.programa_repository.get_by_id(idPrograma)

        if programa is None:
            return []

        return self.pla_repository.get_by_programa(idPrograma)

    def get_pla_detallat(self, idPla: int) -> dict | None:
        pla = self.pla_repository.get_by_id(idPla)

        if pla is None:
            return None

        objectius = self.objectiu_repository.get_by_pla(idPla)

        objectius_detallats = []

        for objectiu in objectius:
            accions = self.accio_repository.get_by_objectiu(objectiu.idObjectiu)

            objectius_detallats.append({
                "idObjectiu": objectiu.idObjectiu,
                "idPla": objectiu.idPla,
                "titol": objectiu.titol,
                "descripcio": objectiu.descripcio,
                "ordre": objectiu.ordre,
                "accions": accions
            })

        return {
            "idPla": pla.idPla,
            "idPrograma": pla.idPrograma,
            "titol": pla.titol,
            "descripcio": pla.descripcio,
            "dataCreacio": pla.dataCreacio,
            "actiu": pla.actiu,
            "objectius": objectius_detallats
        }