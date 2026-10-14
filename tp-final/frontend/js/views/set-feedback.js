// Posición en vivo: después de guardar una serie, cómo quedaste en el grupo y a quién tenés adelante.
import { api } from "../api.js";
import { el, num, toDisplay } from "../ui.js";

const PR_TEXT = { weight: "¡PR de peso!", reps: "¡PR de reps!", "1rm": "¡PR de 1RM!" };

export function listNames(names) {
  return names.length < 2 ? names.join("") : `${names.slice(0, -1).join(", ")} y ${names.at(-1)}`;
}

/** Sin señal o sin peso corporal no hay tarjeta: la serie igual queda en el borrador. */
export function fetchStanding(code, set, bodyweightKg) {
  if (!bodyweightKg) return Promise.resolve(null);
  return api.post(`/groups/${code}/standing`, { ...set, bodyweight_kg: bodyweightKg }).catch(() => null);
}

/** Cómo venía y cómo terminó cada ejercicio en la sesión, para el resumen. */
export function track(draft, exerciseId, result) {
  draft.standings ??= {};
  const previous = draft.standings[exerciseId];
  draft.standings[exerciseId] = {
    before: previous ? previous.before : result.position_before,
    after: result.position,
    total: result.total,
    passed: [...new Set([...(previous?.passed ?? []), ...result.passed.map((p) => p.display_name)])],
    next: result.next,
  };
}

function rivalButton(next, unit, onPick) {
  if (!next) return "";
  if (next.weight_kg === null) return el("span", { class: "muted small" }, `Adelante: ${next.display_name}`);
  return el("button", { type: "button", class: "chip target rival", onclick: () => onPick(next),
    "aria-label": `Cargar ${num(toDisplay(next.weight_kg, unit))} ${unit} por ${next.reps} para pasar a ${next.display_name}` },
  `Pasar a ${next.display_name}: ${num(toDisplay(next.weight_kg, unit))} × ${next.reps}`);
}

function placeText(result, exercise) {
  const where = `${result.position}º de ${result.total} en ${exercise} este mes`;
  if (result.position_before === null) return `Entraste a la tabla: ${where}`;
  if (result.position_before > result.position) return `Subiste del ${result.position_before}º al ${result.position}º en ${exercise}`;
  return `Vas ${where}`;
}

/** La tarjeta que aparece unos segundos en la barra, después de guardar. */
export function feedbackCard(result, exercise, unit, onPick) {
  const lines = [];
  if (result.pr) lines.push(el("strong", { class: "feedback-pr" }, PR_TEXT[result.pr]));
  if (result.dots === null) {
    lines.push(el("span", { class: "muted small" }, "Con más de 10 reps no se estima el 1RM: tu lugar no cambia."));
  } else if (result.position !== null) {
    lines.push(el("span", { class: "feedback-place" }, placeText(result, exercise)));
  }
  if (result.passed.length) lines.push(el("strong", { class: "feedback-passed" }, `¡Pasaste a ${listNames(result.passed.map((p) => p.display_name))}!`));
  if (result.position === 1 && !result.next) lines.push(el("strong", { class: "feedback-passed" }, "Sos el primero del grupo."));
  lines.push(rivalButton(result.next, unit, onPick));
  return el("div", { class: `feedback${result.pr ? " hot" : ""}`, role: "status" }, lines);
}

/** En la tarjeta del ejercicio: tu lugar actual y el botón para pasar al siguiente. */
export function standingRow(tracked, unit, onPick) {
  if (!tracked || tracked.after === null) return "";
  return el("div", { class: "targets" }, el("span", { class: "muted small" }, `Vas ${tracked.after}º de ${tracked.total}.`),
    rivalButton(tracked.next, unit, onPick));
}
