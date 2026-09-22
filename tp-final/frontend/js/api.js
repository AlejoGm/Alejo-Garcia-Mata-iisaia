async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`/api${path}`, options);
  } catch {
    throw new Error("No se pudo conectar con el servidor.");
  }
  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(describeError(response.status, body));
  }
  return body;
}

function describeError(status, body) {
  if (body && typeof body.detail === "string") {
    return body.detail;
  }
  if (status === 422) {
    return "Revisá los datos: hay un campo vacío o fuera de rango.";
  }
  return `El servidor respondió con un error (${status}).`;
}

function postJson(path, data) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

const groupPath = (code) => `/groups/${encodeURIComponent(code)}`;

export function createGroup(name) {
  return postJson("/groups", { name });
}

export function getGroup(code) {
  return request(groupPath(code));
}

export function joinGroup(code, nickname, bodyweightKg) {
  return postJson(`${groupPath(code)}/members`, { nickname, bodyweight_kg: bodyweightKg });
}

export function postSession(code, nickname, date, sets) {
  return postJson(`${groupPath(code)}/members/${encodeURIComponent(nickname)}/sessions`, { date, sets });
}

export function getRankings(code) {
  return request(`${groupPath(code)}/rankings`);
}
