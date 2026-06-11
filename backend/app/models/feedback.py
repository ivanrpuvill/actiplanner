from pydantic import BaseModel


class FeedbackBase(BaseModel):
    idPrograma: int
    idUsuariSupervisor: int
    idUsuariParticipant: int
    comentari: str
    validacio: bool = False


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    idPrograma: int | None = None
    idUsuariSupervisor: int | None = None
    idUsuariParticipant: int | None = None
    comentari: str | None = None
    validacio: bool | None = None
    dataCreacio: str | None = None


class FeedbackRead(FeedbackBase):
    idFeedback: int
    dataCreacio: str


class Feedback(FeedbackRead):
    pass