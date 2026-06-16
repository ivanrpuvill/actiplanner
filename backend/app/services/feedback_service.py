from datetime import date
from app.models.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.programa_participant_repository import ProgramaParticipantRepository
from app.repositories.programa_supervisor_repository import ProgramaSupervisorRepository
from app.repositories.programa_formacio_repository import ProgramaFormacioRepository


class FeedbackService:
    def __init__(self):
        self.feedback_repository = FeedbackRepository()
        self.participant_repository = ProgramaParticipantRepository()
        self.supervisor_repository = ProgramaSupervisorRepository()
        self.programa_repository = ProgramaFormacioRepository()

    def get_feedbacks(self) -> list[Feedback]:
        return self.feedback_repository.get_all()

    def get_feedback(self, idFeedback: int) -> Feedback | None:
        return self.feedback_repository.get_by_id(idFeedback)

    def get_feedbacks_programa(self, idPrograma: int) -> list[Feedback]:
        return self.feedback_repository.get_by_programa(idPrograma)

    def get_feedbacks_participant(self, idUsuariParticipant: int) -> list[Feedback]:
        return self.feedback_repository.get_by_participant(idUsuariParticipant)

    def get_feedbacks_supervisor(self, idUsuariSupervisor: int) -> list[Feedback]:
        return self.feedback_repository.get_by_supervisor(idUsuariSupervisor)

    def get_feedbacks_programa_participant(
        self,
        idPrograma: int,
        idUsuariParticipant: int
    ) -> list[Feedback]:
        return self.feedback_repository.get_by_programa_participant(
            idPrograma,
            idUsuariParticipant
        )

    def create_feedback(self, feedback: FeedbackCreate) -> Feedback | None:
        if self.programa_repository.get_by_id(feedback.idPrograma) is None:
            raise ValueError("programa_no_trobat")

        es_supervisor = any(
            item.idPrograma == feedback.idPrograma
            and item.idUsuari == feedback.idUsuariSupervisor
            for item in self.supervisor_repository.get_all()
        )

        es_participant = any(
            item.idPrograma == feedback.idPrograma
            and item.idUsuari == feedback.idUsuariParticipant
            for item in self.participant_repository.get_all()
        )

        if not es_supervisor or not es_participant:
            return None

        nou_feedback = Feedback(
            idFeedback=self.feedback_repository.next_id(),
            dataCreacio=date.today().isoformat(),
            **feedback.model_dump()
        )

        return self.feedback_repository.create(nou_feedback)

    def update_feedback(self, idFeedback: int, feedback: FeedbackUpdate):
        feedback_actual = self.feedback_repository.get_by_id(idFeedback)

        if feedback_actual is None:
            return None

        data = feedback_actual.model_dump()
        data.update(feedback.model_dump(exclude_unset=True))
        data["idFeedback"] = idFeedback

        feedback_actualitzat = Feedback(**data)

        return self.feedback_repository.update(idFeedback, feedback_actualitzat)