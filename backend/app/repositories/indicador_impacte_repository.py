import json
from pathlib import Path

from app.models.indicador_impacte import IndicadorImpacte


class IndicadorImpacteRepository:
    def __init__(self):
        self.file_path = Path("app/data/indicador_impacte.json")

    def get_all(self) -> list[IndicadorImpacte]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [IndicadorImpacte(**item) for item in data]

    def get_by_programa(self, idPrograma: int) -> list[IndicadorImpacte]:
        return [
            indicador
            for indicador in self.get_all()
            if indicador.idPrograma == idPrograma
        ]

    def get_by_id(self, idIndicadorImpacte: int) -> IndicadorImpacte | None:
        for indicador in self.get_all():
            if indicador.idIndicadorImpacte == idIndicadorImpacte:
                return indicador

        return None

    def _write_all(self, indicadors):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [indicador.model_dump() for indicador in indicadors],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        indicadors = self.get_all()

        if not indicadors:
            return 1

        return max(
            indicador.idIndicadorImpacte
            for indicador in indicadors
        ) + 1

    def create(self, indicador):
        indicadors = self.get_all()
        indicadors.append(indicador)

        self._write_all(indicadors)

        return indicador

    def update(self, idIndicadorImpacte: int, indicador_actualitzat):
        indicadors = self.get_all()

        for index, indicador in enumerate(indicadors):
            if indicador.idIndicadorImpacte == idIndicadorImpacte:
                indicadors[index] = indicador_actualitzat

                self._write_all(indicadors)

                return indicador_actualitzat

        return None