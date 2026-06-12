from pydantic import BaseModel


class KPIBase(BaseModel):
    idAccio: int
    nom: str
    descripcio: str
    periodicitat: str
    tipusCalcul: str = "acumulat"


class KPICreate(KPIBase):
    pass


class KPIUpdate(BaseModel):
    idAccio: int | None = None
    nom: str | None = None
    descripcio: str | None = None
    periodicitat: str | None = None
    tipusCalcul: str | None = None


class KPIRead(KPIBase):
    idKPI: int


class KPI(KPIRead):
    pass