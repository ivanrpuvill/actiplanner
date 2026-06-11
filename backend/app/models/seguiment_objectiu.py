from pydantic import BaseModel


class SeguimentObjectiuBase(BaseModel):
    idObjectiu: int
    idPrograma: int
    idUsuari: int


class SeguimentObjectiuCreate(SeguimentObjectiuBase):
    pass


class SeguimentObjectiuUpdate(BaseModel):
    idObjectiu: int | None = None
    idPrograma: int | None = None
    idUsuari: int | None = None


class SeguimentObjectiuRead(SeguimentObjectiuBase):
    idSeguiment: int


class SeguimentObjectiu(SeguimentObjectiuRead):
    pass