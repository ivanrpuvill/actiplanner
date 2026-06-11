import { apiGet, apiPost, apiPut } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirUsuariActiu } from "../state.js";

export async function renderP10GestioFeedback(app, navegar) {
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Gestió feedback", `
    <div class="card">
      <h3>Selecciona un participant</h3>

      <div class="form-grid">
        <div>
          <label>Participant</label>
          <select id="participantSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarFeedback">Carregar feedback</button>
        </div>
      </div>
    </div>

    <div id="feedbackContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorParticipants(programa);

  document.getElementById("btnCarregarFeedback").addEventListener("click", async () => {
    const idParticipant = document.getElementById("participantSelect").value;
    await carregarFeedbackParticipant(idParticipant, navegar);
  });
}

async function carregarSelectorParticipants(programa) {
  const select = document.getElementById("participantSelect");

  try {
    const usuaris = await apiGet("/usuaris");
    const participants = [];

    for (const usuari of usuaris) {
      const rols = await apiGet(`/usuaris/${usuari.idUsuari}/rols`);

      if ((rols.programesParticipant || []).includes(programa.idPrograma)) {
        participants.push(usuari);
      }
    }

    if (!participants.length) {
      select.innerHTML = `<option>No hi ha participants assignats</option>`;
      return;
    }

    select.innerHTML = participants.map((usuari) => `
      <option value="${usuari.idUsuari}">
        ${usuari.nom || ""} ${usuari.cognoms || ""} — ${usuari.email || usuari.idUsuari}
      </option>
    `).join("");

    await carregarFeedbackParticipant(participants[0].idUsuari);
  } catch (error) {
    document.getElementById("feedbackContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarFeedbackParticipant(idParticipant, navegar) {
  const programa = obtenirProgramaActiu();
  const supervisor = obtenirUsuariActiu();
  const container = document.getElementById("feedbackContainer");

  try {
    const feedbacks = await apiGet(
      `/programes/${programa.idPrograma}/participants/${idParticipant}/feedback`
    );

    container.innerHTML = `
      <div class="grid two-cols">
        <div class="card">
          <h3>Nou feedback</h3>

          <form id="feedbackForm" class="form">
            <label>Comentari</label>
            <textarea id="comentari" required></textarea>

            <label>
              <input id="validacio" type="checkbox" />
              Marcar com a validat
            </label>

            <button class="btn" type="submit">Crear feedback</button>
          </form>
        </div>

        <div class="card">
          <h3>Feedback existent</h3>

          ${feedbacks.length ? feedbacks.map((feedback) => `
            <div class="list-item">
              <strong>${feedback.dataCreacio || "-"}</strong>
              <p>${feedback.comentari || "-"}</p>
              <p><strong>Validació:</strong> ${feedback.validacio ? "Validat" : "Pendent"}</p>

              <button
                class="btn secondary btn-validar-feedback"
                data-id-feedback="${feedback.idFeedback}"
                data-comentari="${encodeURIComponent(feedback.comentari || "")}"
                data-id-participant="${feedback.idUsuariParticipant}"
              >
                Marcar validat
              </button>
            </div>
          `).join("") : "<p>No hi ha feedback registrat.</p>"}
        </div>
      </div>
    `;

    document.getElementById("feedbackForm").addEventListener("submit", async (event) => {
      event.preventDefault();

      const nouFeedback = {
        idFeedback: Date.now(),
        idPrograma: programa.idPrograma,
        idUsuariSupervisor: supervisor.idUsuari,
        idUsuariParticipant: Number(idParticipant),
        comentari: document.getElementById("comentari").value,
        validacio: document.getElementById("validacio").checked,
        dataCreacio: new Date().toISOString().slice(0, 10)
      };

      await apiPost("/feedback", nouFeedback);
      await carregarFeedbackParticipant(idParticipant, navegar);
    });

    document.querySelectorAll(".btn-validar-feedback").forEach((button) => {
      button.addEventListener("click", async () => {
        const feedbackActualitzat = {
          idFeedback: Number(button.dataset.idFeedback),
          idPrograma: programa.idPrograma,
          idUsuariSupervisor: supervisor.idUsuari,
          idUsuariParticipant: Number(button.dataset.idParticipant),
          comentari: decodeURIComponent(button.dataset.comentari),
          validacio: true,
          dataCreacio: new Date().toISOString().slice(0, 10)
        };

        await apiPut(`/feedback/${feedbackActualitzat.idFeedback}`, feedbackActualitzat);
        await carregarFeedbackParticipant(idParticipant, navegar);
      });
    });

  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}