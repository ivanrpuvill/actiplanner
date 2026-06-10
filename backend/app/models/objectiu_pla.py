from pydantic import BaseModel


class ObjectiuPla(BaseModel):
    idObjectiu: int
    idPla: int
    titol: str
    descripcio: str
    ordre: int