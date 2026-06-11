from app.models.empresa_client import EmpresaClient, EmpresaClientCreate, EmpresaClientUpdate
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

    def create_empresa(self, empresa: EmpresaClientCreate):
        data = empresa.model_dump()
        data["idEmpresa"] = self.empresa_repository.next_id()
        nova_empresa = EmpresaClient(**data)
        return self.empresa_repository.create(nova_empresa)

    def update_empresa(self, idEmpresa: int, empresa: EmpresaClientUpdate):
        empresa_actual = self.empresa_repository.get_by_id(idEmpresa)

        if empresa_actual is None:
            return None

        data = empresa_actual.model_dump()
        data.update(empresa.model_dump(exclude_unset=True))
        data["idEmpresa"] = idEmpresa

        empresa_actualitzada = EmpresaClient(**data)
        return self.empresa_repository.update(idEmpresa, empresa_actualitzada)