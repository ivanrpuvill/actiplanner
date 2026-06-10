from pydantic import BaseModel


class PlaAccio(BaseModel):
    idPla: int
    idPrograma: int
    titol: str
    descripcio: str
    dataCreacio: str
    actiu: bool