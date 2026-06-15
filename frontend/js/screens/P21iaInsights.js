import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, obtenirRolActiu } from "../state.js";

export async function renderP21IAInsights(app, navegar) {
  const rol = obtenirRolActiu();
  const programaActiu = obtenirProgramaActiu();

  app.innerHTML = renderLayout("IA Insights i resums executius", `
    <div class="card">
      <h3>Selecciona l'origen</h3>

      <div class="form-grid">
        <div>
          <label>Programa</label>
          <select id="programaSelect"></select>
        </div>

        <div>
          <label>Pla</label>
          <select id="plaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnResumPrograma">Resum programa</button>
        </div>

        <div class="form-actions">
          <button class="btn secondary" id="btnResumPla">Resum pla</button>
        </div>
      </div>
    </div>

    <div id="iaInsightsContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectors(rol, programaActiu);

  document.getElementById("programaSelect").addEventListener("change", async () => {
    await carregarPlans(document.getElementById("programaSelect").value);
  });

  document.getElementById("btnResumPrograma").addEventListener("click", async () => {
    await carregarResumPrograma(document.getElementById("programaSelect").value);
  });

  document.getElementById("btnResumPla").addEventListener("click", async () => {
    await carregarResumPla(document.getElementById("plaSelect").value);
  });
}

async function carregarSelectors(rol, programaActiu) {
  const programaSelect = document.getElementById("programaSelect");

  let programes = await apiGet("/programes");

  if (rol !== "administrador" && programaActiu) {
    programes = programes.filter(
      (programa) => String(programa.idPrograma) === String(programaActiu.idPrograma)
    );
  }

  if (!programes.length) {
    programaSelect.innerHTML = `<option value="">No hi ha programes</option>`;
    document.getElementById("iaInsightsContainer").innerHTML = `
      <div class="card">
        <p>No hi ha programes disponibles per generar insights.</p>
      </div>
    `;
    return;
  }

  programaSelect.innerHTML = programes.map((programa) => `
    <option value="${programa.idPrograma}">
      ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
    </option>
  `).join("");

  await carregarPlans(programes[0].idPrograma);
  await carregarResumPrograma(programes[0].idPrograma);
}

async function carregarPlans(idPrograma) {
  const plaSelect = document.getElementById("plaSelect");

  try {
    const plans = await apiGet(`/programes/${idPrograma}/plans`);

    if (!plans.length) {
      plaSelect.innerHTML = `<option value="">No hi ha plans</option>`;
      return;
    }

    plaSelect.innerHTML = plans.map((pla) => `
      <option value="${pla.idPla}">
        ${pla.titol || pla.nom || `Pla ${pla.idPla}`}
      </option>
    `).join("");
  } catch {
    plaSelect.innerHTML = `<option value="">Error carregant plans</option>`;
  }
}

async function carregarResumPrograma(idPrograma) {
  const container = document.getElementById("iaInsightsContainer");

  if (!idPrograma) {
    container.innerHTML = `<p>No hi ha cap programa seleccionat.</p>`;
    return;
  }

  container.innerHTML = `
    <div class="card">
      <p>Generant anàlisi IA del programa...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(`/ia/programes/${idPrograma}/resum`);
    renderRespostaPrograma(container, resposta);
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarResumPla(idPla) {
  const container = document.getElementById("iaInsightsContainer");

  if (!idPla) {
    container.innerHTML = `<p>No hi ha cap pla seleccionat.</p>`;
    return;
  }

  container.innerHTML = `
    <div class="card">
      <p>Generant anàlisi IA del pla...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(`/ia/plans/${idPla}/resum`);
    renderRespostaPla(container, resposta);
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderRespostaPrograma(container, resposta) {
  const dades = resposta.analisiGenerada || resposta;

  if (dades.error) {
    container.innerHTML = renderErrorIA(dades);
    return;
  }

  container.innerHTML = `
    <div class="card dashboard-wide">
      <h3>Resum executiu del programa</h3>
      <p>${dades.resumExecutiu || dades.resumGeneral || "No hi ha resum disponible."}</p>
    </div>

    <div class="card dashboard-wide">
      <h3>Diagnòstic</h3>
      <p>${dades.diagnostic || "No hi ha diagnòstic disponible."}</p>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Indicadors clau</h3>
        ${renderIndicadors(dades.indicadorsClau)}
      </div>

      <div class="card">
        <h3>Riscos detectats</h3>
        ${renderRiscos(dades.riscos || dades.riscosDetectats)}
      </div>

      <div class="card">
        <h3>Recomanacions</h3>
        ${renderRecomanacions(dades.recomanacions)}
      </div>
    </div>

    <div class="card dashboard-wide">
      <h3>Aspectes positius</h3>
      ${renderLlista(dades.aspectesPositius)}
    </div>
  `;
}

function renderRespostaPla(container, resposta) {
  const dades = resposta.analisiGenerada || resposta;

  if (dades.error) {
    container.innerHTML = renderErrorIA(dades);
    return;
  }

  container.innerHTML = `
    <div class="card dashboard-wide">
      <h3>Avaluació general del pla</h3>
      <p>${dades.avaluacioGeneral || dades.estatGeneral || "No hi ha avaluació disponible."}</p>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Fortaleses</h3>
        ${renderLlista(dades.fortaleses || dades.objectiusAvancats)}
      </div>

      <div class="card">
        <h3>Febleses</h3>
        ${renderLlista(dades.febleses || dades.objectiusAtencio)}
      </div>

      <div class="card">
        <h3>Riscos</h3>
        ${renderLlista(dades.riscos)}
      </div>

      <div class="card">
        <h3>Millores recomanades</h3>
        ${renderLlista(dades.milloresRecomanades || dades.recomanacions)}
      </div>
    </div>

    ${dades.recomanacioFinal ? `
      <div class="card dashboard-wide">
        <h3>Recomanació final</h3>
        <p>${dades.recomanacioFinal}</p>
      </div>
    ` : ""}
  `;
}

function renderIndicadors(indicadors) {
  if (!indicadors || !indicadors.length) {
    return `<p>No hi ha indicadors clau disponibles.</p>`;
  }

  return `
    <div class="list">
      ${indicadors.map((indicador) => `
        <div class="list-item">
          <strong>${indicador.nom || "Indicador"}</strong>
          <p><strong>Valor:</strong> ${indicador.valor ?? "-"}</p>
          <p>${indicador.interpretacio || ""}</p>
        </div>
      `).join("")}
    </div>
  `;
}

function renderRiscos(riscos) {
  if (!riscos || !riscos.length) {
    return `<p>No s'han detectat riscos rellevants.</p>`;
  }

  return `
    <div class="list">
      ${riscos.map((risc) => {
        if (typeof risc === "string") {
          return `<div class="list-item"><p>${risc}</p></div>`;
        }

        return `
          <div class="list-item">
            <strong>${risc.titol || "Risc detectat"}</strong>
            <p><strong>Nivell:</strong> ${formatPrioritat(risc.nivell)}</p>
            <p>${risc.explicacio || ""}</p>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderRecomanacions(recomanacions) {
  if (!recomanacions || !recomanacions.length) {
    return `<p>No hi ha recomanacions disponibles.</p>`;
  }

  return `
    <div class="list">
      ${recomanacions.map((recomanacio) => {
        if (typeof recomanacio === "string") {
          return `<div class="list-item"><p>${recomanacio}</p></div>`;
        }

        return `
          <div class="list-item">
            <strong>${recomanacio.accio || recomanacio.titol || "Recomanació"}</strong>
            <p><strong>Prioritat:</strong> ${formatPrioritat(recomanacio.prioritat)}</p>
            <p>${recomanacio.impacteEsperat || recomanacio.explicacio || ""}</p>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderLlista(items) {
  if (!items || !items.length) {
    return `<p>No hi ha informació disponible.</p>`;
  }

  return `
    <ul>
      ${items.map((item) => `
        <li>${typeof item === "string" ? item : formatObjecte(item)}</li>
      `).join("")}
    </ul>
  `;
}

function renderErrorIA(error) {
  return `
    <div class="card">
      <h3>Servei IA no disponible</h3>
      <p class="error-text">${error.missatge || "No s'ha pogut generar la resposta IA."}</p>
    </div>
  `;
}

function formatPrioritat(valor) {
  const labels = {
    baix: "Baix",
    baixa: "Baixa",
    mitja: "Mitjana",
    mitjana: "Mitjana",
    alt: "Alt",
    alta: "Alta"
  };

  return labels[valor] || valor || "-";
}

function formatObjecte(objecte) {
  if (!objecte || typeof objecte !== "object") {
    return objecte || "-";
  }

  return Object.values(objecte)
    .filter((valor) => valor !== null && valor !== undefined && valor !== "")
    .join(" — ");
}