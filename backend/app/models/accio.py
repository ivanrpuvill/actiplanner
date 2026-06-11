from pydantic import BaseModel


class AccioBase(BaseModel):
    idObjectiu: int
    titol: str
    descripcio: str
    dataInici: str
    dataFi: str


class AccioCreate(AccioBase):
    pass


class AccioUpdate(BaseModel):
    idObjectiu: int | None = None
    titol: str | None = None
    descripcio: str | None = None
    dataInici: str | None = None
    dataFi: str | None = None


class AccioRead(AccioBase):
    idAccio: int


class Accio(AccioRead):
    pass