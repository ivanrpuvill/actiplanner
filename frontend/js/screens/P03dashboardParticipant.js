import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirUsuariActiu } from "../state.js";

export async function renderP03DashboardParticipant(app, navegar) {
  const usuari = obtenirUsuariActiu();
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Dashboard participant", `
    <div id="dashboardContent" class="grid">
      <div class="card">
        <h3>Programa actiu</h3>
        <p>${programa?.nom || programa?.nomPrograma || "Programa no definit"}</p>
      </div>

      <div class="card">
        <h3>Progrés</h3>
        <p id="progresText">Carregant...</p>
      </div>

      <div class="card">
        <h3>Seguiments</h3>
        <p id="seguimentsText">Carregant...</p>
      </div>
    </div>
  `);

  activarLayoutEvents(navegar);

  try {
    const seguiments = await apiGet(
      `/programes/${programa.idPrograma}/usuaris/${usuari.idUsuari}/seguiments`
    );

    document.getElementById("seguimentsText").textContent =
      `${seguiments.length || 0} seguiments registrats`;

    document.getElementById("progresText").textContent =
      "Consulta el detall del pla per veure el progrés complet.";
  } catch {
    document.getElementById("seguimentsText").textContent =
      "No s'han pogut carregar els seguiments.";
    document.getElementById("progresText").textContent =
      "No disponible.";
  }
}