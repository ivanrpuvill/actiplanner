import { apiGet, apiPost } from "../api.js";
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

  await carregarPlans();
}

async function carregarPlans() {
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
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function renderFormPla(navegar) {
  const container = document.getElementById("formContainer");
  const programes = await apiGet("/programes");

  container.classList.remove("hidden");

  container.innerHTML = `
    <h3>Nou pla d'acció</h3>

    <form id="plaForm" class="form-grid">
      <div>
        <label>Programa</label>
        <select id="idPrograma" required>
          ${programes.map((programa) => `
            <option value="${programa.idPrograma}">
              ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
            </option>
          `).join("")}
        </select>
      </div>

      <div>
        <label>Títol</label>
        <input id="titol" required />
      </div>

      <div>
        <label>Data inici</label>
        <input id="dataInici" type="date" />
      </div>

      <div>
        <label>Data fi</label>
        <input id="dataFi" type="date" />
      </div>

      <div>
        <label>Descripció</label>
        <textarea id="descripcio"></textarea>
      </div>

      <div class="form-actions">
        <button class="btn" type="submit">Crear pla</button>
      </div>
    </form>
  `;

  document.getElementById("plaForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const nouPla = {
      idPrograma: Number(document.getElementById("idPrograma").value),
      titol: document.getElementById("titol").value,
      actiu: true
    };

    await apiPost("/plans", nouPla);
    navegar("P16");
  });
}