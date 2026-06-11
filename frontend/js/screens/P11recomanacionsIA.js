import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP11RecomanacionsIA(app, navegar) {
  const programa = obtenirProgramaActiu();

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
      select.innerHTML = `<option>No hi ha participants assignats</option>`;
      document.getElementById("iaContainer").innerHTML = `
        <div class="card">
          <p>No hi ha participants disponibles per generar recomanacions.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = participants.map((usuari) => `
      <option value="${usuari.idUsuari}">
        ${usuari.nom || ""} ${usuari.cognoms || ""} — ${usuari.email || usuari.idUsuari}
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

  container.innerHTML = `
    <div class="card">
      <p>Generant recomanació IA...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(
      `/ia/programes/${idPrograma}/participants/${idParticipant}/feedback`
    );

    container.innerHTML = `
      <div class="grid">
        <div class="card">
          <h3>Resum IA</h3>
          <p>${resposta.resum || resposta.feedback || resposta.text || "-"}</p>
        </div>

        <div class="card">
          <h3>Recomanacions</h3>
          ${renderLlista(resposta.recomanacions || resposta.accionsRecomanades || [])}
        </div>

        <div class="card">
          <h3>Riscos detectats</h3>
          ${renderLlista(resposta.riscos || resposta.alertes || [])}
        </div>

        <div class="card">
          <h3>Properes accions</h3>
          ${renderLlista(resposta.properesAccions || resposta.accions || [])}
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Resposta completa</h3>
        <pre class="json-block">${JSON.stringify(resposta, null, 2)}</pre>
      </div>
    `;
  } catch (error) {
    container.innerHTML = `
      <div class="card">
        <p class="error-text">${error.message}</p>
      </div>
    `;
  }
}

function renderLlista(items) {
  if (!items || !items.length) {
    return `<p>No hi ha informació disponible.</p>`;
  }

  return `
    <ul>
      ${items.map((item) => `
        <li>${typeof item === "string" ? item : JSON.stringify(item)}</li>
      `).join("")}
    </ul>
  `;
}