// Dos modos: Auth0 con Google, o login de desarrollo cuando el servidor no tiene Auth0 configurado.
const DEV_KEY = "gymbro.devToken";
const AUTH0_SDK = "https://cdn.auth0.com/js/auth0-spa-js/2.1/auth0-spa-js.production.js";

let mode = "dev";
let client = null;

function storage(action, value) {
  try {
    if (action === "get") return localStorage.getItem(DEV_KEY);
    if (action === "set") localStorage.setItem(DEV_KEY, value);
    if (action === "remove") localStorage.removeItem(DEV_KEY);
  } catch {
    return null;
  }
  return null;
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = src;
    script.onload = resolve;
    script.onerror = () => reject(new Error("No se pudo cargar el login de Google. Revisá la conexión."));
    document.head.append(script);
  });
}

function returnUrl() {
  return window.location.origin + window.location.pathname;
}

export async function initAuth() {
  const response = await fetch("/api/config");
  const config = await response.json();
  mode = config.auth;
  if (mode !== "auth0") return;

  await loadScript(AUTH0_SDK);
  client = await window.auth0.createAuth0Client({
    domain: config.domain,
    clientId: config.client_id,
    cacheLocation: "localstorage",
    useRefreshTokens: true,
    authorizationParams: { audience: config.audience, redirect_uri: returnUrl() },
  });
  const params = new URLSearchParams(window.location.search);
  if (params.has("code") && params.has("state")) {
    await client.handleRedirectCallback();
    window.history.replaceState({}, "", returnUrl() + "#/");
  }
}

export function authMode() {
  return mode;
}

export async function isLoggedIn() {
  return mode === "auth0" ? client.isAuthenticated() : Boolean(storage("get"));
}

export async function login(name) {
  if (mode === "auth0") {
    await client.loginWithRedirect({ authorizationParams: { connection: "google-oauth2" } });
    return;
  }
  storage("set", `dev:${name}`);
}

export async function getToken() {
  return mode === "auth0" ? client.getTokenSilently() : storage("get");
}

export async function suggestedName() {
  if (mode === "auth0") {
    const user = await client.getUser();
    return user?.given_name || user?.name || "";
  }
  return (storage("get") || "").replace(/^dev:/, "");
}

export async function logout() {
  if (mode === "auth0") {
    await client.logout({ logoutParams: { returnTo: returnUrl() } });
    return;
  }
  storage("remove");
}
