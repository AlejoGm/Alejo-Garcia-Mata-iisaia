import { api } from "./api.js";
import { initAuth, isLoggedIn } from "./auth.js";
import { el, errorBox } from "./ui.js";
import { routes } from "./routes.js";

const app = document.getElementById("app");
const tabs = document.getElementById("tabs");
const title = document.getElementById("title");
const back = document.getElementById("back");
const profileLink = document.getElementById("profile-link");

export const state = { me: null };

let pollTimer = null;

export async function loadMe(force = false) {
  if (!state.me || force) state.me = await api.get("/me");
  return state.me;
}

/** Repite `fn` cada 30 s mientras la vista siga montada y la pestaña esté visible. */
export function poll(fn) {
  clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    if (document.visibilityState === "visible") fn();
  }, 30000);
}

function match(hash) {
  const path = hash.replace(/^#/, "") || "/";
  for (const route of routes) {
    const result = route.pattern.exec(path);
    if (result) return { route, params: result.groups || {} };
  }
  return null;
}

export function setChrome({ heading = "Gym-bro", backTo = null, tabBar = null } = {}) {
  title.textContent = heading;
  back.hidden = !backTo;
  if (backTo) back.href = backTo;
  tabs.replaceChildren(...(tabBar || []));
  tabs.hidden = !tabBar;
  document.body.classList.toggle("with-tabs", Boolean(tabBar));
}

async function render() {
  clearInterval(pollTimer);
  const found = match(window.location.hash);
  if (!found) {
    window.location.hash = "#/";
    return;
  }
  const { route, params } = found;
  if (!route.public && !(await isLoggedIn())) {
    window.location.hash = "#/login";
    return;
  }
  profileLink.hidden = Boolean(route.public) || route.path === "perfil";
  setChrome();
  app.replaceChildren(el("p", { class: "muted" }, "Cargando..."));
  try {
    if (!route.public && route.path !== "perfil") await loadMe();
    await route.view(app, params);
  } catch (err) {
    if (err.status === 409 || err.status === 401) return;
    app.replaceChildren(errorBox(err.message), el("p", {}, el("a", { href: "#/" }, "Volver al inicio")));
  }
  window.scrollTo(0, 0);
}

async function start() {
  try {
    await initAuth();
  } catch (err) {
    app.replaceChildren(errorBox(err.message));
    return;
  }
  window.addEventListener("hashchange", render);
  render();
}

start();
