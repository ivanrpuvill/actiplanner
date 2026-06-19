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
        return [
            objectiu
            for objectiu in self.get_all()
            if objectiu.idPla == idPla and objectiu.actiu
        ]

    def get_all_by_pla(self, idPla: int) -> list[ObjectiuPla]:
        return [
            objectiu
            for objectiu in self.get_all()
            if objectiu.idPla == idPla
        ]

    def get_by_id(self, idObjectiu: int) -> ObjectiuPla | None:
        for objectiu in self.get_all():
            if objectiu.idObjectiu == idObjectiu:
                return objectiu

        return None

    def _write_all(self, objectius):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [objectiu.model_dump() for objectiu in objectius],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        objectius = self.get_all()

        if not objectius:
            return 1

        return max(
            objectiu.idObjectiu
            for objectiu in objectius
        ) + 1

    def create(self, objectiu):
        objectius = self.get_all()
        objectius.append(objectiu)

        self._write_all(objectius)

        return objectiu

    def update(
        self,
        idObjectiu: int,
        objectiu_actualitzat
    ):
        objectius = self.get_all()

        for index, objectiu in enumerate(objectius):
            if objectiu.idObjectiu == idObjectiu:
                objectius[index] = objectiu_actualitzat

                self._write_all(objectius)

                return objectiu_actualitzat

        return None