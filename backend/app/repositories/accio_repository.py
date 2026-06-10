import json
from pathlib import Path

from app.models.accio import Accio


class AccioRepository:
    def __init__(self):
        self.file_path = Path("app/data/accio.json")

    def get_all(self) -> list[Accio]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [Accio(**item) for item in data]

    def get_by_objectiu(self, idObjectiu: int) -> list[Accio]:
        return [
            accio
            for accio in self.get_all()
            if accio.idObjectiu == idObjectiu
        ]