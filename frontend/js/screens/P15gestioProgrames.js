import { apiGet, apiPost, apiPut } from "../api.js";
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

  await carregarProgrames(navegar);
}

async function carregarProgrames(navegar) {
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
            <th>Estat</th>
            <th></th>
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
              <td>
                <span class="badge ${programa.actiu === false ? "badge-inactiu" : "badge-actiu"}">
                  ${programa.actiu === false ? "Inactiu" : "Actiu"}
                </span>
              </td>
              <td>
                <button class="btn secondary small btn-editar-programa" data-id="${programa.idPrograma}">
                  Editar
                </button>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    container.querySelectorAll(".btn-editar-programa").forEach((button) => {
      button.addEventListener("click", async () => {
        const idPrograma = Number(button.dataset.id);
        const programa = programes.find((p) => p.idPrograma === idPrograma);
        await renderFormPrograma(navegar, programa);
      });
    });
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function renderFormPrograma(navegar, programaExistent = null) {
  const container = document.getElementById("formContainer");
  const empreses = await apiGet("/empreses");
  const esEdicio = programaExistent !== null;

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>${esEdicio ? "Editar programa" : "Nou programa"}</h3>

    <form id="programaForm" class="form-grid">
      <div>
        <label>Nom</label>
        <input id="nom" required value="${esEdicio ? (programaExistent.nom || "") : ""}" />
      </div>

      <div>
        <label>Empresa</label>
        <select id="idEmpresa" required>
          ${empreses.map((empresa) => `
            <option value="${empresa.idEmpresa}" ${esEdicio && programaExistent.idEmpresa === empresa.idEmpresa ? "selected" : ""}>
              ${empresa.nom || `Empresa ${empresa.idEmpresa}`}
            </option>
          `).join("")}
        </select>
      </div>

      <div>
        <label>Data inici</label>
        <input id="dataInici" type="date" value="${esEdicio ? (programaExistent.dataInici || "") : ""}" />
      </div>

      <div>
        <label>Data fi</label>
        <input id="dataFi" type="date" value="${esEdicio ? (programaExistent.dataFi || "") : ""}" />
      </div>

      <div>
        <label>Descripció</label>
        <textarea id="descripcio">${esEdicio ? (programaExistent.descripcio || "") : ""}</textarea>
      </div>

      ${esEdicio ? `
        <div>
          <label>Estat</label>
          <select id="actiu">
            <option value="true" ${programaExistent.actiu !== false ? "selected" : ""}>Actiu</option>
            <option value="false" ${programaExistent.actiu === false ? "selected" : ""}>Inactiu</option>
          </select>
        </div>
      ` : ""}

      <div class="form-actions">
        <button class="btn" type="submit">${esEdicio ? "Guardar canvis" : "Crear programa"}</button>
        ${esEdicio ? `<button class="btn secondary" type="button" id="btnCancelarEdicioPrograma">Cancel·lar</button>` : ""}
      </div>
    </form>
  `;

  if (esEdicio) {
    document.getElementById("btnCancelarEdicioPrograma").addEventListener("click", () => {
      container.classList.add("hidden");
      container.innerHTML = "";
    });
  }

  document.getElementById("programaForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const dadesPrograma = {
      nom: document.getElementById("nom").value,
      idEmpresa: Number(document.getElementById("idEmpresa").value),
      dataInici: document.getElementById("dataInici").value,
      dataFi: document.getElementById("dataFi").value,
      descripcio: document.getElementById("descripcio").value
    };

    if (esEdicio) {
      dadesPrograma.actiu = document.getElementById("actiu").value === "true";
      await apiPut(`/programes/${programaExistent.idPrograma}`, dadesPrograma);
    } else {
      dadesPrograma.actiu = true;
      await apiPost("/programes", dadesPrograma);
    }

    navegar("P15");
  });
}