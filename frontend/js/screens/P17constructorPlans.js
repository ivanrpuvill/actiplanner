import { apiGet, apiPost } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP17ConstructorPlans(app, navegar) {
  app.innerHTML = renderLayout("Constructor objectius-accions-KPI", `
    <div class="card">
      <h3>Selecciona un pla</h3>

      <div class="form-grid">
        <div>
          <label>Pla d'acció</label>
          <select id="plaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarPla">Carregar pla</button>
        </div>
      </div>
    </div>

    <div id="constructorContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorPlans();

  document.getElementById("btnCarregarPla").addEventListener("click", async () => {
    const idPla = document.getElementById("plaSelect").value;
    await carregarConstructor(idPla, navegar);
  });
}

async function carregarSelectorPlans() {
  const select = document.getElementById("plaSelect");
  const programes = await apiGet("/programes");

  const plans = [];

  for (const programa of programes) {
    const plansPrograma = await apiGet(`/programes/${programa.idPrograma}/plans`);

    plansPrograma.forEach((pla) => {
      plans.push({
        ...pla,
        nomPrograma: programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`
      });
    });
  }

  if (!plans.length) {
    select.innerHTML = `<option>No hi ha plans disponibles</option>`;
    return;
  }

  select.innerHTML = plans.map((pla) => `
    <option value="${pla.idPla}">
      ${pla.titol || pla.nom || `Pla ${pla.idPla}`} — ${pla.nomPrograma}
    </option>
  `).join("");
}

async function carregarConstructor(idPla, navegar) {
  const container = document.getElementById("constructorContainer");

  try {
    const pla = await apiGet(`/plans/${idPla}`);

    container.innerHTML = `
      <div class="grid two-cols">
        <div class="card">
          <h3>Nou objectiu</h3>

          <form id="objectiuForm" class="form">
            <label>Títol</label>
            <input id="objectiuTitol" required />

            <label>Descripció</label>
            <textarea id="objectiuDescripcio"></textarea>

            <button class="btn" type="submit">Crear objectiu</button>
          </form>
        </div>

        <div class="card">
          <h3>Nova acció</h3>

          <form id="accioForm" class="form">
            <label>Objectiu</label>
            <select id="accioObjectiu">
              ${(pla.objectius || []).map((objectiu) => `
                <option value="${objectiu.idObjectiu}">
                  ${objectiu.titol || objectiu.nom || `Objectiu ${objectiu.idObjectiu}`}
                </option>
              `).join("")}
            </select>

            <label>Descripció</label>
            <textarea id="accioDescripcio" required></textarea>

            <label>Data límit</label>
            <input id="accioDataLimit" type="date" />

            <button class="btn" type="submit">Crear acció</button>
          </form>
        </div>

        <div class="card">
          <h3>Nou KPI</h3>

          <form id="kpiForm" class="form">
            <label>Objectiu</label>
            <select id="kpiObjectiu">
              ${(pla.objectius || []).map((objectiu) => `
                <option value="${objectiu.idObjectiu}">
                  ${objectiu.titol || objectiu.nom || `Objectiu ${objectiu.idObjectiu}`}
                </option>
              `).join("")}
            </select>

            <label>Nom KPI</label>
            <input id="kpiNom" required />

            <label>Valor objectiu</label>
            <input id="kpiValorObjectiu" type="number" step="0.01" />

            <label>Unitat</label>
            <input id="kpiUnitat" />

            <button class="btn" type="submit">Crear KPI</button>
          </form>
        </div>

        <div class="card">
          <h3>Objectius actuals</h3>
          ${renderObjectius(pla.objectius || [])}
        </div>
      </div>
    `;

    activarForms(idPla, navegar);

  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderObjectius(objectius) {
  if (!objectius.length) {
    return `<p>Encara no hi ha objectius en aquest pla.</p>`;
  }

  return `
    <div class="list">
      ${objectius.map((objectiu) => `
        <div class="list-item">
          <strong>${objectiu.titol || objectiu.nom || `Objectiu ${objectiu.idObjectiu}`}</strong>
          <p>${objectiu.descripcio || ""}</p>
        </div>
      `).join("")}
    </div>
  `;
}

function activarForms(idPla, navegar) {
  document.getElementById("objectiuForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const nouObjectiu = {
      idPla: Number(idPla),
      titol: document.getElementById("objectiuTitol").value,
      descripcio: document.getElementById("objectiuDescripcio").value
    };

    await apiPost("/objectius", nouObjectiu);
    navegar("P17");
  });

  document.getElementById("accioForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const novaAccio = {
      idObjectiu: Number(document.getElementById("accioObjectiu").value),
      descripcio: document.getElementById("accioDescripcio").value,
      dataLimit: document.getElementById("accioDataLimit").value
    };

    await apiPost("/accions", novaAccio);
    navegar("P17");
  });

  document.getElementById("kpiForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const nouKPI = {
      idObjectiu: Number(document.getElementById("kpiObjectiu").value),
      nom: document.getElementById("kpiNom").value,
      valorObjectiu: Number(document.getElementById("kpiValorObjectiu").value),
      unitat: document.getElementById("kpiUnitat").value
    };

    await apiPost("/kpis", nouKPI);
    navegar("P17");
  });
}