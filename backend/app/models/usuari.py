from pydantic import BaseModel


class UsuariBase(BaseModel):
    idEmpresa: int
    nom: str
    cognoms: str
    telefon: str | None = None
    email: str
    esAdministrador: bool
    actiu: bool


class UsuariCreate(UsuariBase):
    password: str


class UsuariUpdate(BaseModel):
    idEmpresa: int | None = None
    nom: str | None = None
    cognoms: str | None = None
    telefon: str | None = None
    email: str | None = None
    password: str | None = None
    esAdministrador: bool | None = None
    actiu: bool | None = None


class UsuariRead(UsuariBase):
    idUsuari: int
    dataCreacio: str


class Usuari(UsuariRead):
    passwordHash: str