import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP18AnaliticaReporting(app, navegar) {
  app.innerHTML = renderLayout("Analítica i reporting", `
    <div class="card">
      <h3>Selecciona un programa</h3>

      <div class="form-grid">
        <div>
          <label>Programa</label>
          <select id="programaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarAnalitica">Carregar analítica</button>
        </div>
      </div>
    </div>

    <div id="analiticaContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorProgrames();

  document.getElementById("btnCarregarAnalitica").addEventListener("click", async () => {
    const idPrograma = document.getElementById("programaSelect").value;
    await carregarAnalitica(idPrograma);
  });
}

async function carregarSelectorProgrames() {
  const select = document.getElementById("programaSelect");
  const programes = await apiGet("/programes");

  select.innerHTML = programes.map((programa) => `
    <option value="${programa.idPrograma}">
      ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
    </option>
  `).join("");

  if (programes.length) {
    await carregarAnalitica(programes[0].idPrograma);
  }
}

async function carregarAnalitica(idPrograma) {
  const container = document.getElementById("analiticaContainer");

  container.innerHTML = `
    <div class="card">
      <p>Carregant analítica...</p>
    </div>
  `;

  try {
    const analisi = await apiGet(`/programes/${idPrograma}/analisi`);
    const objectiusRisc = await apiGet(`/programes/${idPrograma}/objectius-risc`);
    const destacats = await apiGet(`/programes/${idPrograma}/participants-destacats`);
    const desviacio = await apiGet(`/programes/${idPrograma}/participants-desviacio`);

    container.innerHTML = `
      <div class="grid">
        <div class="card">
          <h3>Resum general</h3>
          <p>${analisi.resum || analisi.descripcio || "Anàlisi carregada correctament."}</p>
        </div>

        <div class="card">
          <h3>Objectius en risc</h3>
          <p>${objectiusRisc.length || 0} objectius detectats</p>
        </div>

        <div class="card">
          <h3>Participants destacats</h3>
          <p>${destacats.length || 0} participants</p>
        </div>

        <div class="card">
          <h3>Participants amb desviació</h3>
          <p>${desviacio.length || 0} participants</p>
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Objectius en risc</h3>
        ${renderTaulaObjectius(objectiusRisc)}
      </div>

      <div class="grid two-cols constructor-container">
        <div class="card">
          <h3>Participants destacats</h3>
          ${renderTaulaParticipants(destacats)}
        </div>

        <div class="card">
          <h3>Participants amb desviació</h3>
          ${renderTaulaParticipants(desviacio)}
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Resposta completa d'analítica</h3>
        <pre class="json-block">${JSON.stringify(analisi, null, 2)}</pre>
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderTaulaObjectius(items) {
  if (!items || !items.length) return "<p>No hi ha objectius en risc.</p>";

  return `
    <table>
      <thead>
        <tr>
          <th>Objectiu</th>
          <th>Progrés</th>
          <th>Estat</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item) => `
          <tr>
            <td>${item.descripcio || item.titol || item.idObjectiu || "-"}</td>
            <td>${item.progres ?? item.progresObjectiu ?? "-"}%</td>
            <td>${item.estat || item.estatObjectiu || "-"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderTaulaParticipants(items) {
  if (!items || !items.length) return "<p>No hi ha dades disponibles.</p>";

  return `
    <table>
      <thead>
        <tr>
          <th>Participant</th>
          <th>Valor</th>
          <th>Estat</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item) => `
          <tr>
            <td>${nomParticipant(item)}</td>
            <td>${item.progres ?? item.progresPla ?? item.valor ?? item.desviacio ?? "-"}</td>
            <td>${item.estat || item.estatPla || item.estatObjectiu || "-"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function nomParticipant(item) {
  if (item.nom || item.cognoms) {
    return `${item.nom || ""} ${item.cognoms || ""}`.trim();
  }

  if (item.usuari) {
    return `${item.usuari.nom || ""} ${item.usuari.cognoms || ""}`.trim();
  }

  return `Usuari ${item.idUsuari || item.idParticipant || "-"}`;
}