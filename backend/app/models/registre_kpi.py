from pydantic import BaseModel


class RegistreKPI(BaseModel):
    idRegistre: int
    idKPI: int
    idPrograma: int
    idUsuari: int
    valor: float
    dataRegistre: str