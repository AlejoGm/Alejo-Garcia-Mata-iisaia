import { api } from "./api.js";
import { setChrome } from "./app.js";
import { icon } from "./icons.js";
import { el } from "./ui.js";

// Dos pestañas a cada lado y Entrenar en el centro, elevado: es lo que se toca en el gimnasio.
const LEFT = [["panel", "Panel", "panel"], ["rankings", "Rankings", "rankings"]];
const RIGHT = [["duelos", "Duelos", "duels"], ["grupo", "Grupo", "group"]];

const cache = new Map();

export async function loadGroup(code, force = false) {
  if (force || !cache.has(code)) cache.set(code, await api.get(`/groups/${code}`));
  return cache.get(code);
}

export function forgetGroup(code) {
  cache.delete(code);
}

function tab(group, [key, label, iconName], active) {
  return el("a", { href: `#/g/${group.code}/${key}`, class: key === active ? "active" : null,
    "aria-current": key === active ? "page" : null }, icon(iconName), el("span", {}, label));
}

export function groupChrome(group, active) {
  const fab = el("a", { href: `#/g/${group.code}/entrenar`, class: `fab${active === "entrenar" ? " active" : ""}`,
    "aria-label": "Entrenar", "aria-current": active === "entrenar" ? "page" : null }, icon("train", 30));
  const tabBar = [...LEFT.map((t) => tab(group, t, active)), fab, ...RIGHT.map((t) => tab(group, t, active))];
  setChrome({ heading: group.name, backTo: "#/", tabBar });
}
