from datetime import date
from app.models.pla_accio import PlaAccio, PlaAccioCreate, PlaAccioUpdate
from app.models.objectiu_pla import ObjectiuPla, ObjectiuPlaCreate, ObjectiuPlaUpdate
from app.models.accio import Accio, AccioCreate, AccioUpdate
from app.models.kpi import KPI, KPICreate, KPIUpdate
from app.repositories.pla_accio_repository import PlaAccioRepository
from app.repositories.objectiu_pla_repository import ObjectiuPlaRepository
from app.repositories.accio_repository import AccioRepository
from app.repositories.kpi_repository import KPIRepository
from app.repositories.registre_kpi_repository import RegistreKPIRepository
from app.repositories.programa_formacio_repository import ProgramaFormacioRepository
from app.services.analisi_service import AnalisiService


class PlaAccioService:
    def __init__(self):
        self.pla_repository = PlaAccioRepository()
        self.objectiu_repository = ObjectiuPlaRepository()
        self.accio_repository = AccioRepository()
        self.kpi_repository = KPIRepository()
        self.registre_kpi_repository = RegistreKPIRepository()
        self.programa_repository = ProgramaFormacioRepository()
        self.analisi_service = AnalisiService()

    def get_pla_detallat(self, idPla: int) -> dict | None:
        pla = self.pla_repository.get_by_id(idPla)

        if pla is None:
            return None

        objectius = self.objectiu_repository.get_by_pla(idPla)
        objectius_detallats = []
        progres_objectius = []

        for objectiu in objectius:
            accions = self.accio_repository.get_by_objectiu(objectiu.idObjectiu)
            accions_detallades = []
            valors_accions = []

            for accio in accions:
                kpis = self.kpi_repository.get_by_accio(accio.idAccio)
                kpis_detallats = []
                valors_kpi = []

                for kpi in kpis:
                    registres = self.registre_kpi_repository.get_by_kpi(kpi.idKPI)

                    if registres:
                        valor_agregat = self.analisi_service._agregar_registres_kpi(
                            kpi, registres
                        )
                        assoliment = self.analisi_service._calcular_assoliment_kpi(
                            kpi, valor_agregat
                        )
                        ultim_registre = max(
                            registres,
                            key=lambda registre: registre.dataRegistre
                        )
                        data_ultim_registre = ultim_registre.dataRegistre
                    else:
                        valor_agregat = None
                        assoliment = 0
                        data_ultim_registre = None

                    valors_kpi.append(assoliment)

                    kpis_detallats.append({
                        "idKPI": kpi.idKPI,
                        "nom": kpi.nom,
                        "descripcio": kpi.descripcio,
                        "periodicitat": kpi.periodicitat,
                        "tipus": kpi.tipus,
                        "tipusCalcul": kpi.tipusCalcul,
                        "orientacio": kpi.orientacio,
                        "valorMinim": kpi.valorMinim,
                        "valorMaxim": kpi.valorMaxim,
                        "valorObjectiu": kpi.valorObjectiu,
                        "valorAgregat": valor_agregat,
                        "assoliment": assoliment,
                        "estatKPI": self.analisi_service._calcular_estat_kpi(assoliment),
                        "ultimValor": valor_agregat,
                        "dataUltimRegistre": data_ultim_registre
                    })

                progres_accio = self._calcular_mitjana(valors_kpi)
                valors_accions.append(progres_accio)

                accions_detallades.append({
                    "idAccio": accio.idAccio,
                    "titol": accio.titol,
                    "descripcio": accio.descripcio,
                    "dataInici": accio.dataInici,
                    "dataFi": accio.dataFi,
                    "progresAccio": progres_accio,
                    "estatAccio": self._calcular_estat(progres_accio),
                    "kpis": kpis_detallats
                })

            progres_objectiu = self._calcular_mitjana(valors_accions)
            progres_objectius.append(progres_objectiu)

            objectius_detallats.append({
                "idObjectiu": objectiu.idObjectiu,
                "descripcio": objectiu.descripcio,
                "valor": objectiu.valor,
                "progresObjectiu": progres_objectiu,
                "estatObjectiu": self._calcular_estat(progres_objectiu),
                "accions": accions_detallades
            })

        progres_pla = self._calcular_mitjana(progres_objectius)

        return {
            "idPla": pla.idPla,
            "idPrograma": pla.idPrograma,
            "titol": pla.titol,
            "dataCreacio": pla.dataCreacio,
            "actiu": pla.actiu,
            "progresPla": progres_pla,
            "estatPla": self._calcular_estat(progres_pla),
            "objectius": objectius_detallats
        }

    def _calcular_mitjana(self, valors: list[float]) -> float:
        if not valors:
            return 0

        return round(sum(valors) / len(valors), 2)

    def _calcular_estat(self, progres: float) -> str:
        """
        Estat agregat (acció, objectiu, pla). El llindar d'assoliment es
        manté al 80% perquè, en agregar diversos KPI heterogenis
        mitjançant una mitjana, exigir el 100% faria que gairebé cap
        nivell compost arribés mai a "assolit" tot i tenir un rendiment
        molt alt en tots els seus components. Coherent amb AnalisiService.
        """
        if progres >= 80:
            return "assolit"
        if progres >= 20:
            return "en_progres"
        return "pendent"

    def get_resum_progres_pla(self, idPla: int) -> dict | None:
        pla = self.pla_repository.get_by_id(idPla)

        if pla is None:
            return None

        objectius = self.objectiu_repository.get_by_pla(idPla)
        resum_objectius = []

        for objectiu in objectius:
            accions = self.accio_repository.get_by_objectiu(objectiu.idObjectiu)
            valors_objectiu = []

            for accio in accions:
                kpis = self.kpi_repository.get_by_accio(accio.idAccio)

                for kpi in kpis:
                    registres = self.registre_kpi_repository.get_by_kpi(kpi.idKPI)

                    if registres:
                        valor_agregat = self.analisi_service._agregar_registres_kpi(
                            kpi, registres
                        )
                        assoliment = self.analisi_service._calcular_assoliment_kpi(
                            kpi, valor_agregat
                        )
                        valors_objectiu.append(assoliment)

            progres_objectiu = self._calcular_mitjana(valors_objectiu)

            resum_objectius.append({
                "idObjectiu": objectiu.idObjectiu,
                "descripcio": objectiu.descripcio,
                "valor": objectiu.valor,
                "progresObjectiu": progres_objectiu,
                "estatObjectiu": self._calcular_estat(progres_objectiu)
            })

        progres_pla = self._calcular_mitjana([
            objectiu["progresObjectiu"]
            for objectiu in resum_objectius
        ])

        return {
            "idPla": pla.idPla,
            "idPrograma": pla.idPrograma,
            "titol": pla.titol,
            "progresPla": progres_pla,
            "estatPla": self._calcular_estat(progres_pla),
            "objectius": resum_objectius
        }

    def get_plans_programa(self, idPrograma: int):
        return self.pla_repository.get_by_programa(idPrograma)

    def create_pla(self, pla: PlaAccioCreate):
        programa = self.programa_repository.get_by_id(pla.idPrograma)

        if programa is None:
            return None

        nou_pla = PlaAccio(
            idPla=self.pla_repository.next_id(),
            dataCreacio=date.today().isoformat(),
            **pla.model_dump()
        )

        return self.pla_repository.create(nou_pla)

    def update_pla(self, idPla: int, pla: PlaAccioUpdate):
        pla_actual = self.pla_repository.get_by_id(idPla)

        if pla_actual is None:
            return None

        data = pla_actual.model_dump()
        data.update(pla.model_dump(exclude_unset=True))
        data["idPla"] = idPla

        pla_actualitzat = PlaAccio(**data)

        return self.pla_repository.update(idPla, pla_actualitzat)

    def get_objectiu(self, idObjectiu: int):
        return self.objectiu_repository.get_by_id(idObjectiu)

    def get_objectius_pla(self, idPla: int):
        return self.objectiu_repository.get_all_by_pla(idPla)

    def create_objectiu(self, objectiu: ObjectiuPlaCreate):
        pla = self.pla_repository.get_by_id(objectiu.idPla)

        if pla is None:
            return None

        nou_objectiu = ObjectiuPla(
            idObjectiu=self.objectiu_repository.next_id(),
            **objectiu.model_dump()
        )

        return self.objectiu_repository.create(nou_objectiu)

    def update_objectiu(self, idObjectiu: int, objectiu: ObjectiuPlaUpdate):
        objectiu_actual = self.objectiu_repository.get_by_id(idObjectiu)

        if objectiu_actual is None:
            return None

        data = objectiu_actual.model_dump()
        data.update(objectiu.model_dump(exclude_unset=True))
        data["idObjectiu"] = idObjectiu

        objectiu_actualitzat = ObjectiuPla(**data)

        return self.objectiu_repository.update(idObjectiu, objectiu_actualitzat)

    def get_accio(self, idAccio: int):
        return self.accio_repository.get_by_id(idAccio)

    def get_accions_objectiu(self, idObjectiu: int):
        return self.accio_repository.get_all_by_objectiu(idObjectiu)

    def create_accio(self, accio: AccioCreate):
        objectiu = self.objectiu_repository.get_by_id(accio.idObjectiu)

        if objectiu is None:
            return None

        nova_accio = Accio(
            idAccio=self.accio_repository.next_id(),
            **accio.model_dump()
        )

        return self.accio_repository.create(nova_accio)

    def update_accio(self, idAccio: int, accio: AccioUpdate):
        accio_actual = self.accio_repository.get_by_id(idAccio)

        if accio_actual is None:
            return None

        data = accio_actual.model_dump()
        data.update(accio.model_dump(exclude_unset=True))
        data["idAccio"] = idAccio

        accio_actualitzada = Accio(**data)

        return self.accio_repository.update(idAccio, accio_actualitzada)

    def get_kpis_accio(self, idAccio: int):
        return self.kpi_repository.get_all_by_accio(idAccio)

    def create_kpi(self, kpi: KPICreate):
        accio = self.accio_repository.get_by_id(kpi.idAccio)

        if accio is None:
            return None

        nou_kpi = KPI(
            idKPI=self.kpi_repository.next_id(),
            **kpi.model_dump()
        )

        return self.kpi_repository.create(nou_kpi)

    def update_kpi(self, idKPI: int, kpi: KPIUpdate):
        kpi_actual = self.kpi_repository.get_by_id(idKPI)

        if kpi_actual is None:
            return None

        data = kpi_actual.model_dump()
        data.update(kpi.model_dump(exclude_unset=True))
        data["idKPI"] = idKPI

        kpi_actualitzat = KPI(**data)

        return self.kpi_repository.update(idKPI, kpi_actualitzat)