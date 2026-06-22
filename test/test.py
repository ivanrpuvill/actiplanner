"""
Suite de pruebas funcionales para Actiplanner — v2.

Actualizada tras el commit f8f4ab0 ("bugs solucionats", 2026-06-17 01:27)
y los commits posteriores f02ccdb (indicadors impacte v1),
bd6b16e (ranking + kpi detall) y 4b4c0c3 (millora visualitzacio
participant). La suite v1 (test_actiplanner_api.py original) se ejecutó
el 2026-06-16 18:22, ANTES de esos commits: varios "PASS" de esa
ejecución confirmaban bugs (D1, D2, D3, D5, D6) que ya no existen en el
codigo actual. Este archivo sustituye a esa suite.

Requiere el backend levantado en http://localhost:8000
(uvicorn app.main:app, desde la carpeta backend/, SIN GEMINI_API_KEY
configurada para que las pruebas de IA validen la ruta degradada).

ATENCION: estas pruebas hacen POST/PUT reales contra los ficheros JSON
de backend/app/data/. Haz una copia de seguridad de esa carpeta antes
de ejecutar la suite completa:

    cp -r backend/app/data backend/app/data.bak

Ejecucion:
    pip install pytest httpx
    pytest test_actiplanner_api_v2.py -v
"""
import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="function")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.fixture(scope="session")
def shared_client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.fixture(scope="session")
def empresa(shared_client):
    r = shared_client.post("/empreses", json={"nom": "QA Test Corp", "sector": "Testing"})
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="session")
def usuari(shared_client, empresa):
    payload = {
        "idEmpresa": empresa["idEmpresa"],
        "nom": "Test",
        "cognoms": "QA",
        "email": "qa.test@example.com",
        "esAdministrador": False,
        "actiu": True,
        "password": "secret123",
    }
    r = shared_client.post("/usuaris", json=payload)
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="session")
def programa(shared_client, empresa):
    payload = {
        "idEmpresa": empresa["idEmpresa"],
        "nom": "Programa QA",
        "descripcio": "Programa de prova",
        "dataInici": "2026-01-01",
        "dataFi": "2026-12-31",
        "actiu": True,
    }
    r = shared_client.post("/programes", json=payload)
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="session")
def participant(shared_client, programa):
    """
    Usuari assignat com a participant actiu del programa de sessio,
    necessari per crear registres de KPI vàlids (vegeu D14: create_registre_kpi
    ara valida que l'usuari sigui participant actiu del programa).
    """
    payload = {
        "idEmpresa": None,
        "nom": "Participant",
        "cognoms": "KPI",
        "email": "participant.kpi.v2@example.com",
        "esAdministrador": False,
        "actiu": True,
        "password": "secret123",
    }
    empresa_r = shared_client.get("/empreses")
    payload["idEmpresa"] = empresa_r.json()[0]["idEmpresa"]

    usuari_r = shared_client.post("/usuaris", json=payload)
    assert usuari_r.status_code == 200
    nou_participant = usuari_r.json()

    assignacio = shared_client.post(
        f"/programes/{programa['idPrograma']}/participants",
        json={"idUsuari": nou_participant["idUsuari"], "estatParticipacio": "actiu"},
    )
    assert assignacio.status_code == 200

    return nou_participant


# ---------------------------------------------------------------------------
# 4.1 Empreses (sin cambios respecto a v1)
# ---------------------------------------------------------------------------

class TestEmpreses:
    def test_cp01_create_empresa_ok(self, client):
        r = client.post("/empreses", json={"nom": "Acme SA", "sector": "Industria"})
        assert r.status_code == 200
        body = r.json()
        assert "idEmpresa" in body
        assert body["nom"] == "Acme SA"

    def test_cp02_create_empresa_sin_nom_falla_validacion(self, client):
        r = client.post("/empreses", json={"sector": "Industria"})
        assert r.status_code == 422

    def test_cp03_get_empresa_inexistente_404(self, client):
        r = client.get("/empreses/999999")
        assert r.status_code == 404
        assert r.json()["detail"] == "Empresa client no trobada"

    def test_cp04_update_parcial_conserva_resto(self, client, empresa):
        r = client.put(f"/empreses/{empresa['idEmpresa']}", json={"sector": "Nou sector"})
        assert r.status_code == 200
        body = r.json()
        assert body["sector"] == "Nou sector"
        assert body["nom"] == empresa["nom"]

    def test_cp05_programes_de_empresa_sin_programes_es_lista_vacia(self, client):
        r = client.post("/empreses", json={"nom": "Empresa sin programes"})
        idEmpresa = r.json()["idEmpresa"]
        r2 = client.get(f"/empreses/{idEmpresa}/programes")
        assert r2.status_code == 200
        assert r2.json() == []


# ---------------------------------------------------------------------------
# 4.2 Usuaris
# ---------------------------------------------------------------------------

