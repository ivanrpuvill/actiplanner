from pydantic import BaseModel


class ObjectiuPla(BaseModel):
    idObjectiu: int
    idPla: int
    descripcio: str
    valor: float