from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.empresa_client import EmpresaClientCreate, EmpresaClientUpdate, EmpresaClientRead
from app.models.usuari import UsuariCreate, UsuariUpdate, UsuariRead
from app.models.programa_formacio import ProgramaFormacioCreate, ProgramaFormacioUpdate, ProgramaFormacioRead
from app.models.programa_participant import ProgramaParticipantCreate, ProgramaParticipantUpdate, ProgramaParticipantRead
from app.models.programa_supervisor import ProgramaSupervisorCreate, ProgramaSupervisorUpdate, ProgramaSupervisorRead
from app.models.pla_accio import PlaAccioCreate, PlaAccioUpdate, PlaAccioRead
from app.models.objectiu_pla import ObjectiuPlaCreate, ObjectiuPlaUpdate, ObjectiuPlaRead
from app.models.accio import AccioCreate, AccioUpdate, AccioRead
from app.models.kpi import KPICreate, KPIUpdate, KPIRead
from app.models.registre_kpi import RegistreKPICreate, RegistreKPIUpdate, RegistreKPIRead
from app.models.feedback import FeedbackCreate, FeedbackUpdate, FeedbackRead
from app.models.indicador_impacte import IndicadorImpacteCreate, IndicadorImpacteUpdate, IndicadorImpacteRead
from app.models.registre_impacte import RegistreImpacteCreate, RegistreImpacteUpdate, RegistreImpacteRead

from app.services.empresa_client_service import EmpresaClientService
from app.services.usuari_service import UsuariService
from app.services.programa_formacio_service import ProgramaFormacioService
from app.services.pla_accio_service import PlaAccioService
from app.services.kpi_service import KPIService
from app.services.seguiment_objectiu_service import SeguimentObjectiuService
from app.services.feedback_service import FeedbackService
from app.services.analisi_service import AnalisiService
from app.services.ia_service import IAService
from app.services.impacte_service import ImpacteService

empresa_client_service = EmpresaClientService()
usuari_service = UsuariService()
programa_formacio_service = ProgramaFormacioService()
pla_accio_service = PlaAccioService()
kpi_service = KPIService()
seguiment_objectiu_service = SeguimentObjectiuService()
feedback_service = FeedbackService()
analisi_service = AnalisiService()
ia_service = IAService()
impacte_service = ImpacteService()

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


@app.get("/empreses", response_model=list[EmpresaClientRead])
def get_empreses():
    return empresa_client_service.get_empreses()


@app.get("/empreses/{idEmpresa}", response_model=EmpresaClientRead)
def get_empresa(idEmpresa: int):
    empresa = empresa_client_service.get_empresa(idEmpresa)

    if empresa is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa client no trobada"
        )

    return empresa


@app.get("/empreses/{idEmpresa}/programes", response_model=list[ProgramaFormacioRead])
def get_programes_empresa(idEmpresa: int):
    empresa = empresa_client_service.get_empresa(idEmpresa)

    if empresa is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa client no trobada"
        )

    return empresa_client_service.get_programes_empresa(idEmpresa)


@app.post("/empreses", response_model=EmpresaClientRead)
def create_empresa(empresa: EmpresaClientCreate):
    return empresa_client_service.create_empresa(empresa)


@app.put("/empreses/{idEmpresa}", response_model=EmpresaClientRead)
def update_empresa(idEmpresa: int, empresa: EmpresaClientUpdate):
    empresa_actualitzada = empresa_client_service.update_empresa(idEmpresa, empresa)

    if empresa_actualitzada is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa client no trobada"
        )

    return empresa_actualitzada


@app.get("/usuaris", response_model=list[UsuariRead])
def get_usuaris():
    return usuari_service.get_usuaris()


@app.get("/usuaris/administradors", response_model=list[UsuariRead])
def get_administradors():
    return usuari_service.get_administradors()


@app.get("/usuaris/{idUsuari}", response_model=UsuariRead)
def get_usuari(idUsuari: int):
    usuari = usuari_service.get_usuari(idUsuari)

    if usuari is None:
        raise HTTPException(status_code=404, detail="Usuari no trobat")

    return usuari


@app.get("/usuaris/{idUsuari}/rols")
def get_rols_usuari(idUsuari: int):
    rols = usuari_service.get_rols_usuari(idUsuari)

    if not rols:
        raise HTTPException(status_code=404, detail="Usuari no trobat")

    return rols


