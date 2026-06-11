import { obtenirUsuariActiu, obtenirProgramaActiu, obtenirRolActiu } from "./state.js";

import { renderP01Login } from "./screens/P01login.js";
import { renderP02SeleccioPrograma } from "./screens/P02seleccioPrograma.js";
import { renderP03DashboardParticipant } from "./screens/P03dashboardParticipant.js";
import { renderP04DetallPla } from "./screens/P04detallPla.js";
import { renderP05RegistreKPI } from "./screens/P05registreKPI.js";
import { renderP06FeedbackRebut } from "./screens/P06feedbackRebut.js";
import { renderP07Gamificacio } from "./screens/P07gamificacio.js";
import { renderP08DashboardSupervisor } from "./screens/P08dashboardSupervisor.js";
import { renderP09DetallParticipant } from "./screens/P09detallParticipant.js";
import { renderP10GestioFeedback } from "./screens/P10gestioFeedback.js";
import { renderP11RecomanacionsIA } from "./screens/P11recomanacionsIA.js";
import { renderP12DashboardAdministrador } from "./screens/P12dashboardAdministrador.js";
import { renderP13GestioEmpreses } from "./screens/P13gestioEmpreses.js";
import { renderP14GestioUsuaris } from "./screens/P14gestioUsuaris.js";
import { renderP15GestioProgrames } from "./screens/P15gestioProgrames.js";
import { renderP16BibliotecaPlans } from "./screens/P16bibliotecaPlans.js";
import { renderP17ConstructorPlans } from "./screens/P17constructorPlans.js";
import { renderP18AnaliticaReporting } from "./screens/P18analiticaReporting.js";
import { renderP19Ranquings } from "./screens/P19ranquings.js";
import { renderP20GeneradorIAPlans } from "./screens/P20generadorIAPlans.js";
import { renderP21IAInsights } from "./screens/P21iaInsights.js";

const app = document.getElementById("app");

export function navegar(screen) {
  if (screen === "P01") return renderP01Login(app, navegar);
  if (screen === "P02") return renderP02SeleccioPrograma(app, navegar);
  if (screen === "P03") return renderP03DashboardParticipant(app, navegar);
  if (screen === "P04") return renderP04DetallPla(app, navegar);
  if (screen === "P05") return renderP05RegistreKPI(app, navegar);
  if (screen === "P06") return renderP06FeedbackRebut(app, navegar);
  if (screen === "P07") return renderP07Gamificacio(app, navegar);
  if (screen === "P08") return renderP08DashboardSupervisor(app, navegar);
  if (screen === "P09") return renderP09DetallParticipant(app, navegar);
  if (screen === "P10") return renderP10GestioFeedback(app, navegar);
  if (screen === "P11") return renderP11RecomanacionsIA(app, navegar);
  if (screen === "P12") return renderP12DashboardAdministrador(app, navegar);
  if (screen === "P13") return renderP13GestioEmpreses(app, navegar);
  if (screen === "P14") return renderP14GestioUsuaris(app, navegar);
  if (screen === "P15") return renderP15GestioProgrames(app, navegar);
  if (screen === "P16") return renderP16BibliotecaPlans(app, navegar);
  if (screen === "P17") return renderP17ConstructorPlans(app, navegar);
  if (screen === "P18") return renderP18AnaliticaReporting(app, navegar);
  if (screen === "P19") return renderP19Ranquings(app, navegar);
  if (screen === "P20") return renderP20GeneradorIAPlans(app, navegar);
  if (screen === "P21") return renderP21IAInsights(app, navegar);

  app.innerHTML = `
    <div class="empty-screen">
      <h2>Pantalla en desenvolupament</h2>
      <p>La pantalla ${screen} encara no està implementada.</p>
      <button class="btn" id="btnTornar">Tornar</button>
    </div>
  `;

  document.getElementById("btnTornar").addEventListener("click", renderPantallaInicial);
}

export function renderPantallaInicial() {
  const usuari = obtenirUsuariActiu();
  const programa = obtenirProgramaActiu();
  const rol = obtenirRolActiu();

  if (!usuari) return navegar("P01");
  if (rol === "administrador") return navegar("P12");
  if (!programa || !rol) return navegar("P02");
  if (rol === "participant") return navegar("P03");
  if (rol === "supervisor") return navegar("P08");

  navegar("P02");
}

renderPantallaInicial();