import { api } from "../api.js";
import { state } from "../app.js";
import { clearDraft, loadDraft, newDraft, saveDraft } from "../draft.js";
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

async function historyCard(unit) {
  const sessions = await api.get("/me/sessions?limit=5");
  if (!sessions.length) return el("div", { class: "card" }, el("h3", {}, "Tus sesiones"), el("p", { class: "muted" }, "Todavía no cargaste ninguna."));
  const error = el("p", { class: "error", role: "alert" });
  const blocks = sessions.map((s) => {
    const remove = el("button", { type: "button", class: "danger", style: "flex:0" }, "Borrar");
    remove.addEventListener("click", () => {
      if (!window.confirm(`¿Borrar la sesión del ${s.date}? No se puede deshacer.`)) return;
      busy(remove, error, async () => {
        await api.del(`/me/sessions/${s.id}`);
        remove.closest("details").remove();
      });
    });
    return el("details", { class: "session" },
      el("summary", {}, `${s.date} · ${s.sets.length} series${s.sets.some((x) => x.pr) ? " · PR" : ""}`),
      el("ul", { class: "list" }, s.sets.map((x) => setLine(x, unit))), remove);
  });
  return el("div", { class: "card" }, el("h3", {}, "Tus últimas sesiones"), blocks, error);
}

export async function trainView(app, group) {
  const draft = loadDraft();
  const free = el("button", { type: "button", class: "primary big" }, "Carga libre");
  free.addEventListener("click", () => startDraft(group, {}));
  const routinesSlot = el("div", { id: "routine-days" });
  app.replaceChildren(
    pendingCard(group, draft) || "",
    el("div", { class: "card" }, el("h3", {}, "Entrenar hoy"), routinesSlot, free),
    await historyCard(state.me.unit),
  );
  return { routinesSlot, startDraft: (options) => startDraft(group, options), hasDraft: Boolean(draft) };
}
