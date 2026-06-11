from pydantic import BaseModel


class KPI(BaseModel):
    idKPI: int
    idAccio: int
    nom: str
    descripcio: str
    periodicitat: str