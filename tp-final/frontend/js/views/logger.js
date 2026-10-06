import { api } from "../api.js";
import { state } from "../app.js";
import { clearDraft, loadDraft, saveDraft, setsDone } from "../draft.js";
import { el, errorBox, toDisplay, toKg, weight } from "../ui.js";
import { sessionSummary } from "./session-summary.js";

function stepper(label, value, step, onChange) {
  const input = el("input", { type: "number", inputmode: "decimal", value: String(value ?? ""), "aria-label": label });
  input.addEventListener("input", () => onChange(input.value === "" ? null : Number(input.value)));
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

function lastLine(last, unit) {
  const parts = [];
  if (last.mine) parts.push(`vos ${weight(last.mine.weight_kg, unit)} × ${last.mine.reps}`);
  for (const other of last.others) parts.push(`${other.display_name} ${weight(other.weight_kg, unit)} × ${other.reps}`);
  return parts.length ? `La última vez: ${parts.join(" · ")}` : "Primera vez que alguien del grupo carga este ejercicio.";
}

export async function loggerView(app, group) {
  const draft = loadDraft();
  if (!draft || draft.code !== group.code) {
    window.location.hash = `#/g/${group.code}/entrenar`;
    return;
  }
  const unit = state.me.unit;
  const exercises = await api.get("/exercises");
  const byId = new Map(exercises.map((e) => [e.id, e]));
  const lastCache = new Map();
  const entry = { weight: null, reps: null };

  async function lastFor(exerciseId) {
    if (!lastCache.has(exerciseId)) {
      lastCache.set(exerciseId, await api.get(`/groups/${group.code}/last?exercise_id=${exerciseId}`).catch(() => null));
    }
    return lastCache.get(exerciseId);
  }

  function persist() {
    saveDraft(draft);
  }

  async function prefill() {
    const previous = [...draft.sets].reverse().find((s) => s.exercise_id === draft.exerciseId);
    const last = previous ? null : await lastFor(draft.exerciseId);
    const base = previous || last?.mine;
    const exercise = byId.get(draft.exerciseId);
    entry.weight = base ? toDisplay(base.weight_kg, unit) : exercise?.bodyweight ? 0 : toDisplay(20, unit);
    entry.reps = base ? base.reps : 8;
  }

  function planItem() {
    return draft.plan[draft.step];
  }

  function chooseExercise(id) {
    draft.exerciseId = id;
    persist();
    prefill().then(render);
  }

  function saveSet() {
    if (!draft.exerciseId || entry.reps === null || entry.weight === null) return;
    draft.sets.push({ exercise_id: draft.exerciseId, weight_kg: toKg(entry.weight, unit), reps: entry.reps });
    const item = planItem();
    if (item && item.exercise_id === draft.exerciseId && setsDone(draft, item.exercise_id) >= item.sets) {
      advance();
    }
    persist();
    render();
  }

  function advance() {
    if (draft.step < draft.plan.length - 1) {
      draft.step += 1;
      draft.exerciseId = planItem().exercise_id;
      prefill().then(render);
    } else {
      draft.step = draft.plan.length;
    }
  }

  async function finish(button, slot) {
    if (!draft.bodyweight) {
      slot.replaceChildren(errorBox("Falta tu peso corporal del día: lo usa DOTS. Cargalo arriba."));
      window.scrollTo(0, 0);
      return;
    }
    button.disabled = true;
    button.textContent = "Guardando...";
    slot.replaceChildren();
    try {
      const saved = await api.post("/me/sessions", {
        date: draft.date,
        bodyweight_kg: toKg(draft.bodyweight, unit),
        routine_day_id: draft.routineDayId,
        sets: draft.sets,
      });
      clearDraft();
      sessionSummary(app, group, saved, unit);
    } catch (err) {
      slot.replaceChildren(errorBox(`${err.message} La sesión quedó guardada en este celular: probá de nuevo.`));
      button.disabled = false;
      button.textContent = "Reintentar";
    }
  }

  function exercisePicker() {
    const option = (e) => el("option", { value: String(e.id), selected: e.id === draft.exerciseId }, e.name);
    const challengeIds = new Set(group.challenges.map((c) => c.id));
    const select = el("select", { "aria-label": "Ejercicio" },
      el("option", { value: "" }, "Elegí un ejercicio"),
      el("optgroup", { label: "Desafíos del grupo" }, exercises.filter((e) => challengeIds.has(e.id)).map(option)),
      el("optgroup", { label: "Todos" }, exercises.filter((e) => !challengeIds.has(e.id)).map(option)));
    select.addEventListener("change", () => select.value && chooseExercise(Number(select.value)));
    return select;
  }

  function planChips() {
    if (!draft.plan.length) return null;
    return el("div", { class: "chips" }, draft.plan.map((item, index) => {
      const done = setsDone(draft, item.exercise_id);
      const chip = el("button", { type: "button", class: `chip${index === draft.step ? " active" : ""}${done >= item.sets ? " done" : ""}` },
        `${item.name} ${done}/${item.sets}`);
      chip.addEventListener("click", () => {
        draft.step = index;
        chooseExercise(item.exercise_id);
      });
      return chip;
    }));
  }

  async function exerciseCard() {
    const card = el("div", { class: "card logger" });
    const item = planItem();
    const exercise = byId.get(draft.exerciseId);
    if (!exercise) {
      card.append(el("h3", {}, draft.plan.length ? "Rutina terminada" : "¿Qué ejercicio hacés?"),
        el("p", { class: "muted small" }, draft.plan.length ? "Podés sumar otro ejercicio o terminar la sesión." : ""),
        exercisePicker());
      return card;
    }
    const doneHere = setsDone(draft, exercise.id);
    const setLabel = item && item.exercise_id === exercise.id ? `Serie ${Math.min(doneHere + 1, item.sets)} de ${item.sets}` : `Serie ${doneHere + 1}`;
    const last = await lastFor(exercise.id);
    const weightLabel = exercise.bodyweight ? `Lastre (${unit})` : `Peso (${unit})`;
    card.append(
      el("div", { class: "spread" }, el("h3", { class: "exercise-name" }, exercise.name), el("span", { class: "pill accent" }, setLabel)),
      el("p", { class: "muted small" }, last ? lastLine(last, unit) : ""),
      el("div", { class: "steppers" },
        stepper(weightLabel, entry.weight, unit === "lb" ? 5 : 2.5, (v) => { entry.weight = v; }),
        stepper("Reps", entry.reps, 1, (v) => { entry.reps = v; })),
      el("button", { type: "button", class: "primary big save-set", onclick: saveSet }, "Guardar serie"),
      el("div", { class: "row" },
        item ? el("button", { type: "button", class: "secondary", onclick: () => { advance(); persist(); render(); } }, "Siguiente ejercicio") : null,
        el("details", { class: "change" }, el("summary", {}, "Cambiar ejercicio"), exercisePicker())),
    );
    return card;
  }

  function setsCard() {
    if (!draft.sets.length) return null;
    const items = draft.sets.map((s, index) => el("li", {},
      el("span", {}, `${byId.get(s.exercise_id)?.name ?? "?"} · ${weight(s.weight_kg, unit)} × ${s.reps}`),
      el("button", { type: "button", class: "secondary", style: "flex:0", "aria-label": "Borrar serie",
        onclick: () => { draft.sets.splice(index, 1); persist(); render(); } }, "×"))).reverse();
    return el("div", { class: "card" }, el("h3", {}, `Series de hoy (${draft.sets.length})`), el("ul", { class: "list" }, items));
  }

  function sessionCard() {
    const date = el("input", { type: "date", value: draft.date, max: new Date().toLocaleDateString("en-CA") });
    date.addEventListener("change", () => { draft.date = date.value; persist(); });
    const bodyweight = el("input", { type: "number", inputmode: "decimal", value: String(draft.bodyweight ?? "") });
    bodyweight.addEventListener("input", () => { draft.bodyweight = Number(bodyweight.value); persist(); });
    return el("details", { class: "card", open: !draft.bodyweight },
      el("summary", {}, `${draft.title} · ${draft.date} · ${draft.bodyweight ? `${draft.bodyweight} ${unit}` : "falta tu peso"}`),
      el("div", { class: "row" }, el("label", {}, "Fecha", date), el("label", {}, `Peso corporal (${unit})`, bodyweight)));
  }

  function footer() {
    const slot = el("div");
    const finishButton = el("button", { type: "button", class: "primary big", disabled: draft.sets.length === 0 }, `Terminar sesión (${draft.sets.length})`);
    finishButton.addEventListener("click", () => finish(finishButton, slot));
    const discard = el("button", { type: "button", class: "secondary" }, "Descartar");
    discard.addEventListener("click", () => {
      if (draft.sets.length && !window.confirm("¿Descartar las series de esta sesión?")) return;
      clearDraft();
      window.location.hash = `#/g/${group.code}/entrenar`;
    });
    return el("div", { class: "logger-footer" }, slot, el("div", { class: "row" }, discard, finishButton));
  }

  async function render() {
    app.replaceChildren(sessionCard(), planChips() || "", await exerciseCard(), setsCard() || "", footer());
  }

  if (draft.exerciseId) await prefill();
  await render();
}
