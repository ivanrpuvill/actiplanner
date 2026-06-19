import { apiGet, apiPost, apiPut } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP16BibliotecaPlans(app, navegar) {
  const filtrePrograma = sessionStorage.getItem("filtreProgramaPlans");
  app.innerHTML = renderLayout(
    filtrePrograma ? "Plans del programa" : "Biblioteca plans", `
    <div class="page-actions">
      <button class="btn" id="btnNouPla">Nou pla</button>
    </div>

    <div id="formContainer" class="card hidden"></div>
    <div id="plansContainer" class="table-card">Carregant plans...</div>
  `);

  activarLayoutEvents(navegar);

  document.getElementById("btnNouPla").addEventListener("click", async () => {
    await renderFormPla(navegar);
  });

  await carregarPlans(navegar);
}

async function carregarPlans(navegar) {
  const container = document.getElementById("plansContainer");
  const filtrePrograma = sessionStorage.getItem("filtreProgramaPlans");

  try {
    const totsElsProgrames = await apiGet("/programes");

    const programes = filtrePrograma
      ? totsElsProgrames.filter(
          (programa) =>
            String(programa.idPrograma) === String(filtrePrograma)
        )
      : totsElsProgrames;
    const totsElsPlans = [];

    for (const programa of programes) {
      const plans = await apiGet(`/programes/${programa.idPrograma}/plans`);
      plans.forEach((pla) => {
        totsElsPlans.push({
          ...pla,
          nomPrograma: programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`
        });
      });
    }

    if (!totsElsPlans.length) {
      container.innerHTML = "<p>No hi ha plans registrats.</p>";
      return;
    }

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Títol</th>
            <th>Programa</th>
            <th>Data inici</th>
            <th>Data fi</th>
            <th>Estat</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${totsElsPlans.map((pla) => `
            <tr>
              <td>${pla.idPla}</td>
              <td>${pla.titol || pla.nom || "-"}</td>
              <td>${pla.nomPrograma}</td>
              <td>${pla.dataInici || "-"}</td>
              <td>${pla.dataFi || "-"}</td>
              <td>
                <span class="badge ${pla.actiu === false ? "badge-inactiu" : "badge-actiu"}">
                  ${pla.actiu === false ? "Inactiu" : "Actiu"}
                </span>
              </td>
              <td>
                <button class="btn secondary small btn-editar-pla" data-id="${pla.idPla}">
                  Editar
                </button>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    container.querySelectorAll(".btn-editar-pla").forEach((button) => {
      button.addEventListener("click", async () => {
        const idPla = Number(button.dataset.id);
        const pla = totsElsPlans.find((p) => p.idPla === idPla);
        await renderFormPla(navegar, pla);
      });
    });
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function renderFormPla(navegar, plaExistent = null) {
  const container = document.getElementById("formContainer");
  const programes = await apiGet("/programes");
  const esEdicio = plaExistent !== null;

  container.classList.remove("hidden");

  container.innerHTML = `
    <h3>${esEdicio ? "Editar pla d'acció" : "Nou pla d'acció"}</h3>

    <form id="plaForm" class="form-grid">
      <div>
        <label>Programa</label>
        <select id="idPrograma" required>
          ${programes.map((programa) => `
            <option value="${programa.idPrograma}" ${esEdicio && plaExistent.idPrograma === programa.idPrograma ? "selected" : ""}>
              ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
            </option>
          `).join("")}
        </select>
      </div>

      <div>
        <label>Títol</label>
        <input id="titol" required value="${esEdicio ? (plaExistent.titol || "") : ""}" />
      </div>

      <div>
        <label>Data inici</label>
        <input id="dataInici" type="date" value="${esEdicio ? (plaExistent.dataInici || "") : ""}" />
      </div>

      <div>
        <label>Data fi</label>
        <input id="dataFi" type="date" value="${esEdicio ? (plaExistent.dataFi || "") : ""}" />
      </div>

      <div>
        <label>Descripció</label>
        <textarea id="descripcio">${esEdicio ? (plaExistent.descripcio || "") : ""}</textarea>
      </div>

      ${esEdicio ? `
        <div>
          <label>Estat</label>
          <select id="actiu">
            <option value="true" ${plaExistent.actiu !== false ? "selected" : ""}>Actiu</option>
            <option value="false" ${plaExistent.actiu === false ? "selected" : ""}>Inactiu</option>
          </select>
        </div>
      ` : ""}

      <div class="form-actions">
        <button class="btn" type="submit">${esEdicio ? "Guardar canvis" : "Crear pla"}</button>
        ${esEdicio ? `<button class="btn secondary" type="button" id="btnCancelarEdicioPla">Cancel·lar</button>` : ""}
      </div>
    </form>
  `;

  if (esEdicio) {
    document.getElementById("btnCancelarEdicioPla").addEventListener("click", () => {
      container.classList.add("hidden");
      container.innerHTML = "";
    });
  }

  document.getElementById("plaForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    if (esEdicio) {
      const dadesPla = {
        idPrograma: Number(document.getElementById("idPrograma").value),
        titol: document.getElementById("titol").value,
        actiu: document.getElementById("actiu").value === "true"
      };

      await apiPut(`/plans/${plaExistent.idPla}`, dadesPla);
    } else {
      const nouPla = {
        idPrograma: Number(document.getElementById("idPrograma").value),
        titol: document.getElementById("titol").value,
        actiu: true
      };

      await apiPost("/plans", nouPla);
    }

    navegar("P16");
  });
}