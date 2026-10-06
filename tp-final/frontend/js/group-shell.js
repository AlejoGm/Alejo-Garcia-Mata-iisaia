import { api } from "./api.js";
import { setChrome } from "./app.js";
import { el } from "./ui.js";

const TABS = [
  ["entrenar", "Entrenar"],
  ["rankings", "Rankings"],
  ["feed", "Feed"],
  ["duelos", "Duelos"],
  ["grupo", "Grupo"],
];

const cache = new Map();

export async function loadGroup(code, force = false) {
  if (force || !cache.has(code)) cache.set(code, await api.get(`/groups/${code}`));
  return cache.get(code);
}

export function forgetGroup(code) {
  cache.delete(code);
}

export function groupChrome(group, active) {
  const tabBar = TABS.map(([key, label]) =>
    el("a", { href: `#/g/${group.code}/${key}`, class: key === active ? "active" : null }, label));
  setChrome({ heading: group.name, backTo: "#/", tabBar });
}
