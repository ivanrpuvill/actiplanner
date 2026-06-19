import { apiGet, apiPost, apiPut } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP14GestioUsuaris(app, navegar) {
  app.innerHTML = renderLayout("Gestió usuaris i permisos", `
    <div class="page-actions">
      <button class="btn" id="btnNouUsuari">Nou usuari</button>
      <button class="btn secondary" id="btnAssignarRol">Assignar rol a programa</button>
    </div>

    <div id="formContainer" class="card hidden"></div>
    <div id="usuarisContainer" class="table-card">Carregant usuaris...</div>

    <h3 class="section-title">Assignacions a programes</h3>
    <div id="assignacionsContainer" class="table-card">Carregant assignacions...</div>
  `);

  activarLayoutEvents(navegar);

  document.getElementById("btnNouUsuari").addEventListener("click", async () => {
    await renderFormUsuari(navegar);
  });

  document.getElementById("btnAssignarRol").addEventListener("click", async () => {
    await renderFormAssignacio(navegar);
  });

  await carregarUsuaris(navegar);
  await carregarAssignacions();
}

async function carregarUsuaris(navegar) {
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
            <th>Estat</th>
            <th></th>
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
              <td>
                <span class="badge ${usuari.actiu === false ? "badge-inactiu" : "badge-actiu"}">
                  ${usuari.actiu === false ? "Inactiu" : "Actiu"}
                </span>
              </td>
              <td>
                <button class="btn secondary small btn-editar-usuari" data-id="${usuari.idUsuari}">
                  Editar
                </button>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    container.querySelectorAll(".btn-editar-usuari").forEach((button) => {
      button.addEventListener("click", async () => {
        const idUsuari = Number(button.dataset.id);
        const usuari = usuaris.find((u) => u.idUsuari === idUsuari);
        await renderFormUsuari(navegar, usuari);
      });
    });
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarAssignacions() {
  const container = document.getElementById("assignacionsContainer");

  try {
    const [usuaris, programes] = await Promise.all([
      apiGet("/usuaris"),
      apiGet("/programes")
    ]);

    const nomUsuari = (idUsuari) => {
      const usuari = usuaris.find((u) => u.idUsuari === idUsuari);
      return usuari ? `${usuari.nom || ""} ${usuari.cognoms || ""}`.trim() : `Usuari ${idUsuari}`;
    };

    const nomPrograma = (idPrograma) => {
      const programa = programes.find((p) => p.idPrograma === idPrograma);
      return programa ? (programa.nom || programa.nomPrograma || `Programa ${idPrograma}`) : `Programa ${idPrograma}`;
    };

    const totesLesAssignacions = [];

    for (const programa of programes) {
      const participants = await apiGet(`/programes/${programa.idPrograma}/participants`);
      participants.forEach((p) => totesLesAssignacions.push({ ...p, rol: "Participant" }));

      const supervisors = await apiGet(`/programes/${programa.idPrograma}/supervisors`);
      supervisors.forEach((s) => totesLesAssignacions.push({ ...s, rol: "Supervisor" }));
    }

    if (!totesLesAssignacions.length) {
      container.innerHTML = "<p>No hi ha assignacions registrades.</p>";
      return;
    }

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Usuari</th>
            <th>Programa</th>
            <th>Rol</th>
            <th>Data assignació</th>
            <th>Estat</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${totesLesAssignacions.map((assignacio) => `
            <tr>
              <td>${nomUsuari(assignacio.idUsuari)}</td>
              <td>${nomPrograma(assignacio.idPrograma)}</td>
              <td>${assignacio.rol}</td>
              <td>${assignacio.dataAssignacio || "-"}</td>
              <td>
                <span class="badge ${assignacio.actiu === false ? "badge-inactiu" : "badge-actiu"}">
                  ${assignacio.actiu === false ? "Inactiu" : "Actiu"}
                </span>
              </td>
              <td>
                <button
                  class="btn secondary small btn-toggle-assignacio"
                  data-rol="${assignacio.rol}"
                  data-id-programa="${assignacio.idPrograma}"
                  data-id-usuari="${assignacio.idUsuari}"
                  data-actiu="${assignacio.actiu !== false}"
                >
                  ${assignacio.actiu === false ? "Activar" : "Desactivar"}
                </button>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    container.querySelectorAll(".btn-toggle-assignacio").forEach((button) => {
      button.addEventListener("click", async () => {
        const rol = button.dataset.rol;
        const idPrograma = Number(button.dataset.idPrograma);
        const idUsuari = Number(button.dataset.idUsuari);
        const actiuActual = button.dataset.actiu === "true";

        const endpoint =
          rol === "Participant"
            ? `/programes/${idPrograma}/participants/${idUsuari}`
            : `/programes/${idPrograma}/supervisors/${idUsuari}`;

        await apiPut(endpoint, { actiu: !actiuActual });
        await carregarAssignacions();
      });
    });
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function renderFormUsuari(navegar, usuariExistent = null) {
  const container = document.getElementById("formContainer");
  const empreses = await apiGet("/empreses");
  const esEdicio = usuariExistent !== null;

  container.classList.remove("hidden");
  container.innerHTML = `
    <h3>${esEdicio ? "Editar usuari" : "Nou usuari"}</h3>

    <form id="usuariForm" class="form-grid">
      <div>
        <label>Empresa</label>
        <select id="idEmpresa" required>
          ${empreses.map((empresa) => `
            <option value="${empresa.idEmpresa}" ${esEdicio && usuariExistent.idEmpresa === empresa.idEmpresa ? "selected" : ""}>
              ${empresa.nom || `Empresa ${empresa.idEmpresa}`}
            </option>
          `).join("")}
        </select>
      </div>

      <div>
        <label>Nom</label>
        <input id="nom" required value="${esEdicio ? (usuariExistent.nom || "") : ""}" />
      </div>

      <div>
        <label>Cognoms</label>
        <input id="cognoms" required value="${esEdicio ? (usuariExistent.cognoms || "") : ""}" />
      </div>

      <div>
        <label>Telèfon</label>
        <input id="telefon" value="${esEdicio ? (usuariExistent.telefon || "") : ""}" />
      </div>

      <div>
        <label>Email</label>
        <input id="email" type="email" required value="${esEdicio ? (usuariExistent.email || "") : ""}" />
      </div>

      <div>
        <label>Contrasenya${esEdicio ? " (deixa-ho buit per no canviar-la)" : ""}</label>
        <input id="password" type="password" ${esEdicio ? "" : "required"} />
      </div>

      <div>
        <label>
          <input id="esAdministrador" type="checkbox" ${esEdicio && usuariExistent.esAdministrador ? "checked" : ""} />
          Administrador global
        </label>
      </div>

      ${esEdicio ? `
        <div>
          <label>Estat</label>
          <select id="actiu">
            <option value="true" ${usuariExistent.actiu !== false ? "selected" : ""}>Actiu</option>
            <option value="false" ${usuariExistent.actiu === false ? "selected" : ""}>Inactiu</option>
          </select>
        </div>
      ` : ""}

      <div class="form-actions">
        <button class="btn" type="submit">${esEdicio ? "Guardar canvis" : "Crear usuari"}</button>
        ${esEdicio ? `<button class="btn secondary" type="button" id="btnCancelarEdicioUsuari">Cancel·lar</button>` : ""}
      </div>
    </form>
  `;

  if (esEdicio) {
    document.getElementById("btnCancelarEdicioUsuari").addEventListener("click", () => {
      container.classList.add("hidden");
      container.innerHTML = "";
    });
  }

  document.getElementById("usuariForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const password = document.getElementById("password").value;

    if (esEdicio) {
      const dadesUsuari = {
        idEmpresa: Number(document.getElementById("idEmpresa").value),
        nom: document.getElementById("nom").value,
        cognoms: document.getElementById("cognoms").value,
        telefon: document.getElementById("telefon").value || null,
        email: document.getElementById("email").value,
        esAdministrador: document.getElementById("esAdministrador").checked,
        actiu: document.getElementById("actiu").value === "true"
      };

      if (password) {
        dadesUsuari.password = password;
      }

      await apiPut(`/usuaris/${usuariExistent.idUsuari}`, dadesUsuari);
    } else {
      const nouUsuari = {
        idEmpresa: Number(document.getElementById("idEmpresa").value),
        nom: document.getElementById("nom").value,
        cognoms: document.getElementById("cognoms").value,
        telefon: document.getElementById("telefon").value || null,
        email: document.getElementById("email").value,
        esAdministrador: document.getElementById("esAdministrador").checked,
        actiu: true,
        password
      };

      await apiPost("/usuaris", nouUsuari);
    }

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

    await apiPost(endpoint, {
      idUsuari,
      ...(rol === "participant" ? { estatParticipacio: "actiu" } : {})
    });

    navegar("P14");
  });
}