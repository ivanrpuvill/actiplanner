import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirUsuariActiu } from "../state.js";

export async function renderP03DashboardParticipant(app, navegar) {
  const usuari = obtenirUsuariActiu();
  const programa = obtenirProgramaActiu();

  if (!usuari || !programa) {
    app.innerHTML = renderLayout("Dashboard participant", `
      <div class="card">
        <h3>No hi ha sessió activa</h3>
        <p>Selecciona un usuari i un programa abans d'accedir al dashboard.</p>
        <button class="btn" id="btnTornar">Tornar a la selecció</button>
      </div>
    `);

    activarLayoutEvents(navegar);

    document.getElementById("btnTornar").addEventListener("click", () => {
      navegar("P02");
    });

    return;
  }

  app.innerHTML = renderLayout("Dashboard participant", `
    <div id="participantDashboardContainer" class="dashboard-grid">
      <div class="card">Carregant dades personals...</div>
    </div>
  `);

  activarLayoutEvents(navegar);

  const container = document.getElementById("participantDashboardContainer");

  try {
    const [seguiments, feedbacks] = await Promise.all([
      apiGet(`/programes/${programa.idPrograma}/usuaris/${usuari.idUsuari}/seguiments`),
      apiGet(`/programes/${programa.idPrograma}/participants/${usuari.idUsuari}/feedback`)
    ]);

    const seguimentsRegistrats = seguiments.length;
    const feedbacksRebuts = feedbacks.length;

    const seguimentsCompletats = seguiments.filter((seguiment) =>
      String(seguiment.estat || seguiment.estatObjectiu || "").toLowerCase().includes("complet")
    ).length;

    const progresMitja = calcularProgresMitja(seguiments);

    const feedbacksPendents = feedbacks.filter((feedback) => !feedback.validacio).length;

    const alertes = [];

    if (seguimentsRegistrats === 0) {
      alertes.push("Encara no tens seguiments registrats.");
    }

    if (feedbacksPendents > 0) {
      alertes.push(`Tens ${feedbacksPendents} feedback(s) pendent(s) de revisar o validar.`);
    }

    if (progresMitja !== null && progresMitja < 50) {
      alertes.push("El teu progrés personal és inferior al 50%.");
    }

    container.innerHTML = `
      <div class="card dashboard-wide">
        <h3>${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}</h3>
        <p>
          Hola, <strong>${usuari.nom || "participant"}</strong>.
          Aquest és el teu espai personal de seguiment.
        </p>
      </div>

      <div class="card stat-card clickable-card" id="cardPla">
        <h3>El meu pla</h3>
        <p class="stat-number">Pla</p>
        <p class="stat-subtitle">Veure objectius, accions i KPI</p>
      </div>

      <div class="card stat-card clickable-card" id="cardSeguiments">
        <h3>Seguiments</h3>
        <p class="stat-number">${seguimentsRegistrats}</p>
        <p class="stat-subtitle">${seguimentsCompletats} completats</p>
      </div>

      <div class="card stat-card clickable-card" id="cardFeedback">
        <h3>Feedback rebut</h3>
        <p class="stat-number">${feedbacksRebuts}</p>
        <p class="stat-subtitle">${feedbacksPendents} pendents</p>
      </div>

      <div class="card stat-card clickable-card" id="cardGamificacio">
        <h3>Gamificació</h3>
        <p class="stat-number">★</p>
        <p class="stat-subtitle">Veure rànquing i destacats</p>
      </div>

      <div class="card stat-card">
        <h3>Progrés personal</h3>
        <p class="stat-number">${progresMitja === null ? "-" : `${progresMitja}%`}</p>
        ${renderBarraProgres(progresMitja)}
        <p class="stat-subtitle">Mitjana dels teus seguiments</p>
      </div>

      <div class="card dashboard-wide">
        <h3>⚠ Alertes personals</h3>
        ${renderAlertes(alertes)}
      </div>

      <div class="card dashboard-wide">
        <h3>Resum personal</h3>
        <p>
          Tens <strong>${seguimentsRegistrats}</strong> seguiments registrats i
          <strong>${feedbacksRebuts}</strong> feedbacks rebuts dins del programa.
        </p>
        <p>
          El teu progrés personal és de
          <strong>${progresMitja === null ? "no disponible" : `${progresMitja}%`}</strong>.
        </p>
      </div>
    `;

    document.getElementById("cardPla").addEventListener("click", () => navegar("P04"));
    document.getElementById("cardSeguiments").addEventListener("click", () => navegar("P04"));
    document.getElementById("cardFeedback").addEventListener("click", () => navegar("P06"));
    document.getElementById("cardGamificacio").addEventListener("click", () => navegar("P07"));

  } catch (error) {
    container.innerHTML = `<div class="card error-text">${error.message}</div>`;
  }
}

function calcularProgresMitja(seguiments) {
  const valors = seguiments
    .map((seguiment) => seguiment.progres ?? seguiment.progresObjectiu)
    .filter((valor) => valor !== undefined && valor !== null && !Number.isNaN(Number(valor)));

  if (!valors.length) {
    return null;
  }

  const suma = valors.reduce((total, valor) => total + Number(valor), 0);

  return Math.round(suma / valors.length);
}

function renderBarraProgres(progres) {
  if (progres === null) {
    return "";
  }

  const valor = Math.max(0, Math.min(100, progres));
  const estat = calcularEstat(valor);

  return `
    <div class="progres-bar-track">
      <div class="progres-bar-fill estat-${estat}" style="width: ${valor}%"></div>
    </div>
  `;
}

function calcularEstat(progres) {
  // Mateixos llindars que AnalisiService._calcular_estat al backend
  // (20% / 80%), replicats aquí només per acolorir la barra visual.
  if (progres >= 80) {
    return "assolit";
  }

  if (progres >= 20) {
    return "en_progres";
  }

  return "pendent";
}

function renderAlertes(alertes) {
  if (!alertes.length) {
    return `<p>No tens alertes personals pendents.</p>`;
  }

  return `
    <ul>
      ${alertes.map((alerta) => `
        <li>${alerta}</li>
      `).join("")}
    </ul>
  `;
}