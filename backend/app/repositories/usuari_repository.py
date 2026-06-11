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

    def _write_all(self, usuaris):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [usuari.model_dump() for usuari in usuaris],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        usuaris = self.get_all()
        if not usuaris:
            return 1
        return max(usuari.idUsuari for usuari in usuaris) + 1

    def create(self, usuari):
        usuaris = self.get_all()
        usuaris.append(usuari)
        self._write_all(usuaris)
        return usuari

    def update(self, idUsuari: int, usuari_actualitzat):
        usuaris = self.get_all()

        for index, usuari in enumerate(usuaris):
            if usuari.idUsuari == idUsuari:
                usuaris[index] = usuari_actualitzat
                self._write_all(usuaris)
                return usuari_actualitzat

        return None