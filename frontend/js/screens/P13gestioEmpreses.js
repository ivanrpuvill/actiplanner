import { apiGet, apiPost, apiPut } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP13GestioEmpreses(app, navegar) {
  app.innerHTML = renderLayout("Gestió empreses", `
    <div class="page-actions">
      <button class="btn" id="btnNovaEmpresa">Nova empresa</button>
    </div>

    <div id="formContainer" class="card hidden"></div>
    <div id="empresesContainer" class="table-card">Carregant empreses...</div>
  `);

  activarLayoutEvents(navegar);

  document.getElementById("btnNovaEmpresa").addEventListener("click", () => {
    renderFormEmpresa(navegar);
  });

  await carregarEmpreses(navegar);
}

async function carregarEmpreses(navegar) {
  const container = document.getElementById("empresesContainer");

  try {
    const empreses = await apiGet("/empreses");

    if (!empreses.length) {
      container.innerHTML = "<p>No hi ha empreses registrades.</p>";
      return;
    }

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nom</th>
            <th>Sector</th>
            <th>Contacte</th>
            <th>Estat</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${empreses.map((empresa) => `
            <tr>
              <td>${empresa.idEmpresa}</td>
              <td>${empresa.nom || "-"}</td>
              <td>${empresa.sector || "-"}</td>
              <td>${empresa.contacte || "-"}</td>
              <td>
                <span class="badge ${empresa.actiu === false ? "badge-inactiu" : "badge-actiu"}">
                  ${empresa.actiu === false ? "Inactiva" : "Activa"}
                </span>
              </td>
              <td>
                <button class="btn secondary small btn-editar-empresa" data-id="${empresa.idEmpresa}">
                  Editar
                </button>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    container.querySelectorAll(".btn-editar-empresa").forEach((button) => {
      button.addEventListener("click", async () => {
        const idEmpresa = Number(button.dataset.id);
        const empresa = empreses.find((e) => e.idEmpresa === idEmpresa);
        renderFormEmpresa(navegar, empresa);
      });
    });
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderFormEmpresa(navegar, empresaExistent = null) {
  const container = document.getElementById("formContainer");
  const esEdicio = empresaExistent !== null;

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>${esEdicio ? "Editar empresa" : "Nova empresa"}</h3>

    <form id="empresaForm" class="form-grid">
      <div>
        <label>Nom</label>
        <input id="nom" required value="${esEdicio ? (empresaExistent.nom || "") : ""}" />
      </div>

      <div>
        <label>Sector</label>
        <input id="sector" value="${esEdicio ? (empresaExistent.sector || "") : ""}" />
      </div>

      <div>
        <label>Email de contacte</label>
        <input id="emailContacte" type="email" value="${esEdicio ? (empresaExistent.contacte || "") : ""}" />
      </div>

      ${esEdicio ? `
        <div>
          <label>Estat</label>
          <select id="actiu">
            <option value="true" ${empresaExistent.actiu !== false ? "selected" : ""}>Activa</option>
            <option value="false" ${empresaExistent.actiu === false ? "selected" : ""}>Inactiva</option>
          </select>
        </div>
      ` : ""}

      <div class="form-actions">
        <button class="btn" type="submit">${esEdicio ? "Guardar canvis" : "Crear empresa"}</button>
        ${esEdicio ? `<button class="btn secondary" type="button" id="btnCancelarEdicio">Cancel·lar</button>` : ""}
      </div>
    </form>
  `;

  if (esEdicio) {
    document.getElementById("btnCancelarEdicio").addEventListener("click", () => {
      container.classList.add("hidden");
      container.innerHTML = "";
    });
  }

  document.getElementById("empresaForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const dadesEmpresa = {
      nom: document.getElementById("nom").value,
      sector: document.getElementById("sector").value,
      contacte: document.getElementById("emailContacte").value
    };

    if (esEdicio) {
      dadesEmpresa.actiu = document.getElementById("actiu").value === "true";
      await apiPut(`/empreses/${empresaExistent.idEmpresa}`, dadesEmpresa);
    } else {
      await apiPost("/empreses", dadesEmpresa);
    }

    navegar("P13");
  });
}