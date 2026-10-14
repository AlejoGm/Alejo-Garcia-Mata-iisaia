import { setsDone } from "../draft.js";
import { pop, vibrate } from "../juice.js";
import { dayLabel, el, num, toDisplay, weight } from "../ui.js";

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
    pop(input);
    vibrate(8);
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

/**
 * Una sola fila de sugerencias que se cargan con un toque: romper tu marca y pasar al siguiente del grupo.
 * Si una serie de hoy ya rompió la marca, lo dice en vez de sugerirla.
 */
export function suggestionRow(targets, todaySets, rival, unit, onPick, isPicked) {
  const reached = targets.some((t) => todaySets.some((s) => s.weight_kg >= t.weight_kg - 0.01 && s.reps >= t.reps));
  const chip = (t, text, cls) => el("button", { type: "button", class: `chip target ${cls}${isPicked(t) ? " active" : ""}`,
    onclick: () => onPick(t), "aria-label": `Cargar ${num(toDisplay(t.weight_kg, unit))} ${unit} por ${t.reps}` },
  `${text} · ${num(toDisplay(t.weight_kg, unit))} × ${t.reps}`);
  const chips = reached ? [] : targets.map((t) => chip(t, t.kind === "reps" ? "PR +1 rep" : "PR +peso", ""));
  if (rival?.weight_kg) chips.push(chip(rival, `Pasar a ${rival.display_name}`, "rival"));
  if (!chips.length && !reached) return "";
  return el("div", { class: "suggestions" },
    reached ? el("p", { class: "notice" }, "Ya rompiste tu marca hoy.") : "",
    chips.length ? el("span", { class: "muted small" }, "Tocá para cargar") : "",
    chips.length ? el("div", { class: "targets" }, chips) : "");
}

/** Cuántas series del plan van hechas, sin contar las extra. */
export function planProgress(draft) {
  const total = draft.plan.reduce((sum, item) => sum + item.sets, 0);
  const done = draft.plan.reduce((sum, item) => sum + Math.min(item.sets, draft.sets.filter((s) => s.exercise_id === item.exercise_id).length), 0);
  return { done, total, complete: total > 0 && done >= total };
}

/** Arriba de todo: cuánto falta del entrenamiento y el único botón para terminarlo. */
export function sessionStrip(draft, onFinish, details) {
  const { done, total } = planProgress(draft);
  const text = total ? `${done} de ${total} series` : `${draft.sets.length} ${draft.sets.length === 1 ? "serie" : "series"}`;
  const title = draft.title.split(" · ").at(-1);
  return el("div", { class: "card session-strip" },
    el("div", { class: "spread" }, el("span", { class: "person-text" }, el("strong", {}, title), el("span", { class: "muted small" }, text)),
      el("button", { type: "button", class: "ghost finish-link", disabled: !draft.sets.length, onclick: (event) => onFinish(event.currentTarget) },
        "Terminar entrenamiento")),
    total ? el("div", { class: "progress" }, el("span", { style: `width:${(100 * done) / total}%` })) : "", details);
}

/** Un punto por serie del ejercicio: lleno las hechas, marcado el que estás por hacer. */
export function setDots(done, planned) {
  const count = Math.max(planned, done + 1);
  return el("div", { class: "set-dots", "aria-hidden": "true" }, Array.from({ length: count }, (_, i) =>
    el("span", { class: i < done ? "done" : i === done ? "current" : i >= planned ? "extra" : "" })));
}

/** Selector de ejercicio: primero los desafíos del grupo, después el resto del catálogo. */
export function pickerSelect(exercises, group, selectedId, onChoose) {
  const option = (e) => el("option", { value: String(e.id), selected: e.id === selectedId }, e.name);
  const challengeIds = new Set(group.challenges.map((c) => c.id));
  const select = el("select", { "aria-label": "Ejercicio" },
    el("option", { value: "" }, "Elegí un ejercicio"),
    el("optgroup", { label: "Desafíos del grupo" }, exercises.filter((e) => challengeIds.has(e.id)).map(option)),
    el("optgroup", { label: "Todos" }, exercises.filter((e) => !challengeIds.has(e.id)).map(option)));
  select.addEventListener("change", () => select.value && onChoose(Number(select.value)));
  return select;
}

/** Fecha y peso corporal de la sesión, plegados cuando ya están; abiertos si falta el peso. */
export function sessionDetails(draft, unit, persist, onDiscard) {
  const summary = el("summary", {});
  const describe = () => { summary.textContent = `${dayLabel(draft.date)} · ${draft.bodyweight ? `${num(draft.bodyweight)} ${unit}` : "falta tu peso corporal"}`; };
  describe();
  const date = el("input", { type: "date", value: draft.date, max: new Date().toLocaleDateString("en-CA") });
  date.addEventListener("change", () => { draft.date = date.value; persist(); describe(); });
  const bodyweight = el("input", { type: "number", inputmode: "decimal", value: String(draft.bodyweight ?? "") });
  bodyweight.addEventListener("input", () => { draft.bodyweight = Number(bodyweight.value) || null; persist(); describe(); });
  const discard = el("button", { type: "button", class: "danger", onclick: onDiscard }, "Descartar sesión");
  return el("details", { class: "session-details", open: !draft.bodyweight }, summary,
    el("div", { class: "row" }, el("label", {}, "Fecha", date), el("label", {}, `Peso corporal (${unit})`, bodyweight)), discard);
}

/** Los ejercicios del plan como pestañas, con cuántas series lleva cada uno. */
export function planChipRow(draft, onChoose) {
  if (!draft.plan.length) return "";
  return el("div", { class: "chips" }, draft.plan.map((item, index) => {
    const done = setsDone(draft, item.exercise_id);
    return el("button", { type: "button", class: `chip${index === draft.step ? " active" : ""}${done >= item.sets ? " done" : ""}`,
      onclick: () => onChoose(index, item.exercise_id) }, `${item.name} ${done}/${item.sets}`);
  }));
}

/** Las series ya hechas: tocar una la corrige, la cruz la borra (con deshacer). */
export function setsList(draft, byId, unit, editing, onEdit, onRemove) {
  if (!draft.sets.length) return "";
  const items = draft.sets.map((s, index) => el("li", { class: index === editing ? "editing" : null },
    el("button", { type: "button", class: "set-edit", onclick: () => onEdit(index), "aria-label": "Corregir serie" },
      `${index + 1}. ${byId.get(s.exercise_id)?.name ?? "?"} · ${loadText(s.weight_kg, unit, byId.get(s.exercise_id)?.bodyweight)} × ${s.reps}`),
    el("button", { type: "button", class: "secondary", style: "flex:0", "aria-label": "Borrar serie", onclick: () => onRemove(index) }, "×")));
  return el("div", { class: "card" }, el("h3", {}, `Series hechas (${draft.sets.length})`),
    el("p", { class: "muted small" }, "Tocá una serie para corregirla."), el("ul", { class: "list" }, items));
}
