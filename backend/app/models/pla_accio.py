from pydantic import BaseModel


class PlaAccio(BaseModel):
    idPla: int
    idPrograma: int
    titol: str
    dataCreacio: str
    actiu: bool