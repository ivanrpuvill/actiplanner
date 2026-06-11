import json
from pathlib import Path

from app.models.seguiment_objectiu import SeguimentObjectiu


class SeguimentObjectiuRepository:
    def __init__(self):
        self.file_path = Path("app/data/seguiment_objectiu.json")

    def get_all(self) -> list[SeguimentObjectiu]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [SeguimentObjectiu(**item) for item in data]

    def get_by_objectiu(self, idObjectiu: int) -> list[SeguimentObjectiu]:
        return [
            seguiment
            for seguiment in self.get_all()
            if seguiment.idObjectiu == idObjectiu
        ]

    def get_by_usuari(self, idUsuari: int) -> list[SeguimentObjectiu]:
        return [
            seguiment
            for seguiment in self.get_all()
            if seguiment.idUsuari == idUsuari
        ]

    def get_by_programa_usuari(
        self,
        idPrograma: int,
        idUsuari: int
    ) -> list[SeguimentObjectiu]:
        return [
            seguiment
            for seguiment in self.get_all()
            if seguiment.idPrograma == idPrograma
            and seguiment.idUsuari == idUsuari
        ]

    def get_by_objectiu_usuari(
        self,
        idObjectiu: int,
        idUsuari: int
    ) -> SeguimentObjectiu | None:
        for seguiment in self.get_all():
            if (
                seguiment.idObjectiu == idObjectiu
                and seguiment.idUsuari == idUsuari
            ):
                return seguiment

        return None