import { apiGet, apiPost } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import {
  obtenirProgramaActiu,
  obtenirUsuariActiu,
  obtenirPlaActiu,
  guardarPlaActiu
} from "../state.js";

export async function renderP05RegistreKPI(app, navegar) {
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Registre KPI", `
    <div class="card">
      <h3>Selecciona un pla</h3>

      <div class="form-grid">
        <div>
          <label>Pla d'acció</label>
          <select id="plaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarPla">Carregar KPI</button>
        </div>
      </div>
    </div>

    <div id="kpiContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  try {
    const plans = await apiGet(`/programes/${programa.idPrograma}/plans`);
    const select = document.getElementById("plaSelect");

    if (!plans.length) {
      select.innerHTML = `<option value="">No hi ha plans</option>`;
      document.getElementById("kpiContainer").innerHTML = `
        <div class="card">
          <p>No hi ha plans disponibles.</p>
        </div>
      `;
      return;
    }

    select.innerHTML = plans.map((pla) => `
      <option value="${pla.idPla}">
        ${pla.titol || pla.nom || `Pla ${pla.idPla}`}
      </option>
    `).join("");

    document.getElementById("btnCarregarPla").addEventListener("click", async () => {
      await carregarKPIs(select.value, navegar);
    });

    const plaActiu = obtenirPlaActiu();

    if (plaActiu) {
      select.value = plaActiu.idPla;
      await carregarKPIs(plaActiu.idPla, navegar);
    } else {
      await carregarKPIs(plans[0].idPla, navegar);
    }
  } catch (error) {
    document.getElementById("kpiContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarKPIs(idPla, navegar) {
  const container = document.getElementById("kpiContainer");

  try {
    const pla = await apiGet(`/plans/${idPla}`);
    guardarPlaActiu(pla);

    const kpis = [];

    (pla.objectius || []).forEach((objectiu) => {
      (objectiu.accions || []).forEach((accio) => {
        (accio.kpis || []).forEach((kpi) => {
          kpis.push({
            ...kpi,
            objectiu,
            accio
          });
        });
      });
    });

    if (!kpis.length) {
      container.innerHTML = `
        <div class="card">
          <p>Aquest pla encara no té KPI registrats.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="grid">
        ${kpis.map((kpi) => `
          <div class="card">
            <h3>${kpi.nom || `KPI ${kpi.idKPI}`}</h3>
            <p>${kpi.descripcio || ""}</p>
            <p><strong>Objectiu:</strong> ${kpi.objectiu.descripcio || `Objectiu ${kpi.objectiu.idObjectiu}`}</p>
            <p><strong>Acció:</strong> ${kpi.accio.titol || `Acció ${kpi.accio.idAccio}`}</p>
            <p><strong>Periodicitat:</strong> ${kpi.periodicitat || "-"}</p>
            <p><strong>Tipus:</strong> ${formatTipusKPI(kpi.tipus)}</p>
            <p><strong>Valor objectiu:</strong> ${kpi.valorObjectiu ?? "-"}</p>

            <form class="form registre-kpi-form" data-id-kpi="${kpi.idKPI}">
              <label>Nou valor</label>
              <input name="valor" type="number" step="0.01" required />

              <label>Comentari / observacions</label>
              <textarea
                name="comentari"
                rows="3"
                placeholder="Explica el context d'aquest registre..."
              ></textarea>

              <button class="btn" type="submit">Registrar valor</button>
            </form>

            <div id="registres-${kpi.idKPI}" class="registre-list">
              Carregant registres...
            </div>
          </div>
        `).join("")}
      </div>
    `;

    activarFormsRegistre(navegar);
    await carregarRegistres(kpis);

  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarRegistres(kpis) {
  for (const kpi of kpis) {
    const container = document.getElementById(`registres-${kpi.idKPI}`);

    try {
      const registres = await apiGet(`/kpis/${kpi.idKPI}/registres`);

      if (!registres.length) {
        container.innerHTML = `<p>No hi ha registres previs.</p>`;
        continue;
      }

      container.innerHTML = `
        <h4>Històric</h4>
        <ul>
          ${registres.map((registre) => `
            <li>
              <strong>${registre.dataRegistre || "-"}</strong> — ${registre.valor}
              ${registre.comentari ? `<br><em>${registre.comentari}</em>` : ""}
            </li>
          `).join("")}
        </ul>
      `;
    } catch {
      container.innerHTML = `<p>No s'han pogut carregar els registres.</p>`;
    }
  }
}

function activarFormsRegistre(navegar) {
  document.querySelectorAll(".registre-kpi-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const programa = obtenirProgramaActiu();
      const usuari = obtenirUsuariActiu();
      const idKPI = Number(form.dataset.idKpi);
      const valor = Number(form.valor.value);
      const comentari = form.comentari.value.trim();

      if (Number.isNaN(valor)) {
        alert("Cal indicar un valor numèric.");
        return;
      }

      const registre = {
        idKPI,
        idPrograma: programa.idPrograma,
        idUsuari: usuari.idUsuari,
        valor,
        dataRegistre: new Date().toISOString().split("T")[0],
        comentari
      };

      await apiPost("/registres-kpi", registre);
      navegar("P05");
    });
  });
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