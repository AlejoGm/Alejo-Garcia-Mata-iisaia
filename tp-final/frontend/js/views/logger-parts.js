import { el, num, toDisplay, weight } from "../ui.js";

export const REST_SECONDS = 90;

export function stepper(label, value, step, onChange) {
  const input = el("input", { type: "number", inputmode: "decimal", value: String(value ?? ""), "aria-label": label });
  input.addEventListener("input", () => onChange(input.value === "" ? null : Number(input.value)));
  // Al tocar el campo se selecciona todo: escribir "60" reemplaza en vez de insertarse en el medio.
    // Vale para cada toque, también con el campo ya activo: en el gimnasio se reemplaza, no se edita un dígito.
  input.addEventListener("focus", () => input.select());
  input.addEventListener("pointerup", (event) => { event.preventDefault(); input.select(); });
  const bump = (delta) => {
    const next = Math.max(0, Math.round(((Number(input.value) || 0) + delta) * 100) / 100);
    input.value = String(next);
    onChange(next);
  };
  return el("div", { class: "stepper" },
    el("span", { class: "stepper-label" }, label),
    el("div", { class: "stepper-row" },
      el("button", { type: "button", class: "step", onclick: () => bump(-step), "aria-label": `Menos ${label}` }, "−"),
      input,
      el("button", { type: "button", class: "step", onclick: () => bump(step), "aria-label": `Más ${label}` }, "+")),
  );
}

/** En ejercicios con tu peso, el peso cargado es lastre: "peso corporal + 10 kg". */
export function loadText(weightKg, unit, bodyweightExercise) {
  if (!bodyweightExercise) return weight(weightKg, unit);
  return weightKg ? `peso corporal + ${weight(weightKg, unit)}` : "peso corporal";
}

export function lastLine(last, unit, bodyweightExercise = false) {
  const parts = [];
  const text = (s) => `${loadText(s.weight_kg, unit, bodyweightExercise)} × ${s.reps}`;
  if (last.mine) parts.push(`vos ${text(last.mine)}`);
  for (const other of last.others) parts.push(`${other.display_name} ${text(other)}`);
  return parts.length ? `La última vez: ${parts.join(" · ")}` : "Primera vez que alguien del grupo carga este ejercicio.";
}

/** Un peso sospechoso pide un segundo toque: más de 300 kg, o más de 1,5 veces tu referencia. */
export function suspicious(weightKg, referenceKg) {
  if (weightKg > 300) return true;
  return Boolean(referenceKg) && weightKg > referenceKg * 1.5 && weightKg - referenceKg > 10;
}

/** Timer de descanso: cuenta hacia atrás y vibra al terminar. */
export function restTimer(onTick) {
  let end = null;
  let handle = null;
  const tick = () => {
    if (end === null) return;
    const left = Math.max(0, Math.round((end - Date.now()) / 1000));
    onTick(left);
    if (left === 0) {
      clearInterval(handle);
      end = null;
      if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
    }
  };
  return {
    start(seconds = REST_SECONDS) {
      end = Date.now() + seconds * 1000;
      clearInterval(handle);
      handle = setInterval(tick, 1000);
      tick();
    },
    add(seconds) {
      if (end !== null) { end += seconds * 1000; tick(); }
    },
    stop() {
      clearInterval(handle);
      end = null;
      onTick(null);
    },
    running: () => end !== null,
  };
}

export function clock(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

const BAR = { kg: 20, lb: 45 };
const PLATES = { kg: [25, 20, 15, 10, 5, 2.5, 1.25], lb: [45, 35, 25, 10, 5, 2.5] };

/** Discos por lado para llegar a `total`, en la unidad del perfil, con barra olímpica. */
export function platesPerSide(total, unit) {
  let side = (total - BAR[unit]) / 2;
  if (!(side >= 0)) return null;
  const plates = [];
  for (const plate of PLATES[unit]) {
    while (side >= plate - 0.001) {
      plates.push(plate);
      side -= plate;
    }
  }
  return { plates, rest: Math.round(side * 100) / 100 };
}

export function platesText(total, unit) {
  const result = total ? platesPerSide(total, unit) : null;
  if (!result) return `Menos que la barra sola (${BAR[unit]} ${unit}).`;
  if (!result.plates.length) return `Solo la barra (${BAR[unit]} ${unit}).`;
  if (result.plates.length > 10) return "Revisá el peso: no entra en la barra.";
  const rest = result.rest ? `, y sobran ${num(result.rest)} ${unit} que no salen con discos` : "";
  return `Por lado: ${result.plates.map((p) => num(p, 2)).join(" + ")}${rest}.`;
}

/** Botones del objetivo para PR. Si una serie de hoy ya lo alcanzó, lo festeja en vez de sugerir. */
export function targetButtons(targets, todaySets, unit, onPick, isPicked = () => false) {
  if (!targets.length) return "";
  const reached = targets.some((t) => todaySets.some((s) => s.weight_kg >= t.weight_kg - 0.01 && s.reps >= t.reps));
  if (reached) return el("p", { class: "notice" }, "Ya rompiste tu marca hoy.");
  return el("div", { class: "targets" }, el("span", { class: "muted small" }, "Para PR:"),
    targets.map((t) => el("button", { type: "button", class: `chip target${isPicked(t) ? " active" : ""}`, onclick: () => onPick(t),
      "aria-label": `Cargar ${num(toDisplay(t.weight_kg, unit))} ${unit} por ${t.reps}` },
    `${t.kind === "reps" ? "+1 rep" : "+peso"}: ${num(toDisplay(t.weight_kg, unit))} × ${t.reps}`)));
}