class TestUsuaris:
    def test_cp06_create_usuari_no_expone_password(self, client, empresa):
        payload = {
            "idEmpresa": empresa["idEmpresa"],
            "nom": "Joan",
            "cognoms": "Garcia",
            "email": "joan.garcia@example.com",
            "esAdministrador": False,
            "actiu": True,
            "password": "supersecret",
        }
        r = client.post("/usuaris", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert "password" not in body
        assert "passwordHash" not in body

    def test_cp05r_d5_corregit_usuari_idEmpresa_inexistent_ara_dona_404(self, client):
        """
        Antes D5 (suite v1, defecto confirmado el 16/06): se creaba el
        usuario sin validar idEmpresa (HTTP 200). Corregido en el commit
        f8f4ab0 ("bugs solucionats", 17/06 01:27): usuari_service.create_usuari
        ahora comprueba EmpresaClientRepository.get_by_id() y main.py traduce
        el None a HTTPException 404. Esta prueba verifica que la correccion
        sigue vigente.
        """
        payload = {
            "idEmpresa": 999999,
            "nom": "Fantasma",
            "cognoms": "Sense Empresa",
            "email": "fantasma@example.com",
            "esAdministrador": False,
            "actiu": True,
            "password": "x",
        }
        r = client.post("/usuaris", json=payload)
        assert r.status_code == 404, (
            "Regresion: D5 estaba corregido a 17/06 y ha vuelto a comportarse "
            "como en la ejecucion del 16/06 (creaba el usuario sin validar)."
        )
        assert r.json()["detail"] == "Empresa no trobada"

    def test_cp10_get_rols_usuari_inexistente_404(self, client):
        r = client.get("/usuaris/999999/rols")
        assert r.status_code == 404

    def test_cp09_rols_usuari_sin_asignaciones(self, client, usuari):
        r = client.get(f"/usuaris/{usuari['idUsuari']}/rols")
        assert r.status_code == 200
        body = r.json()
        assert body["programesParticipant"] == []
        assert body["programesSupervisor"] == []

    def test_cp11_comprovar_participant_programa_inexistent_no_da_error(self, client, usuari):
        """
        Este endpoint (GET, de solo lectura) sigue devolviendo 200 con
        esParticipant=False para un programa inexistente. A diferencia de
        D3 (POST que crea una asignacion), aqui no hay efecto secundario
        que proteger, asi que NO se considera defecto: es razonable que
        una comprobacion de pertenencia devuelva "false" en vez de 404
        cuando el recurso padre no existe.
        """
        r = client.get(f"/programes/999999/participants/{usuari['idUsuari']}")
        assert r.status_code == 200
        assert r.json()["esParticipant"] is False

    def test_d7_password_buit_sense_validar(self, client, usuari):
        """
        D7 (sin cambios desde la suite v1): UsuariUpdate no valida longitud
        ni formato de 'password'. Un PUT con password="" sobreescribe el
        hash con cadena vacia sin ningun error. Sigue siendo un defecto
        vigente en el codigo actual.
        """
        r = client.put(f"/usuaris/{usuari['idUsuari']}", json={"password": ""})
        assert r.status_code == 200, (
            "Si esto falla, D7 fue corregido: ahora se valida el formato/"
            "longitud de la contrasenya en las actualizaciones."
        )

    def test_d9_get_usuaris_sin_paginacion(self, client):
        """
        D9 (sin cambios): /usuaris devuelve la coleccion completa sin
        parametros de paginacion ni limite. No es un crash, pero es un
        riesgo de rendimiento y de exposicion de datos (cualquiera puede
        listar todos los usuarios, incluidos campos como telefon y email,
        sin autenticacion).
        """
        r = client.get("/usuaris")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        # Documentamos la ausencia de cualquier mecanismo de paginacion:
        # no hay query params soportados (?page=, ?limit=, ?offset=).

    def test_d10_sin_autenticacion_cualquiera_puede_volverse_admin(self, client, usuari):
        """
        D10 (sin cambios desde la suite v1): no hay autenticacion ni
        autorizacion en ningun endpoint del backend. Sigue siendo
        reproducible: cualquier cliente sin credenciales puede convertir
        a un usuario en administrador.
        """
        r = client.put(f"/usuaris/{usuari['idUsuari']}", json={"esAdministrador": True})
        assert r.status_code == 200
        assert r.json()["esAdministrador"] is True, (
            "Si esto falla, D10 fue corregido: ahora algun mecanismo de "
            "autenticacion/autorizacion protege este endpoint."
        )


# ---------------------------------------------------------------------------
# 4.3 Programes / participants / supervisors
# ---------------------------------------------------------------------------

class TestProgramesAssignacions:
    def test_cp12_create_programa_ok(self, client, empresa):
        payload = {
            "idEmpresa": empresa["idEmpresa"],
            "nom": "Programa B",
            "descripcio": "desc",
            "dataInici": "2026-02-01",
            "dataFi": "2026-11-30",
            "actiu": True,
        }
        r = client.post("/programes", json=payload)
        assert r.status_code == 200

    def test_cp14_assignar_participant_usuari_inexistent_400(self, client, programa):
        r = client.post(
            f"/programes/{programa['idPrograma']}/participants",
            json={"idUsuari": 999999, "estatParticipacio": "actiu"},
        )
        assert r.status_code == 400

    def test_cp15_assignar_participant_duplicado_400(self, client, programa, usuari):
        payload = {"idUsuari": usuari["idUsuari"], "estatParticipacio": "actiu"}
        r1 = client.post(f"/programes/{programa['idPrograma']}/participants", json=payload)
        assert r1.status_code == 200
        r2 = client.post(f"/programes/{programa['idPrograma']}/participants", json=payload)
        assert r2.status_code == 400

    def test_cp16r_d3_corregit_participant_programa_inexistent_ara_400(self, client, usuari):
        """
        Antes D3 (suite v1): no se validaba que el programa existiera al
        asignar un participante (HTTP 200, asignacion "huerfana").
        Corregido en f8f4ab0: usuari_service.assignar_participant ahora
        comprueba ProgramaFormacioRepository.get_by_id() antes de crear
        la asignacion.

        Nota: el codigo devuelve 400 (no 404) porque el servicio sigue
        devolviendo None tanto si el programa no existe como si el
        usuario no existe o ya esta asignado, y main.py traduce cualquier
        None a 400 con un mensaje generico. Es decir, el bug funcional
        (se podia crear la asignacion sin validar) esta resuelto, pero el
        codigo de estado/mensaje sigue sin distinguir la causa exacta.
        """
        nou_usuari = client.post(
            "/usuaris",
            json={
                "idEmpresa": 1,
                "nom": "Temp",
                "cognoms": "Usuari",
                "email": "temp.usuari.v2@example.com",
                "esAdministrador": False,
                "actiu": True,
                "password": "x",
            },
        ).json()
        r = client.post(
            "/programes/999999/participants",
            json={"idUsuari": nou_usuari["idUsuari"], "estatParticipacio": "actiu"},
        )
        assert r.status_code == 400, (
            "Si esto falla con 200, D3 ha vuelto a romperse. Si falla con "
            "404, el mensaje de error fue mejorado para distinguir la causa "
            "(actualizar esta prueba en ese caso, seria una mejora, no una "
            "regresion)."
        )
        assert r.json()["detail"] == (
            "El programa o l'usuari no existeixen, o l'usuari ja està "
            "assignat com a participant"
        )

    def test_d4_supervisor_programa_inexistent_mateix_patro_que_d3(self, client, usuari):
        """
        D4 (mismo defecto que D3 pero via assignar_supervisor): tambien
        corregido en f8f4ab0 con el mismo patron (valida programa, pero
        sigue devolviendo 400 generico en vez de distinguir la causa).
        """
        r = client.post(
            "/programes/999999/supervisors",
            json={"idUsuari": usuari["idUsuari"]},
        )
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# 4.4 / 4.5 Plans, Objectius, Accions, KPIs, Registres
# ---------------------------------------------------------------------------

class TestPlansKPIs:
    def test_cp02r_d2_corregit_create_pla_programa_inexistent_ara_404(self, client):
        """
        Antes D2 (suite v1): create_pla no validaba idPrograma (HTTP 200,
        plan "huerfano"). Corregido en f8f4ab0: pla_accio_service.create_pla
        ahora comprueba ProgramaFormacioRepository.get_by_id() y main.py
        devuelve 404 "Programa no trobat" si no existe.
        """
        r = client.post("/plans", json={"idPrograma": 999999, "titol": "Pla fantasma", "actiu": True})
        assert r.status_code == 404, (
            "Si esto falla con 200, D2 ha vuelto a romperse (regresion)."
        )
        assert r.json()["detail"] == "Programa no trobat"

    def test_cp17_cadena_completa_y_validacion_de_padres(self, client, programa):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla QA", "actiu": True}).json()

        r_obj_bad = client.post("/objectius", json={"idPla": 999999, "descripcio": "x", "valor": 100})
        assert r_obj_bad.status_code == 404

        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "Reduir incidencies", "valor": 100}).json()

        r_acc_bad = client.post("/accions", json={
            "idObjectiu": 999999, "titol": "x", "descripcio": "x",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        })
        assert r_acc_bad.status_code == 404

        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "Formacio inicial",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()

        r_kpi_bad = client.post("/kpis", json={
            "idAccio": 999999, "nom": "x", "descripcio": "x", "periodicitat": "setmanal",
        })
        assert r_kpi_bad.status_code == 404

        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "Adopcio", "descripcio": "desc",
            "periodicitat": "setmanal", "tipus": "percentatge",
            "tipusCalcul": "acumulat", "orientacio": "major_millor",
            "valorMinim": 0, "valorMaxim": 100, "valorObjectiu": 80,
        }).json()
        assert kpi["idKPI"] is not None

    def test_cp18_pla_sense_objectius_progres_zero(self, client, programa):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla buit", "actiu": True}).json()
        r = client.get(f"/plans/{pla['idPla']}")
        assert r.status_code == 200
        body = r.json()
        assert body["progresPla"] == 0
        assert body["estatPla"] == "pendent"
        assert body["objectius"] == []

    def test_d15_corregit_pla_detallat_inclou_descripcio_i_dates(self, client, programa):
        """
        D15 (corregido): get_pla_detallat() (usado per GET /plans/{id})
        no incloïa descripcio, dataInici ni dataFi a la resposta, tot i
        que aquests camps ja es desaven correctament al crear/editar un
        pla des de P16. L'endpoint de llistat (GET /programes/{id}/plans)
        sí els retornava, per la qual cosa la inconsistencia nomes
        afectava la vista detallada del pla.
        """
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla amb dades completes",
            "descripcio": "Descripcio de prova", "dataInici": "2026-03-01",
            "dataFi": "2026-06-30", "actiu": True,
        }).json()

        r = client.get(f"/plans/{pla['idPla']}")
        assert r.status_code == 200
        body = r.json()
        assert body["descripcio"] == "Descripcio de prova", (
            "Si esto falla, get_pla_detallat() ha dejado de incluir "
            "'descripcio' en la respuesta (regresion)."
        )
        assert body["dataInici"] == "2026-03-01"
        assert body["dataFi"] == "2026-06-30"

    def test_cp19r_progres_pla_i_progres_endpoint_ara_coincideixen(self, client, programa, participant):
        """
        Antes (plan v1, CP19): /plans/{id} (get_pla_detallat) y
        /plans/{id}/progres (get_resum_progres_pla) usaban formulas
        distintas — el detallado agregaba todos los registros segun
        tipusCalcul, mientras que el resumen usaba solo el ultimo
        registro. Esto se senalaba como inconsistencia de diseno a
        documentar, no como bug con aserciones fijas.

        Tras el commit bd6b16e ("ranking + kpi detall", 17/06 07:31),
        get_resum_progres_pla fue reescrito para reutilizar
        AnalisiService._agregar_registres_kpi/_calcular_assoliment_kpi,
        el mismo criterio que usa get_pla_detallat. Esta prueba fija el
        nuevo comportamiento: ambos endpoints deben devolver el mismo
        progresPla para el mismo plan.
        """
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla coherencia", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI coherencia", "descripcio": "desc",
            "periodicitat": "mensual", "valorMinim": 0, "valorMaxim": 100,
        }).json()
        for valor in (20, 80):
            r_registre = client.post("/registres-kpi", json={
                "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
                "idUsuari": participant["idUsuari"], "valor": valor,
            })
            assert r_registre.status_code == 200

        detallat = client.get(f"/plans/{pla['idPla']}").json()
        progres = client.get(f"/plans/{pla['idPla']}/progres").json()

        assert detallat["progresPla"] == progres["progresPla"], (
            "Si esto falla, los dos endpoints han vuelto a divergir "
            "(regresion sobre la correccion del commit bd6b16e)."
        )

    def test_cp20_umbrales_estat(self, client):
        from app.services.analisi_service import AnalisiService

        servei = AnalisiService()
        assert servei._calcular_estat(19.99) == "pendent"
        assert servei._calcular_estat(20.0) == "en_progres"
        assert servei._calcular_estat(79.99) == "en_progres"
        assert servei._calcular_estat(80.0) == "assolit"

    def test_cp23_evolucio_kpi_mitjana(self, client, programa, participant):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla mitjana", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI mitjana", "descripcio": "desc",
            "periodicitat": "mensual", "tipusCalcul": "mitjana",
        }).json()
        for valor in (10, 20, 30):
            client.post("/registres-kpi", json={
                "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
                "idUsuari": participant["idUsuari"], "valor": valor,
            })
        r = client.get(f"/kpis/{kpi['idKPI']}/evolucio")
        assert r.status_code == 200
        valors_calculats = [e["valorCalculat"] for e in r.json()]
        assert valors_calculats == [10.0, 15.0, 20.0]

    def test_cp24_evolucio_kpi_acumulat(self, client, programa, participant):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla acumulat", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI acumulat", "descripcio": "desc",
            "periodicitat": "mensual", "tipusCalcul": "acumulat",
        }).json()
        for valor in (10, 20, 30):
            client.post("/registres-kpi", json={
                "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
                "idUsuari": participant["idUsuari"], "valor": valor,
            })
        r = client.get(f"/kpis/{kpi['idKPI']}/evolucio")
        assert r.status_code == 200
        valors_calculats = [e["valorCalculat"] for e in r.json()]
        assert valors_calculats == [10, 30, 60]

    def test_cp22r_d1_corregit_evolucio_kpi_tipus_calcul_ultim_ara_200(self, client, programa, participant):
        """
        Antes D1 (suite v1, 16/06): GET /kpis/{id}/evolucio con un KPI
        tipusCalcul="ultim" devolvia HTTP 500 (UnboundLocalError sobre
        'valor_calculat', porque la rama "ultim" no estaba implementada).

        Corregido en f8f4ab0: se anadio la rama 'elif kpi.tipusCalcul ==
        "ultim": valor_calculat = registre.valor', mas un 'else: raise
        ValueError(...)' para tipos de calculo no soportados, capturado en
        main.py como HTTPException 400. El caso "ultim" ya es soportado.
        """
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla ultim", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI ultim", "descripcio": "desc",
            "periodicitat": "mensual", "tipusCalcul": "ultim",
        }).json()
        for valor in (10, 25):
            client.post("/registres-kpi", json={
                "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
                "idUsuari": participant["idUsuari"], "valor": valor,
            })
        r = client.get(f"/kpis/{kpi['idKPI']}/evolucio")
        assert r.status_code == 200, (
            "Si esto falla con 500, D1 ha vuelto a romperse (regresion)."
        )
        valors_calculats = [e["valorCalculat"] for e in r.json()]
        assert valors_calculats == [10.0, 25.0]

    def test_cp25_assoliment_sin_registres(self, client, programa):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla X", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI sense registres", "descripcio": "desc",
            "periodicitat": "mensual",
        }).json()
        r = client.get(f"/kpis/{kpi['idKPI']}/assoliment")
        assert r.status_code == 200
        body = r.json()
        assert body["assoliment"] == 0
        assert "valorActual" not in body

    def test_cp26_assoliment_menor_millor(self, client, programa, participant):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla menor millor", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI menor millor", "descripcio": "desc",
            "periodicitat": "mensual", "valorMinim": 0, "valorMaxim": 100,
            "orientacio": "menor_millor",
        }).json()
        client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": participant["idUsuari"], "valor": 20,
        })
        r = client.get(f"/kpis/{kpi['idKPI']}/assoliment")
        assert r.status_code == 200
        assert r.json()["assoliment"] == 80.0

    def test_cp27_assoliment_valorMaxim_igual_valorMinim(self, client, programa, participant):
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla Y", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI edge", "descripcio": "desc",
            "periodicitat": "mensual", "valorMinim": 50, "valorMaxim": 50,
        }).json()
        r_registre = client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": participant["idUsuari"], "valor": 50,
        })
        assert r_registre.status_code == 200
        r = client.get(f"/kpis/{kpi['idKPI']}/assoliment")
        assert r.status_code == 200
        assert r.json()["assoliment"] == 0.0

    def test_d8b_corregit_registre_fora_de_rang_amb_minim_major_que_maxim(self, client, programa, participant):
        """
        D8b (defecto detectado al verificar D8 contra el codigo, antes de
        la validacion de rango): el KPI seguia permetent crear un registre
        amb un valor molt per sobre del maxim quan valorMinim > valorMaxim
        (configuracio invertida), produint un assoliment 100.0 enganyos.

        Amb la validacio de rang afegida a create_registre_kpi (vegeu
        apartat 9), aquest registre concret (valor=200 amb valorMaxim=0)
        ara es rebutja directament amb 400, perque 200 > valorMaxim. Es a
        dir, la nova validacio de rang corregeix aquest cas com a efecte
        collateral, encara que KPICreate/KPIUpdate segueix sense validar
        que valorMaxim > valorMinim en si mateix (es podria configurar un
        KPI invertit i registrar-hi, per exemple, un valor de 50, que
        encara produiria un assoliment incoherent).
        """
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla edge2", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI invertit", "descripcio": "desc",
            "periodicitat": "mensual", "valorMinim": 100, "valorMaxim": 0,
            "orientacio": "menor_millor",
        }).json()
        assert kpi["idKPI"] is not None, (
            "Si esto falla, ahora se valida valorMaxim > valorMinim al crear "
            "un KPI (mejora adicional); actualizar esta prueba en ese caso."
        )
        r_registre = client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": participant["idUsuari"], "valor": 200,
        })
        assert r_registre.status_code == 400, (
            "Si esto falla con 200, la validacion de rango de "
            "create_registre_kpi ha dejado de aplicarse (regresion)."
        )

    def test_d14a_registre_kpi_valor_fora_de_rang_rebutjat(self, client, programa, participant):
        """
        D14a (corregido): create_registre_kpi() ahora valida que el valor
        introducido se encuentre dentro del rango definido por el KPI
        (valorMinim/valorMaxim). Antes de esta validacion, un participante
        podia registrar cualquier valor numerico, incluso muy por encima o
        por debajo del rango esperado para el indicador, sin que el sistema
        lo rechazara (vegeu l'apartat 9, nota d'implementacio del cas d'us
        "Registrar valor de KPI").
        """
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla rang", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI amb rang", "descripcio": "desc",
            "periodicitat": "mensual", "valorMinim": 0, "valorMaxim": 10,
        }).json()

        r_per_sobre = client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": participant["idUsuari"], "valor": 15,
        })
        assert r_per_sobre.status_code == 400, (
            "Si esto falla con 200, la validacion de rang superior ha "
            "dejado de aplicarse (regresion)."
        )
        assert r_per_sobre.json()["detail"] == "El valor registrat es troba fora del rang definit pel KPI"

        r_per_sota = client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": participant["idUsuari"], "valor": -5,
        })
        assert r_per_sota.status_code == 400, (
            "Si esto falla con 200, la validacion de rang inferior ha "
            "dejado de aplicarse (regresion)."
        )

        r_dins_rang = client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": participant["idUsuari"], "valor": 7,
        })
        assert r_dins_rang.status_code == 200, (
            "Un valor dins del rang definit ha de seguir acceptant-se."
        )

    def test_d14b_registre_kpi_usuari_no_participant_rebutjat(self, client, programa, empresa):
        """
        D14b (corregido): create_registre_kpi() ahora valida que l'usuari
        que registra el valor sigui efectivament un participant actiu del
        programa indicat. Abans, qualsevol usuari (per exemple un altre
        participant d'un programa diferent, o un administrador) podia
        registrar valors de KPI en nom de qualsevol programa, sense cap
        comprovacio de pertinença (vegeu l'apartat 9, nota d'implementacio
        del cas d'us "Registrar valor de KPI").
        """
        pla = client.post("/plans", json={"idPrograma": programa["idPrograma"], "titol": "Pla participant", "actiu": True}).json()
        objectiu = client.post("/objectius", json={"idPla": pla["idPla"], "descripcio": "obj", "valor": 100}).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI participant", "descripcio": "desc",
            "periodicitat": "mensual",
        }).json()

        # Usuari nou, no assignat com a participant de cap programa
        usuari_aliè = client.post("/usuaris", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Alie", "cognoms": "D14b",
            "email": "alie.d14b.v2@example.com", "esAdministrador": False,
            "actiu": True, "password": "x",
        }).json()

        r = client.post("/registres-kpi", json={
            "idKPI": kpi["idKPI"], "idPrograma": programa["idPrograma"],
            "idUsuari": usuari_aliè["idUsuari"], "valor": 5,
        })
        assert r.status_code == 400, (
            "Si esto falla con 200, la validacion de pertenencia al "
            "programa ha dejado de aplicarse (regresion)."
        )
        assert r.json()["detail"] == "L'usuari no és participant actiu del programa indicat"


