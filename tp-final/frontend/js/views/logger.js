import { api } from "../api.js";
import { loadMe, state } from "../app.js";
import { clearDraft, loadDraft, saveDraft, setsDone } from "../draft.js";
import { el, errorBox, toDisplay, toKg, weight } from "../ui.js";
import {
  clock, lastLine, pickerSelect, planProgress, platesText, restTimer, sessionDetails, sessionStrip, setDots, stepper,
  planChipRow, setsList, suggestionRow, suspicious,
} from "./logger-parts.js";
import { earnedMedals, sessionSummary } from "./session-summary.js";
import { feedbackCard, fetchStanding, track } from "./set-feedback.js";
import { celebrate, vibrate } from "../juice.js";

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
  const entry = { weight: null, reps: null, confirm: false, limit: false, editing: null };
  // El descanso es un estado, no un botón: un texto con dos acciones chicas al lado.
  const restText = el("span", {});
  const more = el("button", { type: "button", class: "link", onclick: () => timer.add(30) }, "+30 s");
  const bar = { timer: el("div", { class: "rest-line", hidden: true }, restText, more,
    el("button", { type: "button", class: "link", onclick: () => timer.stop() }, "Saltar")), toast: el("div", { class: "toast", hidden: true }) };
  const timer = restTimer((left) => {
    bar.timer.hidden = left === null;
    more.hidden = left === 0;
    restText.textContent = left === 0 ? "Descanso terminado" : `Descanso ${clock(left ?? 0)}`;
  });
  let undo = null;
  let feedback = null;
  let justSaved = null;
  let feedbackTimer = null;

  const lastFor = async (exerciseId) => {
    if (!lastCache.has(exerciseId)) {
      lastCache.set(exerciseId, await api.get(`/groups/${group.code}/last?exercise_id=${exerciseId}`).catch(() => null));
    }
    return lastCache.get(exerciseId);
  };
  const persist = () => saveDraft(draft);
  const planItem = () => draft.plan[draft.step];

  async function reference(exerciseId) {
    const previous = [...draft.sets].reverse().find((s) => s.exercise_id === exerciseId);
    return previous || (await lastFor(exerciseId))?.mine || null;
  }

  async function prefill() {
    const base = await reference(draft.exerciseId);
    const exercise = byId.get(draft.exerciseId);
    entry.weight = base ? toDisplay(base.weight_kg, unit) : exercise?.bodyweight ? 0 : unit === "lb" ? 45 : 20;
    entry.reps = base ? base.reps : 8;
    entry.confirm = false;
  }

  async function chooseExercise(id) {
    draft.exerciseId = id;
    persist();
    await prefill();
    render();
  }

  function advanceToNextIncomplete() {
    const pending = draft.plan.map((item, index) => ({ item, index })).filter(({ item }) => setsDone(draft, item.exercise_id) < item.sets);
    const next = pending.find(({ index }) => index > draft.step) || pending[0];
    draft.step = next ? next.index : draft.plan.length;
    draft.exerciseId = next ? next.item.exercise_id : null;
  }

  async function saveSet() {
    if (!draft.exerciseId || !entry.reps || entry.weight === null) return;
    const weightKg = toKg(entry.weight, unit);
    if (weightKg > 500) {
      entry.limit = true;
      render();
      return;
    }
    entry.limit = false;
    const ref = await reference(draft.exerciseId);
    if (!entry.confirm && suspicious(weightKg, ref?.weight_kg)) {
      entry.confirm = true;
      render();
      return;
    }
    const set = { exercise_id: draft.exerciseId, weight_kg: weightKg, reps: entry.reps };
    if (entry.editing !== null) {
      draft.sets[entry.editing] = set;
      entry.editing = null;
      entry.confirm = false;
      persist();
      render();
      return;
    }
    draft.sets.push(set);
    vibrate(25);
    clearTimeout(justSaved);
    justSaved = setTimeout(() => { justSaved = null; renderBar(); }, 900);
    showStanding(set);
    const item = planItem();
    const justCompleted = item && item.exercise_id === draft.exerciseId && setsDone(draft, item.exercise_id) === item.sets;
    if (justCompleted) {
      advanceToNextIncomplete();
      if (draft.exerciseId) await prefill();
    }
    entry.confirm = false;
    persist();
    timer.start();
    render();
  }

  function pickTarget(t) {
    entry.weight = toDisplay(t.weight_kg, unit);
    entry.reps = t.reps;
    entry.confirm = false;
    render();
  }

  function showStanding(set) {
    const exercise = byId.get(set.exercise_id)?.name ?? "";
    fetchStanding(group.code, set, draft.bodyweight ? toKg(draft.bodyweight, unit) : null).then((result) => {
      if (!result) return;
      track(draft, set.exercise_id, result);
      persist();
      if (result.pr) celebrate();
      feedback = { result, exercise };
      clearTimeout(feedbackTimer);
      feedbackTimer = setTimeout(() => { feedback = null; renderBar(); }, 9000);
      render();
    });
  }

  function removeSet(index) {
    entry.editing = null;
    const [removed] = draft.sets.splice(index, 1);
    persist();
    clearTimeout(undo?.handle);
    undo = { removed, index, handle: setTimeout(() => { undo = null; renderBar(); }, 10000) };
    render();
  }

  function editSet(index) {
    const set = draft.sets[index];
    entry.editing = index;
    draft.exerciseId = set.exercise_id;
    entry.weight = toDisplay(set.weight_kg, unit);
    entry.reps = set.reps;
    render();
    window.scrollTo(0, 0);
  }

  async function cancelEdit() {
    entry.editing = null;
    await prefill();
    render();
  }

  async function finish(button, slot) {
    if (!draft.bodyweight) {
      slot.replaceChildren(errorBox("Falta tu peso corporal del día: lo usa DOTS. Cargalo arriba."));
      window.scrollTo(0, 0);
      return;
    }
    button.disabled = true;
    button.textContent = "Guardando...";
    try {
      const saved = await api.post("/me/sessions", { date: draft.date, bodyweight_kg: toKg(draft.bodyweight, unit),
        routine_day_id: draft.routineDayId, sets: draft.sets });
      clearDraft();
      timer.stop();
      document.body.classList.remove("with-logger-bar");
      await loadMe(true);
      await sessionSummary(app, group, saved, unit, draft);
    } catch (err) {
      slot.replaceChildren(errorBox(`${err.message} La sesión quedó guardada en este celular: probá de nuevo.`));
      button.disabled = false;
      button.textContent = "Reintentar";
    }
  }

  const exercisePicker = () => pickerSelect(exercises, group, draft.exerciseId, chooseExercise);

  const planChips = () => planChipRow(draft, (index, exerciseId) => { draft.step = index; chooseExercise(exerciseId); });

  async function exerciseCard() {
    const item = planItem();
    const exercise = byId.get(draft.exerciseId);
    if (!exercise) {
      return el("div", { class: "card logger" },
        el("h3", {}, draft.plan.length ? "¡Rutina completa!" : "¿Qué ejercicio hacés?"),
        draft.plan.length ? el("p", { class: "muted small" }, "Tocá «Terminar entrenamiento» para ver tu resumen, o sumá un ejercicio extra.") : "",
        exercisePicker());
    }
    const done = setsDone(draft, exercise.id);
    const planned = item && item.exercise_id === exercise.id ? item.sets : 0;
    const label = entry.editing !== null ? `Editando la serie ${entry.editing + 1}` : planned
      ? (done < planned ? `Serie ${done + 1} de ${planned}` : `Serie ${done + 1}, extra`) : `Serie ${done + 1}`;
    const tracked = draft.standings?.[exercise.id];
    const last = await lastFor(exercise.id);
    const editing = entry.editing !== null
      ? el("div", { class: "notice spread" }, el("span", {}, `Editando la serie ${entry.editing + 1}`),
        el("button", { type: "button", class: "secondary", style: "flex:0", onclick: cancelEdit }, "Cancelar"))
      : "";
    const plates = exercise.barbell ? el("p", { class: "muted small plates" }) : "";
    const showPlates = () => { if (plates) plates.textContent = platesText(entry.weight, unit); };
    showPlates();
    return el("div", { class: "card logger" },
      el("div", { class: "exercise-head" },
        el("h3", { class: "exercise-name" }, exercise.name),
        el("div", { class: "spread" }, el("span", { class: "set-label" }, label),
          tracked?.after ? el("span", { class: "muted small" }, `${tracked.after}º de ${tracked.total} en el grupo`) : ""),
        setDots(done, planned)),
      editing,
      el("div", { class: "steppers" },
        stepper(exercise.bodyweight ? `Lastre (${unit})` : `Peso (${unit})`, entry.weight, unit === "lb" ? 5 : 2.5,
          (v) => { const warned = entry.confirm || entry.limit; entry.weight = v; entry.confirm = false; entry.limit = false; showPlates(); if (warned) renderBar(); }),
        stepper("Reps", entry.reps, 1, (v) => { const warned = entry.confirm; entry.reps = v; entry.confirm = false; if (warned) renderBar(); })),
      plates,
      // Debajo de los números, cerca del pulgar: lo que ayuda a decidir la serie.
      suggestionRow(last?.targets ?? [], draft.sets.filter((s) => s.exercise_id === exercise.id), tracked?.next, unit,
        pickTarget, (t) => toKg(entry.weight, unit) === t.weight_kg && entry.reps === t.reps),
      el("p", { class: "muted small" }, last ? lastLine(last, unit, exercise.bodyweight) : ""),
      exercise.bodyweight ? el("p", { class: "muted small" }, "Ejercicio con tu peso: cargá solo el lastre. El 1RM suma tu peso corporal.") : "",
      el("div", { class: "row quiet-actions" },
        item ? el("button", { type: "button", class: "link", onclick: async () => { advanceToNextIncomplete(); if (draft.exerciseId) await prefill(); persist(); render(); } }, "Saltar ejercicio") : "",
        el("details", { class: "change" }, el("summary", {}, "Cambiar ejercicio"), exercisePicker())));
  }

  const setsCard = () => setsList(draft, byId, unit, entry.editing, editSet, removeSet);

  const sessionCard = () => sessionDetails(draft, unit, persist, () => {
    if (draft.sets.length && !window.confirm("¿Descartar las series de esta sesión?")) return;
    clearDraft();
    timer.stop();
    document.body.classList.remove("with-logger-bar");
    window.location.hash = `#/g/${group.code}/entrenar`;
  });

  const slot = el("div");
  const barNode = el("div", { class: "logger-bar" });

  function nextLabel() {
    const item = planItem();
    const done = setsDone(draft, draft.exerciseId);
    return item && item.exercise_id === draft.exerciseId && done < item.sets ? `serie ${done + 1} de ${item.sets}` : `serie ${done + 1}`;
  }

  function finishEarly(button) {
    const { done, total } = planProgress(draft);
    if (total && done < total && !window.confirm(`Te faltan ${total - done} series de la rutina. ¿Terminar igual?`)) return;
    finish(button, slot);
  }

  function renderBar() {
    // Una sola acción grande por momento: hacer la serie, confirmar un peso raro, guardar una corrección o terminar.
    const complete = planProgress(draft).complete && !draft.exerciseId;
    const save = el("button", { type: "button", class: "primary big save-set", disabled: !draft.exerciseId && !complete,
      onclick: complete ? (event) => finish(event.currentTarget, slot) : saveSet },
    complete ? "Terminar entrenamiento" : entry.confirm ? `Confirmar ${weight(toKg(entry.weight, unit), unit)}`
      : entry.editing !== null ? "Guardar corrección" : justSaved ? "✓ Serie guardada" : draft.exerciseId ? `✓ Hice la ${nextLabel()}` : "Elegí un ejercicio");
    if (justSaved) save.classList.add("saved");
    const warning = entry.limit ? el("p", { class: "notice" }, `El máximo es ${weight(500, unit)}. Revisá el peso.`)
      : entry.confirm ? el("p", { class: "notice" }, `¿Seguro ${weight(toKg(entry.weight, unit), unit)}? Es mucho más que tu referencia. Tocá de nuevo para confirmar.`)
        : "";
    bar.toast.hidden = !undo;
    if (undo) {
      bar.toast.replaceChildren(el("span", {}, "Serie borrada"), el("button", { type: "button", class: "secondary", onclick: () => {
        draft.sets.splice(undo.index, 0, undo.removed);
        clearTimeout(undo.handle);
        undo = null;
        persist();
        render();
      } }, "Deshacer"));
    }
    const card = feedback ? feedbackCard(feedback.result, feedback.exercise, unit, pickTarget) : "";
    barNode.replaceChildren(slot, warning, card, bar.toast, bar.timer, save);
  }

  async function render() {
    app.replaceChildren(sessionStrip(draft, finishEarly, sessionCard()), planChips(), await exerciseCard(), setsCard());
    renderBar();
    app.append(barNode);
  }

  // La barra crece con el descanso, los avisos o el deshacer: el fondo de la página crece con ella.
  const resize = new ResizeObserver(() => document.body.style.setProperty("--logger-bar-h", `${barNode.offsetHeight}px`));
  resize.observe(barNode);
  // Las medallas de antes de la sesión, para festejar al final las que se ganen.
  if (!draft.medalsBefore) earnedMedals(group).then(({ keys }) => { draft.medalsBefore = keys; persist(); }).catch(() => {});
  document.body.classList.add("with-logger-bar");
  window.addEventListener("hashchange", () => { timer.stop(); resize.disconnect(); document.body.classList.remove("with-logger-bar"); }, { once: true });
  if (draft.exerciseId) await prefill();
  await render();
}
