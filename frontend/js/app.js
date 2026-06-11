const API_URL = "http://127.0.0.1:8000";

function getUsuariActiu() {
    return JSON.parse(localStorage.getItem("usuariActiu"));
}

function getProgramaActiu() {
    return JSON.parse(localStorage.getItem("programaActiu"));
}

async function renderLogin() {
    const resposta = await fetch(`${API_URL}/usuaris`);
    const usuaris = await resposta.json();

    document.getElementById("app").innerHTML = `
        <section class="login-page">
            <div class="login-card">
                <div class="logo">Acti<span>planner</span></div>
                <p class="subtitle">Selecciona un usuari per accedir al prototip.</p>

                <div class="user-list">
                    ${usuaris.map(usuari => `
                        <button onclick='entrar(${JSON.stringify(usuari)})'>
                            ${usuari.nom} ${usuari.cognoms}
                            ${usuari.esAdministrador ? "(Administrador)" : ""}
                        </button>
                    `).join("")}
                </div>
            </div>
        </section>
    `;
}

function entrar(usuari) {
    localStorage.setItem("usuariActiu", JSON.stringify(usuari));
    renderSeleccioPrograma();
}

async function renderSeleccioPrograma() {
    const usuari = getUsuariActiu();

    const resposta = await fetch(
        `${API_URL}/empreses/${usuari.idEmpresa}/programes`
    );

    const programes = await resposta.json();

    document.getElementById("app").innerHTML = `
        <header class="header">
            <div class="logo">Acti<span>planner</span></div>
            <div>${usuari.nom} ${usuari.cognoms}</div>
        </header>

        <main class="main">
            <div class="page-title">
                <h1>Selecció de programa</h1>
                <p>Tria el programa de formació amb què vols treballar.</p>
            </div>

            <section class="card-grid">
                ${programes.map(programa => `
                    <article class="card">
                        <h2>${programa.nom}</h2>
                        <p class="secondary">${programa.descripcio}</p>
                        <p class="secondary">${programa.dataInici} - ${programa.dataFi}</p>
                        <button onclick='seleccionarPrograma(${JSON.stringify(programa)})'>
                            Accedir
                        </button>
                    </article>
                `).join("")}
            </section>
        </main>
    `;
}

function seleccionarPrograma(programa) {
    localStorage.setItem("programaActiu", JSON.stringify(programa));

    const usuari = getUsuariActiu();

    if (usuari.esAdministrador) {
        alert("Següent pantalla: P12 Dashboard administrador");
        return;
    }

    renderDashboardParticipant();
}

async function renderDashboardParticipant() {
    const usuari = getUsuariActiu();
    const programa = getProgramaActiu();

    const resposta = await fetch(
        `${API_URL}/programes/${programa.idPrograma}/participants/${usuari.idUsuari}/progres`
    );

    const progres = await resposta.json();

    document.getElementById("app").innerHTML = `
        <header class="header">
            <div class="logo">Acti<span>planner</span></div>
            <button onclick="renderSeleccioPrograma()">Canviar programa</button>
        </header>

        <main class="main">
            <div class="page-title">
                <h1>Dashboard participant</h1>
                <p>${programa.nom}</p>
            </div>

            <section class="card-grid">
                <article class="card">
                    <h2>Progrés global</h2>
                    <div class="metric">${progres.progresGlobal}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:${progres.progresGlobal}%"></div>
                    </div>
                </article>

                <article class="card">
                    <h2>Estat</h2>
                    <span class="badge">${progres.estatGlobal}</span>
                </article>

                <article class="card">
                    <h2>Objectius</h2>
                    <div class="metric">${progres.objectius.length}</div>
                </article>
            </section>

            <section class="card">
                <h2>Objectius del participant</h2>
                ${progres.objectius.map(objectiu => `
                    <div class="list-item">
                        <strong>Objectiu ${objectiu.idObjectiu}</strong>
                        <p class="secondary">
                            Progrés: ${objectiu.progresObjectiu}% · Estat: ${objectiu.estatObjectiu}
                        </p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width:${objectiu.progresObjectiu}%"></div>
                        </div>
                    </div>
                `).join("")}
            </section>
        </main>
    `;
}

renderLogin();