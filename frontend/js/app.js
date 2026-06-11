const API_URL = "http://127.0.0.1:8000";

const usuarisDemo = {
    participant: {
        idUsuari: 1,
        nom: "Participant Demo",
        rol: "participant"
    },
    supervisor: {
        idUsuari: 2,
        nom: "Supervisor Demo",
        rol: "supervisor"
    },
    administrador: {
        idUsuari: 3,
        nom: "Administrador Demo",
        rol: "administrador"
    }
};

function renderLogin() {
    document.getElementById("app").innerHTML = `
        <section class="login-page">
            <div class="login-card">
                <div class="logo">Acti<span>planner</span></div>
                <p class="subtitle">
                    Plataforma de seguiment de plans d'acció.
                </p>

                <label>Email</label>
                <input type="email" placeholder="usuari@empresa.com">

                <label>Contrasenya</label>
                <input type="password" placeholder="********">

                <button onclick="entrarCom('participant')">
                    Iniciar sessió
                </button>

                <div class="demo-buttons">
                    <button onclick="entrarCom('participant')">
                        Entrar com a participant
                    </button>

                    <button onclick="entrarCom('supervisor')">
                        Entrar com a supervisor
                    </button>

                    <button onclick="entrarCom('administrador')">
                        Entrar com a administrador
                    </button>
                </div>
            </div>
        </section>
    `;
}

function entrarCom(rol) {
    const usuari = usuarisDemo[rol];

    localStorage.setItem("usuariActiu", JSON.stringify(usuari));

    renderSeleccioPrograma();
}

async function renderSeleccioPrograma() {
    const usuari = JSON.parse(localStorage.getItem("usuariActiu"));

    const resposta = await fetch(`${API_URL}/empreses/1/programes`);
    const programes = await resposta.json();

    document.getElementById("app").innerHTML = `
        <header class="header">
            <div class="logo">Acti<span>planner</span></div>
            <div>${usuari.nom}</div>
        </header>

        <main class="main">
            <div class="page-title">
                <h1>Selecció de programa i rol</h1>
                <p>Selecciona el programa de formació amb què vols treballar.</p>
            </div>

            <section class="card-grid">
                ${programes.map(programa => `
                    <article class="card">
                        <h2>${programa.nom}</h2>
                        <p class="secondary">${programa.descripcio}</p>
                        <p>
                            <span class="badge">${usuari.rol}</span>
                        </p>
                        <p class="secondary">
                            ${programa.dataInici} - ${programa.dataFi}
                        </p>
                        <button onclick="accedirPrograma(${programa.idPrograma})">
                            Accedir
                        </button>
                    </article>
                `).join("")}
            </section>
        </main>
    `;
}

function accedirPrograma(idPrograma) {
    const usuari = JSON.parse(localStorage.getItem("usuariActiu"));

    localStorage.setItem("idProgramaActiu", idPrograma);

    if (usuari.rol === "participant") {
        alert("Següent pantalla: P03 Dashboard participant");
    }

    if (usuari.rol === "supervisor") {
        alert("Següent pantalla: P08 Dashboard supervisor");
    }

    if (usuari.rol === "administrador") {
        alert("Següent pantalla: P12 Dashboard administrador");
    }
}

renderLogin();