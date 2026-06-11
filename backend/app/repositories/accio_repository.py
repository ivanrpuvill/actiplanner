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

    def get_by_id(self, idAccio: int) -> Accio | None:
        for accio in self.get_all():
            if accio.idAccio == idAccio:
                return accio

        return None

    def _write_all(self, accions):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [accio.model_dump() for accio in accions],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        accions = self.get_all()

        if not accions:
            return 1

        return max(accio.idAccio for accio in accions) + 1

    def create(self, accio):
        accions = self.get_all()
        accions.append(accio)

        self._write_all(accions)

        return accio

    def update(self, idAccio: int, accio_actualitzada):
        accions = self.get_all()

        for index, accio in enumerate(accions):
            if accio.idAccio == idAccio:
                accions[index] = accio_actualitzada

                self._write_all(accions)

                return accio_actualitzada

        return None