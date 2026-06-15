import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu } from "../state.js";

export async function renderP09DetallParticipant(app, navegar) {
  const programa = obtenirProgramaActiu();

  if (!programa) {
    app.innerHTML = renderLayout("Detall participant", `
      <div class="card">
        <h3>No hi ha cap programa seleccionat</h3>
        <p>Selecciona un programa abans de consultar el detall d'un participant.</p>
        <button class="btn" id="btnSeleccionarPrograma">Seleccionar programa</button>
      </div>
    `);

    activarLayoutEvents(navegar);

    document.getElementById("btnSeleccionarPrograma").addEventListener("click", () => {
      navegar("P02");
    });

    return;
  }

  app.innerHTML = renderLayout("Detall participant", `
    <div class="card">
      <h3>Selecciona un participant</h3>

      <div class="form-grid">
        <div>
          <label>Participant</label>
          <select id="participantSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarParticipant">Carregar</button>
        </div>
      </div>
    </div>

    <div id="participantContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorParticipants(programa);

  document.getElementById("btnCarregarParticipant").addEventListener("click", async () => {
    const idUsuari = document.getElementById("participantSelect").value;
    await carregarParticipant(programa.idPrograma, idUsuari);
  });
}

async function carregarSelectorParticipants(programa) {
  const select = document.getElementById("participantSelect");
  const participantSeleccionat = sessionStorage.getItem("idUsuariParticipantSeleccionat");

  try {
    const usuaris = await apiGet("/usuaris");
    const opcions = [];

    for (const usuari of usuaris) {
      const rols = await apiGet(`/usuaris/${usuari.idUsuari}/rols`);

      if ((rols.programesParticipant || []).includes(programa.idPrograma)) {
        opcions.push(usuari);
      }
    }

    if (!opcions.length) {
      select.innerHTML = `<option value="">No hi ha participants assignats</option>`;
      document.getElementById("participantContainer").innerHTML = `
        <div class="card">
          <p>No hi ha participants assignats a aquest programa.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = opcions.map((usuari) => `
      <option value="${usuari.idUsuari}">
        ${obtenirNomUsuari(usuari)}
      </option>
    `).join("");

    const participantInicial = opcions.find(
      (usuari) => String(usuari.idUsuari) === String(participantSeleccionat)
    ) || opcions[0];

    select.value = participantInicial.idUsuari;

    await carregarParticipant(programa.idPrograma, participantInicial.idUsuari);

    sessionStorage.removeItem("idUsuariParticipantSeleccionat");
  } catch (error) {
    select.innerHTML = `<option value="">Error carregant participants</option>`;
    document.getElementById("participantContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarParticipant(idPrograma, idUsuari) {
  const container = document.getElementById("participantContainer");

  if (!idUsuari) {
    container.innerHTML = `
      <div class="card">
        <p>Selecciona un participant per veure'n el detall.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="card">
      <p>Carregant detall del participant...</p>
    </div>
  `;

  try {
    const [seguiments, feedbacks] = await Promise.all([
      apiGet(`/programes/${idPrograma}/usuaris/${idUsuari}/seguiments`),
      apiGet(`/programes/${idPrograma}/participants/${idUsuari}/feedback`)
    ]);

    const progresMitja = calcularProgresMitja(seguiments);
    const estatGlobal = calcularEstat(progresMitja);

    container.innerHTML = `
      <div class="grid">
        <div class="card stat-card">
          <h3>Progrés mitjà</h3>
          <p class="stat-number">${formatPercentatge(progresMitja)}</p>
          <p class="stat-subtitle">${formatEstat(estatGlobal)}</p>
        </div>

        <div class="card stat-card">
          <h3>Seguiments</h3>
          <p class="stat-number">${seguiments.length || 0}</p>
          <p class="stat-subtitle">Objectius amb seguiment</p>
        </div>

        <div class="card stat-card">
          <h3>Feedback rebut</h3>
          <p class="stat-number">${feedbacks.length || 0}</p>
          <p class="stat-subtitle">Comentaris registrats</p>
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Progrés per objectiu</h3>
        ${renderSeguiments(seguiments)}
      </div>

      <div class="card constructor-container">
        <h3>Feedback</h3>
        ${renderFeedbacks(feedbacks)}
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderSeguiments(seguiments) {
  if (!seguiments || !seguiments.length) {
    return `<p>No hi ha seguiments disponibles.</p>`;
  }

  return `
    <table>
      <thead>
        <tr>
          <th>Objectiu</th>
          <th>Progrés</th>
          <th>Estat</th>
        </tr>
      </thead>
      <tbody>
        ${seguiments.map((seguiment) => {
          const progres = obtenirProgresSeguiment(seguiment);
          const estat = obtenirEstatSeguiment(seguiment, progres);

          return `
            <tr>
              <td>${obtenirNomObjectiu(seguiment)}</td>
              <td>${formatPercentatge(progres)}</td>
              <td>${formatEstat(estat)}</td>
            </tr>
          `;
        }).join("")}
      </tbody>
    </table>
  `;
}

function renderFeedbacks(feedbacks) {
  if (!feedbacks || !feedbacks.length) {
    return `<p>No hi ha feedback registrat.</p>`;
  }

  return feedbacks.map((feedback) => `
    <div class="list-item">
      <strong>${feedback.dataCreacio || feedback.data || "-"}</strong>
      <p>${feedback.comentari || feedback.text || "-"}</p>
      <p><strong>Validació:</strong> ${feedback.validacio ? "Validat" : "Pendent"}</p>
    </div>
  `).join("");
}

function obtenirProgresSeguiment(seguiment) {
  return (
    seguiment.progresCalculat ??
    seguiment.progres ??
    seguiment.progresObjectiu ??
    seguiment.percentatge ??
    0
  );
}

function obtenirEstatSeguiment(seguiment, progres) {
  return (
    seguiment.estatCalculat ??
    seguiment.estat ??
    seguiment.estatObjectiu ??
    calcularEstat(progres)
  );
}

function obtenirNomObjectiu(seguiment) {
  return (
    seguiment.descripcioObjectiu ||
    seguiment.objectiu ||
    seguiment.nomObjectiu ||
    seguiment.descripcio ||
    `Objectiu ${seguiment.idObjectiu || "-"}`
  );
}

function calcularProgresMitja(seguiments) {
  if (!seguiments || !seguiments.length) {
    return 0;
  }

  const valors = seguiments.map(obtenirProgresSeguiment);

  return Math.round(
    valors.reduce((total, valor) => total + Number(valor || 0), 0) / valors.length
  );
}

function calcularEstat(progres) {
  const valor = Number(progres || 0);

  if (valor >= 80) {
    return "assolit";
  }

  if (valor >= 40) {
    return "en_progres";
  }

  return "pendent";
}

function formatEstat(estat) {
  const labels = {
    assolit: "Assolit",
    en_progres: "En progrés",
    pendent: "Pendent",
    destacat: "Destacat",
    desviacio: "Desviació"
  };

  return labels[estat] || estat || "-";
}

function formatPercentatge(valor) {
  if (valor === undefined || valor === null || Number.isNaN(Number(valor))) {
    return "-";
  }

  return `${Math.round(Number(valor))}%`;
}

function obtenirNomUsuari(usuari) {
  const nomComplet = `${usuari.nom || ""} ${usuari.cognoms || ""}`.trim();

  if (nomComplet) {
    return `${nomComplet} — ${usuari.email || usuari.idUsuari}`;
  }

  return usuari.email || `Usuari ${usuari.idUsuari}`;
}