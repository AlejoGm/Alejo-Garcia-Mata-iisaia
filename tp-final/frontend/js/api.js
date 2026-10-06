import { getToken } from "./auth.js";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function describeError(status, body) {
  if (body && typeof body.detail === "string") return body.detail;
  if (status === 422) return "Revisá los datos: hay un campo vacío o fuera de rango.";
  return `El servidor respondió con un error (${status}).`;
}

export async function request(path, { method = "GET", body } = {}) {
  const headers = {};
  const token = await getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let response;
  try {
    response = await fetch(`/api${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, "No se pudo conectar con el servidor.");
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401) window.location.hash = "#/login";
    if (response.status === 409 && data?.detail === "perfil incompleto") window.location.hash = "#/perfil";
    throw new ApiError(response.status, describeError(response.status, data));
  }
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body = {}) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  del: (path) => request(path, { method: "DELETE" }),
};
