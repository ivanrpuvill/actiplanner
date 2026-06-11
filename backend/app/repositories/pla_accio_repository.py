import json
from pathlib import Path

from app.models.pla_accio import PlaAccio


class PlaAccioRepository:
    def __init__(self):
        self.file_path = Path("app/data/pla_accio.json")

    def get_all(self) -> list[PlaAccio]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [PlaAccio(**item) for item in data]

    def get_by_id(self, idPla: int) -> PlaAccio | None:
        for pla in self.get_all():
            if pla.idPla == idPla:
                return pla

        return None

    def get_by_programa(self, idPrograma: int) -> list[PlaAccio]:
        return [
            pla
            for pla in self.get_all()
            if pla.idPrograma == idPrograma
        ]

    def _write_all(self, plans):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [pla.model_dump() for pla in plans],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        plans = self.get_all()

        if not plans:
            return 1

        return max(pla.idPla for pla in plans) + 1

    def create(self, pla):
        plans = self.get_all()
        plans.append(pla)

        self._write_all(plans)

        return pla

    def update(self, idPla: int, pla_actualitzat):
        plans = self.get_all()

        for index, pla in enumerate(plans):
            if pla.idPla == idPla:
                plans[index] = pla_actualitzat

                self._write_all(plans)

                return pla_actualitzat

        return None