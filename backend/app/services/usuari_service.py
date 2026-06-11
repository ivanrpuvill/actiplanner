from app.models.usuari import Usuari
from app.models.programa_participant import ProgramaParticipant
from app.models.programa_supervisor import ProgramaSupervisor
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

    def create_usuari(self, usuari: Usuari):
        data = usuari.model_dump()
        data["idUsuari"] = self.usuari_repository.next_id()

        nou_usuari = Usuari(**data)

        return self.usuari_repository.create(nou_usuari)

    def update_usuari(self, idUsuari: int, usuari: Usuari):
        data = usuari.model_dump()
        data["idUsuari"] = idUsuari

        usuari_actualitzat = Usuari(**data)

        return self.usuari_repository.update(idUsuari, usuari_actualitzat)

    def assignar_participant(self, participant: ProgramaParticipant):
        if self.get_usuari(participant.idUsuari) is None:
            return None

        return self.programa_participant_repository.create(participant)

    def update_participant_programa(
        self,
        idPrograma: int,
        idUsuari: int,
        participant: ProgramaParticipant
    ):
        participant_actualitzat = ProgramaParticipant(
            **participant.model_dump()
        )
        participant_actualitzat.idPrograma = idPrograma
        participant_actualitzat.idUsuari = idUsuari

        return self.programa_participant_repository.update(
            idPrograma,
            idUsuari,
            participant_actualitzat
        )

    def assignar_supervisor(self, supervisor: ProgramaSupervisor):
        if self.get_usuari(supervisor.idUsuari) is None:
            return None

        return self.programa_supervisor_repository.create(supervisor)