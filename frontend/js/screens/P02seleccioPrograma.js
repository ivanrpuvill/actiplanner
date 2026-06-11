import { apiGet } from "../api.js";
import {
  obtenirUsuariActiu,
  guardarProgramaActiu,
  guardarRolActiu
} from "../state.js";

export async function renderP02SeleccioPrograma(app, navegar) {
  const usuari = obtenirUsuariActiu();

  if (!usuari) {
    navegar("P01");
    return;
  }

  app.innerHTML = `
    <div class="login-page">
      <div class="login-card wide">
        <h1>Selecció de programa</h1>
        <p>Tria el programa i el rol amb què vols treballar.</p>

        <div id="seleccioStatus" class="status">Carregant rols...</div>

        <form id="seleccioForm" class="form hidden">
          <label for="rolProgramaSelect">Programa i rol</label>
          <select id="rolProgramaSelect" required></select>

          <button type="submit" class="btn">Continuar</button>
        </form>
      </div>
    </div>
  `;

  const status = document.getElementById("seleccioStatus");
  const form = document.getElementById("seleccioForm");
  const select = document.getElementById("rolProgramaSelect");

  try {
    const resposta = await apiGet(`/usuaris/${usuari.idUsuari}/rols`);
    const programes = await apiGet("/programes");

    const opcions = [];

    resposta.programesParticipant.forEach((idPrograma) => {
      const programa = programes.find(
        (p) => String(p.idPrograma) === String(idPrograma)
      );

      opcions.push({
        programa: programa || { idPrograma, nom: `Programa ${idPrograma}` },
        rol: "participant"
      });
    });

    resposta.programesSupervisor.forEach((idPrograma) => {
      const programa = programes.find(
        (p) => String(p.idPrograma) === String(idPrograma)
      );

      opcions.push({
        programa: programa || { idPrograma, nom: `Programa ${idPrograma}` },
        rol: "supervisor"
      });
    });

    if (opcions.length === 0) {
      status.textContent = "Aquest usuari no té cap programa assignat.";
      return;
    }

    select.innerHTML = opcions.map((item, index) => `
      <option value="${index}">
        ${item.programa.nom || item.programa.nomPrograma || `Programa ${item.programa.idPrograma}`} — ${item.rol}
      </option>
    `).join("");

    status.classList.add("hidden");
    form.classList.remove("hidden");

    form.addEventListener("submit", (event) => {
      event.preventDefault();

      const item = opcions[Number(select.value)];

      guardarProgramaActiu(item.programa);
      guardarRolActiu(item.rol);

      if (item.rol === "participant") navegar("P03");
      else if (item.rol === "supervisor") navegar("P08");
    });
  } catch (error) {
    status.textContent = error.message;
    status.classList.add("error");
  }
}