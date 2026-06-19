from pydantic import BaseModel


class EmpresaClientBase(BaseModel):
    nom: str
    sector: str | None = None
    contacte: str | None = None
    actiu: bool = True


class EmpresaClientCreate(EmpresaClientBase):
    pass


class EmpresaClientUpdate(BaseModel):
    nom: str | None = None
    sector: str | None = None
    contacte: str | None = None
    actiu: bool | None = None


class EmpresaClientRead(EmpresaClientBase):
    idEmpresa: int


class EmpresaClient(EmpresaClientRead):
    pass