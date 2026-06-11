import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirRolActiu } from "../state.js";

export async function renderP21IAInsights(app, navegar) {
  const rol = obtenirRolActiu();
  const programaActiu = obtenirProgramaActiu();

  app.innerHTML = renderLayout("IA Insights i resums executius", `
    <div class="card">
      <h3>Selecciona l'origen</h3>

      <div class="form-grid">
        <div>
          <label>Programa</label>
          <select id="programaSelect"></select>
        </div>

        <div>
          <label>Pla</label>
          <select id="plaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnResumPrograma">Resum programa</button>
        </div>

        <div class="form-actions">
          <button class="btn secondary" id="btnResumPla">Resum pla</button>
        </div>
      </div>
    </div>

    <div id="iaInsightsContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectors(rol, programaActiu);

  document.getElementById("programaSelect").addEventListener("change", async () => {
    await carregarPlans(document.getElementById("programaSelect").value);
  });

  document.getElementById("btnResumPrograma").addEventListener("click", async () => {
    await carregarResumPrograma(document.getElementById("programaSelect").value);
  });

  document.getElementById("btnResumPla").addEventListener("click", async () => {
    await carregarResumPla(document.getElementById("plaSelect").value);
  });
}

async function carregarSelectors(rol, programaActiu) {
  const programaSelect = document.getElementById("programaSelect");

  let programes = await apiGet("/programes");

  if (rol !== "administrador" && programaActiu) {
    programes = programes.filter(
      (programa) => String(programa.idPrograma) === String(programaActiu.idPrograma)
    );
  }

  programaSelect.innerHTML = programes.map((programa) => `
    <option value="${programa.idPrograma}">
      ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
    </option>
  `).join("");

  if (programes.length) {
    await carregarPlans(programes[0].idPrograma);
    await carregarResumPrograma(programes[0].idPrograma);
  }
}

async function carregarPlans(idPrograma) {
  const plaSelect = document.getElementById("plaSelect");

  try {
    const plans = await apiGet(`/programes/${idPrograma}/plans`);

    if (!plans.length) {
      plaSelect.innerHTML = `<option value="">No hi ha plans</option>`;
      return;
    }

    plaSelect.innerHTML = plans.map((pla) => `
      <option value="${pla.idPla}">
        ${pla.titol || pla.nom || `Pla ${pla.idPla}`}
      </option>
    `).join("");
  } catch {
    plaSelect.innerHTML = `<option value="">Error carregant plans</option>`;
  }
}

async function carregarResumPrograma(idPrograma) {
  const container = document.getElementById("iaInsightsContainer");

  container.innerHTML = `
    <div class="card">
      <p>Generant resum del programa...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(`/ia/programes/${idPrograma}/resum`);
    renderRespostaIA(container, "Resum del programa", resposta);
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarResumPla(idPla) {
  const container = document.getElementById("iaInsightsContainer");

  if (!idPla) {
    container.innerHTML = `<p>No hi ha cap pla seleccionat.</p>`;
    return;
  }

  container.innerHTML = `
    <div class="card">
      <p>Generant resum del pla...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(`/ia/plans/${idPla}/resum`);
    renderRespostaIA(container, "Resum del pla", resposta);
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderRespostaIA(container, titol, resposta) {
  container.innerHTML = `
    <div class="grid">
      <div class="card">
        <h3>${titol}</h3>
        <p>${resposta.resum || resposta.text || resposta.descripcio || "-"}</p>
      </div>

      <div class="card">
        <h3>Recomanacions</h3>
        ${renderLlista(resposta.recomanacions || resposta.accionsRecomanades || [])}
      </div>

      <div class="card">
        <h3>Riscos</h3>
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
}

function renderLlista(items) {
  if (!items || !items.length) return `<p>No hi ha informació disponible.</p>`;

  return `
    <ul>
      ${items.map((item) => `
        <li>${typeof item === "string" ? item : JSON.stringify(item)}</li>
      `).join("")}
    </ul>
  `;
}