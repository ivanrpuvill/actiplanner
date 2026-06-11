from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.empresa_client_service import EmpresaClientService
from app.services.usuari_service import UsuariService
from app.services.pla_accio_service import PlaAccioService
from app.services.kpi_service import KPIService
from app.services.seguiment_objectiu_service import SeguimentObjectiuService
from app.services.feedback_service import FeedbackService
from app.services.analisi_service import AnalisiService
from app.services.ia_service import IAService

from app.models.feedback import Feedback

empresa_client_service = EmpresaClientService()
usuari_service = UsuariService()
pla_accio_service = PlaAccioService()
kpi_service = KPIService()
seguiment_objectiu_service = SeguimentObjectiuService()
feedback_service = FeedbackService()
analisi_service = AnalisiService()
ia_service = IAService()

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

@app.get("/empreses")
def get_empreses():
    return empresa_client_service.get_empreses()


@app.get("/empreses/{idEmpresa}")
def get_empresa(idEmpresa: int):
    empresa = empresa_client_service.get_empresa(idEmpresa)

    if empresa is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa client no trobada"
        )

    return empresa


@app.get("/empreses/{idEmpresa}/programes")
def get_programes_empresa(idEmpresa: int):
    empresa = empresa_client_service.get_empresa(idEmpresa)

    if empresa is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa client no trobada"
        )

    return empresa_client_service.get_programes_empresa(idEmpresa)


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


@app.get("/feedback")
def get_feedbacks():
    return feedback_service.get_feedbacks()


@app.get("/feedback/{idFeedback}")
def get_feedback(idFeedback: int):
    feedback = feedback_service.get_feedback(idFeedback)

    if feedback is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback no trobat"
        )

    return feedback


@app.get("/programes/{idPrograma}/feedback")
def get_feedbacks_programa(idPrograma: int):
    return feedback_service.get_feedbacks_programa(idPrograma)


@app.get("/participants/{idUsuariParticipant}/feedback")
def get_feedbacks_participant(idUsuariParticipant: int):
    return feedback_service.get_feedbacks_participant(idUsuariParticipant)


@app.get("/supervisors/{idUsuariSupervisor}/feedback")
def get_feedbacks_supervisor(idUsuariSupervisor: int):
    return feedback_service.get_feedbacks_supervisor(idUsuariSupervisor)


@app.get("/programes/{idPrograma}/participants/{idUsuariParticipant}/feedback")
def get_feedbacks_programa_participant(
    idPrograma: int,
    idUsuariParticipant: int
):
    return feedback_service.get_feedbacks_programa_participant(
        idPrograma,
        idUsuariParticipant
    )


@app.post("/feedback")
def create_feedback(feedback: Feedback):
    nou_feedback = feedback_service.create_feedback(feedback)

    if nou_feedback is None:
        raise HTTPException(
            status_code=400,
            detail="El supervisor o el participant no pertanyen al programa indicat"
        )

    return nou_feedback


@app.get("/plans/{idPla}/progres")
def get_resum_progres_pla(idPla: int):
    resum = pla_accio_service.get_resum_progres_pla(idPla)

    if resum is None:
        raise HTTPException(
            status_code=404,
            detail="Pla d'acció no trobat"
        )

    return resum


@app.get("/kpis/{idKPI}/evolucio")
def get_evolucio_kpi(idKPI: int):
    return kpi_service.get_evolucio_kpi(idKPI)


@app.get("/programes/{idPrograma}/analisi")
def get_analisi_programa(idPrograma: int):
    return analisi_service.get_analisi_programa(idPrograma)


@app.get("/programes/{idPrograma}/objectius-risc")
def get_objectius_risc(idPrograma: int):
    return analisi_service.get_objectius_risc(idPrograma)


@app.get("/programes/{idPrograma}/participants-destacats")
def get_participants_destacats(idPrograma: int):
    return analisi_service.get_participants_destacats(idPrograma)


@app.get("/programes/{idPrograma}/participants-desviacio")
def get_participants_amb_desviacio(idPrograma: int):
    return analisi_service.get_participants_amb_desviacio(idPrograma)

@app.get("/ia/programes/{idPrograma}/resum")
def generar_resum_programa(idPrograma: int):
    return ia_service.generar_resum_programa(idPrograma)


@app.get("/ia/programes/{idPrograma}/participants/{idUsuariParticipant}/feedback")
def generar_recomanacio_feedback(
    idPrograma: int,
    idUsuariParticipant: int
):
    return ia_service.generar_recomanacio_feedback(
        idPrograma,
        idUsuariParticipant
    )


@app.get("/ia/plans/{idPla}/resum")
def generar_resum_pla(idPla: int):
    return ia_service.generar_resum_pla(idPla)