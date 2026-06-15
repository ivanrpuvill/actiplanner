import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP08DashboardSupervisor(app, navegar) {
  const programa = obtenirProgramaActiu();

  if (!programa) {
    app.innerHTML = renderLayout("Dashboard supervisor", `
      <div class="card">
        <h3>No hi ha cap programa seleccionat</h3>
        <p>Selecciona un programa abans d'accedir al dashboard de supervisor.</p>
        <button class="btn" id="btnSeleccionarPrograma">Seleccionar programa</button>
      </div>
    `);

    activarLayoutEvents(navegar);

    document.getElementById("btnSeleccionarPrograma").addEventListener("click", () => {
      navegar("P02");
    });

    return;
  }

  app.innerHTML = renderLayout("Dashboard supervisor", `
    <div id="supervisorDashboardContainer" class="dashboard-grid">
      <div class="card">Carregant dades del programa...</div>
    </div>
  `);

  activarLayoutEvents(navegar);

  const container = document.getElementById("supervisorDashboardContainer");

  try {
    const [
      analisi,
      objectiusRisc,
      participantsDestacats,
      participantsDesviacio,
      feedbacksPrograma,
      plansPrograma
    ] = await Promise.all([
      apiGet(`/programes/${programa.idPrograma}/analisi`),
      apiGet(`/programes/${programa.idPrograma}/objectius-risc`),
      apiGet(`/programes/${programa.idPrograma}/participants-destacats`),
      apiGet(`/programes/${programa.idPrograma}/participants-desviacio`),
      apiGet(`/programes/${programa.idPrograma}/feedback`),
      apiGet(`/programes/${programa.idPrograma}/plans`)
    ]);

    const totalPlans = plansPrograma.length;
    const totalFeedbacks = feedbacksPrograma.length;
    const totalObjectiusRisc = objectiusRisc.length;
    const totalParticipantsDesviacio = participantsDesviacio.length;
    const totalParticipantsDestacats = participantsDestacats.length;

    const alertes = [];

    if (totalPlans === 0) {
      alertes.push("Aquest programa encara no té plans d'acció associats.");
    }

    if (totalObjectiusRisc > 0) {
      alertes.push(`${totalObjectiusRisc} objectius es troben en situació de risc.`);
    }

    if (totalParticipantsDesviacio > 0) {
      alertes.push(`${totalParticipantsDesviacio} participants presenten desviació.`);
    }

    if (totalFeedbacks === 0) {
      alertes.push("Encara no s'ha registrat cap feedback en aquest programa.");
    }

    container.innerHTML = `
      <div class="card dashboard-wide">
        <h3>${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}</h3>
        <p>Quadre de comandament del supervisor per al seguiment agregat del programa seleccionat.</p>
      </div>

      <div class="card stat-card clickable-card" id="cardPlans">
        <h3>Plans d'acció</h3>
        <p class="stat-number">${totalPlans}</p>
        <p class="stat-subtitle">Veure plans del programa</p>
      </div>

      <div class="card stat-card">
        <h3>Objectius en risc</h3>
        <p class="stat-number">${totalObjectiusRisc}</p>
        <p class="stat-subtitle">Requereixen seguiment</p>
      </div>

      <div class="card stat-card">
        <h3>Participants amb desviació</h3>
        <p class="stat-number">${totalParticipantsDesviacio}</p>
        <p class="stat-subtitle">Possibles casos a revisar</p>
      </div>

      <div class="card stat-card">
        <h3>Participants destacats</h3>
        <p class="stat-number">${totalParticipantsDestacats}</p>
        <p class="stat-subtitle">Millor evolució registrada</p>
      </div>

      <div class="card stat-card">
        <h3>Feedbacks</h3>
        <p class="stat-number">${totalFeedbacks}</p>
        <p class="stat-subtitle">Feedbacks registrats</p>
      </div>

      <div class="card stat-card">
        <h3>Progrés mitjà</h3>
        <p class="stat-number">
          ${formatPercentatge(
            analisi.progresMitjaPrograma ?? analisi.progresMitja
          )}
        </p>
        <p class="stat-subtitle">Indicador agregat del programa</p>
      </div>

      <div class="card dashboard-wide">
        <h3>⚠ Alertes de seguiment</h3>
        ${renderAlertes(alertes)}
      </div>

      <div class="card dashboard-wide">
        <h3>Objectius en risc</h3>
        ${renderObjectiusRisc(objectiusRisc)}
      </div>

      <div class="card dashboard-wide">
        <h3>Participants amb desviació</h3>
        ${renderParticipants(
          participantsDesviacio,
          "No hi ha participants amb desviació detectada.",
          "desviacio"
        )}
      </div>

      <div class="card dashboard-wide">
        <h3>Participants destacats</h3>
        ${renderParticipants(
          participantsDestacats,
          "No hi ha participants destacats detectats.",
          "destacat"
        )}
      </div>

      <div class="card dashboard-wide">
        <h3>Informe del programa</h3>
        <p>
          El programa disposa de <strong>${totalPlans}</strong> plans d'acció,
          <strong>${totalObjectiusRisc}</strong> objectius en risc i
          <strong>${totalParticipantsDesviacio}</strong> participants amb desviació.
        </p>
        <p>
          S'han registrat <strong>${totalFeedbacks}</strong> feedbacks i
          <strong>${totalParticipantsDestacats}</strong> participants apareixen com a destacats.
        </p>
      </div>

      <div class="card dashboard-wide">
        <h3>Accions ràpides</h3>
        <div class="button-grid">
          <button class="btn" id="btnParticipants">Veure participants</button>
          <button class="btn" id="btnFeedback">Gestionar feedback</button>
          <button class="btn secondary" id="btnRecomanacions">Recomanacions IA</button>
          <button class="btn secondary" id="btnRankings">Rànquings</button>
        </div>
      </div>
    `;

    document.getElementById("cardPlans").addEventListener("click", () => {
      sessionStorage.setItem("filtreProgramaPlans", programa.idPrograma);
      navegar("P16");
    });
    document.getElementById("btnParticipants").addEventListener("click", () => navegar("P09"));
    document.getElementById("btnFeedback").addEventListener("click", () => navegar("P10"));
    document.getElementById("btnRecomanacions").addEventListener("click", () => navegar("P11"));
    document.getElementById("btnRankings").addEventListener("click", () => navegar("P19"));
    document.querySelectorAll("[data-id-usuari]").forEach((button) => {
    button.addEventListener("click", () => {
      sessionStorage.setItem(
        "idUsuariParticipantSeleccionat",
        button.dataset.idUsuari
      );

    navegar("P09");
  });
});

  } catch (error) {
    container.innerHTML = `<div class="card error-text">${error.message}</div>`;
  }
}

