import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP20GeneradorIAPlans(app, navegar) {
  app.innerHTML = renderLayout("Generador IA de plans", `
    <div class="card">
      <h3>Selecciona un programa</h3>

      <div class="form-grid">
        <div>
          <label>Programa</label>
          <select id="programaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnGenerarProposta">Generar proposta IA</button>
        </div>
      </div>
    </div>

    <div id="generadorContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorProgrames();

  document.getElementById("btnGenerarProposta").addEventListener("click", async () => {
    const idPrograma = document.getElementById("programaSelect").value;
    await generarProposta(idPrograma);
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
    await generarProposta(programes[0].idPrograma);
  }
}

async function generarProposta(idPrograma) {
  const container = document.getElementById("generadorContainer");

  container.innerHTML = `
    <div class="card">
      <p>Generant proposta de pla amb IA...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(`/ia/programes/${idPrograma}/resum`);

    container.innerHTML = `
      <div class="card">
        <h3>Proposta generada</h3>
        <p>
          Aquesta pantalla mostra una proposta basada en el resum IA del programa.
          La creació automàtica del pla, objectius, accions i KPI es pot implementar
          posteriorment amb els formularis de P16 i P17.
        </p>
      </div>

      <div class="grid constructor-container">
        <div class="card">
          <h3>Resum</h3>
          <p>${resposta.resum || resposta.text || resposta.descripcio || "-"}</p>
        </div>

        <div class="card">
          <h3>Objectius suggerits</h3>
          ${renderLlista(resposta.objectius || resposta.objectiusSuggerits || resposta.recomanacions || [])}
        </div>

        <div class="card">
          <h3>Accions suggerides</h3>
          ${renderLlista(resposta.accions || resposta.accionsRecomanades || resposta.properesAccions || [])}
        </div>

        <div class="card">
          <h3>KPI suggerits</h3>
          ${renderLlista(resposta.kpis || resposta.indicadors || [])}
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Resposta completa</h3>
        <pre class="json-block">${JSON.stringify(resposta, null, 2)}</pre>
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
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