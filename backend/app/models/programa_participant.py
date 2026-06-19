from pydantic import BaseModel


class ProgramaParticipantBase(BaseModel):
    idPrograma: int
    idUsuari: int
    estatParticipacio: str
    actiu: bool = True


class ProgramaParticipantCreate(BaseModel):
    idUsuari: int
    estatParticipacio: str


class ProgramaParticipantUpdate(BaseModel):
    estatParticipacio: str | None = None
    actiu: bool | None = None


class ProgramaParticipantRead(ProgramaParticipantBase):
    dataAssignacio: str


class ProgramaParticipant(ProgramaParticipantRead):
    pass