@app.post("/usuaris", response_model=UsuariRead)
def create_usuari(usuari: UsuariCreate):
    nou_usuari = usuari_service.create_usuari(usuari)
    if nou_usuari is None:
        raise HTTPException(status_code=404, detail="Empresa no trobada")
    return nou_usuari


@app.put("/usuaris/{idUsuari}", response_model=UsuariRead)
def update_usuari(idUsuari: int, usuari: UsuariUpdate):
    usuari_actualitzat = usuari_service.update_usuari(idUsuari, usuari)
    if usuari_actualitzat is None:
        raise HTTPException(status_code=404, detail="Usuari no trobat")
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


@app.get("/programes/{idPrograma}/plans", response_model=list[PlaAccioRead])
def get_plans_programa(idPrograma: int):
    return pla_accio_service.get_plans_programa(idPrograma)


@app.get("/programes", response_model=list[ProgramaFormacioRead])
def get_programes():
    return programa_formacio_service.get_programes()


@app.get("/programes/{idPrograma}", response_model=ProgramaFormacioRead)
def get_programa(idPrograma: int):
    programa = programa_formacio_service.get_programa(idPrograma)

    if programa is None:
        raise HTTPException(
            status_code=404,
            detail="Programa no trobat"
        )

    return programa


@app.post("/programes", response_model=ProgramaFormacioRead)
def create_programa(programa: ProgramaFormacioCreate):
    return programa_formacio_service.create_programa(programa)


@app.put("/programes/{idPrograma}", response_model=ProgramaFormacioRead)
def update_programa(idPrograma: int, programa: ProgramaFormacioUpdate):
    programa_actualitzat = programa_formacio_service.update_programa(idPrograma, programa)
    if programa_actualitzat is None:
        raise HTTPException(status_code=404, detail="Programa no trobat")
    return programa_actualitzat


@app.post("/programes/{idPrograma}/participants", response_model=ProgramaParticipantRead)
def assignar_participant(idPrograma: int, participant: ProgramaParticipantCreate):
    assignacio = usuari_service.assignar_participant(idPrograma, participant)

    if assignacio is None:
        raise HTTPException(
            status_code=400,
            detail="El programa o l'usuari no existeixen, o l'usuari ja està assignat com a participant"
        )

    return assignacio


@app.get("/programes/{idPrograma}/participants", response_model=list[ProgramaParticipantRead])
def get_participants_programa(idPrograma: int):
    return usuari_service.get_participants_programa(idPrograma)


@app.put("/programes/{idPrograma}/participants/{idUsuari}", response_model=ProgramaParticipantRead)
def update_participant(idPrograma: int, idUsuari: int, participant: ProgramaParticipantUpdate):
    assignacio_actualitzada = usuari_service.update_participant_programa(idPrograma, idUsuari, participant)

    if assignacio_actualitzada is None:
        raise HTTPException(status_code=404, detail="Assignació de participant no trobada")

    return assignacio_actualitzada


@app.post("/programes/{idPrograma}/supervisors", response_model=ProgramaSupervisorRead)
def assignar_supervisor(idPrograma: int, supervisor: ProgramaSupervisorCreate):
    assignacio = usuari_service.assignar_supervisor(idPrograma, supervisor)

    if assignacio is None:
        raise HTTPException(
            status_code=400,
            detail="El programa o l'usuari no existeixen, o l'usuari ja està assignat com a supervisor"
        )

    return assignacio


@app.get("/programes/{idPrograma}/supervisors", response_model=list[ProgramaSupervisorRead])
def get_supervisors_programa(idPrograma: int):
    return usuari_service.get_supervisors_programa(idPrograma)


@app.put("/programes/{idPrograma}/supervisors/{idUsuari}", response_model=ProgramaSupervisorRead)
def update_supervisor(idPrograma: int, idUsuari: int, supervisor: ProgramaSupervisorUpdate):
    assignacio_actualitzada = usuari_service.update_supervisor_programa(idPrograma, idUsuari, supervisor)

    if assignacio_actualitzada is None:
        raise HTTPException(status_code=404, detail="Assignació de supervisor no trobada")

    return assignacio_actualitzada