# ---------------------------------------------------------------------------
# 4.6 Feedback
# ---------------------------------------------------------------------------

class TestFeedback:
    def test_cp29_feedback_participant_no_asignado_400(self, client, programa, usuari):
        r = client.post("/feedback", json={
            "idPrograma": programa["idPrograma"],
            "idUsuariSupervisor": usuari["idUsuari"],
            "idUsuariParticipant": usuari["idUsuari"],
            "comentari": "Test",
        })
        assert r.status_code == 400

    def test_cp30r_d6_corregit_feedback_programa_inexistent_ara_404(self, client, usuari):
        """
        Antes D6 (suite v1): se obtenia 400 con el mensaje generico
        "El supervisor o el participant no pertanyen al programa indicat",
        pero por la razon equivocada (no se validaba que el programa
        existiera; al no encontrar supervisores/participantes coincidentes
        en un programa fantasma, el resultado observable era 400 igualmente).

        Corregido en f8f4ab0: feedback_service.create_feedback ahora lanza
        ValueError("programa_no_trobat") si ProgramaFormacioRepository
        .get_by_id() devuelve None, y main.py lo traduce a 404 "Programa no
        trobat" — la causa real ahora coincide con el codigo de estado.
        """
        r = client.post("/feedback", json={
            "idPrograma": 999999,
            "idUsuariSupervisor": usuari["idUsuari"],
            "idUsuariParticipant": usuari["idUsuari"],
            "comentari": "Test",
        })
        assert r.status_code == 404, (
            "Si esto falla con 400, D6 ha vuelto a comportarse como antes "
            "(regresion: ya no se distingue 'programa inexistente' de "
            "'asignacion invalida')."
        )
        assert r.json()["detail"] == "Programa no trobat"

    def test_cp31_feedback_combinacion_valida_lista_vacia(self, client, programa, usuari):
        r = client.get(f"/programes/{programa['idPrograma']}/participants/{usuari['idUsuari']}/feedback")
        assert r.status_code == 200
        assert r.json() == []


