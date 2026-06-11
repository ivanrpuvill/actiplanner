from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.empresa_client import EmpresaClient
from app.models.usuari import Usuari
from app.models.programa_formacio import ProgramaFormacio
from app.models.programa_participant import ProgramaParticipant
from app.models.programa_supervisor import ProgramaSupervisor
from app.models.pla_accio import PlaAccio
from app.models.objectiu_pla import ObjectiuPla
from app.models.accio import Accio
from app.models.kpi import KPI
from app.models.registre_kpi import RegistreKPI
from app.models.feedback import Feedback

from app.services.empresa_client_service import EmpresaClientService
from app.services.usuari_service import UsuariService
from app.services.programa_formacio_service import ProgramaFormacioService
from app.services.pla_accio_service import PlaAccioService
from app.services.kpi_service import KPIService
from app.services.seguiment_objectiu_service import SeguimentObjectiuService
from app.services.feedback_service import FeedbackService
from app.services.analisi_service import AnalisiService
from app.services.ia_service import IAService

empresa_client_service = EmpresaClientService()
usuari_service = UsuariService()
programa_formacio_service = ProgramaFormacioService()
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


@app.post("/empreses")
def create_empresa(empresa: EmpresaClient):
    return empresa_client_service.create_empresa(empresa)


@app.put("/empreses/{idEmpresa}")
def update_empresa(idEmpresa: int, empresa: EmpresaClient):
    empresa_actualitzada = empresa_client_service.update_empresa(idEmpresa, empresa)

    if empresa_actualitzada is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa client no trobada"
        )

    return empresa_actualitzada


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


@app.post("/usuaris")
def create_usuari(usuari: Usuari):
    return usuari_service.create_usuari(usuari)


@app.put("/usuaris/{idUsuari}")
def update_usuari(idUsuari: int, usuari: Usuari):
    usuari_actualitzat = usuari_service.update_usuari(idUsuari, usuari)

    if usuari_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="Usuari no trobat"
        )

    return usuari_actualitzat


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


@app.get("/programes")
def get_programes():
    return programa_formacio_service.get_programes()


@app.get("/programes/{idPrograma}")
def get_programa(idPrograma: int):
    programa = programa_formacio_service.get_programa(idPrograma)

    if programa is None:
        raise HTTPException(
            status_code=404,
            detail="Programa no trobat"
        )

    return programa


@app.post("/programes")
def create_programa(programa: ProgramaFormacio):
    return programa_formacio_service.create_programa(programa)


@app.put("/programes/{idPrograma}")
def update_programa(idPrograma: int, programa: ProgramaFormacio):
    programa_actualitzat = programa_formacio_service.update_programa(
        idPrograma,
        programa
    )

    if programa_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="Programa no trobat"
        )

    return programa_actualitzat


@app.post("/programes/{idPrograma}/participants")
def assignar_participant(idPrograma: int, participant: ProgramaParticipant):
    data = participant.model_dump()
    data["idPrograma"] = idPrograma

    participant = ProgramaParticipant(**data)

    assignacio = usuari_service.assignar_participant(participant)

    if assignacio is None:
        raise HTTPException(
            status_code=400,
            detail="L'usuari no existeix o ja està assignat com a participant"
        )

    return assignacio


@app.post("/programes/{idPrograma}/supervisors")
def assignar_supervisor(idPrograma: int, supervisor: ProgramaSupervisor):
    data = supervisor.model_dump()
    data["idPrograma"] = idPrograma

    supervisor = ProgramaSupervisor(**data)

    assignacio = usuari_service.assignar_supervisor(supervisor)

    if assignacio is None:
        raise HTTPException(
            status_code=400,
            detail="L'usuari no existeix o ja està assignat com a supervisor"
        )

    return assignacio


@app.get("/plans/{idPla}")
def get_pla_detallat(idPla: int):
    pla = pla_accio_service.get_pla_detallat(idPla)

    if pla is None:
        raise HTTPException(status_code=404, detail="Pla d'acció no trobat")

    return pla


@app.post("/plans")
def create_pla(pla: PlaAccio):
    return pla_accio_service.create_pla(pla)


@app.put("/plans/{idPla}")
def update_pla(idPla: int, pla: PlaAccio):
    pla_actualitzat = pla_accio_service.update_pla(
        idPla,
        pla
    )

    if pla_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="Pla d'acció no trobat"
        )

    return pla_actualitzat


@app.post("/accions")
def create_accio(accio: Accio):
    nova_accio = pla_accio_service.create_accio(
        accio
    )

    if nova_accio is None:
        raise HTTPException(
            status_code=404,
            detail="Objectiu no trobat"
        )

    return nova_accio


@app.put("/accions/{idAccio}")
def update_accio(
    idAccio: int,
    accio: Accio
):
    accio_actualitzada = (
        pla_accio_service.update_accio(
            idAccio,
            accio
        )
    )

    if accio_actualitzada is None:
        raise HTTPException(
            status_code=404,
            detail="Acció no trobada"
        )

    return accio_actualitzada


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


@app.post("/kpis")
def create_kpi(kpi: KPI):
    nou_kpi = pla_accio_service.create_kpi(
        kpi
    )

    if nou_kpi is None:
        raise HTTPException(
            status_code=404,
            detail="Acció no trobada"
        )

    return nou_kpi


@app.put("/kpis/{idKPI}")
def update_kpi(
    idKPI: int,
    kpi: KPI
):
    kpi_actualitzat = (
        pla_accio_service.update_kpi(
            idKPI,
            kpi
        )
    )

    if kpi_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="KPI no trobat"
        )

    return kpi_actualitzat


@app.post("/registres-kpi")
def create_registre_kpi(
    registre: RegistreKPI
):
    nou_registre = (
        kpi_service.create_registre_kpi(
            registre
        )
    )

    if nou_registre is None:
        raise HTTPException(
            status_code=404,
            detail="KPI no trobat"
        )

    return nou_registre


@app.put("/registres-kpi/{idRegistre}")
def update_registre_kpi(
    idRegistre: int,
    registre: RegistreKPI
):
    registre_actualitzat = (
        kpi_service.update_registre_kpi(
            idRegistre,
            registre
        )
    )

    if registre_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="Registre KPI no trobat"
        )

    return registre_actualitzat


@app.get("/objectius/{idObjectiu}/seguiments")
def get_seguiments_objectiu(idObjectiu: int):
    return seguiment_objectiu_service.get_seguiments_objectiu(idObjectiu)


@app.post("/objectius")
def create_objectiu(
    objectiu: ObjectiuPla
):
    nou_objectiu = (
        pla_accio_service.create_objectiu(
            objectiu
        )
    )

    if nou_objectiu is None:
        raise HTTPException(
            status_code=404,
            detail="Pla d'acció no trobat"
        )

    return nou_objectiu


@app.put("/objectius/{idObjectiu}")
def update_objectiu(
    idObjectiu: int,
    objectiu: ObjectiuPla
):
    objectiu_actualitzat = (
        pla_accio_service.update_objectiu(
            idObjectiu,
            objectiu
        )
    )

    if objectiu_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="Objectiu no trobat"
        )

    return objectiu_actualitzat


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


@app.put("/feedback/{idFeedback}")
def update_feedback(idFeedback: int, feedback: Feedback):
    feedback_actualitzat = feedback_service.update_feedback(
        idFeedback,
        feedback
    )

    if feedback_actualitzat is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback no trobat"
        )

    return feedback_actualitzat


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