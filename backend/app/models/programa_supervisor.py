from pydantic import BaseModel


class ProgramaSupervisorBase(BaseModel):
    idPrograma: int
    idUsuari: int
    actiu: bool = True


class ProgramaSupervisorCreate(BaseModel):
    idUsuari: int


class ProgramaSupervisorUpdate(BaseModel):
    actiu: bool | None = None


class ProgramaSupervisorRead(ProgramaSupervisorBase):
    dataAssignacio: str


class ProgramaSupervisor(ProgramaSupervisorRead):
    pass