@app.get("/plans/{idPla}")
def get_pla_detallat(idPla: int):
    pla = pla_accio_service.get_pla_detallat(idPla)

    if pla is None:
        raise HTTPException(status_code=404, detail="Pla d'acció no trobat")

    return pla


@app.post("/plans", response_model=PlaAccioRead)
def create_pla(pla: PlaAccioCreate):
    nou_pla = pla_accio_service.create_pla(pla)
    if nou_pla is None:
        raise HTTPException(status_code=404, detail="Programa no trobat")
    return nou_pla


@app.put("/plans/{idPla}", response_model=PlaAccioRead)
def update_pla(idPla: int, pla: PlaAccioUpdate):
    pla_actualitzat = pla_accio_service.update_pla(idPla, pla)
    if pla_actualitzat is None:
        raise HTTPException(status_code=404, detail="Pla d'acció no trobat")
    return pla_actualitzat


@app.get("/objectius/{idObjectiu}/seguiments")
def get_seguiments_objectiu(idObjectiu: int):
    return seguiment_objectiu_service.get_seguiments_objectiu(idObjectiu)


@app.get("/objectius/{idObjectiu}", response_model=ObjectiuPlaRead)
def get_objectiu(idObjectiu: int):
    objectiu = pla_accio_service.get_objectiu(idObjectiu)
    if objectiu is None:
        raise HTTPException(status_code=404, detail="Objectiu no trobat")
    return objectiu


@app.get("/plans/{idPla}/objectius", response_model=list[ObjectiuPlaRead])
def get_objectius_pla(idPla: int):
    return pla_accio_service.get_objectius_pla(idPla)


@app.post("/objectius", response_model=ObjectiuPlaRead)
def create_objectiu(objectiu: ObjectiuPlaCreate):
    nou_objectiu = pla_accio_service.create_objectiu(objectiu)
    if nou_objectiu is None:
        raise HTTPException(status_code=404, detail="Pla d'acció no trobat")
    return nou_objectiu


@app.put("/objectius/{idObjectiu}", response_model=ObjectiuPlaRead)
def update_objectiu(idObjectiu: int, objectiu: ObjectiuPlaUpdate):
    objectiu_actualitzat = pla_accio_service.update_objectiu(idObjectiu, objectiu)
    if objectiu_actualitzat is None:
        raise HTTPException(status_code=404, detail="Objectiu no trobat")
    return objectiu_actualitzat


@app.get("/accions/{idAccio}", response_model=AccioRead)
def get_accio(idAccio: int):
    accio = pla_accio_service.get_accio(idAccio)
    if accio is None:
        raise HTTPException(status_code=404, detail="Acció no trobada")
    return accio


@app.get("/objectius/{idObjectiu}/accions", response_model=list[AccioRead])
def get_accions_objectiu(idObjectiu: int):
    return pla_accio_service.get_accions_objectiu(idObjectiu)


@app.post("/accions", response_model=AccioRead)
def create_accio(accio: AccioCreate):
    nova_accio = pla_accio_service.create_accio(accio)
    if nova_accio is None:
        raise HTTPException(status_code=404, detail="Objectiu no trobat")
    return nova_accio


@app.put("/accions/{idAccio}", response_model=AccioRead)
def update_accio(idAccio: int, accio: AccioUpdate):
    accio_actualitzada = pla_accio_service.update_accio(idAccio, accio)
    if accio_actualitzada is None:
        raise HTTPException(status_code=404, detail="Acció no trobada")
    return accio_actualitzada


@app.get("/kpis/{idKPI}", response_model=KPIRead)
def get_kpi(idKPI: int):
    kpi = kpi_service.get_kpi(idKPI)

    if kpi is None:
        raise HTTPException(status_code=404, detail="KPI no trobat")

    return kpi


@app.get("/kpis/{idKPI}/assoliment")
def get_assoliment_kpi(idKPI: int):
    kpi = kpi_service.get_kpi(idKPI)
    if kpi is None:
        raise HTTPException(status_code=404, detail="KPI no trobat")

    registres = kpi_service.get_registres_kpi(idKPI)
    if not registres:
        return {"idKPI": idKPI, "assoliment": 0}

    ultim = sorted(registres, key=lambda r: r.dataRegistre)[-1]
    return {
        "idKPI": idKPI,
        "valorActual": ultim.valor,
        "assoliment": kpi_service.calcular_assoliment_kpi(kpi, ultim.valor)
    }


