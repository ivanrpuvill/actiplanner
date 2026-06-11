from app.models.empresa_client import EmpresaClient
from app.repositories.empresa_client_repository import EmpresaClientRepository
from app.repositories.programa_formacio_repository import ProgramaFormacioRepository


class EmpresaClientService:
    def __init__(self):
        self.empresa_repository = EmpresaClientRepository()
        self.programa_repository = ProgramaFormacioRepository()

    def get_empreses(self) -> list[EmpresaClient]:
        return self.empresa_repository.get_all()

    def get_empresa(self, idEmpresa: int) -> EmpresaClient | None:
        return self.empresa_repository.get_by_id(idEmpresa)

    def get_programes_empresa(self, idEmpresa: int) -> list:
        empresa = self.empresa_repository.get_by_id(idEmpresa)

        if empresa is None:
            return []

        return self.programa_repository.get_by_empresa(idEmpresa)