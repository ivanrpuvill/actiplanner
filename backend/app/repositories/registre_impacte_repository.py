import json
from pathlib import Path

from app.models.registre_impacte import RegistreImpacte


class RegistreImpacteRepository:
    def __init__(self):
        self.file_path = Path("app/data/registre_impacte.json")

    def get_all(self) -> list[RegistreImpacte]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [RegistreImpacte(**item) for item in data]

    def get_by_indicador(self, idIndicadorImpacte: int) -> list[RegistreImpacte]:
        return [
            registre
            for registre in self.get_all()
            if registre.idIndicadorImpacte == idIndicadorImpacte
        ]

    def get_by_indicador_and_usuari(
        self,
        idIndicadorImpacte: int,
        idUsuari: int
    ) -> list[RegistreImpacte]:
        return [
            registre
            for registre in self.get_all()
            if registre.idIndicadorImpacte == idIndicadorImpacte
            and registre.idUsuari == idUsuari
        ]

    def get_by_programa(self, idPrograma: int) -> list[RegistreImpacte]:
        return [
            registre
            for registre in self.get_all()
            if registre.idPrograma == idPrograma
        ]

    def get_by_programa_and_usuari(
        self,
        idPrograma: int,
        idUsuari: int
    ) -> list[RegistreImpacte]:
        return [
            registre
            for registre in self.get_all()
            if registre.idPrograma == idPrograma
            and registre.idUsuari == idUsuari
        ]

    def get_by_id(self, idRegistreImpacte: int) -> RegistreImpacte | None:
        for registre in self.get_all():
            if registre.idRegistreImpacte == idRegistreImpacte:
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
            registre.idRegistreImpacte
            for registre in registres
        ) + 1

    def create(self, registre):
        registres = self.get_all()
        registres.append(registre)

        self._write_all(registres)

        return registre

    def update(self, idRegistreImpacte: int, registre_actualitzat):
        registres = self.get_all()

        for index, registre in enumerate(registres):
            if registre.idRegistreImpacte == idRegistreImpacte:
                registres[index] = registre_actualitzat

                self._write_all(registres)

                return registre_actualitzat

        return None