import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

export async function renderP18AnaliticaReporting(app, navegar) {
  app.innerHTML = renderLayout("Analítica i reporting", `
    <div class="card">
      <h3>Selecciona un programa</h3>

      <div class="form-grid">
        <div>
          <label>Programa</label>
          <select id="programaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarAnalitica">Carregar analítica</button>
        </div>
      </div>
    </div>

    <div id="analiticaContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorProgrames();

  document.getElementById("btnCarregarAnalitica").addEventListener("click", async () => {
    const idPrograma = document.getElementById("programaSelect").value;
    await carregarAnalitica(idPrograma);
  });
}

async function carregarSelectorProgrames() {
  const select = document.getElementById("programaSelect");

  try {
    const programes = await apiGet("/programes");

    if (!programes.length) {
      select.innerHTML = `<option value="">No hi ha programes</option>`;
      document.getElementById("analiticaContainer").innerHTML = `
        <div class="card">
          <p>No hi ha programes disponibles.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = programes.map((programa) => `
      <option value="${programa.idPrograma}">
        ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
      </option>
    `).join("");

    await carregarAnalitica(programes[0].idPrograma);
  } catch (error) {
    document.getElementById("analiticaContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarAnalitica(idPrograma) {
  const container = document.getElementById("analiticaContainer");

  if (!idPrograma) {
    container.innerHTML = `
      <div class="card">
        <p>Selecciona un programa per veure l'analítica.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="card">
      <p>Carregant analítica...</p>
    </div>
  `;

  try {
    const [
      analisi,
      objectiusRisc,
      destacats,
      desviacio
    ] = await Promise.all([
      apiGet(`/programes/${idPrograma}/analisi`),
      apiGet(`/programes/${idPrograma}/objectius-risc`),
      apiGet(`/programes/${idPrograma}/participants-destacats`),
      apiGet(`/programes/${idPrograma}/participants-desviacio`)
    ]);

    const indicadorsImpacte = await apiGet(
      `/programes/${idPrograma}/indicadors-impacte`
    ).catch(() => []);

    container.innerHTML = `
      <div class="grid">
        <div class="card stat-card">
          <h3>Participants</h3>
          <p class="stat-number">${analisi.nombreParticipants ?? 0}</p>
          <p class="stat-subtitle">Participants del programa</p>
        </div>

        <div class="card stat-card">
          <h3>Progrés mitjà</h3>
          <p class="stat-number">${formatPercentatge(analisi.progresMitjaPrograma)}</p>
          <p class="stat-subtitle">${formatEstat(analisi.estatPrograma)}</p>
        </div>

        <div class="card stat-card">
          <h3>Objectius en risc</h3>
          <p class="stat-number">${objectiusRisc.length || 0}</p>
          <p class="stat-subtitle">Objectius detectats</p>
        </div>

        <div class="card stat-card">
          <h3>Participants amb desviació</h3>
          <p class="stat-number">${desviacio.length || 0}</p>
          <p class="stat-subtitle">Participants per revisar</p>
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Interpretació de l'analítica</h3>
        ${renderInterpretacioAnalitica(analisi, objectiusRisc, destacats, desviacio)}
      </div>

      <div class="card constructor-container">
        <h3>🎯 Validació de l'impacte real de la formació</h3>
        <p class="stat-subtitle">
          Aquest bloc respon a una pregunta diferent de l'anterior: no si els
          participants compleixen el pla, sinó si la formació ha canviat
          realment un indicador de negoci extern al sistema.
        </p>
        ${await renderImpacteFormacio(idPrograma, indicadorsImpacte)}
      </div>

      <div class="card constructor-container">
        <h3>Objectius en risc</h3>
        ${renderTaulaObjectius(objectiusRisc)}
      </div>

      <div class="grid two-cols constructor-container">
        <div class="card">
          <h3>Participants destacats</h3>
          ${renderTaulaParticipants(destacats, "destacat")}
        </div>

        <div class="card">
          <h3>Participants amb desviació</h3>
          ${renderTaulaParticipants(desviacio, "desviacio")}
        </div>
      </div>

      <div class="card constructor-container">
        <h3>Detall de participants</h3>
        ${renderTaulaParticipants(analisi.participants || [], "general")}
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderInterpretacioAnalitica(analisi, objectiusRisc, destacats, desviacio) {
  const progres = Number(analisi.progresMitjaPrograma || 0);
  const estat = analisi.estatPrograma || calcularEstat(progres);

  let missatge = "El programa encara no té prou dades registrades per extreure una conclusió sòlida.";

  if (progres >= 80) {
    missatge = "El programa mostra un nivell d'assoliment alt. La majoria de participants presenten una evolució positiva i el seguiment indica una bona consolidació dels objectius.";
  } else if (progres >= 40) {
    missatge = "El programa presenta un progrés intermedi. Hi ha avenços visibles, però encara existeixen objectius o participants que requereixen seguiment específic.";
  } else if (progres > 0) {
    missatge = "El programa es troba en una fase inicial o presenta un progrés baix. Es recomana revisar els objectius en risc i reforçar el seguiment dels participants amb desviació.";
  }

  return `
    <div class="list">
      <div class="list-item">
        <strong>Estat global</strong>
        <p>${formatEstat(estat)} · ${formatPercentatge(progres)}</p>
        <p>${missatge}</p>
      </div>

      <div class="list-item">
        <strong>Lectura dels riscos</strong>
        <p>${renderTextRiscos(objectiusRisc, desviacio)}</p>
      </div>

      <div class="list-item">
        <strong>Lectura dels resultats positius</strong>
        <p>${renderTextDestacats(destacats)}</p>
      </div>

      <div class="list-item">
        <strong>Recomanació operativa</strong>
        <p>${renderRecomanacio(progres, objectiusRisc, desviacio)}</p>
      </div>
    </div>
  `;
}

async function renderImpacteFormacio(idPrograma, indicadors) {
  if (!indicadors || !indicadors.length) {
    return `
      <div class="alert-block warning-alert">
        <h4>Cap indicador d'impacte definit</h4>
        <p>
          Aquest programa encara no té cap indicador de negoci (extern al
          pla d'acció) configurat. El progrés mostrat a dalt només indica
          el grau de compliment del pla, no si la formació ha tingut un
          efecte real. Es recomana definir almenys un indicador (p. ex.
          un KPI operatiu o de client) i registrar-ne un valor abans i
          després de la formació.
        </p>
      </div>
    `;
  }

  const blocs = await Promise.all(
    indicadors.map((indicador) => renderBlocIndicador(idPrograma, indicador))
  );

  return `<div class="list">${blocs.join("")}</div>`;
}

async function renderBlocIndicador(idPrograma, indicador) {
  const idIndicador = indicador.idIndicadorImpacte;

  try {
    const [deltes, correlacio] = await Promise.all([
      apiGet(`/indicadors-impacte/${idIndicador}/programes/${idPrograma}/deltes`),
      apiGet(`/indicadors-impacte/${idIndicador}/programes/${idPrograma}/correlacio`)
    ]);

    const deltesDisponibles = deltes.filter((d) => d.disponible);
    const deltaMitja = deltesDisponibles.length
      ? deltesDisponibles.reduce((acc, d) => acc + d.delta, 0) / deltesDisponibles.length
      : null;

    return `
      <div class="list-item">
        <strong>${indicador.nom}</strong>
        <p class="stat-subtitle">
          Font: ${indicador.fontDades} · Unitat: ${indicador.unitat}
        </p>

        <div class="grid two-cols">
          <div>
            <p><strong>Millora mitjana pre/post</strong></p>
            <p class="stat-number">${formatDelta(deltaMitja, indicador.unitat)}</p>
            <p class="stat-subtitle">
              ${deltesDisponibles.length} de ${deltes.length} participant(s) amb
              dada pre i post disponible
            </p>
          </div>

          <div>
            <p><strong>Correlació amb el compliment del pla</strong></p>
            <p class="stat-number">${formatCoeficient(correlacio.coeficientPearson)}</p>
            <p class="stat-subtitle">${correlacio.nParticipants} participant(s) analitzats</p>
          </div>
        </div>

        <p>${correlacio.interpretacio}</p>
      </div>
    `;
  } catch (error) {
    return `
      <div class="list-item">
        <strong>${indicador.nom}</strong>
        <p class="error-text">No s'ha pogut calcular l'impacte: ${error.message}</p>
      </div>
    `;
  }
}

function formatDelta(valor, unitat) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) {
    return "-";
  }

  const signe = valor > 0 ? "+" : "";

  return `${signe}${valor.toFixed(2)} ${unitat || ""}`.trim();
}

function formatCoeficient(r) {
  if (r === null || r === undefined || Number.isNaN(r)) {
    return "-";
  }

  return `r = ${r}`;
}

function renderTextRiscos(objectiusRisc, desviacio) {
  if ((!objectiusRisc || !objectiusRisc.length) && (!desviacio || !desviacio.length)) {
    return "No s'han detectat riscos rellevants en el programa.";
  }

  const parts = [];

  if (objectiusRisc.length) {
    parts.push(`${objectiusRisc.length} objectiu(s) en risc`);
  }

  if (desviacio.length) {
    parts.push(`${desviacio.length} participant(s) amb desviació`);
  }

  return `S'han detectat ${parts.join(" i ")}. Cal revisar-ne el detall i prioritzar accions de seguiment.`;
}

function renderTextDestacats(destacats) {
  if (!destacats || !destacats.length) {
    return "Encara no hi ha participants destacats identificats.";
  }

  return `${destacats.length} participant(s) mostren un rendiment destacat i poden servir com a referència per identificar bones pràctiques.`;
}

function renderRecomanacio(progres, objectiusRisc, desviacio) {
  if ((desviacio && desviacio.length) || (objectiusRisc && objectiusRisc.length)) {
    return "Prioritzar reunions de seguiment amb els participants amb desviació i revisar els KPI dels objectius en risc.";
  }

  if (progres >= 80) {
    return "Mantenir el ritme de seguiment i documentar les bones pràctiques detectades.";
  }

  return "Continuar registrant KPI i feedback per disposar d'una visió més completa de l'evolució del programa.";
}

function renderTaulaObjectius(items) {
  if (!items || !items.length) {
    return "<p>No hi ha objectius en risc.</p>";
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
        ${items.map((item) => `
          <tr>
            <td>${item.descripcio || item.titol || item.idObjectiu || "-"}</td>
            <td>${formatPercentatge(item.progres ?? item.progresObjectiu)}</td>
            <td>${formatEstat(item.estat || item.estatObjectiu)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderTaulaParticipants(items, tipus) {
  if (!items || !items.length) {
    return "<p>No hi ha dades disponibles.</p>";
  }

  return `
    <table>
      <thead>
        <tr>
          <th>Participant</th>
          <th>Progrés</th>
          <th>Estat</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item) => `
          <tr>
            <td>${nomParticipant(item)}</td>
            <td>${formatPercentatge(item.progres ?? item.progresPla ?? item.valor ?? item.desviacio)}</td>
            <td>${formatEstat(item.estat || item.estatPla || item.estatObjectiu || tipus)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function nomParticipant(item) {
  if (item.nom || item.cognoms) {
    return `${item.nom || ""} ${item.cognoms || ""}`.trim();
  }

  if (item.usuari) {
    return `${item.usuari.nom || ""} ${item.usuari.cognoms || ""}`.trim();
  }

  return `Usuari ${item.idUsuari || item.idParticipant || "-"}`;
}

function formatPercentatge(valor) {
  if (valor === undefined || valor === null || Number.isNaN(Number(valor))) {
    return "-";
  }

  return `${Math.round(Number(valor))}%`;
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