import { api } from "../api.js";
import { loadMe, state } from "../app.js";
import { clearDraft, loadDraft, newDraft, saveDraft } from "../draft.js";
import { icon } from "../icons.js";
import { busy, el, today, toDisplay } from "../ui.js";
import { setLine } from "./session-summary.js";

function startDraft(group, options) {
  saveDraft(newDraft({ code: group.code, date: today(), bodyweight: toDisplay(state.me.last_bodyweight_kg, state.me.unit), ...options }));
  window.location.hash = `#/g/${group.code}/carga`;
}

function pendingCard(group, draft) {
  if (!draft) return null;
  const resume = el("a", { class: "button primary big", href: `#/g/${draft.code}/carga` }, "Seguir");
  const discard = el("button", { type: "button", class: "secondary" }, "Descartar");
  discard.addEventListener("click", () => {
    if (!window.confirm("¿Descartar la sesión sin terminar?")) return;
    clearDraft();
    trainView(document.getElementById("app"), group);
  });
  return el("div", { class: "card highlight" },
    el("h3", {}, "Tenés una sesión sin terminar"),
    el("p", { class: "muted" }, `${draft.title} · ${draft.sets.length} series cargadas`),
    el("div", { class: "row" }, discard, resume));
}

function dateLabel(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "short" });
}

async function historyCard(unit) {
  const sessions = await api.get("/me/sessions?limit=5");
  if (!sessions.length) return el("div", { class: "card" }, el("h3", {}, "Tus sesiones"), el("p", { class: "muted" }, "Todavía no cargaste ninguna."));
  const error = el("p", { class: "error", role: "alert" });
  const blocks = sessions.map((s) => {
    const prs = s.sets.filter((x) => x.pr).length;
    const remove = el("button", { type: "button", class: "danger" }, "Borrar sesión");
    remove.addEventListener("click", () => {
      if (!window.confirm(`¿Borrar la sesión del ${s.date}? No se puede deshacer.`)) return;
      busy(remove, error, async () => {
        await api.del(`/me/sessions/${s.id}`);
        remove.closest("details").remove();
      });
    });
    return el("details", { class: "activity" },
      el("summary", {},
        el("span", { class: `activity-icon${prs ? " hot" : ""}` }, icon(prs ? "trophy" : "train", 26)),
        el("span", { class: "activity-text" },
          el("strong", {}, s.routine_day_name || "Carga libre"),
          el("span", { class: "muted small" }, prs ? `${dateLabel(s.date)}, ${prs} PR` : dateLabel(s.date))),
        el("span", { class: "activity-number" }, el("strong", {}, String(s.sets.length)), el("span", {}, "series"))),
      el("ul", { class: "list" }, s.sets.map((x) => setLine(x, unit))), remove);
  });
  return el("section", { class: "card" }, el("h3", {}, "Tus últimas sesiones"), el("div", { class: "activity-list" }, blocks), error);
}

function dayButtons(group, routine, hasDraft) {
  if (!routine) {
    return el("p", { class: "muted small" }, "No seguís ninguna rutina. Elegí una en Grupo → Rutinas, o cargá libre.");
  }
  return el("div", { class: "actions" }, el("p", { class: "muted small" }, routine.name), routine.days.map((day) => {
    const button = el("button", { type: "button", class: "big day-button" },
      el("span", {}, day.name), el("span", { class: "muted small" }, day.items.map((i) => i.exercise).join(" · ")));
    button.addEventListener("click", () => {
      if (hasDraft && !window.confirm("Tenés una sesión sin terminar. ¿Empezar otra y descartarla?")) return;
      startDraft(group, {
        title: `${routine.name} · ${day.name}`,
        routineDayId: day.id,
        plan: day.items.map((i) => ({ exercise_id: i.exercise_id, name: i.exercise, sets: i.sets })),
      });
    });
    return button;
  }));
}

export async function trainView(app, group) {
  await loadMe(true);
  const draft = loadDraft();
  const myRoutineId = group.members.find((m) => m.user_id === group.me)?.routine_id;
  const routines = myRoutineId ? await api.get(`/groups/${group.code}/routines`) : [];
  const free = el("button", { type: "button", class: "secondary big" }, "Carga libre");
  free.addEventListener("click", () => {
    if (draft && !window.confirm("Tenés una sesión sin terminar. ¿Empezar otra y descartarla?")) return;
    startDraft(group, {});
  });
  app.replaceChildren(
    pendingCard(group, draft) || "",
    el("div", { class: "card" }, el("h3", {}, "Entrenar hoy"),
      dayButtons(group, routines.find((r) => r.id === myRoutineId), Boolean(draft)), free),
    await historyCard(state.me.unit),
  );
}
