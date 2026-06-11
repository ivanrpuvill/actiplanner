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
Ets un assistent d'Actiplanner, una plataforma de seguiment de plans d'acció derivats de processos de formació empresarial.

Analitza les dades següents d'un programa de formació i genera una resposta professional per a un supervisor.

Dades del programa:
{self._format_context(context)}

Retorna únicament JSON vàlid amb aquesta estructura:

{{
  "resumGeneral": "",
  "aspectesPositius": [],
  "riscosDetectats": [],
  "recomanacions": []
}}

Condicions:
- Escriu en català.
- No afegeixis text fora del JSON.
- No utilitzis markdown.
- No inventis dades que no apareguin al context.
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
Ets un assistent d'Actiplanner que ajuda supervisors a redactar feedback constructiu.

Genera una proposta de feedback breu, clara i professional per al participant indicat.

Context:
{self._format_context(context)}

Retorna únicament JSON vàlid amb aquesta estructura:

{{
  "feedbackProposat": "",
  "puntsForts": [],
  "aspectesMillora": [],
  "to": "constructiu"
}}

Condicions:
- Escriu en català.
- No afegeixis text fora del JSON.
- No utilitzis markdown.
- No inventis dades concretes que no apareguin al context.
- No facis canvis automàtics al sistema.
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
Ets un assistent d'Actiplanner.

Analitza el resum de progrés del pla d'acció següent i genera una interpretació breu per a un supervisor o administrador.

Dades del pla:
{self._format_context(resum_pla)}

Retorna únicament JSON vàlid amb aquesta estructura:

{{
  "estatGeneral": "",
  "objectiusAvancats": [],
  "objectiusAtencio": [],
  "recomanacioFinal": ""
}}

Condicions:
- Escriu en català.
- No afegeixis text fora del JSON.
- No utilitzis markdown.
- No inventis dades que no apareguin al context.
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