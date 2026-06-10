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