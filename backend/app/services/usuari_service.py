from datetime import date
from app.models.usuari import Usuari, UsuariCreate, UsuariUpdate
from app.models.programa_participant import ProgramaParticipant, ProgramaParticipantCreate, ProgramaParticipantUpdate
from app.models.programa_supervisor import ProgramaSupervisor, ProgramaSupervisorCreate
from app.repositories.usuari_repository import UsuariRepository
from app.repositories.programa_participant_repository import ProgramaParticipantRepository
from app.repositories.programa_supervisor_repository import ProgramaSupervisorRepository


class UsuariService:
    def __init__(self):
        self.usuari_repository = UsuariRepository()
        self.participant_repository = ProgramaParticipantRepository()
        self.supervisor_repository = ProgramaSupervisorRepository()
        self.programa_participant_repository = ProgramaParticipantRepository()
        self.programa_supervisor_repository = ProgramaSupervisorRepository()

    def get_usuaris(self) -> list[Usuari]:
        return self.usuari_repository.get_all()

    def get_usuari(self, idUsuari: int) -> Usuari | None:
        return self.usuari_repository.get_by_id(idUsuari)

    def get_administradors(self) -> list[Usuari]:
        return self.usuari_repository.get_administradors()

    def es_participant(self, idUsuari: int, idPrograma: int) -> bool:
        participacions = self.participant_repository.get_by_usuari(idUsuari)

        return any(
            item.idPrograma == idPrograma
            for item in participacions
        )

    def es_supervisor(self, idUsuari: int, idPrograma: int) -> bool:
        supervisiones = self.supervisor_repository.get_by_usuari(idUsuari)

        return any(
            item.idPrograma == idPrograma
            for item in supervisiones
        )

    def get_rols_usuari(self, idUsuari: int) -> dict:
        usuari = self.get_usuari(idUsuari)

        if usuari is None:
            return {}

        programes_participant = self.participant_repository.get_by_usuari(idUsuari)
        programes_supervisor = self.supervisor_repository.get_by_usuari(idUsuari)

        return {
            "idUsuari": usuari.idUsuari,
            "nom": usuari.nom,
            "cognoms": usuari.cognoms,
            "esAdministrador": usuari.esAdministrador,
            "programesParticipant": [
                item.idPrograma for item in programes_participant
            ],
            "programesSupervisor": [
                item.idPrograma for item in programes_supervisor
            ]
        }

    def create_usuari(self, usuari: UsuariCreate):
        data = usuari.model_dump()
        password = data.pop("password")

        nou_usuari = Usuari(
            idUsuari=self.usuari_repository.next_id(),
            passwordHash=password,
            dataCreacio=date.today().isoformat(),
            **data
        )

        return self.usuari_repository.create(nou_usuari)

    def update_usuari(self, idUsuari: int, usuari: UsuariUpdate):
        usuari_actual = self.usuari_repository.get_by_id(idUsuari)

        if usuari_actual is None:
            return None

        data = usuari_actual.model_dump()
        update_data = usuari.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["passwordHash"] = update_data.pop("password")

        data.update(update_data)
        data["idUsuari"] = idUsuari

        usuari_actualitzat = Usuari(**data)

        return self.usuari_repository.update(idUsuari, usuari_actualitzat)

    def assignar_participant(self, idPrograma: int, participant: ProgramaParticipantCreate):
        if self.get_usuari(participant.idUsuari) is None:
            return None

        nou_participant = ProgramaParticipant(
            idPrograma=idPrograma,
            idUsuari=participant.idUsuari,
            estatParticipacio=participant.estatParticipacio,
            dataAssignacio=date.today().isoformat()
        )

        return self.programa_participant_repository.create(nou_participant)

    def update_participant_programa(self, idPrograma: int, idUsuari: int, participant: ProgramaParticipantUpdate):
        participant_actual = self.programa_participant_repository.get_by_programa_usuari(
            idPrograma,
            idUsuari
        )

        if participant_actual is None:
            return None

        data = participant_actual.model_dump()
        data.update(participant.model_dump(exclude_unset=True))
        data["idPrograma"] = idPrograma
        data["idUsuari"] = idUsuari

        participant_actualitzat = ProgramaParticipant(**data)

        return self.programa_participant_repository.update(
            idPrograma,
            idUsuari,
            participant_actualitzat
        )

    def assignar_supervisor(self, idPrograma: int, supervisor: ProgramaSupervisorCreate):
        if self.get_usuari(supervisor.idUsuari) is None:
            return None

        nou_supervisor = ProgramaSupervisor(
            idPrograma=idPrograma,
            idUsuari=supervisor.idUsuari,
            dataAssignacio=date.today().isoformat()
        )

        return self.programa_supervisor_repository.create(nou_supervisor)