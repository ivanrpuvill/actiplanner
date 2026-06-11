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