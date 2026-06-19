from pydantic import BaseModel


class ObjectiuPlaBase(BaseModel):
    idPla: int
    descripcio: str
    valor: float
    actiu: bool = True


class ObjectiuPlaCreate(ObjectiuPlaBase):
    pass


class ObjectiuPlaUpdate(BaseModel):
    idPla: int | None = None
    descripcio: str | None = None
    valor: float | None = None
    actiu: bool | None = None


class ObjectiuPlaRead(ObjectiuPlaBase):
    idObjectiu: int


class ObjectiuPla(ObjectiuPlaRead):
    pass