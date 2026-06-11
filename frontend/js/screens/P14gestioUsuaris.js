import { apiGet, apiPost } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP14GestioUsuaris(app, navegar) {
  app.innerHTML = renderLayout("Gestió usuaris i permisos", `
    <div class="page-actions">
      <button class="btn" id="btnNouUsuari">Nou usuari</button>
      <button class="btn secondary" id="btnAssignarRol">Assignar rol a programa</button>
    </div>

    <div id="formContainer" class="card hidden"></div>
    <div id="usuarisContainer" class="table-card">Carregant usuaris...</div>
  `);

  activarLayoutEvents(navegar);

  document.getElementById("btnNouUsuari").addEventListener("click", () => {
    renderFormUsuari(navegar);
  });

  document.getElementById("btnAssignarRol").addEventListener("click", async () => {
    await renderFormAssignacio(navegar);
  });

  await carregarUsuaris();
}

async function carregarUsuaris() {
  const container = document.getElementById("usuarisContainer");

  try {
    const usuaris = await apiGet("/usuaris");

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nom</th>
            <th>Cognoms</th>
            <th>Email</th>
            <th>Administrador</th>
          </tr>
        </thead>
        <tbody>
          ${usuaris.map((usuari) => `
            <tr>
              <td>${usuari.idUsuari}</td>
              <td>${usuari.nom || "-"}</td>
              <td>${usuari.cognoms || "-"}</td>
              <td>${usuari.email || "-"}</td>
              <td>${usuari.esAdministrador ? "Sí" : "No"}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderFormUsuari(navegar) {
  const container = document.getElementById("formContainer");

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>Nou usuari</h3>

    <form id="usuariForm" class="form-grid">
      <div>
        <label>Nom</label>
        <input id="nom" required />
      </div>

      <div>
        <label>Cognoms</label>
        <input id="cognoms" />
      </div>

      <div>
        <label>Email</label>
        <input id="email" type="email" required />
      </div>

      <div>
        <label>
          <input id="esAdministrador" type="checkbox" />
          Administrador global
        </label>
      </div>

      <div class="form-actions">
        <button class="btn" type="submit">Crear usuari</button>
      </div>
    </form>
  `;

  document.getElementById("usuariForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const nouUsuari = {
      nom: document.getElementById("nom").value,
      cognoms: document.getElementById("cognoms").value,
      email: document.getElementById("email").value,
      esAdministrador: document.getElementById("esAdministrador").checked
    };

    await apiPost("/usuaris", nouUsuari);
    navegar("P14");
  });
}

async function renderFormAssignacio(navegar) {
  const container = document.getElementById("formContainer");

  const usuaris = await apiGet("/usuaris");
  const programes = await apiGet("/programes");

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>Assignar rol a programa</h3>

    <form id="assignacioForm" class="form-grid">
      <div>
        <label>Usuari</label>
        <select id="idUsuari" required>
          ${usuaris.map((usuari) => `
            <option value="${usuari.idUsuari}">
              ${usuari.nom || ""} ${usuari.cognoms || ""} — ${usuari.email || usuari.idUsuari}
            </option>
          `).join("")}
        </select>
      </div>

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
        <label>Rol</label>
        <select id="rol" required>
          <option value="participant">Participant</option>
          <option value="supervisor">Supervisor</option>
        </select>
      </div>

      <div class="form-actions">
        <button class="btn" type="submit">Assignar</button>
      </div>
    </form>
  `;

  document.getElementById("assignacioForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const idUsuari = Number(document.getElementById("idUsuari").value);
    const idPrograma = Number(document.getElementById("idPrograma").value);
    const rol = document.getElementById("rol").value;

    const endpoint =
      rol === "participant"
        ? `/programes/${idPrograma}/participants`
        : `/programes/${idPrograma}/supervisors`;

    await apiPost(endpoint, { idUsuari });

    navegar("P14");
  });
}