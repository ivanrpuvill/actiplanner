from enum import Enum
from pydantic import BaseModel


class MomentMesura(str, Enum):
    pre = "pre"
    post = "post"


class RegistreImpacteBase(BaseModel):
    idIndicadorImpacte: int
    idPrograma: int
    idUsuari: int
    moment: MomentMesura
    valor: float
    comentari: str | None = None


class RegistreImpacteCreate(RegistreImpacteBase):
    pass


class RegistreImpacteUpdate(BaseModel):
    idIndicadorImpacte: int | None = None
    idPrograma: int | None = None
    idUsuari: int | None = None
    moment: MomentMesura | None = None
    valor: float | None = None
    comentari: str | None = None
    dataRegistre: str | None = None


class RegistreImpacteRead(RegistreImpacteBase):
    idRegistreImpacte: int
    dataRegistre: str


class RegistreImpacte(RegistreImpacteRead):
    pass