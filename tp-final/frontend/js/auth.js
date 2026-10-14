// Tres modos: Auth0 con Google, usuario y contraseña ("local", el de siempre sin Auth0) o desarrollo, solo con un nombre.
const DEV_KEY = "gymbro.devToken";
const SESSION_KEY = "gymbro.session";
const AUTH0_SDK = "https://cdn.auth0.com/js/auth0-spa-js/2.1/auth0-spa-js.production.js";

let mode = "dev";
let client = null;

function storage(action, value, key = mode === "local" ? SESSION_KEY : DEV_KEY) {
  try {
    if (action === "get") return localStorage.getItem(key);
    if (action === "set") localStorage.setItem(key, value);
    if (action === "remove") localStorage.removeItem(key);
  } catch {
    return null;
  }
  return null;
}

/** Entrar o registrarse con usuario y contraseña: el servidor devuelve un token de sesión. */
async function account(path, username, password) {
  const response = await fetch(`/api/auth/${path}`, { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }) }).catch(() => null);
  if (!response) throw new Error("No se pudo conectar con el servidor.");
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(typeof data?.detail === "string" ? data.detail
      : path === "register" ? "El usuario va de 3 a 30 letras, números, punto o guion, y la contraseña de 6 caracteres o más."
        : "Completá el usuario y la contraseña.");
  }
  storage("set", JSON.stringify({ token: data.token, username: username.trim().toLowerCase() }));
}

function session() {
  try {
    return JSON.parse(storage("get") || "null");
  } catch {
    return null;
  }
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
  if (params.has("error")) {
    // Auth0 vuelve con el motivo en la URL: se limpia y se muestra, en vez de dejar el login sin explicación.
    window.history.replaceState({}, "", returnUrl() + "#/login");
    throw new Error(`Auth0 rechazó el login: ${params.get("error_description") || params.get("error")}`);
  }
  if (params.has("code") && params.has("state")) {
    await client.handleRedirectCallback();
    window.history.replaceState({}, "", returnUrl() + "#/");
  }
}

export function authMode() {
  return mode;
}

export async function isLoggedIn() {
  if (mode === "auth0") return client.isAuthenticated();
  return mode === "local" ? Boolean(session()?.token) : Boolean(storage("get"));
}

export async function login(name, password) {
  if (mode === "auth0") {
    await client.loginWithRedirect({ authorizationParams: { connection: "google-oauth2" } });
    return;
  }
  if (mode === "local") {
    await account("login", name, password);
    return;
  }
  storage("set", `dev:${encodeURIComponent(name)}`);
}

export async function register(name, password) {
  await account("register", name, password);
}

export async function getToken() {
  if (mode === "auth0") return client.getTokenSilently();
  return mode === "local" ? session()?.token ?? null : storage("get");
}

export async function suggestedName() {
  if (mode === "auth0") {
    const user = await client.getUser();
    return user?.given_name || user?.name || "";
  }
  if (mode === "local") {
    const username = session()?.username || "";
    return username.charAt(0).toUpperCase() + username.slice(1);
  }
  return decodeURIComponent((storage("get") || "").replace(/^dev:/, ""));
}

export async function logout() {
  if (mode === "auth0") {
    await client.logout({ logoutParams: { returnTo: returnUrl() } });
    return;
  }
  const token = await getToken();
  if (mode === "local" && token) {
    await fetch("/api/auth/logout", { method: "POST", headers: { Authorization: `Bearer ${token}` } }).catch(() => null);
  }
  storage("remove");
}
