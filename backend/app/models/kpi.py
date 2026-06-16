from enum import Enum
from pydantic import BaseModel


class TipusKPI(str, Enum):
    numeric = "numeric"
    percentatge = "percentatge"
    escala = "escala"
    boolea = "boolea"


class TipusCalculKPI(str, Enum):
    acumulat = "acumulat"
    mitjana = "mitjana"
    ultim = "ultim"


class OrientacioKPI(str, Enum):
    major_millor = "major_millor"
    menor_millor = "menor_millor"


class KPIBase(BaseModel):
    idAccio: int
    nom: str
    descripcio: str
    periodicitat: str
    tipus: TipusKPI = TipusKPI.numeric
    tipusCalcul: TipusCalculKPI = TipusCalculKPI.acumulat
    orientacio: OrientacioKPI = OrientacioKPI.major_millor
    valorMinim: float | None = 0
    valorMaxim: float | None = None
    valorObjectiu: float | None = None


class KPICreate(KPIBase):
    pass


class KPIUpdate(BaseModel):
    idAccio: int | None = None
    nom: str | None = None
    descripcio: str | None = None
    periodicitat: str | None = None
    tipus: TipusKPI | None = None
    tipusCalcul: TipusCalculKPI | None = None
    orientacio: OrientacioKPI | None = None
    valorMinim: float | None = None
    valorMaxim: float | None = None
    valorObjectiu: float | None = None


class KPIRead(KPIBase):
    idKPI: int


class KPI(KPIRead):
    pass