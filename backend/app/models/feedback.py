from pydantic import BaseModel


class Feedback(BaseModel):
    idFeedback: int
    idPrograma: int
    idUsuariSupervisor: int
    idUsuariParticipant: int
    comentari: str
    validacio: bool
    dataCreacio: str