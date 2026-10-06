import { api } from "../api.js";
import { loadMe, state } from "../app.js";
import { clearDraft, loadDraft, saveDraft, setsDone } from "../draft.js";
import { el, errorBox, num, toDisplay, toKg, weight } from "../ui.js";
import { clock, lastLine, loadText, restTimer, stepper, suspicious } from "./logger-parts.js";
import { sessionSummary } from "./session-summary.js";

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
  const bar = { timer: el("button", { type: "button", class: "rest", hidden: true }), toast: el("div", { class: "toast", hidden: true }) };
  const timer = restTimer((left) => {
    bar.timer.hidden = left === null;
    bar.timer.textContent = left === 0 ? "¡Descanso terminado!" : `Descanso ${clock(left ?? 0)} · +30 s`;
  });
  bar.timer.addEventListener("click", () => (timer.running() ? timer.add(30) : timer.stop()));
  let undo = null;

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

  function removeSet(index) {
    entry.editing = null;
    const [removed] = draft.sets.splice(index, 1);
    persist();
    clearTimeout(undo?.handle);
    undo = { removed, index, handle: setTimeout(() => { undo = null; renderBar(); }, 6000) };
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
    if (!draft.plan.length) return "";
    return el("div", { class: "chips" }, draft.plan.map((item, index) => {
      const done = setsDone(draft, item.exercise_id);
      return el("button", { type: "button", class: `chip${index === draft.step ? " active" : ""}${done >= item.sets ? " done" : ""}`,
        onclick: () => { draft.step = index; chooseExercise(item.exercise_id); } }, `${item.name} ${done}/${item.sets}`);
    }));
  }

  async function exerciseCard() {
    const item = planItem();
    const exercise = byId.get(draft.exerciseId);
    if (!exercise) {
      return el("div", { class: "card logger" },
        el("h3", {}, draft.plan.length ? "Rutina completa" : "¿Qué ejercicio hacés?"),
        draft.plan.length ? el("p", { class: "muted small" }, "Sumá otro ejercicio o terminá la sesión.") : "",
        exercisePicker());
    }
    const done = setsDone(draft, exercise.id);
    const label = item && item.exercise_id === exercise.id
      ? (done < item.sets ? `Serie ${done + 1} de ${item.sets}` : `Serie ${done + 1} (extra)`) : `Serie ${done + 1}`;
    const last = await lastFor(exercise.id);
    const editing = entry.editing !== null
      ? el("div", { class: "notice spread" }, el("span", {}, `Editando la serie ${entry.editing + 1}`),
        el("button", { type: "button", class: "secondary", style: "flex:0", onclick: cancelEdit }, "Cancelar"))
      : "";
    return el("div", { class: "card logger" },
      el("div", { class: "spread" }, el("h3", { class: "exercise-name" }, exercise.name), el("span", { class: "pill accent" }, label)),
      editing,
      el("p", { class: "muted small" }, last ? lastLine(last, unit, exercise.bodyweight) : ""),
      exercise.bodyweight ? el("p", { class: "muted small" }, "Ejercicio con tu peso: cargá solo el lastre. El 1RM suma tu peso corporal.") : "",
      el("div", { class: "steppers" },
        stepper(exercise.bodyweight ? `Lastre (${unit})` : `Peso (${unit})`, entry.weight, unit === "lb" ? 5 : 2.5,
          (v) => { entry.weight = v; entry.confirm = false; entry.limit = false; }),
        stepper("Reps", entry.reps, 1, (v) => { entry.reps = v; entry.confirm = false; })),
      el("div", { class: "row" },
        item ? el("button", { type: "button", class: "secondary", onclick: async () => { advanceToNextIncomplete(); if (draft.exerciseId) await prefill(); persist(); render(); } }, "Siguiente ejercicio") : "",
        el("details", { class: "change" }, el("summary", {}, "Cambiar ejercicio"), exercisePicker())));
  }

  function setsCard() {
    if (!draft.sets.length) return "";
    const items = draft.sets.map((s, index) => el("li", { class: index === entry.editing ? "editing" : null },
      el("button", { type: "button", class: "set-edit", onclick: () => editSet(index), "aria-label": "Corregir serie" },
        `${index + 1}. ${byId.get(s.exercise_id)?.name ?? "?"} · ${loadText(s.weight_kg, unit, byId.get(s.exercise_id)?.bodyweight)} × ${s.reps}`),
      el("button", { type: "button", class: "secondary", style: "flex:0", "aria-label": "Borrar serie", onclick: () => removeSet(index) }, "×")));
    return el("div", { class: "card" }, el("h3", {}, `Series de hoy (${draft.sets.length})`),
      el("p", { class: "muted small" }, "Tocá una serie para corregirla."), el("ul", { class: "list" }, items));
  }

  function sessionCard() {
    const summary = el("summary", {});
    const describe = () => { summary.textContent = `${draft.title} · ${draft.date} · ${draft.bodyweight ? `${num(draft.bodyweight)} ${unit}` : "falta tu peso"}`; };
    describe();
    const date = el("input", { type: "date", value: draft.date, max: new Date().toLocaleDateString("en-CA") });
    date.addEventListener("change", () => { draft.date = date.value; persist(); describe(); });
    const bodyweight = el("input", { type: "number", inputmode: "decimal", value: String(draft.bodyweight ?? "") });
    bodyweight.addEventListener("input", () => { draft.bodyweight = Number(bodyweight.value) || null; persist(); describe(); });
    const discard = el("button", { type: "button", class: "danger" }, "Descartar sesión");
    discard.addEventListener("click", () => {
      if (draft.sets.length && !window.confirm("¿Descartar las series de esta sesión?")) return;
      clearDraft();
      timer.stop();
      document.body.classList.remove("with-logger-bar");
      window.location.hash = `#/g/${group.code}/entrenar`;
    });
    return el("details", { class: "card", open: !draft.bodyweight }, summary,
      el("div", { class: "row" }, el("label", {}, "Fecha", date), el("label", {}, `Peso corporal (${unit})`, bodyweight)), discard);
  }

  const slot = el("div");
  const barNode = el("div", { class: "logger-bar" });

  function renderBar() {
    const save = el("button", { type: "button", class: "primary big save-set", disabled: !draft.exerciseId, onclick: saveSet },
      entry.confirm ? `Confirmar ${weight(toKg(entry.weight, unit), unit)}` : entry.editing !== null ? "Guardar cambio" : "Guardar serie");
    const warning = entry.limit ? el("p", { class: "notice" }, `El máximo es ${weight(500, unit)}. Revisá el peso.`)
      : entry.confirm ? el("p", { class: "notice" }, `¿Seguro ${weight(toKg(entry.weight, unit), unit)}? Es mucho más que tu referencia. Tocá de nuevo para confirmar.`)
        : "";
    const finishButton = el("button", { type: "button", class: "secondary finish", disabled: draft.sets.length === 0 }, `Terminar (${draft.sets.length})`);
    finishButton.addEventListener("click", () => finish(finishButton, slot));
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
    barNode.replaceChildren(slot, warning, bar.toast, bar.timer, el("div", { class: "bar-row" }, finishButton, save));
  }

  async function render() {
    app.replaceChildren(sessionCard(), planChips(), await exerciseCard(), setsCard());
    renderBar();
    app.append(barNode);
  }

  document.body.classList.add("with-logger-bar");
  window.addEventListener("hashchange", () => { timer.stop(); document.body.classList.remove("with-logger-bar"); }, { once: true });
  if (draft.exerciseId) await prefill();
  await render();
}
