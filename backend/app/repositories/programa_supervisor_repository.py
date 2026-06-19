import json
from pathlib import Path

from app.models.programa_supervisor import ProgramaSupervisor


class ProgramaSupervisorRepository:
    def __init__(self):
        self.file_path = Path("app/data/programa_supervisor.json")

    def get_all(self) -> list[ProgramaSupervisor]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [ProgramaSupervisor(**item) for item in data]

    def get_by_programa(self, idPrograma: int) -> list[ProgramaSupervisor]:
        return [
            item
            for item in self.get_all()
            if item.idPrograma == idPrograma and item.actiu
        ]

    def get_all_by_programa(self, idPrograma: int) -> list[ProgramaSupervisor]:
        return [
            item
            for item in self.get_all()
            if item.idPrograma == idPrograma
        ]

    def get_by_usuari(self, idUsuari: int) -> list[ProgramaSupervisor]:
        return [
            item
            for item in self.get_all()
            if item.idUsuari == idUsuari
        ]

    def get_by_programa_usuari(self, idPrograma: int, idUsuari: int) -> ProgramaSupervisor | None:
        for item in self.get_all():
            if item.idPrograma == idPrograma and item.idUsuari == idUsuari:
                return item

        return None

    def _write_all(self, supervisors):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [supervisor.model_dump() for supervisor in supervisors],
                file,
                ensure_ascii=False,
                indent=2
            )

    def create(self, supervisor):
        supervisors = self.get_all()

        ja_existeix = any(
            s.idPrograma == supervisor.idPrograma and
            s.idUsuari == supervisor.idUsuari
            for s in supervisors
        )

        if ja_existeix:
            return None

        supervisors.append(supervisor)
        self._write_all(supervisors)
        return supervisor

    def update(self, idPrograma: int, idUsuari: int, supervisor_actualitzat):
        supervisors = self.get_all()

        for index, supervisor in enumerate(supervisors):
            if (
                supervisor.idPrograma == idPrograma and
                supervisor.idUsuari == idUsuari
            ):
                supervisors[index] = supervisor_actualitzat
                self._write_all(supervisors)
                return supervisor_actualitzat

        return None