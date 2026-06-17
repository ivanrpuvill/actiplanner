import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirUsuariActiu, obtenirPlaActiu } from "../state.js";

export async function renderP07Gamificacio(app, navegar) {
  const programa = obtenirProgramaActiu();
  const usuari = obtenirUsuariActiu();
  const plaActiu = obtenirPlaActiu();

  app.innerHTML = renderLayout("Gamificació personal", `
    <div class="grid">
      <div class="card">
        <h3>Progrés personal</h3>
        <p id="progresPersonal">Carregant...</p>
      </div>

      <div class="card">
        <h3>Estat del pla</h3>
        <p id="estatPla">Carregant...</p>
      </div>

      <div class="card">
        <h3>Posició destacada</h3>
        <p id="posicioParticipant">Carregant...</p>
      </div>
    </div>

    <div class="card constructor-container">
      <h3>Rànquing del programa</h3>
      <div id="rankingContainer">Carregant rànquing...</div>
    </div>
  `);

  activarLayoutEvents(navegar);

  await carregarGamificacio(programa, usuari, plaActiu);
}

async function carregarGamificacio(programa, usuari, plaActiu) {
  const progresPersonal = document.getElementById("progresPersonal");
  const estatPla = document.getElementById("estatPla");
  const posicioParticipant = document.getElementById("posicioParticipant");
  const rankingContainer = document.getElementById("rankingContainer");

  try {
    let pla = plaActiu;

    if (!pla) {
      const plans = await apiGet(`/programes/${programa.idPrograma}/plans`);

      if (plans.length) {
        pla = await apiGet(`/plans/${plans[0].idPla}`);
      }
    }

    if (pla) {
      progresPersonal.textContent = `${pla.progresPla ?? 0}%`;
      estatPla.textContent = pla.estatPla || "Sense estat";
    } else {
      progresPersonal.textContent = "No disponible";
      estatPla.textContent = "No hi ha cap pla disponible";
    }
  } catch {
    progresPersonal.textContent = "No disponible";
    estatPla.textContent = "No disponible";
  }

  try {
    const ranquing = await apiGet(`/programes/${programa.idPrograma}/ranquing`);

    if (!ranquing.length) {
      posicioParticipant.textContent = "Encara no hi ha rànquing.";
      rankingContainer.innerHTML = "<p>Encara no hi ha participants en aquest programa.</p>";
      return;
    }

    const itemParticipant = ranquing.find((item) =>
      String(item.idUsuari) === String(usuari.idUsuari)
    );

    posicioParticipant.textContent = itemParticipant
      ? `Posició ${itemParticipant.posicio} de ${ranquing.length}${itemParticipant.destacat ? " — Participant destacat ⭐" : ""}`
      : "Encara no apareixes al rànquing.";

    rankingContainer.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Posició</th>
            <th>Participant</th>
            <th>Progrés</th>
          </tr>
        </thead>
        <tbody>
          ${ranquing.map((item) => `
            <tr ${String(item.idUsuari) === String(usuari.idUsuari) ? 'class="fila-propia"' : ""}>
              <td>${item.posicio}${item.destacat ? " ⭐" : ""}</td>
              <td>${item.nom}</td>
              <td>${item.progres}%</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    posicioParticipant.textContent = "No disponible";
    rankingContainer.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}