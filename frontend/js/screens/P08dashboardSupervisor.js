import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP08DashboardSupervisor(app, navegar) {
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Dashboard supervisor", `
    <div class="grid">
      <div class="card">
        <h3>Programa</h3>
        <p>${programa?.nom || programa?.nomPrograma || "Programa no definit"}</p>
      </div>

      <div class="card">
        <h3>Anàlisi general</h3>
        <p id="analisiText">Carregant...</p>
      </div>

      <div class="card">
        <h3>Objectius en risc</h3>
        <p id="riscText">Carregant...</p>
      </div>

      <div class="card">
        <h3>Participants amb desviació</h3>
        <p id="desviacioText">Carregant...</p>
      </div>
    </div>
  `);

  activarLayoutEvents(navegar);

  try {
    const analisi = await apiGet(`/programes/${programa.idPrograma}/analisi`);
    const risc = await apiGet(`/programes/${programa.idPrograma}/objectius-risc`);
    const desviacio = await apiGet(`/programes/${programa.idPrograma}/participants-desviacio`);

    document.getElementById("analisiText").textContent =
      analisi.resum || "Anàlisi carregada correctament.";

    document.getElementById("riscText").textContent =
      `${risc.length || 0} objectius en risc`;

    document.getElementById("desviacioText").textContent =
      `${desviacio.length || 0} participants amb desviació`;
  } catch {
    document.getElementById("analisiText").textContent = "No disponible.";
    document.getElementById("riscText").textContent = "No disponible.";
    document.getElementById("desviacioText").textContent = "No disponible.";
  }
}