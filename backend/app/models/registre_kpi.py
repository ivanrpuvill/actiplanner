from pydantic import BaseModel


class RegistreKPIBase(BaseModel):
    idKPI: int
    idPrograma: int
    idUsuari: int
    valor: float
    comentari: str | None = None


class RegistreKPICreate(RegistreKPIBase):
    pass


class RegistreKPIUpdate(BaseModel):
    idKPI: int | None = None
    idPrograma: int | None = None
    idUsuari: int | None = None
    valor: float | None = None
    comentari: str | None = None
    dataRegistre: str | None = None


class RegistreKPIRead(RegistreKPIBase):
    idRegistre: int
    dataRegistre: str


class RegistreKPI(RegistreKPIRead):
    pass