@app.get("/kpis/{idKPI}/registres", response_model=list[RegistreKPIRead])
def get_registres_kpi(idKPI: int):
    return kpi_service.get_registres_kpi(idKPI)


@app.get("/kpis/{idKPI}/usuaris/{idUsuari}/registres", response_model=list[RegistreKPIRead])
def get_registres_kpi_usuari(idKPI: int, idUsuari: int):
    return kpi_service.get_registres_kpi_usuari(idKPI, idUsuari)


@app.get("/accions/{idAccio}/kpis", response_model=list[KPIRead])
def get_kpis_accio(idAccio: int):
    return pla_accio_service.get_kpis_accio(idAccio)


@app.post("/kpis", response_model=KPIRead)
def create_kpi(kpi: KPICreate):
    nou_kpi = pla_accio_service.create_kpi(kpi)
    if nou_kpi is None:
        raise HTTPException(status_code=404, detail="Acció no trobada")
    return nou_kpi


@app.put("/kpis/{idKPI}", response_model=KPIRead)
def update_kpi(idKPI: int, kpi: KPIUpdate):
    kpi_actualitzat = pla_accio_service.update_kpi(idKPI, kpi)
    if kpi_actualitzat is None:
        raise HTTPException(status_code=404, detail="KPI no trobat")
    return kpi_actualitzat


@app.post("/registres-kpi", response_model=RegistreKPIRead)
def create_registre_kpi(registre: RegistreKPICreate):
    try:
        nou_registre = kpi_service.create_registre_kpi(registre)
    except ValueError as error:
        if str(error) == "usuari_no_es_participant":
            raise HTTPException(
                status_code=400,
                detail="L'usuari no és participant actiu del programa indicat"
            )
        if str(error) == "valor_fora_de_rang":
            raise HTTPException(
                status_code=400,
                detail="El valor registrat es troba fora del rang definit pel KPI"
            )
        raise

    if nou_registre is None:
        raise HTTPException(status_code=404, detail="KPI no trobat")
    return nou_registre


@app.put("/registres-kpi/{idRegistre}", response_model=RegistreKPIRead)
def update_registre_kpi(idRegistre: int, registre: RegistreKPIUpdate):
    registre_actualitzat = kpi_service.update_registre_kpi(idRegistre, registre)
    if registre_actualitzat is None:
        raise HTTPException(status_code=404, detail="Registre KPI no trobat")
    return registre_actualitzat


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
def get_detall_seguiment_objectiu_usuari(idObjectiu: int, idUsuari: int):
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


@app.get("/feedback", response_model=list[FeedbackRead])
def get_feedbacks():
    return feedback_service.get_feedbacks()


@app.get("/feedback/{idFeedback}", response_model=FeedbackRead)
def get_feedback(idFeedback: int):
    feedback = feedback_service.get_feedback(idFeedback)

    if feedback is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback no trobat"
        )

    return feedback


@app.post("/feedback", response_model=FeedbackRead)
def create_feedback(feedback: FeedbackCreate):
    try:
        nou_feedback = feedback_service.create_feedback(feedback)
    except ValueError as error:
        if str(error) == "programa_no_trobat":
            raise HTTPException(status_code=404, detail="Programa no trobat")
        raise

    if nou_feedback is None:
        raise HTTPException(
            status_code=400,
            detail="El supervisor o el participant no pertanyen al programa indicat"
        )
    return nou_feedback


@app.put("/feedback/{idFeedback}", response_model=FeedbackRead)
def update_feedback(idFeedback: int, feedback: FeedbackUpdate):
    feedback_actualitzat = feedback_service.update_feedback(idFeedback, feedback)
    if feedback_actualitzat is None:
        raise HTTPException(status_code=404, detail="Feedback no trobat")
    return feedback_actualitzat


@app.get("/programes/{idPrograma}/feedback", response_model=list[FeedbackRead])
def get_feedbacks_programa(idPrograma: int):
    return feedback_service.get_feedbacks_programa(idPrograma)


@app.get("/participants/{idUsuariParticipant}/feedback", response_model=list[FeedbackRead])
def get_feedbacks_participant(idUsuariParticipant: int):
    return feedback_service.get_feedbacks_participant(idUsuariParticipant)


