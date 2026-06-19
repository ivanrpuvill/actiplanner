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
            if kpi.idAccio == idAccio and kpi.actiu
        ]

    def get_all_by_accio(self, idAccio: int) -> list[KPI]:
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

    def _write_all(self, kpis):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [kpi.model_dump() for kpi in kpis],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        kpis = self.get_all()

        if not kpis:
            return 1

        return max(kpi.idKPI for kpi in kpis) + 1

    def create(self, kpi):
        kpis = self.get_all()
        kpis.append(kpi)

        self._write_all(kpis)

        return kpi

    def update(self, idKPI: int, kpi_actualitzat):
        kpis = self.get_all()

        for index, kpi in enumerate(kpis):
            if kpi.idKPI == idKPI:
                kpis[index] = kpi_actualitzat

                self._write_all(kpis)

                return kpi_actualitzat

        return None