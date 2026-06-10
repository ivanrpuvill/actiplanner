from pydantic import BaseModel


class ProgramaSupervisor(BaseModel):
    idPrograma: int
    idUsuari: int
    dataAssignacio: str