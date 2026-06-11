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
        nomPrograma: programa.nom || `Programa ${programa.idPrograma}`
      });
    });
  }

  if (!plans.length) {
    select.innerHTML = `<option>No hi ha plans disponibles</option>`;
    return;
  }

  select.innerHTML = plans.map((pla) => `
    <option value="${pla.idPla}">
      ${pla.titol || `Pla ${pla.idPla}`} — ${pla.nomPrograma}
    </option>
  `).join("");
}

async function carregarConstructor(idPla, navegar) {
  const container = document.getElementById("constructorContainer");

  try {
    const pla = await apiGet(`/plans/${idPla}`);
    const objectius = pla.objectius || [];
    const accions = obtenirAccions(objectius);

    container.innerHTML = `
      <div class="grid two-cols">
        <div class="card">
          <h3>Nou objectiu</h3>

          <form id="objectiuForm" class="form">
            <label>Descripció</label>
            <textarea id="objectiuDescripcio" required></textarea>

            <label>Valor objectiu</label>
            <input id="objectiuValor" type="number" step="0.01" required />

            <button class="btn" type="submit">Crear objectiu</button>
          </form>
        </div>

        <div class="card">
          <h3>Nova acció</h3>

          <form id="accioForm" class="form">
            <label>Objectiu</label>
            <select id="accioObjectiu" required>
              ${objectius.map((objectiu) => `
                <option value="${objectiu.idObjectiu}">
                  ${objectiu.descripcio || `Objectiu ${objectiu.idObjectiu}`}
                </option>
              `).join("")}
            </select>

            <label>Títol</label>
            <input id="accioTitol" required />

            <label>Descripció</label>
            <textarea id="accioDescripcio" required></textarea>

            <label>Data límit</label>
            <input id="accioDataLimit" type="date" required />

            <button class="btn" type="submit">Crear acció</button>
          </form>
        </div>

        <div class="card">
          <h3>Nou KPI</h3>

          <form id="kpiForm" class="form">
            <label>Acció</label>
            <select id="kpiAccio" required>
              ${accions.map((accio) => `
                <option value="${accio.idAccio}">
                  ${accio.titol || accio.descripcio || `Acció ${accio.idAccio}`}
                </option>
              `).join("")}
            </select>

            <label>Nom KPI</label>
            <input id="kpiNom" required />

            <label>Descripció</label>
            <input id="kpiDescripcio" required />

            <label>Periodicitat</label>
            <select id="kpiPeriodicitat" required>
              <option value="diari">Diari</option>
              <option value="setmanal">Setmanal</option>
              <option value="mensual">Mensual</option>
            </select>

            <button class="btn" type="submit">Crear KPI</button>
          </form>
        </div>

        <div class="card">
          <h3>Objectius actuals</h3>
          ${renderObjectius(objectius)}
        </div>
      </div>
    `;

    activarForms(idPla, navegar);

  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function obtenirAccions(objectius) {
  const accions = [];

  objectius.forEach((objectiu) => {
    (objectiu.accions || []).forEach((accio) => {
      accions.push(accio);
    });
  });

  return accions;
}

function renderObjectius(objectius) {
  if (!objectius.length) {
    return `<p>Encara no hi ha objectius en aquest pla.</p>`;
  }

  return `
    <div class="list">
      ${objectius.map((objectiu) => `
        <div class="list-item">
          <strong>${objectiu.descripcio || `Objectiu ${objectiu.idObjectiu}`}</strong>
          <p>Valor objectiu: ${objectiu.valor}</p>

          ${(objectiu.accions || []).length ? `
            <ul>
              ${objectiu.accions.map((accio) => `
                <li>${accio.titol || accio.descripcio || `Acció ${accio.idAccio}`}</li>
              `).join("")}
            </ul>
          ` : `<p>No hi ha accions associades.</p>`}
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
      descripcio: document.getElementById("objectiuDescripcio").value,
      valor: Number(document.getElementById("objectiuValor").value)
    };

    await apiPost("/objectius", nouObjectiu);
    navegar("P17");
  });

  document.getElementById("accioForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const novaAccio = {
      idObjectiu: Number(document.getElementById("accioObjectiu").value),
      titol: document.getElementById("accioTitol").value,
      descripcio: document.getElementById("accioDescripcio").value,
      dataInici: new Date().toISOString().slice(0, 10),
      dataFi: document.getElementById("accioDataLimit").value
    };

    await apiPost("/accions", novaAccio);
    navegar("P17");
  });

  document.getElementById("kpiForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const nouKPI = {
      idAccio: Number(document.getElementById("kpiAccio").value),
      nom: document.getElementById("kpiNom").value,
      descripcio: document.getElementById("kpiDescripcio").value,
      periodicitat: document.getElementById("kpiPeriodicitat").value
    };

    await apiPost("/kpis", nouKPI);
    navegar("P17");
  });
}