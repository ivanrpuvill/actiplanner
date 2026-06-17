from enum import Enum
from pydantic import BaseModel


class OrientacioImpacte(str, Enum):
    major_millor = "major_millor"
    menor_millor = "menor_millor"


class IndicadorImpacteBase(BaseModel):
    idPrograma: int
    nom: str
    descripcio: str
    unitat: str
    orientacio: OrientacioImpacte = OrientacioImpacte.major_millor
    fontDades: str


class IndicadorImpacteCreate(IndicadorImpacteBase):
    pass


class IndicadorImpacteUpdate(BaseModel):
    idPrograma: int | None = None
    nom: str | None = None
    descripcio: str | None = None
    unitat: str | None = None
    orientacio: OrientacioImpacte | None = None
    fontDades: str | None = None


class IndicadorImpacteRead(IndicadorImpacteBase):
    idIndicadorImpacte: int


class IndicadorImpacte(IndicadorImpacteRead):
    pass