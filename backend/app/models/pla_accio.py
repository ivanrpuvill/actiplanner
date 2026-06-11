from pydantic import BaseModel


class PlaAccioBase(BaseModel):
    idPrograma: int
    titol: str
    actiu: bool


class PlaAccioCreate(PlaAccioBase):
    pass


class PlaAccioUpdate(BaseModel):
    idPrograma: int | None = None
    titol: str | None = None
    actiu: bool | None = None


class PlaAccioRead(PlaAccioBase):
    idPla: int
    dataCreacio: str


class PlaAccio(PlaAccioRead):
    pass