import json
from pathlib import Path

from app.models.registre_kpi import RegistreKPI


class RegistreKPIRepository:
    def __init__(self):
        self.file_path = Path("app/data/registre_kpi.json")

    def get_all(self) -> list[RegistreKPI]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [RegistreKPI(**item) for item in data]

    def get_by_kpi(self, idKPI: int) -> list[RegistreKPI]:
        return [
            registre
            for registre in self.get_all()
            if registre.idKPI == idKPI
        ]

    def get_ultim_by_kpi(self, idKPI: int) -> RegistreKPI | None:
        registres = self.get_by_kpi(idKPI)

        if not registres:
            return None

        return sorted(
            registres,
            key=lambda registre: registre.dataRegistre,
            reverse=True
        )[0]