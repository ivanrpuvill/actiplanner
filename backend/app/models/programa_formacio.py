from pydantic import BaseModel


class ProgramaFormacioBase(BaseModel):
    idEmpresa: int
    nom: str
    descripcio: str
    dataInici: str
    dataFi: str
    actiu: bool


class ProgramaFormacioCreate(ProgramaFormacioBase):
    pass


class ProgramaFormacioUpdate(BaseModel):
    idEmpresa: int | None = None
    nom: str | None = None
    descripcio: str | None = None
    dataInici: str | None = None
    dataFi: str | None = None
    actiu: bool | None = None


class ProgramaFormacioRead(ProgramaFormacioBase):
    idPrograma: int


class ProgramaFormacio(ProgramaFormacioRead):
    pass