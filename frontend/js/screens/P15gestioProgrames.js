import { apiGet, apiPost } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP15GestioProgrames(app, navegar) {
  app.innerHTML = renderLayout("Gestió programes", `
    <div class="page-actions">
      <button class="btn" id="btnNouPrograma">Nou programa</button>
    </div>

    <div id="formContainer" class="card hidden"></div>
    <div id="programesContainer" class="table-card">Carregant programes...</div>
  `);

  activarLayoutEvents(navegar);

  document.getElementById("btnNouPrograma").addEventListener("click", async () => {
    await renderFormPrograma(navegar);
  });

  await carregarProgrames();
}

async function carregarProgrames() {
  const container = document.getElementById("programesContainer");

  try {
    const programes = await apiGet("/programes");

    if (!programes.length) {
      container.innerHTML = "<p>No hi ha programes registrats.</p>";
      return;
    }

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nom</th>
            <th>Empresa</th>
            <th>Data inici</th>
            <th>Data fi</th>
          </tr>
        </thead>
        <tbody>
          ${programes.map((programa) => `
            <tr>
              <td>${programa.idPrograma}</td>
              <td>${programa.nom || programa.nomPrograma || "-"}</td>
              <td>${programa.idEmpresa || "-"}</td>
              <td>${programa.dataInici || "-"}</td>
              <td>${programa.dataFi || "-"}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function renderFormPrograma(navegar) {
  const container = document.getElementById("formContainer");
  const empreses = await apiGet("/empreses");

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>Nou programa</h3>

    <form id="programaForm" class="form-grid">
      <div>
        <label>Nom</label>
        <input id="nom" required />
      </div>

      <div>
        <label>Empresa</label>
        <select id="idEmpresa" required>
          ${empreses.map((empresa) => `
            <option value="${empresa.idEmpresa}">
              ${empresa.nom || `Empresa ${empresa.idEmpresa}`}
            </option>
          `).join("")}
        </select>
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
        <button class="btn" type="submit">Crear programa</button>
      </div>
    </form>
  `;

  document.getElementById("programaForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const nouPrograma = {
      nom: document.getElementById("nom").value,
      idEmpresa: Number(document.getElementById("idEmpresa").value),
      dataInici: document.getElementById("dataInici").value,
      dataFi: document.getElementById("dataFi").value,
      descripcio: document.getElementById("descripcio").value
    };

    await apiPost("/programes", nouPrograma);
    navegar("P15");
  });
}