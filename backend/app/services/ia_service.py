import json
import os

from dotenv import load_dotenv
from google import genai

from app.services.analisi_service import AnalisiService
from app.services.feedback_service import FeedbackService
from app.services.pla_accio_service import PlaAccioService


class IAService:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

        self.analisi_service = AnalisiService()
        self.feedback_service = FeedbackService()
        self.pla_accio_service = PlaAccioService()

    def generar_resum_programa(self, idPrograma: int) -> dict:
        analisi = self.analisi_service.get_analisi_programa(idPrograma)
        objectius_risc = self.analisi_service.get_objectius_risc(idPrograma)
        participants_desviacio = (
            self.analisi_service.get_participants_amb_desviacio(idPrograma)
        )

        context = {
            "analisiPrograma": analisi,
            "objectiusRisc": objectius_risc,
            "participantsAmbDesviacio": participants_desviacio
        }

        prompt = f"""
Actua com un consultor expert en gestió del canvi i seguiment de programes de formació.

Analitza les dades següents.

Context:
{self._format_context(context)}

No facis un resum descriptiu.

Genera:
- una valoració global
- una interpretació dels KPI i del progrés
- riscos de consolidació
- recomanacions accionables per al supervisor
- prioritats de seguiment

Retorna exclusivament JSON vàlid:

{{
  "resumExecutiu": "",
  "diagnostic": "",
  "riscos": [
    {{
      "titol": "",
      "nivell": "baix|mitja|alt",
      "explicacio": ""
    }}
  ],
  "recomanacions": [
    {{
      "accio": "",
      "prioritat": "baixa|mitjana|alta",
      "impacteEsperat": ""
    }}
  ],
  "indicadorsClau": [
    {{
      "nom": "",
      "valor": "",
      "interpretacio": ""
    }}
  ]
}}
"""

        analisi_generada = self._generar_json(prompt)

        return {
            "idPrograma": idPrograma,
            "tipus": "resum_programa",
            "analisiGenerada": analisi_generada
        }

    def generar_recomanacio_feedback(
        self,
        idPrograma: int,
        idUsuariParticipant: int
    ) -> dict:
        feedbacks = self.feedback_service.get_feedbacks_programa_participant(
            idPrograma,
            idUsuariParticipant
        )

        progres = self.analisi_service._calcular_progres_participant(
            idPrograma,
            idUsuariParticipant
        )

        context = {
            "idPrograma": idPrograma,
            "idUsuariParticipant": idUsuariParticipant,
            "progresCalculat": progres,
            "feedbacksPrevis": [
                feedback.model_dump()
                for feedback in feedbacks
            ]
        }

        prompt = f"""
Actua com un supervisor expert en desenvolupament professional.

Context:
{self._format_context(context)}

Genera feedback accionable i específic.

Retorna exclusivament:

{{
  "missatgeFeedback": "",
  "puntsForts": [],
  "puntsMillora": [],
  "properesAccions": [],
  "nivellPrioritat": "baix|mitja|alt"
}}
"""

        feedback_generat = self._generar_json(prompt)

        return {
            "idPrograma": idPrograma,
            "idUsuariParticipant": idUsuariParticipant,
            "tipus": "recomanacio_feedback",
            "feedbackGenerat": feedback_generat
        }

    def generar_resum_pla(self, idPla: int) -> dict:
        resum_pla = self.pla_accio_service.get_resum_progres_pla(idPla)

        if resum_pla is None:
            return {
                "idPla": idPla,
                "tipus": "resum_pla",
                "resposta": "No s'ha trobat el pla d'acció indicat."
            }

        prompt = f"""
Actua com un consultor en seguiment de plans d'acció.

Context:
{self._format_context(resum_pla)}

Avalua:
- qualitat del pla
- coherència entre objectius i KPI
- riscos
- millores

Retorna exclusivament:

{{
  "avaluacioGeneral": "",
  "fortaleses": [],
  "febleses": [],
  "riscos": [],
  "milloresRecomanades": []
}}
"""

        analisi_generada = self._generar_json(prompt)

        return {
            "idPla": idPla,
            "tipus": "resum_pla",
            "analisiGenerada": analisi_generada
        }

    def _generar_json(self, prompt: str) -> dict:
        if self.client is None:
            return {
                "error": True,
                "missatge": (
                    "El mòdul d'intel·ligència artificial no està disponible "
                    "perquè no s'ha configurat la variable GEMINI_API_KEY."
                )
            }

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()

            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            elif text.startswith("```"):
                text = text.replace("```", "").strip()

            return json.loads(text)

        except Exception as error:
            print(f"Error IA: {error}")

            return {
                "error": True,
                "missatge": (
                    "El servei d'intel·ligència artificial no està disponible temporalment."
                    "La resta de funcionalitats d'Actiplanner continuen operatives."
                )
            }

    def _format_context(self, data) -> str:
        return json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    def generar_proposta_pla(self, idPrograma: int) -> dict:
        analisi = self.analisi_service.get_analisi_programa(idPrograma)
        objectius_risc = self.analisi_service.get_objectius_risc(idPrograma)
        participants_desviacio = self.analisi_service.get_participants_amb_desviacio(idPrograma)

        context = {
            "analisiPrograma": analisi,
            "objectiusRisc": objectius_risc,
            "participantsAmbDesviacio": participants_desviacio
        }

        prompt = f"""
    Actua com un consultor expert en disseny de plans d'acció per consolidar canvis després d'una formació empresarial.

    A partir de les dades del programa, genera una proposta de pla d'acció que es pugui incorporar a Actiplanner.

    Context:
    {self._format_context(context)}

    Retorna exclusivament JSON vàlid amb aquesta estructura:

    {{
    "titol": "",
    "descripcio": "",
    "objectius": [
        {{
        "descripcio": "",
        "valor": 100,
        "accions": [
            {{
            "titol": "",
            "descripcio": "",
            "kpis": [
                {{
                "nom": "",
                "descripcio": "",
                "periodicitat": "setmanal",
                "tipus": "numeric|percentatge|escala|boolea",
                "orientacio": "major_millor|menor_millor",
                "valorMinim": 0,
                "valorMaxim": 100,
                "valorObjectiu": 80
                }}
            ]
            }}
        ]
        }}
    ]
    }}

    Condicions:
    - Escriu en català.
    - Genera entre 2 i 4 objectius.
    - Cada objectiu ha de tenir entre 1 i 3 accions.
    - Cada acció ha de tenir entre 1 i 2 KPI.
    - Els KPI han de ser mesurables.
    - Si el KPI és percentatge, usa valorMinim=0, valorMaxim=100.
    - Si el KPI és boolea, usa valorMinim=0, valorMaxim=1, valorObjectiu=1.
    - No afegeixis text fora del JSON.
    - No utilitzis markdown.
    - No inventis dades personals de participants.
    """

        proposta = self._generar_json(prompt)

        return {
            "idPrograma": idPrograma,
            "tipus": "proposta_pla",
            "proposta": proposta
        }