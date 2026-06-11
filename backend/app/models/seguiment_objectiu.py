from pydantic import BaseModel


class SeguimentObjectiu(BaseModel):
    idSeguiment: int
    idObjectiu: int
    idPrograma: int
    idUsuari: int