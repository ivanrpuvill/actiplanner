from app.models.programa_formacio import ProgramaFormacio, ProgramaFormacioCreate, ProgramaFormacioUpdate
from app.repositories.programa_formacio_repository import ProgramaFormacioRepository


class ProgramaFormacioService:
    def __init__(self):
        self.repository = ProgramaFormacioRepository()

    def get_programes(self):
        return self.repository.get_all()

    def get_programa(self, idPrograma: int):
        return self.repository.get_by_id(idPrograma)

    def create_programa(self, programa: ProgramaFormacioCreate):
        nou_programa = ProgramaFormacio(
            idPrograma=self.repository.next_id(),
            **programa.model_dump()
        )

        return self.repository.create(nou_programa)

    def update_programa(self, idPrograma: int, programa: ProgramaFormacioUpdate):
        programa_actual = self.repository.get_by_id(idPrograma)

        if programa_actual is None:
            return None

        data = programa_actual.model_dump()
        data.update(programa.model_dump(exclude_unset=True))
        data["idPrograma"] = idPrograma

        programa_actualitzat = ProgramaFormacio(**data)

        return self.repository.update(idPrograma, programa_actualitzat)