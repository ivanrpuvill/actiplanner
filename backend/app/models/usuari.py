from pydantic import BaseModel


class Usuari(BaseModel):
    idUsuari: int
    idEmpresa: int
    nom: str
    cognoms: str
    passwordHash: str
    telefon: str | None = None
    email: str
    esAdministrador: bool
    actiu: bool
    dataCreacio: str