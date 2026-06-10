import json
from pathlib import Path

from app.models.objectiu_pla import ObjectiuPla


class ObjectiuPlaRepository:
    def __init__(self):
        self.file_path = Path("app/data/objectiu_pla.json")

    def get_all(self) -> list[ObjectiuPla]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [ObjectiuPla(**item) for item in data]

    def get_by_pla(self, idPla: int) -> list[ObjectiuPla]:
        objectius = [
            objectiu
            for objectiu in self.get_all()
            if objectiu.idPla == idPla
        ]

        return sorted(objectius, key=lambda objectiu: objectiu.ordre)