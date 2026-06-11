function getApp() {
    return document.getElementById("app");
}

function navegar(pantalla) {
    if (pantalla === "login") {
        renderLogin();
        return;
    }

    if (pantalla === "seleccio-programa") {
        renderSeleccioPrograma();
        return;
    }

    if (pantalla === "participant-dashboard") {
        renderDashboardParticipant();
        return;
    }

    if (pantalla === "supervisor-dashboard") {
        renderDashboardSupervisor();
        return;
    }

    if (pantalla === "admin-dashboard") {
        renderDashboardAdministrador();
        return;
    }

    renderLogin();
}

function renderPantallaInicial() {
    const usuari = obtenirUsuariActiu();
    const programa = obtenirProgramaActiu();
    const rol = obtenirRolActiu();

    if (!usuari) {
        renderLogin();
        return;
    }

    if (!programa || !rol) {
        renderSeleccioPrograma();
        return;
    }

    if (rol === "participant") {
        renderDashboardParticipant();
        return;
    }

    if (rol === "supervisor") {
        renderDashboardSupervisor();
        return;
    }

    if (rol === "administrador") {
        renderDashboardAdministrador();
        return;
    }

    renderSeleccioPrograma();
}

document.addEventListener("DOMContentLoaded", function () {
    renderPantallaInicial();
});