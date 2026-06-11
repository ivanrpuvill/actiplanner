from app.models.programa_formacio import ProgramaFormacio
from app.repositories.programa_formacio_repository import ProgramaFormacioRepository


class ProgramaFormacioService:
    def __init__(self):
        self.repository = ProgramaFormacioRepository()

    def get_programes(self):
        return self.repository.get_all()

    def get_programa(self, idPrograma: int):
        return self.repository.get_by_id(idPrograma)

    def create_programa(self, programa: ProgramaFormacio):
        data = programa.model_dump()
        data["idPrograma"] = self.repository.next_id()

        nou_programa = ProgramaFormacio(**data)

        return self.repository.create(nou_programa)

    def update_programa(self, idPrograma: int, programa: ProgramaFormacio):
        data = programa.model_dump()
        data["idPrograma"] = idPrograma

        programa_actualitzat = ProgramaFormacio(**data)

        return self.repository.update(idPrograma, programa_actualitzat)