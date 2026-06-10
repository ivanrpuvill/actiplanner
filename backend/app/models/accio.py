from pydantic import BaseModel


class Accio(BaseModel):
    idAccio: int
    idObjectiu: int
    titol: str
    descripcio: str
    dataInici: str
    dataFi: str
    obligatoria: bool