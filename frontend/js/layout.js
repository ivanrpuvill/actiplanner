import { tancarSessio, obtenirRolActiu, obtenirUsuariActiu } from "./state.js";

export function renderLayout(titol, contingutHtml) {
  const usuari = obtenirUsuariActiu();
  const rol = obtenirRolActiu();

  return `
    <div class="app-layout">
      <aside class="sidebar">
        <div class="brand">
          <h1>Actiplanner</h1>
          <p>${rol || ""}</p>
        </div>

        <nav class="menu">
          ${renderMenu(rol)}
        </nav>
      </aside>

      <main class="main">
        <header class="topbar">
          <div>
            <h2>${titol}</h2>
            <p>${usuari ? usuari.nom || usuari.email || "Usuari actiu" : ""}</p>
          </div>
          <button id="btnLogout" class="btn secondary">Tancar sessió</button>
        </header>

        <section class="content">
          ${contingutHtml}
        </section>
      </main>
    </div>
  `;
}

function renderMenu(rol) {
  if (rol === "participant") {
    return `
      <button data-screen="P03" class="menu-item">Dashboard</button>
      <button data-screen="P04" class="menu-item">Pla d'acció</button>
      <button data-screen="P05" class="menu-item">Registre KPI</button>
      <button data-screen="P06" class="menu-item">Feedback</button>
      <button data-screen="P07" class="menu-item">Gamificació</button>
    `;
  }

  if (rol === "supervisor") {
    return `
      <button data-screen="P08" class="menu-item">Dashboard</button>
      <button data-screen="P09" class="menu-item">Participants</button>
      <button data-screen="P10" class="menu-item">Feedback</button>
      <button data-screen="P11" class="menu-item">Recomanacions IA</button>
      <button data-screen="P19" class="menu-item">Rànquings</button>
      <button data-screen="P21" class="menu-item">IA Insights</button>
    `;
  }

  if (rol === "administrador") {
    return `
      <button data-screen="P12" class="menu-item">Dashboard</button>
      <button data-screen="P13" class="menu-item">Empreses</button>
      <button data-screen="P14" class="menu-item">Usuaris</button>
      <button data-screen="P15" class="menu-item">Programes</button>
      <button data-screen="P16" class="menu-item">Plans</button>
      <button data-screen="P17" class="menu-item">Constructor</button>
      <button data-screen="P18" class="menu-item">Analítica</button>
      <button data-screen="P20" class="menu-item">Generador IA</button>
      <button data-screen="P21" class="menu-item">IA Insights</button>
    `;
  }

  return "";
}

export function activarLayoutEvents(navegar) {
  const logout = document.getElementById("btnLogout");

  if (logout) {
    logout.addEventListener("click", () => {
      tancarSessio();
      navegar("P01");
    });
  }

  document.querySelectorAll("[data-screen]").forEach((button) => {
    button.addEventListener("click", () => {
      navegar(button.dataset.screen);
    });
  });
}