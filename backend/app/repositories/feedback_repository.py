import json
from pathlib import Path

from app.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self):
        self.file_path = Path("app/data/feedback.json")

    def get_all(self) -> list[Feedback]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [Feedback(**item) for item in data]

    def get_by_id(self, idFeedback: int) -> Feedback | None:
        for feedback in self.get_all():
            if feedback.idFeedback == idFeedback:
                return feedback

        return None

    def get_by_programa(self, idPrograma: int) -> list[Feedback]:
        return [
            feedback
            for feedback in self.get_all()
            if feedback.idPrograma == idPrograma
        ]

    def get_by_participant(self, idUsuariParticipant: int) -> list[Feedback]:
        return [
            feedback
            for feedback in self.get_all()
            if feedback.idUsuariParticipant == idUsuariParticipant
        ]

    def get_by_supervisor(self, idUsuariSupervisor: int) -> list[Feedback]:
        return [
            feedback
            for feedback in self.get_all()
            if feedback.idUsuariSupervisor == idUsuariSupervisor
        ]

    def get_by_programa_participant(
        self,
        idPrograma: int,
        idUsuariParticipant: int
    ) -> list[Feedback]:
        return [
            feedback
            for feedback in self.get_all()
            if feedback.idPrograma == idPrograma
            and feedback.idUsuariParticipant == idUsuariParticipant
        ]

    def create(self, nou_feedback: Feedback) -> Feedback:
        feedbacks = self.get_all()
        feedbacks.append(nou_feedback)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [feedback.model_dump() for feedback in feedbacks],
                file,
                ensure_ascii=False,
                indent=2
            )

        return nou_feedback