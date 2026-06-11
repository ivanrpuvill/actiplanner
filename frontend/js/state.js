const USUARI_KEY = "actiplanner_usuari_actiu";
const PROGRAMA_KEY = "actiplanner_programa_actiu";
const ROL_KEY = "actiplanner_rol_actiu";
const PLA_KEY = "actiplanner_pla_actiu";

function guardar(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function obtenir(key) {
  const value = localStorage.getItem(key);
  return value ? JSON.parse(value) : null;
}

export function guardarUsuariActiu(usuari) {
  guardar(USUARI_KEY, usuari);
}

export function obtenirUsuariActiu() {
  return obtenir(USUARI_KEY);
}

export function guardarProgramaActiu(programa) {
  guardar(PROGRAMA_KEY, programa);
}

export function obtenirProgramaActiu() {
  return obtenir(PROGRAMA_KEY);
}

export function guardarRolActiu(rol) {
  guardar(ROL_KEY, rol);
}

export function obtenirRolActiu() {
  return obtenir(ROL_KEY);
}

export function guardarPlaActiu(pla) {
  guardar(PLA_KEY, pla);
}

export function obtenirPlaActiu() {
  return obtenir(PLA_KEY);
}

export function tancarSessio() {
  localStorage.removeItem(USUARI_KEY);
  localStorage.removeItem(PROGRAMA_KEY);
  localStorage.removeItem(ROL_KEY);
  localStorage.removeItem(PLA_KEY);
}