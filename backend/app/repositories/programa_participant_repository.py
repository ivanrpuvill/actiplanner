import json
from pathlib import Path

from app.models.programa_participant import ProgramaParticipant


class ProgramaParticipantRepository:
    def __init__(self):
        self.file_path = Path("app/data/programa_participant.json")

    def get_all(self) -> list[ProgramaParticipant]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [ProgramaParticipant(**item) for item in data]

    def get_by_programa(self, idPrograma: int) -> list[ProgramaParticipant]:
        return [
            item
            for item in self.get_all()
            if item.idPrograma == idPrograma
        ]

    def get_by_usuari(self, idUsuari: int) -> list[ProgramaParticipant]:
        return [
            item
            for item in self.get_all()
            if item.idUsuari == idUsuari
        ]

    def _write_all(self, participants):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [participant.model_dump() for participant in participants],
                file,
                ensure_ascii=False,
                indent=2
            )

    def create(self, participant):
        participants = self.get_all()

        ja_existeix = any(
            p.idPrograma == participant.idPrograma and
            p.idUsuari == participant.idUsuari
            for p in participants
        )

        if ja_existeix:
            return None

        participants.append(participant)
        self._write_all(participants)
        return participant

    def update(self, idPrograma: int, idUsuari: int, participant_actualitzat):
        participants = self.get_all()

        for index, participant in enumerate(participants):
            if (
                participant.idPrograma == idPrograma and
                participant.idUsuari == idUsuari
            ):
                participants[index] = participant_actualitzat
                self._write_all(participants)
                return participant_actualitzat

        return None