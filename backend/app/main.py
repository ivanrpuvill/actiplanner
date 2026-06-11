from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.usuari_service import UsuariService
from app.services.pla_accio_service import PlaAccioService
from app.services.kpi_service import KPIService
from app.services.seguiment_objectiu_service import SeguimentObjectiuService

usuari_service = UsuariService()
pla_accio_service = PlaAccioService()
kpi_service = KPIService()
seguiment_objectiu_service = SeguimentObjectiuService()

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

@app.get("/kpis/{idKPI}")
def get_kpi(idKPI: int):
    kpi = kpi_service.get_kpi(idKPI)

    if kpi is None:
        raise HTTPException(status_code=404, detail="KPI no trobat")

    return kpi


@app.get("/kpis/{idKPI}/registres")
def get_registres_kpi(idKPI: int):
    return kpi_service.get_registres_kpi(idKPI)


@app.get("/kpis/{idKPI}/usuaris/{idUsuari}/registres")
def get_registres_kpi_usuari(idKPI: int, idUsuari: int):
    return kpi_service.get_registres_kpi_usuari(idKPI, idUsuari)

@app.get("/objectius/{idObjectiu}/seguiments")
def get_seguiments_objectiu(idObjectiu: int):
    return seguiment_objectiu_service.get_seguiments_objectiu(idObjectiu)


@app.get("/usuaris/{idUsuari}/seguiments")
def get_seguiments_usuari(idUsuari: int):
    return seguiment_objectiu_service.get_seguiments_usuari(idUsuari)


@app.get("/programes/{idPrograma}/usuaris/{idUsuari}/seguiments")
def get_seguiments_programa_usuari(idPrograma: int, idUsuari: int):
    return seguiment_objectiu_service.get_seguiments_programa_usuari(
        idPrograma,
        idUsuari
    )


@app.get("/objectius/{idObjectiu}/usuaris/{idUsuari}/seguiment")
def get_detall_seguiment_objectiu_usuari(
    idObjectiu: int,
    idUsuari: int
):
    detall = seguiment_objectiu_service.get_detall_seguiment_objectiu_usuari(
        idObjectiu,
        idUsuari
    )

    if detall is None:
        raise HTTPException(
            status_code=404,
            detail="Seguiment d'objectiu no trobat"
        )

    return detall