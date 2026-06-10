from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.usuari_service import UsuariService
from app.services.pla_accio_service import PlaAccioService

usuari_service = UsuariService()
pla_accio_service = PlaAccioService()

app = FastAPI(
    title="Actiplanner API",
    description="Backend del sistema Actiplanner",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Actiplanner funciona correctament"}

@app.get("/health")
def health():
    return {"status": "ok"}

app = FastAPI(
    title="Actiplanner API",
    description="Backend del sistema Actiplanner",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Actiplanner funciona correctament"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/usuaris")
def get_usuaris():
    return usuari_service.get_usuaris()


@app.get("/usuaris/{idUsuari}")
def get_usuari(idUsuari: int):
    usuari = usuari_service.get_usuari(idUsuari)

    if usuari is None:
        raise HTTPException(status_code=404, detail="Usuari no trobat")

    return usuari


@app.get("/usuaris/administradors")
def get_administradors():
    return usuari_service.get_administradors()


@app.get("/usuaris/{idUsuari}/rols")
def get_rols_usuari(idUsuari: int):
    rols = usuari_service.get_rols_usuari(idUsuari)

    if not rols:
        raise HTTPException(status_code=404, detail="Usuari no trobat")

    return rols


@app.get("/programes/{idPrograma}/participants/{idUsuari}")
def comprovar_participant(idPrograma: int, idUsuari: int):
    return {
        "idPrograma": idPrograma,
        "idUsuari": idUsuari,
        "esParticipant": usuari_service.es_participant(idUsuari, idPrograma)
    }


@app.get("/programes/{idPrograma}/supervisors/{idUsuari}")
def comprovar_supervisor(idPrograma: int, idUsuari: int):
    return {
        "idPrograma": idPrograma,
        "idUsuari": idUsuari,
        "esSupervisor": usuari_service.es_supervisor(idUsuari, idPrograma)
    }

    @app.get("/empreses/{idEmpresa}/programes")
def get_programes_empresa(idEmpresa: int):
    return pla_accio_service.get_programes_empresa(idEmpresa)


@app.get("/programes/{idPrograma}/plans")
def get_plans_programa(idPrograma: int):
    return pla_accio_service.get_plans_programa(idPrograma)


@app.get("/plans/{idPla}")
def get_pla_detallat(idPla: int):
    pla = pla_accio_service.get_pla_detallat(idPla)

    if pla is None:
        raise HTTPException(status_code=404, detail="Pla d'acció no trobat")

    return pla