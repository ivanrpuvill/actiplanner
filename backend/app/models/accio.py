from pydantic import BaseModel


class AccioBase(BaseModel):
    idObjectiu: int
    titol: str
    descripcio: str
    dataInici: str
    dataFi: str
    actiu: bool = True


class AccioCreate(AccioBase):
    pass


class AccioUpdate(BaseModel):
    idObjectiu: int | None = None
    titol: str | None = None
    descripcio: str | None = None
    dataInici: str | None = None
    dataFi: str | None = None
    actiu: bool | None = None


class AccioRead(AccioBase):
    idAccio: int


class Accio(AccioRead):
    pass