import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP12DashboardAdministrador(app, navegar) {
  app.innerHTML = renderLayout("Dashboard administrador", `
    <div id="adminDashboardContainer" class="dashboard-grid">
      <div class="card">Carregant dades...</div>
    </div>
  `);

  activarLayoutEvents(navegar);

  const container = document.getElementById("adminDashboardContainer");

  try {
    const [empreses, usuaris, programes, feedbacks] = await Promise.all([
      apiGet("/empreses"),
      apiGet("/usuaris"),
      apiGet("/programes"),
      apiGet("/feedback")
    ]);

    const plans = [];

    for (const programa of programes) {
      const plansPrograma = await apiGet(`/programes/${programa.idPrograma}/plans`);
      plans.push(...plansPrograma);
    }

    const administradors = usuaris.filter((usuari) => usuari.esAdministrador);
    const usuarisActius = usuaris.filter((usuari) => usuari.actiu);

    const programesSensePlans = programes.filter(
      (programa) => !plans.some((pla) => pla.idPrograma === programa.idPrograma)
    );

    const empresesSenseUsuaris = empreses.filter(
      (empresa) => !usuaris.some((usuari) => usuari.idEmpresa === empresa.idEmpresa)
    );

    const programesSenseFeedback = programes.filter(
      (programa) =>
        !feedbacks.some((feedback) => feedback.idPrograma === programa.idPrograma)
    );

    container.innerHTML = `
      <div class="card stat-card clickable-card" id="cardEmpreses">
        <h3>Empreses</h3>
        <p class="stat-number">${empreses.length}</p>
        <p class="stat-subtitle">Empreses registrades</p>
      </div>

      <div class="card stat-card clickable-card" id="cardUsuaris">
        <h3>Usuaris</h3>
        <p class="stat-number">${usuaris.length}</p>
        <p class="stat-subtitle">${usuarisActius.length} actius</p>
      </div>

      <div class="card stat-card clickable-card" id="cardAdministradors">
        <h3>Administradors</h3>
        <p class="stat-number">${administradors.length}</p>
        <p class="stat-subtitle">Administradors globals</p>
      </div>

      <div class="card stat-card clickable-card" id="cardProgrames">
        <h3>Programes</h3>
        <p class="stat-number">${programes.length}</p>
        <p class="stat-subtitle">Programes de formació</p>
      </div>

      <div class="card stat-card clickable-card" id="cardPlans">
        <h3>Plans d'acció</h3>
        <p class="stat-number">${plans.length}</p>
        <p class="stat-subtitle">Biblioteca de plans</p>
      </div>

      <div class="card stat-card clickable-card" id="cardFeedbacks">
        <h3>Feedbacks</h3>
        <p class="stat-number">${feedbacks.length}</p>
        <p class="stat-subtitle">Feedbacks registrats</p>
      </div>

      <div class="card stat-card clickable-card" id="cardIA">
        <h3>IA Insights</h3>
        <p class="stat-number">IA</p>
        <p class="stat-subtitle">Resums i recomanacions</p>
      </div>

      <div class="card dashboard-wide">
        <h3>⚠ Alertes del sistema</h3>

        ${renderAlertaDetallada(
          "Programes sense plans d'acció",
          programesSensePlans,
          "nom",
          "Tots els programes tenen plans d'acció associats."
        )}

        ${renderAlertaDetallada(
          "Empreses sense usuaris",
          empresesSenseUsuaris,
          "nom",
          "Totes les empreses tenen usuaris associats."
        )}

        ${renderAlertaDetallada(
          "Programes sense feedback registrat",
          programesSenseFeedback,
          "nom",
          "Tots els programes tenen feedback registrat."
        )}
      </div>

      <div class="card dashboard-wide">
        <h3>📊 Informe general del sistema</h3>
        <p>
          El sistema disposa de <strong>${empreses.length}</strong> empreses,
          <strong>${usuaris.length}</strong> usuaris i
          <strong>${programes.length}</strong> programes de formació.
        </p>
        <p>
          S'han registrat <strong>${plans.length}</strong> plans d'acció i
          <strong>${feedbacks.length}</strong> feedbacks.
        </p>
        <p>
          Les alertes permeten identificar entitats incompletes o programes que encara
          requereixen configuració o seguiment.
        </p>
      </div>
    `;

    document.getElementById("cardEmpreses").addEventListener("click", () => navegar("P13"));
    document.getElementById("cardUsuaris").addEventListener("click", () => navegar("P14"));
    document.getElementById("cardAdministradors").addEventListener("click", () => navegar("P14"));
    document.getElementById("cardProgrames").addEventListener("click", () => navegar("P15"));

    document.getElementById("cardPlans").addEventListener("click", () => {
      sessionStorage.removeItem("filtreProgramaPlans");
      navegar("P16");
    });

    document.getElementById("cardFeedbacks").addEventListener("click", () => navegar("P10"));
    document.getElementById("cardIA").addEventListener("click", () => navegar("P21"));

  } catch (error) {
    container.innerHTML = `<div class="card error-text">${error.message}</div>`;
  }
}

function renderAlertaDetallada(titol, items, campNom, missatgeBuit) {
  if (!items || !items.length) {
    return `
      <div class="alert-block success-alert">
        <h4>${titol}</h4>
        <p>${missatgeBuit}</p>
      </div>
    `;
  }

  return `
    <div class="alert-block warning-alert">
      <h4>${titol}</h4>
      <p>${items.length} element(s) detectat(s):</p>
      <ul>
        ${items.map((item) => `
          <li>${item[campNom] || item.nomPrograma || item.titol || `ID ${item.idPrograma || item.idEmpresa || "-"}`}</li>
        `).join("")}
      </ul>
    </div>
  `;
}