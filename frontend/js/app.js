const API_URL = "http://127.0.0.1:8000";
const ID_PROGRAMA = 1;

async function carregarDashboard() {
    await carregarAnalisiPrograma();
    await carregarParticipantsDestacats();
    await carregarObjectiusRisc();
}

async function carregarAnalisiPrograma() {
    const resposta = await fetch(`${API_URL}/programes/${ID_PROGRAMA}/analisi`);
    const dades = await resposta.json();

    document.getElementById("nombreParticipants").textContent =
        dades.nombreParticipants;

    document.getElementById("progresMitja").textContent =
        `${dades.progresMitjaPrograma}%`;

    document.getElementById("estatPrograma").textContent =
        dades.estatPrograma;

    document.getElementById("barraProgres").style.width =
        `${dades.progresMitjaPrograma}%`;
}

async function carregarParticipantsDestacats() {
    const resposta = await fetch(
        `${API_URL}/programes/${ID_PROGRAMA}/participants-destacats`
    );

    const dades = await resposta.json();
    const llista = document.getElementById("participantsDestacats");

    llista.innerHTML = "";

    if (dades.length === 0) {
        llista.innerHTML = "<li>No hi ha participants destacats.</li>";
        return;
    }

    dades.forEach(participant => {
        const item = document.createElement("li");
        item.textContent = `Usuari ${participant.idUsuari} - ${participant.progres}%`;
        llista.appendChild(item);
    });
}

async function carregarObjectiusRisc() {
    const resposta = await fetch(
        `${API_URL}/programes/${ID_PROGRAMA}/objectius-risc`
    );

    const dades = await resposta.json();
    const llista = document.getElementById("objectiusRisc");

    llista.innerHTML = "";

    if (dades.length === 0) {
        llista.innerHTML = "<li>No hi ha objectius en risc.</li>";
        return;
    }

    dades.forEach(objectiu => {
        const item = document.createElement("li");
        item.textContent = `${objectiu.descripcio} - ${objectiu.progres}%`;
        llista.appendChild(item);
    });
}

async function carregarIA() {
    const contenidor = document.getElementById("resumIA");
    contenidor.innerHTML = "Generant resum...";

    const resposta = await fetch(
        `${API_URL}/ia/programes/${ID_PROGRAMA}/resum`
    );

    const dades = await resposta.json();
    const analisi = dades.analisiGenerada;

    contenidor.innerHTML = `
        <p><strong>Resum general:</strong> ${analisi.resumGeneral}</p>

        <p><strong>Aspectes positius:</strong></p>
        <ul>
            ${analisi.aspectesPositius.map(item => `<li>${item}</li>`).join("")}
        </ul>

        <p><strong>Riscos detectats:</strong></p>
        <ul>
            ${
                analisi.riscosDetectats.length > 0
                    ? analisi.riscosDetectats.map(item => `<li>${item}</li>`).join("")
                    : "<li>No s'han detectat riscos.</li>"
            }
        </ul>

        <p><strong>Recomanacions:</strong></p>
        <ul>
            ${analisi.recomanacions.map(item => `<li>${item}</li>`).join("")}
        </ul>
    `;
}

carregarDashboard();