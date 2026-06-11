import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP19Ranquings(app, navegar) {
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Rànquings i gamificació", `
    <div class="grid">
      <div class="card">
        <h3>Participants destacats</h3>
        <div id="destacatsContainer">Carregant...</div>
      </div>

      <div class="card">
        <h3>Participants amb desviació</h3>
        <div id="desviacioContainer">Carregant...</div>
      </div>
    </div>
  `);

  activarLayoutEvents(navegar);

  await carregarRanquings(programa.idPrograma);
}

async function carregarRanquings(idPrograma) {
  const destacatsContainer = document.getElementById("destacatsContainer");
  const desviacioContainer = document.getElementById("desviacioContainer");

  try {
    const destacats = await apiGet(`/programes/${idPrograma}/participants-destacats`);

    if (!destacats.length) {
      destacatsContainer.innerHTML = "<p>No hi ha participants destacats.</p>";
    } else {
      destacatsContainer.innerHTML = renderTaulaParticipants(destacats, true);
    }
  } catch (error) {
    destacatsContainer.innerHTML = `<p class="error-text">${error.message}</p>`;
  }

  try {
    const desviacio = await apiGet(`/programes/${idPrograma}/participants-desviacio`);

    if (!desviacio.length) {
      desviacioContainer.innerHTML = "<p>No hi ha participants amb desviació.</p>";
    } else {
      desviacioContainer.innerHTML = renderTaulaParticipants(desviacio, false);
    }
  } catch (error) {
    desviacioContainer.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderTaulaParticipants(items, mostrarPosicio) {
  return `
    <table>
      <thead>
        <tr>
          ${mostrarPosicio ? "<th>Posició</th>" : ""}
          <th>Participant</th>
          <th>Valor</th>
          <th>Estat</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item, index) => `
          <tr>
            ${mostrarPosicio ? `<td>${index + 1}</td>` : ""}
            <td>${nomParticipant(item)}</td>
            <td>${item.progres ?? item.progresPla ?? item.valor ?? item.desviacio ?? "-"}${item.progres || item.progresPla ? "%" : ""}</td>
            <td>${item.estat || item.estatPla || item.estatObjectiu || "-"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function nomParticipant(item) {
  if (item.nom || item.cognoms) {
    return `${item.nom || ""} ${item.cognoms || ""}`.trim();
  }

  if (item.usuari) {
    return `${item.usuari.nom || ""} ${item.usuari.cognoms || ""}`.trim();
  }

  return `Usuari ${item.idUsuari || item.idParticipant || "-"}`;
}