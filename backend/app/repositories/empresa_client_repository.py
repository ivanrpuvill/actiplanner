import json
from pathlib import Path

from app.models.empresa_client import EmpresaClient


class EmpresaClientRepository:
    def __init__(self):
        self.file_path = Path("app/data/empresa_client.json")

    def get_all(self) -> list[EmpresaClient]:
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [EmpresaClient(**item) for item in data]

    def get_by_id(self, idEmpresa: int) -> EmpresaClient | None:
        for empresa in self.get_all():
            if empresa.idEmpresa == idEmpresa:
                return empresa

        return None