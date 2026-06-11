import json
from pathlib import Path

from app.models.programa_formacio import ProgramaFormacio


class ProgramaFormacioRepository:
    def __init__(self):
        self.file_path = Path("app/data/programa_formacio.json")

    def get_all(self) -> list[ProgramaFormacio]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [ProgramaFormacio(**item) for item in data]

    def get_by_id(self, idPrograma: int) -> ProgramaFormacio | None:
        for programa in self.get_all():
            if programa.idPrograma == idPrograma:
                return programa
        return None

    def get_by_empresa(self, idEmpresa: int) -> list[ProgramaFormacio]:
        return [
            programa
            for programa in self.get_all()
            if programa.idEmpresa == idEmpresa
        ]

    def _write_all(self, programes):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [programa.model_dump() for programa in programes],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        programes = self.get_all()
        if not programes:
            return 1
        return max(programa.idPrograma for programa in programes) + 1

    def create(self, programa):
        programes = self.get_all()
        programes.append(programa)
        self._write_all(programes)
        return programa

    def update(self, idPrograma: int, programa_actualitzat):
        programes = self.get_all()

        for index, programa in enumerate(programes):
            if programa.idPrograma == idPrograma:
                programes[index] = programa_actualitzat
                self._write_all(programes)
                return programa_actualitzat

        return None