@app.get("/supervisors/{idUsuariSupervisor}/feedback", response_model=list[FeedbackRead])
def get_feedbacks_supervisor(idUsuariSupervisor: int):
    return feedback_service.get_feedbacks_supervisor(idUsuariSupervisor)


@app.get("/programes/{idPrograma}/participants/{idUsuariParticipant}/feedback", response_model=list[FeedbackRead])
def get_feedbacks_programa_participant(idPrograma: int, idUsuariParticipant: int):
    return feedback_service.get_feedbacks_programa_participant(
        idPrograma,
        idUsuariParticipant
    )


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
    try:
        return kpi_service.get_evolucio_kpi(idKPI)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


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


@app.get("/programes/{idPrograma}/ranquing")
def get_ranquing_programa(idPrograma: int):
    return analisi_service.get_ranquing_programa(idPrograma)


@app.get("/ia/programes/{idPrograma}/participants/{idUsuariParticipant}/feedback")
def generar_recomanacio_feedback(idPrograma: int, idUsuariParticipant: int):
    return ia_service.generar_recomanacio_feedback(
        idPrograma,
        idUsuariParticipant
    )


@app.get("/ia/plans/{idPla}/resum")
def generar_resum_pla(idPla: int):
    return ia_service.generar_resum_pla(idPla)


@app.get("/ia/programes/{idPrograma}/proposta-pla")
def generar_proposta_pla(idPrograma: int):
    return ia_service.generar_proposta_pla(idPrograma)


@app.get("/programes/{idPrograma}/indicadors-impacte", response_model=list[IndicadorImpacteRead])
def get_indicadors_impacte_programa(idPrograma: int):
    return impacte_service.get_indicadors_programa(idPrograma)


@app.post("/indicadors-impacte", response_model=IndicadorImpacteRead)
def create_indicador_impacte(indicador: IndicadorImpacteCreate):
    return impacte_service.create_indicador(indicador)


@app.get("/indicadors-impacte/{idIndicadorImpacte}/registres", response_model=list[RegistreImpacteRead])
def get_registres_indicador_impacte(idIndicadorImpacte: int):
    return impacte_service.get_registres_indicador(idIndicadorImpacte)


@app.post("/registres-impacte", response_model=RegistreImpacteRead)
def create_registre_impacte(registre: RegistreImpacteCreate):
    nou_registre = impacte_service.create_registre_impacte(registre)

    if nou_registre is None:
        raise HTTPException(
            status_code=404,
            detail="Indicador d'impacte no trobat"
        )

    return nou_registre


@app.get("/indicadors-impacte/{idIndicadorImpacte}/usuaris/{idUsuari}/delta")
def get_delta_impacte_usuari(idIndicadorImpacte: int, idUsuari: int):
    delta = impacte_service.get_delta_impacte_usuari(idIndicadorImpacte, idUsuari)

    if delta is None:
        raise HTTPException(
            status_code=404,
            detail="Indicador d'impacte no trobat"
        )

    return delta


@app.get("/indicadors-impacte/{idIndicadorImpacte}/programes/{idPrograma}/deltes")
def get_deltes_programa(idIndicadorImpacte: int, idPrograma: int):
    return impacte_service.get_deltes_programa(idIndicadorImpacte, idPrograma)


@app.get("/indicadors-impacte/{idIndicadorImpacteFormat}/comparacio-grups")
def comparar_grups_impacte(
    idIndicadorImpacteFormat: int,
    idProgramaFormat: int,
    idProgramaControl: int | None = None,
    idIndicadorImpacteControl: int | None = None
):
    return impacte_service.comparar_grups(
        idIndicadorImpacteFormat,
        idProgramaFormat,
        idIndicadorImpacteControl,
        idProgramaControl
    )


@app.get("/indicadors-impacte/{idIndicadorImpacte}/programes/{idPrograma}/correlacio")
def get_correlacio_progres_impacte(idIndicadorImpacte: int, idPrograma: int):
    return impacte_service.correlacio_progres_impacte(idIndicadorImpacte, idPrograma)


@app.get("/indicadors-impacte/{id_indicador}/programes/{id_programa}/comparacio-control")
def comparar_amb_grup_control(id_indicador: int, id_programa: int):
    return impacte_service.comparar_grups(
        idIndicadorImpacteFormat=id_indicador,
        idProgramaFormat=id_programa
    )