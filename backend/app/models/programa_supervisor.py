from pydantic import BaseModel


class ProgramaSupervisorBase(BaseModel):
    idPrograma: int
    idUsuari: int


class ProgramaSupervisorCreate(BaseModel):
    idUsuari: int


class ProgramaSupervisorUpdate(BaseModel):
    pass


class ProgramaSupervisorRead(ProgramaSupervisorBase):
    dataAssignacio: str


class ProgramaSupervisor(ProgramaSupervisorRead):
    pass