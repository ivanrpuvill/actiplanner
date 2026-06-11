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

    def _write_all(self, empreses):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [empresa.model_dump() for empresa in empreses],
                file,
                ensure_ascii=False,
                indent=2
            )

    def next_id(self):
        empreses = self.get_all()
        if not empreses:
            return 1
        return max(empresa.idEmpresa for empresa in empreses) + 1

    def create(self, empresa):
        empreses = self.get_all()
        empreses.append(empresa)
        self._write_all(empreses)
        return empresa

    def update(self, idEmpresa: int, empresa_actualitzada):
        empreses = self.get_all()

        for index, empresa in enumerate(empreses):
            if empresa.idEmpresa == idEmpresa:
                empreses[index] = empresa_actualitzada
                self._write_all(empreses)
                return empresa_actualitzada

        return None