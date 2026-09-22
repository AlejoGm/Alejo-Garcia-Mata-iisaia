// Sin login: el navegador recuerda a qué grupo pertenecés y con qué nickname.
const KEY = "gymbro.membership";

export function loadMembership() {
  try {
    const value = JSON.parse(localStorage.getItem(KEY));
    return value && value.code && value.nickname ? value : null;
  } catch {
    return null;
  }
}

export function saveMembership(code, nickname) {
  try {
    localStorage.setItem(KEY, JSON.stringify({ code, nickname }));
  } catch {
    // Sin storage la sesión dura lo que dure la pestaña.
  }
}

export function clearMembership() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // Nada que limpiar.
  }
}