# ---------------------------------------------------------------------------
# 4.7 Analisi (incluye ranquing, nuevo desde el commit bd6b16e)
# ---------------------------------------------------------------------------

class TestAnalisi:
    def test_cp32_analisi_programa_sin_participantes_no_crashea(self, client, empresa):
        nou_programa = client.post("/programes", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Programa sense participants",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-12-31", "actiu": True,
        }).json()
        r = client.get(f"/programes/{nou_programa['idPrograma']}/analisi")
        assert r.status_code == 200
        body = r.json()
        assert body["nombreParticipants"] == 0
        assert body["progresMitjaPrograma"] == 0
        assert body["estatPrograma"] == "pendent"

    def test_cp33_objectius_risc_sin_plans(self, client, empresa):
        nou_programa = client.post("/programes", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Programa sense plans",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-12-31", "actiu": True,
        }).json()
        r = client.get(f"/programes/{nou_programa['idPrograma']}/objectius-risc")
        assert r.status_code == 200
        assert r.json() == []

    def test_cp39_ranquing_programa_sense_participants_llista_buida(self, client, empresa):
        """
        Cobertura nueva: GET /programes/{id}/ranquing, introducido en el
        commit bd6b16e. Un programa sin participantes debe devolver lista
        vacia, no error.
        """
        nou_programa = client.post("/programes", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Programa sense ranking",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-12-31", "actiu": True,
        }).json()
        r = client.get(f"/programes/{nou_programa['idPrograma']}/ranquing")
        assert r.status_code == 200
        assert r.json() == []

    def test_cp40_ranquing_ordenat_i_amb_posicions(self, client, programa, usuari):
        """
        Verifica que /ranquing devuelve el array ordenado por progres
        descendente, con 'posicio' 1-indexada y 'destacat' coherente con
        el umbral de 80% usado en participants-destacats.
        """
        r = client.get(f"/programes/{programa['idPrograma']}/ranquing")
        assert r.status_code == 200
        ranquing = r.json()
        assert isinstance(ranquing, list)
        if len(ranquing) >= 2:
            progres_valors = [item["progres"] for item in ranquing]
            assert progres_valors == sorted(progres_valors, reverse=True)
        for index, item in enumerate(ranquing, start=1):
            assert item["posicio"] == index
            assert item["destacat"] == (item["progres"] >= 80)


