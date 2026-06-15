import { apiGet, apiPost } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

let propostaActual = null;
let programaSeleccionat = null;

export async function renderP20GeneradorIAPlans(app, navegar) {
  propostaActual = null;
  programaSeleccionat = null;

  app.innerHTML = renderLayout("Generador IA de plans", `
    <div class="card">
      <h3>Generar proposta de pla amb IA</h3>
      <p>
        La IA analitza el programa seleccionat i proposa un pla d'acció amb objectius,
        accions i KPI. La proposta es pot revisar abans d'afegir-la a la biblioteca.
      </p>

      <div class="form-grid">
        <div>
          <label>Programa</label>
          <select id="programaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnGenerarProposta">Generar proposta IA</button>
        </div>
      </div>
    </div>

    <div id="generadorContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorProgrames();

  document.getElementById("btnGenerarProposta").addEventListener("click", async () => {
    const idPrograma = document.getElementById("programaSelect").value;
    await generarProposta(idPrograma);
  });
}

async function carregarSelectorProgrames() {
  const select = document.getElementById("programaSelect");

  try {
    const programes = await apiGet("/programes");

    if (!programes.length) {
      select.innerHTML = `<option value="">No hi ha programes</option>`;
      document.getElementById("generadorContainer").innerHTML = `
        <div class="card">
          <p>No hi ha programes disponibles per generar propostes.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = programes.map((programa) => `
      <option value="${programa.idPrograma}">
        ${programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`}
      </option>
    `).join("");

    await generarProposta(programes[0].idPrograma);
  } catch (error) {
    document.getElementById("generadorContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function generarProposta(idPrograma) {
  const container = document.getElementById("generadorContainer");

  if (!idPrograma) {
    container.innerHTML = `
      <div class="card">
        <p>Selecciona un programa per generar una proposta.</p>
      </div>
    `;
    return;
  }

  propostaActual = null;
  programaSeleccionat = Number(idPrograma);

  container.innerHTML = `
    <div class="card">
      <p>Generant proposta de pla amb IA...</p>
    </div>
  `;

  try {
    const resposta = await apiGet(`/ia/programes/${idPrograma}/proposta-pla`);

    propostaActual = resposta.proposta || resposta;

    renderProposta(container, propostaActual);
  } catch (error) {
    container.innerHTML = `
      <div class="card">
        <p class="error-text">${error.message}</p>
      </div>
    `;
  }
}

function renderProposta(container, proposta) {
  if (!proposta) {
    container.innerHTML = `
      <div class="card">
        <p>No s'ha pogut generar cap proposta.</p>
      </div>
    `;
    return;
  }

  if (proposta.error) {
    container.innerHTML = `
      <div class="card">
        <h3>Servei IA no disponible</h3>
        <p class="error-text">${proposta.missatge || "No s'ha pogut generar la proposta."}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="card dashboard-wide">
      <h3>${proposta.titol || "Pla d'acció proposat"}</h3>
      <p>${proposta.descripcio || "Proposta generada automàticament a partir de l'anàlisi del programa."}</p>

      <div class="form-actions">
        <button class="btn" id="btnAfegirBiblioteca">
          Afegir proposta a la biblioteca
        </button>
      </div>
    </div>

    <div class="card dashboard-wide">
      <h3>Objectius proposats</h3>
      ${renderObjectius(proposta.objectius)}
    </div>
  `;

  document.getElementById("btnAfegirBiblioteca").addEventListener("click", afegirPropostaBiblioteca);
}

function renderObjectius(objectius) {
  if (!objectius || !objectius.length) {
    return `<p>No hi ha objectius proposats.</p>`;
  }

  return `
    <div class="list">
      ${objectius.map((objectiu, indexObjectiu) => `
        <div class="list-item">
          <h4>Objectiu ${indexObjectiu + 1}: ${objectiu.descripcio || objectiu.nom || "Sense descripció"}</h4>
          <p><strong>Valor:</strong> ${objectiu.valor ?? 100}</p>

          <div class="list">
            ${renderAccions(objectiu.accions)}
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderAccions(accions) {
  if (!accions || !accions.length) {
    return `<p>No hi ha accions proposades.</p>`;
  }

  return accions.map((accio, indexAccio) => `
    <div class="list-item">
      <strong>Acció ${indexAccio + 1}: ${accio.titol || accio.nom || "Sense títol"}</strong>
      <p>${accio.descripcio || ""}</p>

      <h5>KPI proposats</h5>
      ${renderKPIs(accio.kpis)}
    </div>
  `).join("");
}

function renderKPIs(kpis) {
  if (!kpis || !kpis.length) {
    return `<p>No hi ha KPI proposats.</p>`;
  }

  return `
    <table>
      <thead>
        <tr>
          <th>KPI</th>
          <th>Tipus</th>
          <th>Periodicitat</th>
          <th>Objectiu</th>
        </tr>
      </thead>
      <tbody>
        ${kpis.map((kpi) => `
          <tr>
            <td>${kpi.nom || "KPI sense nom"}</td>
            <td>${formatTipusKPI(kpi.tipus)}</td>
            <td>${kpi.periodicitat || "setmanal"}</td>
            <td>${kpi.valorObjectiu ?? "-"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function afegirPropostaBiblioteca() {
  if (!propostaActual || !programaSeleccionat) {
    alert("No hi ha cap proposta disponible per afegir.");
    return;
  }

  const confirmar = confirm(
    "Vols afegir aquesta proposta a la biblioteca de plans? Es crearà el pla amb els seus objectius, accions i KPI."
  );

  if (!confirmar) {
    return;
  }

  const boto = document.getElementById("btnAfegirBiblioteca");
  boto.disabled = true;
  boto.textContent = "Afegint proposta...";

  try {
    const plaCreat = await apiPost("/plans", {
      idPrograma: programaSeleccionat,
      titol: propostaActual.titol || "Pla d'acció generat amb IA",
      descripcio: propostaActual.descripcio || "Pla generat automàticament amb suport d'intel·ligència artificial."
    });

    for (const objectiu of propostaActual.objectius || []) {
      const objectiuCreat = await apiPost("/objectius", {
        idPla: plaCreat.idPla,
        descripcio: objectiu.descripcio || objectiu.nom || "Objectiu generat amb IA",
        valor: objectiu.valor ?? 100
      });

      for (const accio of objectiu.accions || []) {
        const accioCreat = await apiPost("/accions", {
          idObjectiu: objectiuCreat.idObjectiu,
          titol: accio.titol || accio.nom || "Acció generada amb IA",
          descripcio: accio.descripcio || "",
          dataInici: accio.dataInici || null,
          dataFi: accio.dataFi || null
        });

        for (const kpi of accio.kpis || []) {
          const kpiNormalitzat = normalitzarKPI(kpi);

          await apiPost("/kpis", {
            idAccio: accioCreat.idAccio,
            nom: kpiNormalitzat.nom,
            descripcio: kpiNormalitzat.descripcio,
            periodicitat: kpiNormalitzat.periodicitat,
            tipus: kpiNormalitzat.tipus,
            orientacio: kpiNormalitzat.orientacio,
            valorMinim: kpiNormalitzat.valorMinim,
            valorMaxim: kpiNormalitzat.valorMaxim,
            valorObjectiu: kpiNormalitzat.valorObjectiu
          });
        }
      }
    }

    boto.textContent = "Proposta afegida";
    alert("La proposta s'ha afegit correctament a la biblioteca de plans.");
  } catch (error) {
    boto.disabled = false;
    boto.textContent = "Afegir proposta a la biblioteca";
    alert(error.message);
  }
}

function normalitzarKPI(kpi) {
  const tipus = normalitzarTipus(kpi.tipus);

  const resultat = {
    nom: kpi.nom || "KPI generat amb IA",
    descripcio: kpi.descripcio || "",
    periodicitat: kpi.periodicitat || "setmanal",
    tipus,
    orientacio: normalitzarOrientacio(kpi.orientacio),
    valorMinim: parseNullableNumber(kpi.valorMinim),
    valorMaxim: parseNullableNumber(kpi.valorMaxim),
    valorObjectiu: parseNullableNumber(kpi.valorObjectiu)
  };

  if (resultat.tipus === "boolea") {
    resultat.valorMinim = 0;
    resultat.valorMaxim = 1;
    resultat.valorObjectiu = 1;
    resultat.orientacio = "major_millor";
  }

  if (resultat.tipus === "percentatge") {
    resultat.valorMinim = 0;
    resultat.valorMaxim = 100;
    resultat.valorObjectiu = resultat.valorObjectiu ?? 80;
  }

  if (resultat.tipus === "escala") {
    resultat.valorMinim = resultat.valorMinim ?? 1;
    resultat.valorMaxim = resultat.valorMaxim ?? 5;
    resultat.valorObjectiu = resultat.valorObjectiu ?? 4;
  }

  if (resultat.tipus === "numeric") {
    resultat.valorMinim = resultat.valorMinim ?? 0;
    resultadoValorMaximNumeric(resultat);
    resultat.valorObjectiu = resultat.valorObjectiu ?? resultat.valorMaxim;
  }

  return resultat;
}

function resultadoValorMaximNumeric(kpi) {
  if (kpi.valorMaxim === null || kpi.valorMaxim === undefined) {
    kpi.valorMaxim = kpi.valorObjectiu ?? 10;
  }
}

function normalitzarTipus(tipus) {
  const valor = String(tipus || "").toLowerCase();

  if (["numeric", "numèric", "numerico", "number"].includes(valor)) {
    return "numeric";
  }

  if (["percentatge", "porcentaje", "percent", "percentage"].includes(valor)) {
    return "percentatge";
  }

  if (["escala", "scale"].includes(valor)) {
    return "escala";
  }

  if (["boolea", "booleà", "boolean", "si_no", "sí/no", "si/no"].includes(valor)) {
    return "boolea";
  }

  return "numeric";
}

function normalitzarOrientacio(orientacio) {
  const valor = String(orientacio || "").toLowerCase();

  if (["menor_millor", "menor es millor", "menor és millor", "lower_is_better"].includes(valor)) {
    return "menor_millor";
  }

  return "major_millor";
}

function parseNullableNumber(valor) {
  if (valor === "" || valor === null || valor === undefined) {
    return null;
  }

  const numero = Number(valor);
  return Number.isNaN(numero) ? null : numero;
}

function formatTipusKPI(tipus) {
  const labels = {
    numeric: "Numèric",
    percentatge: "Percentatge",
    escala: "Escala",
    boolea: "Sí / No"
  };

  return labels[normalitzarTipus(tipus)] || tipus || "-";
}