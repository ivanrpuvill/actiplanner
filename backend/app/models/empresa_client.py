from pydantic import BaseModel


class EmpresaClient(BaseModel):
    idEmpresa: int
    nom: str
    sector: str | None = None
    contacte: str | None = None