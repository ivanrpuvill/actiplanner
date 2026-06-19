import { apiGet, apiPost, apiPut } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";

let plaActual = null;

export async function renderP17ConstructorPlans(app, navegar) {
  app.innerHTML = renderLayout("Constructor de plans", `
    <div class="card">
      <h3>Selecciona un pla d'acció</h3>

      <div class="form-grid">
        <div>
          <label>Pla</label>
          <select id="plaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarPla">Carregar pla</button>
        </div>
      </div>
    </div>

    <div id="constructorContainer" class="constructor-container">
      <div class="card">Carregant plans...</div>
    </div>
  `);

  activarLayoutEvents(navegar);

  await carregarSelectorPlans();

  document.getElementById("btnCarregarPla").addEventListener("click", async () => {
    const idPla = Number(document.getElementById("plaSelect").value);
    await carregarPla(idPla);
  });
}

async function carregarSelectorPlans() {
  const select = document.getElementById("plaSelect");

  try {
    const programes = await apiGet("/programes");
    const plans = [];

    for (const programa of programes) {
      const plansPrograma = await apiGet(`/programes/${programa.idPrograma}/plans`);
      plansPrograma.forEach((pla) => {
        plans.push({
          ...pla,
          nomPrograma: programa.nom || programa.nomPrograma || `Programa ${programa.idPrograma}`
        });
      });
    }

    if (!plans.length) {
      select.innerHTML = `<option value="">No hi ha plans disponibles</option>`;
      document.getElementById("constructorContainer").innerHTML = `
        <div class="card">
          <p>No hi ha cap pla d'acció creat.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = plans.map((pla) => `
      <option value="${pla.idPla}">
        ${pla.titol || `Pla ${pla.idPla}`} — ${pla.nomPrograma}
      </option>
    `).join("");

    await carregarPla(plans[0].idPla);
  } catch (error) {
    document.getElementById("constructorContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarPla(idPla) {
  const container = document.getElementById("constructorContainer");

  container.innerHTML = `
    <div class="card">
      <p>Carregant estructura del pla...</p>
    </div>
  `;

  try {
    plaActual = await apiGet(`/plans/${idPla}`);
    renderConstructor();
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderConstructor() {
  const container = document.getElementById("constructorContainer");

  container.innerHTML = `
    <div class="card">
      <h3>${plaActual.titol || `Pla ${plaActual.idPla}`}</h3>
      <p>Constructor d'objectius, accions i KPI del pla seleccionat.</p>
    </div>

    <div class="grid constructor-container">
      <div class="card">
        <h3>Nou objectiu</h3>

        <div class="form-grid">
          <div>
            <label>Descripció</label>
            <input id="objectiuDescripcio" type="text" placeholder="Ex. Millorar la comunicació interna">
          </div>

          <div>
            <label>Valor / pes</label>
            <input id="objectiuValor" type="number" step="0.01" value="100">
          </div>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCrearObjectiu">Afegir objectiu</button>
        </div>
      </div>

      <div class="card">
        <h3>Nova acció</h3>

        <div class="form-grid">
          <div>
            <label>Objectiu</label>
            <select id="accioObjectiuSelect">
              ${renderOptionsObjectius()}
            </select>
          </div>

          <div>
            <label>Títol</label>
            <input id="accioTitol" type="text" placeholder="Ex. Fer reunions setmanals">
          </div>

          <div>
            <label>Descripció</label>
            <input id="accioDescripcio" type="text" placeholder="Descripció de l'acció">
          </div>

          <div>
            <label>Data inici</label>
            <input id="accioDataInici" type="date">
          </div>

          <div>
            <label>Data fi</label>
            <input id="accioDataFi" type="date">
          </div>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCrearAccio">Afegir acció</button>
        </div>
      </div>

      <div class="card">
        <h3>Nou KPI</h3>

        <div class="form-grid">
          <div>
            <label>Acció</label>
            <select id="kpiAccioSelect">
              ${renderOptionsAccions()}
            </select>
          </div>

          <div>
            <label>Nom</label>
            <input id="kpiNom" type="text" placeholder="Ex. Nombre de reunions realitzades">
          </div>

          <div>
            <label>Descripció</label>
            <input id="kpiDescripcio" type="text" placeholder="Què mesura aquest indicador">
          </div>

          <div>
            <label>Periodicitat</label>
            <select id="kpiPeriodicitat">
              <option value="diari">Diari</option>
              <option value="setmanal">Setmanal</option>
              <option value="mensual">Mensual</option>
            </select>
          </div>

          <div>
            <label>Tipus de càlcul</label>
            <select id="kpiTipusCalcul">
              <option value="acumulat">Acumulat (suma tots els registres)</option>
              <option value="mitjana">Mitjana (mitjana de tots els registres)</option>
              <option value="ultim">Últim valor (només el registre més recent)</option>
            </select>
            <p id="kpiAjudaCalcul" class="muted-text"></p>
          </div>

          <div>
            <label>Tipus de KPI</label>
            <select id="kpiTipus">
              <option value="numeric">Numèric</option>
              <option value="percentatge">Percentatge</option>
              <option value="escala">Escala</option>
              <option value="boolea">Sí / No</option>
            </select>
          </div>

          <div>
            <label>Orientació</label>
            <select id="kpiOrientacio">
              <option value="major_millor">Com més alt, millor</option>
              <option value="menor_millor">Com més baix, millor</option>
            </select>
          </div>

          <div>
            <label>Valor mínim</label>
            <input id="kpiValorMinim" type="number" step="0.01" value="0">
          </div>

          <div>
            <label>Valor màxim</label>
            <input id="kpiValorMaxim" type="number" step="0.01" placeholder="Ex. 100">
          </div>

          <div>
            <label>Valor objectiu</label>
            <input id="kpiValorObjectiu" type="number" step="0.01" placeholder="Ex. 80">
          </div>
        </div>

        <p id="kpiAjuda" class="muted-text">
          Defineix com s'ha d'interpretar el KPI per calcular el percentatge d'assoliment.
        </p>

        <div class="form-actions">
          <button class="btn" id="btnCrearKPI">Afegir KPI</button>
        </div>
      </div>
    </div>

    <div class="card constructor-container">
      <h3>Estructura actual del pla</h3>
      ${renderEstructuraPla()}
    </div>

    <div class="card constructor-container">
      <h3>Elements desactivats</h3>
      <div id="elementsDesactivatsContainer">Carregant...</div>
    </div>
  `;

  activarEventsConstructor();
  carregarElementsDesactivats();
}

function activarEventsConstructor() {
  document.getElementById("btnCrearObjectiu").addEventListener("click", crearObjectiu);
  document.getElementById("btnCrearAccio").addEventListener("click", crearAccio);
  document.getElementById("btnCrearKPI").addEventListener("click", crearKPI);

  document.getElementById("kpiTipus").addEventListener("change", actualitzarAjudaKPI);
  document.getElementById("kpiTipusCalcul").addEventListener("change", actualitzarAjudaCalcul);
  actualitzarAjudaKPI();
  actualitzarAjudaCalcul();

  document.querySelectorAll(".btn-editar-objectiu").forEach((button) => {
    button.addEventListener("click", () => obrirEdicioObjectiu(Number(button.dataset.id)));
  });
  document.querySelectorAll(".btn-desactivar-objectiu").forEach((button) => {
    button.addEventListener("click", () => canviarEstatObjectiu(Number(button.dataset.id), false));
  });

  document.querySelectorAll(".btn-editar-accio").forEach((button) => {
    button.addEventListener("click", () => obrirEdicioAccio(Number(button.dataset.id)));
  });
  document.querySelectorAll(".btn-desactivar-accio").forEach((button) => {
    button.addEventListener("click", () => canviarEstatAccio(Number(button.dataset.id), false));
  });

  document.querySelectorAll(".btn-editar-kpi").forEach((button) => {
    button.addEventListener("click", () => obrirEdicioKPI(Number(button.dataset.id)));
  });
  document.querySelectorAll(".btn-desactivar-kpi").forEach((button) => {
    button.addEventListener("click", () => canviarEstatKPI(Number(button.dataset.id), false));
  });
}

async function crearObjectiu() {
  const payload = {
    idPla: plaActual.idPla,
    descripcio: document.getElementById("objectiuDescripcio").value.trim(),
    valor: parseNullableNumber(document.getElementById("objectiuValor").value) ?? 100
  };

  if (!payload.descripcio) {
    alert("Cal indicar una descripció per a l'objectiu.");
    return;
  }

  await apiPost("/objectius", payload);
  await carregarPla(plaActual.idPla);
}

async function crearAccio() {
  const payload = {
    idObjectiu: Number(document.getElementById("accioObjectiuSelect").value),
    titol: document.getElementById("accioTitol").value.trim(),
    descripcio: document.getElementById("accioDescripcio").value.trim(),
    dataInici: document.getElementById("accioDataInici").value || null,
    dataFi: document.getElementById("accioDataFi").value || null
  };

  if (!payload.idObjectiu) {
    alert("Cal seleccionar un objectiu.");
    return;
  }

  if (!payload.titol) {
    alert("Cal indicar un títol per a l'acció.");
    return;
  }

  await apiPost("/accions", payload);
  await carregarPla(plaActual.idPla);
}

async function crearKPI() {
  const tipus = document.getElementById("kpiTipus").value;

  const payload = {
    idAccio: Number(document.getElementById("kpiAccioSelect").value),
    nom: document.getElementById("kpiNom").value.trim(),
    descripcio: document.getElementById("kpiDescripcio").value.trim(),
    periodicitat: document.getElementById("kpiPeriodicitat").value,
    tipusCalcul: document.getElementById("kpiTipusCalcul").value,
    tipus,
    orientacio: document.getElementById("kpiOrientacio").value,
    valorMinim: parseNullableNumber(document.getElementById("kpiValorMinim").value),
    valorMaxim: parseNullableNumber(document.getElementById("kpiValorMaxim").value),
    valorObjectiu: parseNullableNumber(document.getElementById("kpiValorObjectiu").value)
  };

  if (!payload.idAccio) {
    alert("Cal seleccionar una acció.");
    return;
  }

  if (!payload.nom) {
    alert("Cal indicar un nom per al KPI.");
    return;
  }

  normalitzarValorsKPI(payload);

  const error = validarKPI(payload);
  if (error) {
    alert(error);
    return;
  }

  await apiPost("/kpis", payload);
  await carregarPla(plaActual.idPla);
}

async function canviarEstatObjectiu(idObjectiu, nouEstat) {
  await apiPut(`/objectius/${idObjectiu}`, { actiu: nouEstat });
  await carregarPla(plaActual.idPla);
}

async function canviarEstatAccio(idAccio, nouEstat) {
  await apiPut(`/accions/${idAccio}`, { actiu: nouEstat });
  await carregarPla(plaActual.idPla);
}

async function canviarEstatKPI(idKPI, nouEstat) {
  await apiPut(`/kpis/${idKPI}`, { actiu: nouEstat });
  await carregarPla(plaActual.idPla);
}

async function obrirEdicioObjectiu(idObjectiu) {
  const objectiu = await apiGet(`/objectius/${idObjectiu}`);

  const descripcioNova = prompt("Descripció de l'objectiu:", objectiu.descripcio || "");
  if (descripcioNova === null) {
    return;
  }

  const valorNou = prompt("Valor / pes de l'objectiu:", objectiu.valor ?? "100");
  if (valorNou === null) {
    return;
  }

  await apiPut(`/objectius/${idObjectiu}`, {
    descripcio: descripcioNova.trim(),
    valor: parseNullableNumber(valorNou) ?? objectiu.valor
  });

  await carregarPla(plaActual.idPla);
}

async function obrirEdicioAccio(idAccio) {
  const accio = await apiGet(`/accions/${idAccio}`);

  const titolNou = prompt("Títol de l'acció:", accio.titol || "");
  if (titolNou === null) {
    return;
  }

  const descripcioNova = prompt("Descripció de l'acció:", accio.descripcio || "");
  if (descripcioNova === null) {
    return;
  }

  const dataIniciNova = prompt("Data d'inici (AAAA-MM-DD):", accio.dataInici || "");
  if (dataIniciNova === null) {
    return;
  }

  const dataFiNova = prompt("Data de fi (AAAA-MM-DD):", accio.dataFi || "");
  if (dataFiNova === null) {
    return;
  }

  await apiPut(`/accions/${idAccio}`, {
    titol: titolNou.trim(),
    descripcio: descripcioNova.trim(),
    dataInici: dataIniciNova.trim() || null,
    dataFi: dataFiNova.trim() || null
  });

  await carregarPla(plaActual.idPla);
}

async function obrirEdicioKPI(idKPI) {
  const kpi = await apiGet(`/kpis/${idKPI}`);

  const nomNou = prompt("Nom del KPI:", kpi.nom || "");
  if (nomNou === null) {
    return;
  }

  const descripcioNova = prompt("Descripció del KPI:", kpi.descripcio || "");
  if (descripcioNova === null) {
    return;
  }

  const valorObjectiuNou = prompt("Valor objectiu:", kpi.valorObjectiu ?? "");
  if (valorObjectiuNou === null) {
    return;
  }

  const payload = {
    nom: nomNou.trim(),
    descripcio: descripcioNova.trim(),
    valorObjectiu: parseNullableNumber(valorObjectiuNou)
  };

  const error = validarKPI({ ...kpi, ...payload });
  if (error) {
    alert(error);
    return;
  }

  await apiPut(`/kpis/${idKPI}`, payload);
  await carregarPla(plaActual.idPla);
}

async function carregarElementsDesactivats() {
  const container = document.getElementById("elementsDesactivatsContainer");

  try {
    const objectius = await apiGet(`/plans/${plaActual.idPla}/objectius`);
    const objectiusInactius = objectius.filter((objectiu) => objectiu.actiu === false);

    const accionsInactivesPerObjectiu = await Promise.all(
      objectius.map((objectiu) => apiGet(`/objectius/${objectiu.idObjectiu}/accions`))
    );
    const totesLesAccions = accionsInactivesPerObjectiu.flat();
    const accionsInactives = totesLesAccions.filter((accio) => accio.actiu === false);

    const kpisInactiusPerAccio = await Promise.all(
      totesLesAccions.map((accio) => apiGet(`/accions/${accio.idAccio}/kpis`))
    );
    const kpisInactius = kpisInactiusPerAccio.flat().filter((kpi) => kpi.actiu === false);

    if (!objectiusInactius.length && !accionsInactives.length && !kpisInactius.length) {
      container.innerHTML = "<p>No hi ha cap element desactivat en aquest pla.</p>";
      return;
    }

    container.innerHTML = `
      ${objectiusInactius.length ? `
        <h4>Objectius</h4>
        <table>
          <thead><tr><th>Descripció</th><th></th></tr></thead>
          <tbody>
            ${objectiusInactius.map((objectiu) => `
              <tr>
                <td>${objectiu.descripcio}</td>
                <td><button class="btn secondary small btn-reactivar-objectiu" data-id="${objectiu.idObjectiu}">Activar</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      ` : ""}

      ${accionsInactives.length ? `
        <h4>Accions</h4>
        <table>
          <thead><tr><th>Títol</th><th></th></tr></thead>
          <tbody>
            ${accionsInactives.map((accio) => `
              <tr>
                <td>${accio.titol}</td>
                <td><button class="btn secondary small btn-reactivar-accio" data-id="${accio.idAccio}">Activar</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      ` : ""}

      ${kpisInactius.length ? `
        <h4>KPI</h4>
        <table>
          <thead><tr><th>Nom</th><th></th></tr></thead>
          <tbody>
            ${kpisInactius.map((kpi) => `
              <tr>
                <td>${kpi.nom}</td>
                <td><button class="btn secondary small btn-reactivar-kpi" data-id="${kpi.idKPI}">Activar</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      ` : ""}
    `;

    container.querySelectorAll(".btn-reactivar-objectiu").forEach((button) => {
      button.addEventListener("click", () => canviarEstatObjectiu(Number(button.dataset.id), true));
    });
    container.querySelectorAll(".btn-reactivar-accio").forEach((button) => {
      button.addEventListener("click", () => canviarEstatAccio(Number(button.dataset.id), true));
    });
    container.querySelectorAll(".btn-reactivar-kpi").forEach((button) => {
      button.addEventListener("click", () => canviarEstatKPI(Number(button.dataset.id), true));
    });
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function normalitzarValorsKPI(kpi) {
  if (kpi.tipus === "boolea") {
    kpi.valorMinim = 0;
    kpi.valorMaxim = 1;
    kpi.valorObjectiu = 1;
    kpi.orientacio = "major_millor";
  }

  if (kpi.tipus === "percentatge") {
    kpi.valorMinim = 0;
    kpi.valorMaxim = 100;
    kpi.valorObjectiu = kpi.valorObjectiu ?? 100;
  }

  if (kpi.tipus === "escala") {
    kpi.valorMinim = kpi.valorMinim ?? 1;
    kpi.valorMaxim = kpi.valorMaxim ?? 5;
    kpi.valorObjectiu = kpi.valorObjectiu ?? kpi.valorMaxim;
  }

  if (kpi.tipus === "numeric") {
    kpi.valorMinim = kpi.valorMinim ?? 0;
    kpi.valorObjectiu = kpi.valorObjectiu ?? kpi.valorMaxim;
  }
}

function validarKPI(kpi) {
  if (kpi.tipus === "boolea") {
    return null;
  }

  if (kpi.tipus === "percentatge") {
    if (kpi.valorObjectiu === null || kpi.valorObjectiu === undefined) {
      return "Cal indicar el percentatge objectiu.";
    }

    if (kpi.valorObjectiu < 0 || kpi.valorObjectiu > 100) {
      return "El percentatge objectiu ha d'estar entre 0 i 100.";
    }

    return null;
  }

  if (kpi.valorMinim === null || kpi.valorMinim === undefined) {
    return "Cal indicar el valor mínim.";
  }

  if (kpi.valorMaxim === null || kpi.valorMaxim === undefined) {
    return "Cal indicar el valor màxim.";
  }

  if (kpi.valorMaxim === kpi.valorMinim) {
    return "El valor màxim ha de ser diferent del valor mínim.";
  }

  if (kpi.valorObjectiu === null || kpi.valorObjectiu === undefined) {
    return "Cal indicar el valor objectiu.";
  }

  if (
    kpi.valorObjectiu < Math.min(kpi.valorMinim, kpi.valorMaxim) ||
    kpi.valorObjectiu > Math.max(kpi.valorMinim, kpi.valorMaxim)
  ) {
    return "El valor objectiu ha d'estar entre el valor mínim i el valor màxim.";
  }

  return null;
}

function renderOptionsObjectius() {
  const objectius = plaActual.objectius || [];

  if (!objectius.length) {
    return `<option value="">No hi ha objectius disponibles</option>`;
  }

  return objectius.map((objectiu) => `
    <option value="${objectiu.idObjectiu}">
      ${objectiu.descripcio || objectiu.nom || `Objectiu ${objectiu.idObjectiu}`}
    </option>
  `).join("");
}

function renderOptionsAccions() {
  const accions = obtenirAccionsPla();

  if (!accions.length) {
    return `<option value="">No hi ha accions disponibles</option>`;
  }

  return accions.map((accio) => `
    <option value="${accio.idAccio}">
      ${accio.titol || accio.nom || `Acció ${accio.idAccio}`}
    </option>
  `).join("");
}

function renderEstructuraPla() {
  const objectius = plaActual.objectius || [];

  if (!objectius.length) {
    return `<p>Encara no hi ha objectius definits en aquest pla.</p>`;
  }

  return objectius.map((objectiu) => `
    <div class="list-item">
      <div class="list-item-header">
        <h4>${objectiu.descripcio || objectiu.nom || `Objectiu ${objectiu.idObjectiu}`}</h4>
        <div class="list-item-actions">
          <button class="btn secondary small btn-editar-objectiu" data-id="${objectiu.idObjectiu}">Editar</button>
          <button class="btn secondary small btn-desactivar-objectiu" data-id="${objectiu.idObjectiu}">Desactivar</button>
        </div>
      </div>
      <p>
        <strong>Valor:</strong> ${objectiu.valor ?? "-"}
        ${objectiu.progresObjectiu !== undefined ? ` · <strong>Progrés:</strong> ${formatPercentatge(objectiu.progresObjectiu)}` : ""}
      </p>

      ${renderAccionsObjectiu(objectiu)}
    </div>
  `).join("");
}

function renderAccionsObjectiu(objectiu) {
  const accions = objectiu.accions || [];

  if (!accions.length) {
    return `<p>No hi ha accions associades.</p>`;
  }

  return `
    <div class="list">
      ${accions.map((accio) => `
        <div class="list-item">
          <div class="list-item-header">
            <strong>${accio.titol || accio.nom || `Acció ${accio.idAccio}`}</strong>
            <div class="list-item-actions">
              <button class="btn secondary small btn-editar-accio" data-id="${accio.idAccio}">Editar</button>
              <button class="btn secondary small btn-desactivar-accio" data-id="${accio.idAccio}">Desactivar</button>
            </div>
          </div>
          <p>${accio.descripcio || ""}</p>
          <p class="stat-subtitle">
            ${accio.progresAccio !== undefined ? `<strong>Progrés:</strong> ${formatPercentatge(accio.progresAccio)}` : ""}
            ${accio.estatAccio ? ` · <strong>Estat:</strong> ${formatEstatKPI(accio.estatAccio)}` : ""}
          </p>
          ${renderKPIsAccio(accio)}
        </div>
      `).join("")}
    </div>
  `;
}

function renderKPIsAccio(accio) {
  const kpis = accio.kpis || accio.indicadors || [];

  if (!kpis.length) {
    return `<p>No hi ha KPI associats.</p>`;
  }

  return `
    <table>
      <thead>
        <tr>
          <th>KPI</th>
          <th>Tipus</th>
          <th>Càlcul</th>
          <th>Orientació</th>
          <th>Rang</th>
          <th>Objectiu</th>
          <th>Periodicitat</th>
          <th>Progrés</th>
          <th>Estat</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        ${kpis.map((kpi) => `
          <tr>
            <td>${kpi.nom || `KPI ${kpi.idKPI}`}</td>
            <td>${formatTipusKPI(kpi.tipus)}</td>
            <td>${formatTipusCalculKPI(kpi.tipusCalcul)}</td>
            <td>${formatOrientacioKPI(kpi.orientacio)}</td>
            <td>${formatRangKPI(kpi)}</td>
            <td>${kpi.valorObjectiu ?? "-"}</td>
            <td>${kpi.periodicitat || "-"}</td>
            <td>${kpi.assoliment ?? "-"}${kpi.assoliment != null ? "%" : ""}</td>
            <td>${formatEstatKPI(kpi.estatKPI)}</td>
            <td>
              <button class="btn secondary small btn-editar-kpi" data-id="${kpi.idKPI}">Editar</button>
              <button class="btn secondary small btn-desactivar-kpi" data-id="${kpi.idKPI}">Desactivar</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function formatTipusCalculKPI(tipusCalcul) {
  const labels = {
    acumulat: "Acumulat",
    mitjana: "Mitjana",
    ultim: "Últim valor"
  };

  return labels[tipusCalcul] || tipusCalcul || "-";
}

function formatEstatKPI(estat) {
  const labels = {
    assolit: "✅ Assolit",
    en_progres: "🟡 En progrés",
    pendent: "🔴 Pendent"
  };

  return labels[estat] || estat || "-";
}

function obtenirAccionsPla() {
  const accions = [];

  (plaActual.objectius || []).forEach((objectiu) => {
    (objectiu.accions || []).forEach((accio) => {
      accions.push(accio);
    });
  });

  return accions;
}

function actualitzarAjudaKPI() {
  const tipus = document.getElementById("kpiTipus").value;
  const ajuda = document.getElementById("kpiAjuda");

  const campMinim = document.getElementById("kpiValorMinim").closest("div");
  const campMaxim = document.getElementById("kpiValorMaxim").closest("div");
  const campObjectiu = document.getElementById("kpiValorObjectiu").closest("div");
  const campOrientacio = document.getElementById("kpiOrientacio").closest("div");

  campMinim.style.display = "";
  campMaxim.style.display = "";
  campObjectiu.style.display = "";
  campOrientacio.style.display = "";

  if (tipus === "numeric") {
    ajuda.textContent = "Numèric: indica mínim, màxim i valor objectiu.";
  } else if (tipus === "escala") {
    ajuda.textContent = "Escala: indica el rang, per exemple 1-5, i el valor objectiu.";
  } else if (tipus === "percentatge") {
    campMinim.style.display = "none";
    campMaxim.style.display = "none";
    ajuda.textContent = "Percentatge: només cal indicar el percentatge objectiu.";
  } else if (tipus === "boolea") {
    campMinim.style.display = "none";
    campMaxim.style.display = "none";
    campObjectiu.style.display = "none";
    campOrientacio.style.display = "none";
    ajuda.textContent = "Sí / No: Sí equival a 100% i No equival a 0%.";
  }
}

function actualitzarAjudaCalcul() {
  const tipusCalcul = document.getElementById("kpiTipusCalcul").value;
  const ajuda = document.getElementById("kpiAjudaCalcul");

  const textos = {
    acumulat: "Tots els registres se sumen. Útil per a comptadors, com el nombre de reunions fetes.",
    mitjana: "Es calcula la mitjana de tots els registres. Útil per a puntuacions recollides diverses vegades, com una valoració d'1 a 5.",
    ultim: "Només compta el registre més recent. Útil per a indicadors d'estat puntual, com una certificació obtinguda."
  };

  ajuda.textContent = textos[tipusCalcul] || "";
}

function parseNullableNumber(valor) {
  if (valor === "" || valor === null || valor === undefined) {
    return null;
  }

  const numero = Number(valor);
  return Number.isNaN(numero) ? null : numero;
}

function formatPercentatge(valor) {
  if (valor === undefined || valor === null || Number.isNaN(Number(valor))) {
    return "-";
  }

  return `${Math.round(Number(valor))}%`;
}

function formatTipusKPI(tipus) {
  const labels = {
    numeric: "Numèric",
    percentatge: "Percentatge",
    escala: "Escala",
    boolea: "Sí / No"
  };

  return labels[tipus] || tipus || "-";
}

function formatOrientacioKPI(orientacio) {
  const labels = {
    major_millor: "Major és millor",
    menor_millor: "Menor és millor"
  };

  return labels[orientacio] || orientacio || "-";
}

function formatRangKPI(kpi) {
  if (kpi.tipus === "boolea") {
    return "0 / 1";
  }

  return `${kpi.valorMinim ?? "-"} - ${kpi.valorMaxim ?? "-"}`;
}