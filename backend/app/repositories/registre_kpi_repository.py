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

    def get_by_kpi_and_usuari(self, idKPI: int, idUsuari: int) -> list[RegistreKPI]:
        return [
            registre
            for registre in self.get_all()
            if registre.idKPI == idKPI and registre.idUsuari == idUsuari
        ]

    def get_by_id(self, idRegistre: int) -> RegistreKPI | None:
        for registre in self.get_all():
            if registre.idRegistre == idRegistre:
                return registre

        return None

    def _write_all(self, registres):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [registre.model_dump() for registre in registres],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        registres = self.get_all()

        if not registres:
            return 1

        return max(
            registre.idRegistre
            for registre in registres
        ) + 1

    def create(self, registre):
        registres = self.get_all()
        registres.append(registre)

        self._write_all(registres)

        return registre

    def update(
        self,
        idRegistre: int,
        registre_actualitzat
    ):
        registres = self.get_all()

        for index, registre in enumerate(registres):
            if registre.idRegistre == idRegistre:
                registres[index] = registre_actualitzat

                self._write_all(registres)

                return registre_actualitzat

        return None