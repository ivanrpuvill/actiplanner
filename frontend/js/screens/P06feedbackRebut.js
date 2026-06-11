import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirUsuariActiu } from "../state.js";

export async function renderP06FeedbackRebut(app, navegar) {
  const programa = obtenirProgramaActiu();
  const usuari = obtenirUsuariActiu();

  app.innerHTML = renderLayout("Feedback rebut", `
    <div id="feedbackContainer" class="grid">
      <div class="card">
        <p>Carregant feedback...</p>
      </div>
    </div>
  `);

  activarLayoutEvents(navegar);

  const container = document.getElementById("feedbackContainer");

  try {
    const feedbacks = await apiGet(
      `/programes/${programa.idPrograma}/participants/${usuari.idUsuari}/feedback`
    );

    if (!feedbacks.length) {
      container.innerHTML = `
        <div class="card">
          <h3>Sense feedback</h3>
          <p>Encara no has rebut cap feedback en aquest programa.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = feedbacks.map((feedback) => `
      <div class="card">
        <h3>Feedback</h3>
        <p>${feedback.comentari || "-"}</p>

        <p>
          <strong>Validació:</strong>
          ${feedback.validacio ? "Validat" : "Pendent"}
        </p>

        <p>
          <strong>Data:</strong>
          ${feedback.dataCreacio || "-"}
        </p>

        <p>
          <strong>Supervisor:</strong>
          ${feedback.idUsuariSupervisor || "-"}
        </p>
      </div>
    `).join("");
  } catch (error) {
    container.innerHTML = `
      <div class="card">
        <p class="error-text">${error.message}</p>
      </div>
    `;
  }
}