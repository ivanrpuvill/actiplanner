function renderLayout(titol, subtitol, contingut, rol) {
    const app = getApp();

    app.innerHTML = `
        <div class="app-layout">
            ${renderSidebar(rol)}

            <main class="main-content">
                <header class="page-header">
                    <div>
                        <h1>${titol}</h1>
                        <p>${subtitol || ""}</p>
                    </div>

                    <button class="btn-secondary" onclick="tancarSessio()">
                        Tancar sessió
                    </button>
                </header>

                <section class="page-content">
                    ${contingut}
                </section>
            </main>
        </div>
    `;
}


function renderSidebar(rol) {
    if (rol === "participant") {
        return `
            <aside class="sidebar">
                <div class="sidebar-logo">Actiplanner</div>

                <nav class="sidebar-nav">
                    <button onclick="renderDashboardParticipant()">Dashboard</button>
                    <button onclick="renderDetallPlaParticipant()">Pla d'acció</button>
                    <button onclick="renderRegistreKPI()">KPI</button>
                    <button onclick="renderFeedbackRebut()">Feedback</button>
                    <button onclick="renderGamificacioParticipant()">Gamificació</button>
                </nav>
            </aside>
        `;
    }

    if (rol === "supervisor") {
        return `
            <aside class="sidebar">
                <div class="sidebar-logo">Actiplanner</div>

                <nav class="sidebar-nav">
                    <button onclick="renderDashboardSupervisor()">Dashboard</button>
                    <button onclick="renderParticipantsSupervisor()">Participants</button>
                    <button onclick="renderGestioFeedback()">Feedback</button>
                    <button onclick="renderRecomanacionsIA()">Recomanacions IA</button>
                    <button onclick="renderRanquings()">Rànquings</button>
                    <button onclick="renderIAInsights()">IA Insights</button>
                </nav>
            </aside>
        `;
    }

    if (rol === "administrador") {
        return `
            <aside class="sidebar">
                <div class="sidebar-logo">Actiplanner</div>

                <nav class="sidebar-nav">
                    <button onclick="renderDashboardAdministrador()">Dashboard</button>
                    <button onclick="renderGestioEmpreses()">Empreses</button>
                    <button onclick="renderGestioUsuaris()">Usuaris</button>
                    <button onclick="renderGestioProgrames()">Programes</button>
                    <button onclick="renderBibliotecaPlans()">Plans</button>
                    <button onclick="renderConstructorPlans()">Constructor</button>
                    <button onclick="renderAnaliticaReporting()">Analítica</button>
                    <button onclick="renderRanquings()">Rànquings</button>
                    <button onclick="renderGeneradorIAPlans()">Generador IA</button>
                    <button onclick="renderIAInsights()">IA Insights</button>
                </nav>
            </aside>
        `;
    }

    return "";
}