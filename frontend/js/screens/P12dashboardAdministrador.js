import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP12DashboardAdministrador(app, navegar) {
  app.innerHTML = renderLayout("Dashboard administrador", `
    <div class="grid">
      <div class="card">
        <h3>Empreses</h3>
        <p id="empresesText">Carregant...</p>
      </div>

      <div class="card">
        <h3>Usuaris</h3>
        <p id="usuarisText">Carregant...</p>
      </div>

      <div class="card">
        <h3>Programes</h3>
        <p id="programesText">Carregant...</p>
      </div>
    </div>
  `);

  activarLayoutEvents(navegar);

  try {
    const empreses = await apiGet("/empreses");
    const usuaris = await apiGet("/usuaris");
    const programes = await apiGet("/programes");

    document.getElementById("empresesText").textContent = `${empreses.length || 0} empreses`;
    document.getElementById("usuarisText").textContent = `${usuaris.length || 0} usuaris`;
    document.getElementById("programesText").textContent = `${programes.length || 0} programes`;
  } catch {
    document.getElementById("empresesText").textContent = "No disponible.";
    document.getElementById("usuarisText").textContent = "No disponible.";
    document.getElementById("programesText").textContent = "No disponible.";
  }
}