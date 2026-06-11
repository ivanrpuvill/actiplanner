import { apiGet, apiPost } from "../api.js";
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

  await carregarEmpreses();
}

async function carregarEmpreses() {
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
          </tr>
        </thead>
        <tbody>
          ${empreses.map((empresa) => `
            <tr>
              <td>${empresa.idEmpresa}</td>
              <td>${empresa.nom || "-"}</td>
              <td>${empresa.sector || "-"}</td>
              <td>${empresa.emailContacte || empresa.contacte || "-"}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderFormEmpresa(navegar) {
  const container = document.getElementById("formContainer");

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>Nova empresa</h3>

    <form id="empresaForm" class="form-grid">
      <div>
        <label>Nom</label>
        <input id="nom" required />
      </div>

      <div>
        <label>Sector</label>
        <input id="sector" />
      </div>

      <div>
        <label>Email de contacte</label>
        <input id="emailContacte" type="email" />
      </div>

      <div class="form-actions">
        <button class="btn" type="submit">Crear empresa</button>
      </div>
    </form>
  `;

  document.getElementById("empresaForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const novaEmpresa = {
      nom: document.getElementById("nom").value,
      sector: document.getElementById("sector").value,
      emailContacte: document.getElementById("emailContacte").value
    };

    await apiPost("/empreses", novaEmpresa);
    navegar("P13");
  });
}