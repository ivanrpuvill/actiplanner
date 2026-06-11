import { apiGet } from "../api.js";
import {
  guardarUsuariActiu,
  guardarRolActiu,
  guardarProgramaActiu
} from "../state.js";

export async function renderP01Login(app, navegar) {
  app.innerHTML = `
    <div class="login-page">
      <div class="login-card">
        <h1>Actiplanner</h1>
        <p>Selecciona un usuari per iniciar sessió.</p>

        <div id="loginStatus" class="status">Carregant usuaris...</div>

        <form id="loginForm" class="form hidden">
          <label for="usuariSelect">Usuari</label>
          <select id="usuariSelect" required></select>

          <button type="submit" class="btn">Entrar</button>
        </form>
      </div>
    </div>
  `;

  const status = document.getElementById("loginStatus");
  const form = document.getElementById("loginForm");
  const select = document.getElementById("usuariSelect");

  try {
    const usuaris = await apiGet("/usuaris");

    select.innerHTML = usuaris.map((usuari) => `
      <option value="${usuari.idUsuari}">
        ${usuari.nom || usuari.email || usuari.idUsuari}
      </option>
    `).join("");

    status.classList.add("hidden");
    form.classList.remove("hidden");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const idUsuari = select.value;
      const usuariSeleccionat = usuaris.find(
        (u) => String(u.idUsuari) === String(idUsuari)
      );

      guardarUsuariActiu(usuariSeleccionat);

      const rols = await apiGet(`/usuaris/${usuariSeleccionat.idUsuari}/rols`);

      if (rols.esAdministrador === true) {
        guardarRolActiu("administrador");
        guardarProgramaActiu(null);
        navegar("P12");
        return;
      }

      navegar("P02");
    });
  } catch (error) {
    status.textContent = error.message;
    status.classList.add("error");
  }
}