from pydantic import BaseModel


class ProgramaFormacio(BaseModel):
    idPrograma: int
    idEmpresa: int
    nom: str
    descripcio: str
    dataInici: str
    dataFi: str
    actiu: bool