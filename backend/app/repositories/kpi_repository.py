import json
from pathlib import Path

from app.models.kpi import KPI


class KPIRepository:
    def __init__(self):
        self.file_path = Path("app/data/kpi.json")

    def get_all(self) -> list[KPI]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [KPI(**item) for item in data]

    def get_by_accio(self, idAccio: int) -> list[KPI]:
        return [
            kpi
            for kpi in self.get_all()
            if kpi.idAccio == idAccio
        ]
    
    def get_by_id(self, idKPI: int) -> KPI | None:
        for kpi in self.get_all():
            if kpi.idKPI == idKPI:
                return kpi

        return None