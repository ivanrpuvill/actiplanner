import json
from pathlib import Path

from app.models.usuari import Usuari


class UsuariRepository:
    def __init__(self):
        self.file_path = Path("app/data/usuari.json")

    def get_all(self) -> list[Usuari]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [Usuari(**item) for item in data]

    def get_by_id(self, idUsuari: int) -> Usuari | None:
        for usuari in self.get_all():
            if usuari.idUsuari == idUsuari:
                return usuari

        return None

    def get_administradors(self) -> list[Usuari]:
        return [
            usuari
            for usuari in self.get_all()
            if usuari.esAdministrador and usuari.actiu
        ]