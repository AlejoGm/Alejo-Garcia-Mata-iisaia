// Helpers de DOM. Todo el texto entra por textContent: nada que venga de la API pasa por innerHTML.

export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key in node && typeof value !== "string") node[key] = value;
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

export function errorBox(message) {
  return el("p", { class: "error", role: "alert" }, message);
}

export function loading(text = "Cargando...") {
  return el("p", { class: "muted" }, text);
}

/** Corre una acción asíncrona de un botón: lo deshabilita y muestra el error al lado. */
export async function busy(button, errorSlot, action) {
  const label = button.textContent;
  button.disabled = true;
  button.textContent = "Un momento...";
  errorSlot.textContent = "";
  try {
    await action();
  } catch (err) {
    errorSlot.textContent = err.message;
  } finally {
    button.disabled = false;
    button.textContent = label;
  }
}

const LB = 0.45359237;

export function toDisplay(kg, unit) {
  if (kg === null || kg === undefined) return null;
  const value = unit === "lb" ? kg / LB : kg;
  return Math.round(value * 10) / 10;
}

export function toKg(value, unit) {
  const number = Number(value);
  return unit === "lb" ? Math.round((number * LB) * 100) / 100 : number;
}

export function num(value, digits = 1) {
  return value === null || value === undefined ? "—" : Number(value).toLocaleString("es-AR", { maximumFractionDigits: digits });
}

export function weight(kg, unit) {
  return kg === null || kg === undefined ? "—" : `${num(toDisplay(kg, unit))} ${unit}`;
}

export function today() {
  // en-CA formatea como YYYY-MM-DD en la zona horaria local.
  return new Date().toLocaleDateString("en-CA");
}

export function storageGet(key, fallback = null) {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function storageSet(key, value) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Sin storage se pierde el borrador al cerrar la pestaña; la app sigue andando.
  }
}

// Avatar con iniciales: el tono sale del nombre, siempre dentro de la paleta (lima, menta, brasa, arena).
const TONES = ["lime", "mint", "ember", "sand"];

export function avatar(name, size = "md") {
  const letters = String(name).split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("") || "?";
  let hash = 0;
  for (const char of String(name)) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return el("span", { class: `avatar-dot ${size} tone-${TONES[hash % TONES.length]}`, "aria-hidden": "true" }, letters);
}