function renderAlertes(alertes) {
  if (!alertes.length) {
    return `<p>No s'han detectat alertes rellevants en aquest programa.</p>`;
  }

  return `
    <ul>
      ${alertes.map((alerta) => `
        <li>${alerta}</li>
      `).join("")}
    </ul>
  `;
}

function renderObjectiusRisc(objectius) {
  if (!objectius || !objectius.length) {
    return `<p>No hi ha objectius en risc detectats.</p>`;
  }

  return `
    <div class="list">
      ${objectius.map((objectiu) => `
        <div class="list-item">
          <strong>${objectiu.descripcio || objectiu.nom || objectiu.titol || `Objectiu ${objectiu.idObjectiu || "-"}`}</strong>
          <p>${obtenirIndicadorObjectiu(objectiu)}</p>
        </div>
      `).join("")}
    </div>
  `;
}

function renderParticipants(participants, missatgeBuit, tipus) {
  if (!participants || !participants.length) {
    return `<p>${missatgeBuit}</p>`;
  }

  return `
    <div class="list">
      ${participants.map((participant) => `
        <div class="list-item">
          <strong>${obtenirNomParticipant(participant)}</strong>
          <p>${obtenirIndicadorParticipant(participant, tipus)}</p>
          <button
            class="btn secondary"
            type="button"
            data-id-usuari="${participant.idUsuari || participant.idUsuariParticipant}"
          >
            Veure detall
          </button>
        </div>
      `).join("")}
    </div>
  `;
}

function obtenirNomParticipant(participant) {
  return (
    participant.nomComplet ||
    participant.nom ||
    participant.email ||
    `Usuari ${participant.idUsuari || participant.idUsuariParticipant || "-"}`
  );
}

function obtenirIndicadorObjectiu(objectiu) {
  if (objectiu.progres !== undefined) {
    return `Progrés actual: ${formatPercentatge(objectiu.progres)}`;
  }

  if (objectiu.percentatge !== undefined) {
    return `Progrés actual: ${formatPercentatge(objectiu.percentatge)}`;
  }

  if (objectiu.valorActual !== undefined && objectiu.valorObjectiu !== undefined) {
    return `Valor actual: ${objectiu.valorActual} / ${objectiu.valorObjectiu}`;
  }

  if (objectiu.motiu) {
    return objectiu.motiu;
  }

  return "Aquest objectiu requereix seguiment.";
}

function obtenirIndicadorParticipant(participant, tipus) {
  if (participant.progres !== undefined) {
    return `Progrés: ${formatPercentatge(participant.progres)}`;
  }

  if (participant.percentatge !== undefined) {
    return `Progrés: ${formatPercentatge(participant.percentatge)}`;
  }

  if (participant.desviacio !== undefined) {
    return `Desviació detectada: ${formatPercentatge(participant.desviacio)}`;
  }

  if (participant.motiu) {
    return participant.motiu;
  }

  if (tipus === "destacat") {
    return "Participant amb evolució positiva.";
  }

  return "Participant que requereix seguiment.";
}

function formatPercentatge(valor) {
  if (valor === undefined || valor === null || Number.isNaN(Number(valor))) {
    return "-";
  }

  return `${Math.round(Number(valor))}%`;
}