import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP09DetallParticipant(app, navegar) {
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Detall participant", `
    <div class="card">
      <h3>Selecciona un participant</h3>

      <div class="form-grid">
        <div>
          <label>Participant</label>
          <select id="participantSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarParticipant">Carregar</button>
        </div>
      </div>
    </div>

    <div id="participantContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorParticipants(programa);

  document.getElementById("btnCarregarParticipant").addEventListener("click", async () => {
    const idUsuari = document.getElementById("participantSelect").value;
    await carregarParticipant(programa.idPrograma, idUsuari);
  });
}

async function carregarSelectorParticipants(programa) {
  const select = document.getElementById("participantSelect");

  try {
    const usuaris = await apiGet("/usuaris");
    const opcions = [];

    for (const usuari of usuaris) {
      const rols = await apiGet(`/usuaris/${usuari.idUsuari}/rols`);

      if ((rols.programesParticipant || []).includes(programa.idPrograma)) {
        opcions.push(usuari);
      }
    }

    if (!opcions.length) {
      select.innerHTML = `<option>No hi ha participants assignats</option>`;
      return;
    }

    select.innerHTML = opcions.map((usuari) => `
      <option value="${usuari.idUsuari}">
        ${usuari.nom || ""} ${usuari.cognoms || ""} — ${usuari.email || usuari.idUsuari}
      </option>
    `).join("");

    await carregarParticipant(programa.idPrograma, opcions[0].idUsuari);
  } catch (error) {
    select.innerHTML = `<option>Error carregant participants</option>`;
    document.getElementById("participantContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarParticipant(idPrograma, idUsuari) {
  const container = document.getElementById("participantContainer");

  try {
    const seguiments = await apiGet(
      `/programes/${idPrograma}/usuaris/${idUsuari}/seguiments`
    );

    const feedbacks = await apiGet(
      `/programes/${idPrograma}/participants/${idUsuari}/feedback`
    );

    container.innerHTML = `
      <div class="grid">
        <div class="card">
          <h3>Seguiments</h3>
          <p>${seguiments.length || 0} seguiments registrats</p>
        </div>

        <div class="card">
          <h3>Feedback rebut</h3>
          <p>${feedbacks.length || 0} comentaris de feedback</p>
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Detall de seguiments</h3>

        ${seguiments.length ? `
          <table>
            <thead>
              <tr>
                <th>Objectiu</th>
                <th>Progrés</th>
                <th>Estat</th>
              </tr>
            </thead>
            <tbody>
              ${seguiments.map((seguiment) => `
                <tr>
                  <td>${seguiment.idObjectiu || "-"}</td>
                  <td>${seguiment.progres ?? seguiment.progresObjectiu ?? "-"}%</td>
                  <td>${seguiment.estat || seguiment.estatObjectiu || "-"}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        ` : "<p>No hi ha seguiments disponibles.</p>"}
      </div>

      <div class="card constructor-container">
        <h3>Feedback</h3>

        ${feedbacks.length ? feedbacks.map((feedback) => `
          <div class="list-item">
            <strong>${feedback.dataCreacio || "-"}</strong>
            <p>${feedback.comentari || "-"}</p>
            <p><strong>Validació:</strong> ${feedback.validacio ? "Validat" : "Pendent"}</p>
          </div>
        `).join("") : "<p>No hi ha feedback registrat.</p>"}
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}