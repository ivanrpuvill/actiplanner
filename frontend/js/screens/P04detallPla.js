import { apiGet } from "../api.js";
import { renderLayout, activarLayoutEvents } from "../layout.js";
import { obtenirProgramaActiu, guardarPlaActiu } from "../state.js";

export async function renderP04DetallPla(app, navegar) {
  const programa = obtenirProgramaActiu();

  app.innerHTML = renderLayout("Detall pla", `
    <div class="card">
      <h3>Selecciona un pla</h3>

      <div class="form-grid">
        <div>
          <label>Pla d'acció</label>
          <select id="plaSelect"></select>
        </div>

        <div class="form-actions">
          <button class="btn" id="btnCarregarPla">Carregar pla</button>
        </div>
      </div>
    </div>

    <div id="plaContainer" class="constructor-container"></div>
  `);

  activarLayoutEvents(navegar);

  const select = document.getElementById("plaSelect");

  try {
    const plans = await apiGet(`/programes/${programa.idPrograma}/plans`);

    if (!plans.length) {
      select.innerHTML = `<option>No hi ha plans disponibles</option>`;
      return;
    }

    select.innerHTML = plans.map((pla) => `
      <option value="${pla.idPla}">
        ${pla.titol || pla.nom || `Pla ${pla.idPla}`}
      </option>
    `).join("");

    document.getElementById("btnCarregarPla").addEventListener("click", async () => {
      await carregarPla(select.value);
    });

    await carregarPla(plans[0].idPla);

  } catch (error) {
    document.getElementById("plaContainer").innerHTML =
      `<p class="error-text">${error.message}</p>`;
  }
}

async function carregarPla(idPla) {
  const container = document.getElementById("plaContainer");

  try {
    const pla = await apiGet(`/plans/${idPla}`);
    guardarPlaActiu(pla);

    container.innerHTML = `
      <div class="card">
        <h3>${pla.titol || pla.nom || `Pla ${pla.idPla}`}</h3>
        <p><strong>Estat:</strong> ${formatEstat(pla.estatPla)}</p>
        <p><strong>Progrés:</strong> ${pla.progresPla ?? 0}%</p>
        ${renderBarraProgres(pla.progresPla, pla.estatPla)}
        <p><strong>Data creació:</strong> ${pla.dataCreacio || "-"}</p>
      </div>

      <div class="grid">
        ${(pla.objectius || []).map((objectiu) => `
          <div class="card">
            <h3>${objectiu.descripcio || objectiu.titol || `Objectiu ${objectiu.idObjectiu}`}</h3>
            <p><strong>Valor:</strong> ${objectiu.valor ?? "-"}</p>
            <p><strong>Estat:</strong> ${formatEstat(objectiu.estatObjectiu)}</p>
            <p><strong>Progrés:</strong> ${objectiu.progresObjectiu ?? 0}%</p>
            ${renderBarraProgres(objectiu.progresObjectiu, objectiu.estatObjectiu)}

            <h4>Accions</h4>
            ${(objectiu.accions || []).map((accio) => `
              <div class="list-item">
                <strong>${accio.titol || `Acció ${accio.idAccio}`}</strong>
                <p>${accio.descripcio || ""}</p>
                <p>${accio.dataInici || "-"} → ${accio.dataFi || "-"}</p>
                <p><strong>Progrés:</strong> ${accio.progresAccio ?? 0}% · <strong>Estat:</strong> ${formatEstat(accio.estatAccio)}</p>
              </div>
            `).join("") || "<p>No hi ha accions.</p>"}

            <h4>KPI</h4>
            ${(objectiu.accions || []).flatMap((accio) => accio.kpis || []).map((kpi) => `
              <div class="list-item">
                <strong>${kpi.nom || `KPI ${kpi.idKPI}`}</strong>
                <p>${kpi.descripcio || ""}</p>
                <p><strong>Càlcul:</strong> ${formatTipusCalcul(kpi.tipusCalcul)}</p>
                <p><strong>Valor agregat:</strong> ${kpi.valorAgregat ?? kpi.ultimValor ?? "-"}</p>
                <p><strong>Assoliment:</strong> ${kpi.assoliment ?? 0}% · <strong>Estat:</strong> ${formatEstat(kpi.estatKPI)}</p>
              </div>
            `).join("") || "<p>No hi ha KPI.</p>"}
          </div>
        `).join("") || "<p>No hi ha objectius en aquest pla.</p>"}
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${error.message}</p>`;
  }
}

function renderBarraProgres(progres, estat) {
  if (progres === undefined || progres === null) {
    return "";
  }

  const valor = Math.max(0, Math.min(100, progres));
  const classeEstat = estat || "pendent";

  return `
    <div class="progres-bar-track">
      <div class="progres-bar-fill estat-${classeEstat}" style="width: ${valor}%"></div>
    </div>
  `;
}

function formatEstat(estat) {
  const labels = {
    assolit: "✅ Assolit",
    en_progres: "🟡 En progrés",
    pendent: "🔴 Pendent"
  };

  return labels[estat] || estat || "-";
}

function formatTipusCalcul(tipusCalcul) {
  const labels = {
    acumulat: "Acumulat",
    mitjana: "Mitjana",
    ultim: "Últim valor"
  };

  return labels[tipusCalcul] || tipusCalcul || "-";
}