# ---------------------------------------------------------------------------
# 4.8 IA — degradacion sin API key (sin cambios respecto a v1)
# ---------------------------------------------------------------------------

class TestIA:
    def test_cp34_resum_programa_sin_api_key_no_500(self, client, programa):
        r = client.get(f"/ia/programes/{programa['idPrograma']}/resum")
        assert r.status_code == 200
        body = r.json()
        assert "analisiGenerada" in body
        assert body["analisiGenerada"].get("error") is True

    def test_cp34b_proposta_pla_sin_api_key_no_500(self, client, programa):
        r = client.get(f"/ia/programes/{programa['idPrograma']}/proposta-pla")
        assert r.status_code == 200
        assert r.json()["proposta"].get("error") is True


# ---------------------------------------------------------------------------
# 4.10 Indicadors d'impacte (modulo nuevo, commit f02ccdb)
# ---------------------------------------------------------------------------

class TestIndicadorsImpacte:
    def test_cp41_crear_indicador_impacte_ok(self, client, programa):
        r = client.post("/indicadors-impacte", json={
            "idPrograma": programa["idPrograma"],
            "nom": "Temps de resolucio d'incidencies",
            "descripcio": "Temps mitja en hores",
            "unitat": "hores",
            "orientacio": "menor_millor",
            "fontDades": "CRM",
        })
        assert r.status_code == 200
        assert "idIndicadorImpacte" in r.json()

    def test_d11_crear_indicador_impacte_programa_inexistent_no_validat(self, client):
        """
        Defecto nuevo (D11), no presente en el plan de pruebas v1 porque
        el modulo de indicadors d'impacte no existia todavia (se incorporo
        en el commit f02ccdb, posterior a la ejecucion de la suite v1).

        impacte_service.create_indicador no comprueba que idPrograma exista
        antes de crear el indicador — el mismo patron de bug que D2/D5,
        que SI fueron corregidos en sus respectivos servicios, pero que se
        ha repetido aqui al anadir este modulo despues de esa correccion.
        """
        r = client.post("/indicadors-impacte", json={
            "idPrograma": 999999,
            "nom": "Indicador fantasma",
            "descripcio": "desc",
            "unitat": "hores",
            "orientacio": "menor_millor",
            "fontDades": "CRM",
        })
        assert r.status_code == 200, (
            "Si esto falla con 404, D11 fue corregido: ahora se valida que "
            "idPrograma exista al crear un indicador d'impacte."
        )

    def test_cp42_registre_impacte_indicador_inexistent_404(self, client, programa, usuari):
        r = client.post("/registres-impacte", json={
            "idIndicadorImpacte": 999999,
            "idPrograma": programa["idPrograma"],
            "idUsuari": usuari["idUsuari"],
            "moment": "pre",
            "valor": 10,
        })
        assert r.status_code == 404
        assert r.json()["detail"] == "Indicador d'impacte no trobat"

    def test_cp43_delta_impacte_sense_valors_pre_o_post(self, client, programa, usuari):
        indicador = client.post("/indicadors-impacte", json={
            "idPrograma": programa["idPrograma"],
            "nom": "Indicador delta",
            "descripcio": "desc",
            "unitat": "punts",
            "orientacio": "major_millor",
            "fontDades": "Enquesta",
        }).json()

        r = client.get(
            f"/indicadors-impacte/{indicador['idIndicadorImpacte']}"
            f"/usuaris/{usuari['idUsuari']}/delta"
        )
        assert r.status_code == 200
        body = r.json()
        assert body["disponible"] is False
        assert body["delta"] is None

    def test_cp44_correlacio_amb_menys_de_3_participants_no_calcula(self, client, programa):
        indicador = client.post("/indicadors-impacte", json={
            "idPrograma": programa["idPrograma"],
            "nom": "Indicador correlacio",
            "descripcio": "desc",
            "unitat": "punts",
            "orientacio": "major_millor",
            "fontDades": "Enquesta",
        }).json()
        r = client.get(
            f"/indicadors-impacte/{indicador['idIndicadorImpacte']}"
            f"/programes/{programa['idPrograma']}/correlacio"
        )
        assert r.status_code == 200
        body = r.json()
        assert body["coeficientPearson"] is None
        assert "3 participants" in body["interpretacio"]


