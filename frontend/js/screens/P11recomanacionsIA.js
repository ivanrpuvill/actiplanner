import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP11RecomanacionsIA(app, navegar) {
  const programa = obtenirProgramaActiu();

  if (!programa) {
    app.innerHTML = renderLayout("Recomanacions IA", `
      <div class="card">
        <h3>No hi ha cap programa seleccionat</h3>
        <p>Selecciona un programa abans de generar recomanacions IA.</p>
        <button class="btn" id="btnSeleccionarPrograma">Seleccionar programa</button>
      </div>
    `);

    activarLayoutEvents(navegar);

    document.getElementById("btnSeleccionarPrograma").addEventListener("click", () => {
      navegar("P02");
    });

    return;
  }

  app.innerHTML = renderLayout("Recomanacions IA", `
    <div class="card">
      <h3>Selecciona un participant</h3>

      <div class="form-grid">
        <div>
          <label>Participant</label>
          <select id="participantSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnGenerarRecomanacio">Generar recomanació</button>
        </div>
      </div>
    </div>

    <div id="iaContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorParticipants(programa);

  document.getElementById("btnGenerarRecomanacio").addEventListener("click", async () => {
    const idParticipant = document.getElementById("participantSelect").value;
    await carregarRecomanacio(programa.idPrograma, idParticipant);
  });
}

async function carregarSelectorParticipants(programa) {
  const select = document.getElementById("participantSelect");

  try {
    const usuaris = await apiGet("/usuaris");
    const participants = [];

    for (const usuari of usuaris) {
      const rols = await apiGet(`/usuaris/${usuari.idUsuari}/rols`);

      if ((rols.programesParticipant || []).includes(programa.idPrograma)) {
        participants.push(usuari);
      }
    }

    if (!participants.length) {
      select.innerHTML = `<option value="">No hi ha participants assignats</option>`;
      document.getElementById("iaContainer").innerHTML = `
        <div class="card">
          <p>No hi ha participants disponibles per generar recomanacions.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = participants.map((usuari) => `
      <option value="${usuari.idUsuari}">
        ${obtenirNomUsuari(usuari)}
      </option>
    `).join("");

    await carregarRecomanacio(programa.idPrograma, participants[0].idUsuari);
  } catch (error) {
    document.getElementById("iaContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarRecomanacio(idPrograma, idParticipant) {
  const container = document.getElementById("iaContainer");

  if (!idParticipant) {
    container.innerHTML = `
      <div class="card">
        <p>Selecciona un participant per generar feedback IA.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="card">
      <p>Generant recomanació IA...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(
      `/ia/programes/${idPrograma}/participants/${idParticipant}/feedback`
    );

    renderFeedbackIA(container, resposta);
  } catch (error) {
    container.innerHTML = `
      <div class="card">
        <p class="error-text">${error.message}</p>
      </div>
    `;
  }
}

function renderFeedbackIA(container, resposta) {
  const dades = resposta.feedbackGenerat || resposta;

  if (dades.error) {
    container.innerHTML = `
      <div class="card">
        <h3>Servei IA no disponible</h3>
        <p class="error-text">${dades.missatge || "No s'ha pogut generar la recomanació."}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="card dashboard-wide">
      <h3>Feedback proposat</h3>
      <p>${dades.missatgeFeedback || dades.feedbackProposat || "No hi ha feedback generat."}</p>
      <p><strong>Prioritat:</strong> ${formatPrioritat(dades.nivellPrioritat || dades.to)}</p>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Punts forts</h3>
        ${renderLlista(dades.puntsForts)}
      </div>

      <div class="card">
        <h3>Aspectes de millora</h3>
        ${renderLlista(dades.puntsMillora || dades.aspectesMillora)}
      </div>

      <div class="card">
        <h3>Properes accions</h3>
        ${renderLlista(dades.properesAccions || dades.accions)}
      </div>
    </div>
  `;
}

function renderLlista(items) {
  if (!items || !items.length) {
    return `<p>No hi ha informació disponible.</p>`;
  }

  return `
    <ul>
      ${items.map((item) => `
        <li>${typeof item === "string" ? item : formatObjecte(item)}</li>
      `).join("")}
    </ul>
  `;
}

function formatPrioritat(valor) {
  const labels = {
    baix: "Baix",
    baixa: "Baixa",
    mitja: "Mitjana",
    mitjana: "Mitjana",
    alt: "Alt",
    alta: "Alta",
    constructiu: "Constructiu",
    motivador: "Motivador",
    neutral: "Neutral",
    urgent: "Urgent"
  };

  return labels[valor] || valor || "-";
}

function formatObjecte(objecte) {
  if (!objecte || typeof objecte !== "object") {
    return objecte || "-";
  }

  return Object.values(objecte)
    .filter((valor) => valor !== null && valor !== undefined && valor !== "")
    .join(" — ");
}

function obtenirNomUsuari(usuari) {
  const nomComplet = `${usuari.nom || ""} ${usuari.cognoms || ""}`.trim();

  if (nomComplet) {
    return `${nomComplet} — ${usuari.email || usuari.idUsuari}`;
  }

  return usuari.email || `Usuari ${usuari.idUsuari}`;
}