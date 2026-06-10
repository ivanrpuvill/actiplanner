from pydantic import BaseModel


class ProgramaParticipant(BaseModel):
    idPrograma: int
    idUsuari: int
    estatParticipacio: str
    dataAssignacio: str