# ---------------------------------------------------------------------------
# 4.10 Edicio i activacio/desactivacio (funcionalitat incorporada despres
# de la segona iteracio de proves; vegeu el modul docstring)
# ---------------------------------------------------------------------------

class TestEdicioIActivacioDesactivacio:
    """
    Cobreix la funcionalitat d'edicio i activacio/desactivacio incorporada
    al sistema amb posterioritat a la segona iteracio de proves (vegeu
    PLAN_PRUEBAS_ACTIPLANNER_v2.md, seccio 0). Abans d'aquests tests,
    aquesta funcionalitat nomes s'havia validat manualment amb Playwright
    contra el frontend real.

    Cobreix: empreses, usuaris, programes, plans, assignacions de
    participants i supervisors, objectius, accions i KPI. No cobreix
    indicadors d'impacte, que segueixen sense cap mecanisme d'edicio ni
    desactivacio (vegeu l'apartat 9.2.1 de la memoria).
    """

    # --- Empreses --------------------------------------------------------

    def test_cp45_editar_empresa_actiu_false_no_toca_resta_de_camps(self, client):
        empresa = client.post("/empreses", json={
            "nom": "Empresa editable", "sector": "Sector original", "contacte": "x@x.com",
        }).json()

        r = client.put(f"/empreses/{empresa['idEmpresa']}", json={"actiu": False})
        assert r.status_code == 200
        body = r.json()
        assert body["actiu"] is False
        assert body["nom"] == "Empresa editable"
        assert body["sector"] == "Sector original"

        r2 = client.put(f"/empreses/{empresa['idEmpresa']}", json={"actiu": True})
        assert r2.status_code == 200
        assert r2.json()["actiu"] is True

    # --- Usuaris -----------------------------------------------------------

    def test_cp46_desactivar_usuari_no_esborra_password_ni_resta_de_camps(self, client, empresa):
        nou_usuari = client.post("/usuaris", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Editable", "cognoms": "Usuari",
            "email": "editable.usuari.v2@example.com", "esAdministrador": False,
            "actiu": True, "password": "secret123",
        }).json()

        r = client.put(f"/usuaris/{nou_usuari['idUsuari']}", json={"actiu": False})
        assert r.status_code == 200
        body = r.json()
        assert body["actiu"] is False
        assert body["nom"] == "Editable"
        assert body["email"] == "editable.usuari.v2@example.com"
        assert "password" not in body
        assert "passwordHash" not in body

    # --- Programes -----------------------------------------------------------

    def test_cp47_editar_programa_canvia_nom_i_manté_la_resta(self, client, programa):
        r = client.put(f"/programes/{programa['idPrograma']}", json={"nom": "Nom actualitzat"})
        assert r.status_code == 200
        body = r.json()
        assert body["nom"] == "Nom actualitzat"
        assert body["idEmpresa"] == programa["idEmpresa"]

        # Restaurar el nom per no contaminar altres proves que el puguin llegir
        client.put(f"/programes/{programa['idPrograma']}", json={"nom": programa["nom"]})

    def test_cp48_desactivar_i_reactivar_programa(self, client, empresa):
        nou_programa = client.post("/programes", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Programa per desactivar",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-12-31", "actiu": True,
        }).json()

        r = client.put(f"/programes/{nou_programa['idPrograma']}", json={"actiu": False})
        assert r.status_code == 200
        assert r.json()["actiu"] is False

        r2 = client.put(f"/programes/{nou_programa['idPrograma']}", json={"actiu": True})
        assert r2.status_code == 200
        assert r2.json()["actiu"] is True

    # --- Plans -----------------------------------------------------------

    def test_cp49_editar_i_desactivar_pla(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla editable", "actiu": True,
        }).json()

        r = client.put(f"/plans/{pla['idPla']}", json={"titol": "Pla editat"})
        assert r.status_code == 200
        assert r.json()["titol"] == "Pla editat"

        r2 = client.put(f"/plans/{pla['idPla']}", json={"actiu": False})
        assert r2.status_code == 200
        assert r2.json()["actiu"] is False

    # --- Assignacions de participants i supervisors -----------------------

    def test_cp50_desactivar_participant_no_compta_a_analisi_programa(self, client, empresa):
        """
        Verifica que get_by_programa() del repositori de participants
        filtra per actiu: un participant desactivat deixa de comptar
        al nombre de participants de l'analisi del programa, pero la
        seva assignacio NO desapareix de la llista completa que es fa
        servir per gestionar-la (GET /programes/{id}/participants).
        """
        programa_local = client.post("/programes", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Programa desactivacio participant",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-12-31", "actiu": True,
        }).json()
        usuari_local = client.post("/usuaris", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Part", "cognoms": "Desactivable",
            "email": "part.desactivable.v2@example.com", "esAdministrador": False,
            "actiu": True, "password": "x",
        }).json()
        client.post(f"/programes/{programa_local['idPrograma']}/participants", json={
            "idUsuari": usuari_local["idUsuari"], "estatParticipacio": "actiu",
        })

        analisi_abans = client.get(f"/programes/{programa_local['idPrograma']}/analisi").json()
        assert analisi_abans["nombreParticipants"] == 1

        r = client.put(
            f"/programes/{programa_local['idPrograma']}/participants/{usuari_local['idUsuari']}",
            json={"actiu": False},
        )
        assert r.status_code == 200
        assert r.json()["actiu"] is False

        analisi_despres = client.get(f"/programes/{programa_local['idPrograma']}/analisi").json()
        assert analisi_despres["nombreParticipants"] == 0, (
            "Si aixo falla, get_by_programa() del repositori de participants "
            "ha deixat de filtrar per actiu (regressio)."
        )

        llistat_complet = client.get(f"/programes/{programa_local['idPrograma']}/participants").json()
        assert len(llistat_complet) == 1, (
            "El llistat de gestio ha de seguir mostrant l'assignacio "
            "encara que estigui desactivada, per poder-la reactivar."
        )
        assert llistat_complet[0]["actiu"] is False

        # Reactivar i confirmar que torna a comptar
        client.put(
            f"/programes/{programa_local['idPrograma']}/participants/{usuari_local['idUsuari']}",
            json={"actiu": True},
        )
        analisi_final = client.get(f"/programes/{programa_local['idPrograma']}/analisi").json()
        assert analisi_final["nombreParticipants"] == 1

    def test_d12_corregit_crear_feedback_amb_dades_existents(self, client):
        """
        D12 (defecte nou, detectat en dissenyar aquesta seccio de tests):
        FeedbackRepository no tenia el metode next_id() que
        FeedbackService.create_feedback() ja cridava. Com que cap test
        de les iteracions anteriors arribava a crear un feedback amb
        exit (CP29 espera 400, CP30r espera 404, CP31 nomes consulta
        una llista buida), aquest defecte va passar desapercebut: crear
        un feedback amb dades completament valides sempre fallava amb
        HTTP 500 ('FeedbackRepository' object has no attribute
        'next_id'), fins i tot amb les dades llavor originals del
        repositori (idPrograma=1, idUsuariSupervisor=6,
        idUsuariParticipant=13).

        Corregit afegint next_id() a FeedbackRepository, amb el mateix
        patro ja utilitzat a ObjectiuPlaRepository, AccioRepository i
        KPIRepository (max(id existents) + 1, o 1 si no n'hi ha cap).
        """
        r = client.post("/feedback", json={
            "idPrograma": 1,
            "idUsuariSupervisor": 6,
            "idUsuariParticipant": 13,
            "comentari": "Test de regressio D12",
        })
        assert r.status_code == 200, (
            "Si aixo falla amb 500, D12 ha tornat a aparèixer: "
            "FeedbackRepository.next_id() ha desaparegut o esta trencat."
        )
        body = r.json()
        assert "idFeedback" in body
        assert body["comentari"] == "Test de regressio D12"

    def test_cp51_desactivar_supervisor_actualitza_es_supervisor(self, client, empresa):
        """
        Verifica que la creacio de feedback deixa de validar un
        supervisor (o participant) la assignacio del qual ha estat
        desactivada.

        Aquest test va revelar dos defectes durant el seu disseny:
        D12 (vegeu test_d12_corregit_crear_feedback_amb_dades_existents)
        i D13: FeedbackService.create_feedback() no reutilitzava
        UsuariService.es_supervisor()/es_participant() (que si filtren
        per actiu des de la implementacio d'activar/desactivar
        assignacions), sino que duplicava la mateixa comprovacio
        directament amb get_all() sense cap filtre. Aixo provocava que
        un supervisor o participant desactivat seguis sent acceptat
        per crear feedback nou, tot i no apareixer ja a les analitiques
        del programa. Corregit afegint `and item.actiu` a totes dues
        comprovacions de create_feedback().
        """
        programa_local = client.post("/programes", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Programa desactivacio supervisor",
            "descripcio": "desc", "dataInici": "2026-01-01", "dataFi": "2026-12-31", "actiu": True,
        }).json()
        supervisor_local = client.post("/usuaris", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Superv", "cognoms": "Desactivable",
            "email": "superv.desactivable.v2@example.com", "esAdministrador": False,
            "actiu": True, "password": "x",
        }).json()
        participant_local = client.post("/usuaris", json={
            "idEmpresa": empresa["idEmpresa"], "nom": "Part", "cognoms": "ParaSuperv",
            "email": "part.parasuperv.v2@example.com", "esAdministrador": False,
            "actiu": True, "password": "x",
        }).json()
        client.post(f"/programes/{programa_local['idPrograma']}/supervisors", json={
            "idUsuari": supervisor_local["idUsuari"],
        })
        client.post(f"/programes/{programa_local['idPrograma']}/participants", json={
            "idUsuari": participant_local["idUsuari"], "estatParticipacio": "actiu",
        })

        # Amb el supervisor actiu, el feedback s'ha de poder crear
        r_abans = client.post("/feedback", json={
            "idPrograma": programa_local["idPrograma"],
            "idUsuariSupervisor": supervisor_local["idUsuari"],
            "idUsuariParticipant": participant_local["idUsuari"],
            "comentari": "Comentari de prova",
        })
        assert r_abans.status_code == 200

        client.put(
            f"/programes/{programa_local['idPrograma']}/supervisors/{supervisor_local['idUsuari']}",
            json={"actiu": False},
        )

        # Amb el supervisor desactivat, el feedback ha de deixar de validar-se
        r_despres = client.post("/feedback", json={
            "idPrograma": programa_local["idPrograma"],
            "idUsuariSupervisor": supervisor_local["idUsuari"],
            "idUsuariParticipant": participant_local["idUsuari"],
            "comentari": "Segon comentari",
        })
        assert r_despres.status_code == 400, (
            "Si aixo falla, es_supervisor() ja no filtra per actiu "
            "(regressio)."
        )

    def test_cp52_put_participant_inexistent_404(self, client):
        r = client.put("/programes/999999/participants/999999", json={"actiu": False})
        assert r.status_code == 404
        assert r.json()["detail"] == "Assignació de participant no trobada"

    def test_cp53_put_supervisor_inexistent_404(self, client):
        r = client.put("/programes/999999/supervisors/999999", json={"actiu": False})
        assert r.status_code == 404
        assert r.json()["detail"] == "Assignació de supervisor no trobada"

    # --- Objectius, accions i KPI -----------------------------------------

    def test_cp54_editar_objectiu(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla per objectius editables", "actiu": True,
        }).json()
        objectiu = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "Descripcio original", "valor": 100,
        }).json()

        r = client.put(f"/objectius/{objectiu['idObjectiu']}", json={
            "descripcio": "Descripcio editada", "valor": 150,
        })
        assert r.status_code == 200
        body = r.json()
        assert body["descripcio"] == "Descripcio editada"
        assert body["valor"] == 150

    def test_cp55_desactivar_objectiu_no_apareix_a_pla_detallat_pero_si_al_llistat_complet(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla amb objectiu desactivable", "actiu": True,
        }).json()
        objectiu_a_mantenir = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "Objectiu que es manté", "valor": 100,
        }).json()
        objectiu_a_desactivar = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "Objectiu que es desactiva", "valor": 100,
        }).json()

        detall_abans = client.get(f"/plans/{pla['idPla']}").json()
        assert len(detall_abans["objectius"]) == 2

        r = client.put(f"/objectius/{objectiu_a_desactivar['idObjectiu']}", json={"actiu": False})
        assert r.status_code == 200
        assert r.json()["actiu"] is False

        detall_despres = client.get(f"/plans/{pla['idPla']}").json()
        assert len(detall_despres["objectius"]) == 1, (
            "Si aixo falla, get_by_pla() del repositori d'objectius ha "
            "deixat de filtrar per actiu (regressio)."
        )
        assert detall_despres["objectius"][0]["idObjectiu"] == objectiu_a_mantenir["idObjectiu"]

        llistat_complet = client.get(f"/plans/{pla['idPla']}/objectius").json()
        assert len(llistat_complet) == 2, (
            "El llistat de gestio ha de seguir mostrant l'objectiu "
            "desactivat, per poder-lo reactivar."
        )

    def test_cp56_editar_accio(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla per accions editables", "actiu": True,
        }).json()
        objectiu = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "obj", "valor": 100,
        }).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "Titol original", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()

        r = client.put(f"/accions/{accio['idAccio']}", json={"titol": "Titol editat"})
        assert r.status_code == 200
        assert r.json()["titol"] == "Titol editat"

    def test_cp57_desactivar_accio_no_apareix_dins_objectiu_detallat(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla amb accio desactivable", "actiu": True,
        }).json()
        objectiu = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "obj", "valor": 100,
        }).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "Accio a desactivar", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()

        r = client.put(f"/accions/{accio['idAccio']}", json={"actiu": False})
        assert r.status_code == 200

        detall = client.get(f"/plans/{pla['idPla']}").json()
        accions_objectiu = detall["objectius"][0]["accions"]
        assert accions_objectiu == []

        llistat_complet = client.get(f"/objectius/{objectiu['idObjectiu']}/accions").json()
        assert len(llistat_complet) == 1
        assert llistat_complet[0]["actiu"] is False

    def test_cp58_editar_kpi(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla per kpi editable", "actiu": True,
        }).json()
        objectiu = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "obj", "valor": 100,
        }).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "Nom original", "descripcio": "desc",
            "periodicitat": "setmanal",
        }).json()

        r = client.put(f"/kpis/{kpi['idKPI']}", json={"nom": "Nom editat"})
        assert r.status_code == 200
        assert r.json()["nom"] == "Nom editat"

    def test_cp59_desactivar_kpi_no_apareix_dins_accio_detallada(self, client, programa):
        pla = client.post("/plans", json={
            "idPrograma": programa["idPrograma"], "titol": "Pla amb kpi desactivable", "actiu": True,
        }).json()
        objectiu = client.post("/objectius", json={
            "idPla": pla["idPla"], "descripcio": "obj", "valor": 100,
        }).json()
        accio = client.post("/accions", json={
            "idObjectiu": objectiu["idObjectiu"], "titol": "acc", "descripcio": "desc",
            "dataInici": "2026-01-01", "dataFi": "2026-01-31",
        }).json()
        kpi = client.post("/kpis", json={
            "idAccio": accio["idAccio"], "nom": "KPI a desactivar", "descripcio": "desc",
            "periodicitat": "setmanal",
        }).json()

        r = client.put(f"/kpis/{kpi['idKPI']}", json={"actiu": False})
        assert r.status_code == 200

        detall = client.get(f"/plans/{pla['idPla']}").json()
        kpis_accio = detall["objectius"][0]["accions"][0]["kpis"]
        assert kpis_accio == []

        llistat_complet = client.get(f"/accions/{accio['idAccio']}/kpis").json()
        assert len(llistat_complet) == 1
        assert llistat_complet[0]["actiu"] is False

    def test_cp60_put_objectiu_accio_kpi_inexistents_404(self, client):
        r1 = client.put("/objectius/999999", json={"actiu": False})
        assert r1.status_code == 404
        assert r1.json()["detail"] == "Objectiu no trobat"

        r2 = client.put("/accions/999999", json={"actiu": False})
        assert r2.status_code == 404
        assert r2.json()["detail"] == "Acció no trobada"

        r3 = client.put("/kpis/999999", json={"actiu": False})
        assert r3.status_code == 404


# ---------------------------------------------------------------------------
# 4.9 Transversal
# ---------------------------------------------------------------------------

class TestTransversal:
    def test_cp38_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_cp38b_root(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_cp37_cors_header_presente(self, client):
        # allow_origins=["*"] + allow_credentials=True hace que Starlette
        # haga eco del Origin recibido en vez de devolver literalmente "*"
        # (comportamiento estandar del middleware cuando se permiten
        # credenciales). Lo relevante es que CUALQUIER origen sea aceptado.
        origen = "http://cualquier-origen.test"
        r = client.get("/health", headers={"Origin": origen})
        assert r.headers.get("access-control-allow-origin") == origen
        assert r.headers.get("access-control-allow-credentials") == "true"
