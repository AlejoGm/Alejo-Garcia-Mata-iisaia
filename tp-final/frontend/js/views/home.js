import { api } from "../api.js";
import { setChrome, state } from "../app.js";
import { loadDraft } from "../draft.js";
import { icon } from "../icons.js";
import { busy, el, errorBox } from "../ui.js";

const DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

function isoLocal(date) {
  return date.toLocaleDateString("en-CA");
}

/** La semana de lunes a domingo, con un anillo en cada día entrenado. */
export function weekStrip(sessions, goal) {
  const today = new Date();
  const monday = new Date(today);
  monday.setDate(today.getDate() - ((today.getDay() + 6) % 7));
  const trained = new Set(sessions.map((s) => s.date));
  let count = 0;
  const days = DAYS.map((label, index) => {
    const day = new Date(monday);
    day.setDate(monday.getDate() + index);
    const iso = isoLocal(day);
    const done = trained.has(iso);
    if (done) count += 1;
    const isToday = iso === isoLocal(today);
    return el("li", { class: ["day", done ? "done" : "", isToday ? "today" : ""].join(" ").trim() },
      el("span", { class: "day-label" }, label),
      el("span", { class: "day-ring", "aria-label": `${label} ${day.getDate()}${done ? ", entrenaste" : ""}` }, String(day.getDate())));
  });
  const left = goal ? Math.max(0, goal - count) : null;
  const caption = !goal ? `${count} días entrenados esta semana`
    : left === 0 ? `Objetivo cumplido: ${count} de ${goal} días`
      : `${count} de ${goal} días, te faltan ${left}`;
  return el("section", { class: "week", "aria-label": "Tu semana" },
    el("ol", { class: "week-days" }, days),
    el("p", { class: "week-caption" }, caption));
}

function heroCard(groups) {
  const draft = loadDraft();
  if (draft) {
    return el("a", { class: "hero-card", href: `#/g/${draft.code}/carga` },
      el("span", { class: "hero-icon" }, icon("train", 30)),
      el("span", { class: "hero-text" }, el("strong", {}, "Seguí tu sesión"), el("span", {}, `${draft.title}, ${draft.sets.length} series cargadas`)),
      el("span", { class: "hero-cta" }, "Seguir"));
  }
  if (!groups.length) return null;
  return el("a", { class: "hero-card", href: `#/g/${groups[0].code}/entrenar` },
    el("span", { class: "hero-icon" }, icon("train", 30)),
    el("span", { class: "hero-text" }, el("strong", {}, "Entrenar hoy"), el("span", {}, groups[0].name)),
    el("span", { class: "hero-cta" }, "Empezar"));
}

function groupList(groups) {
  if (!groups.length) {
    return el("p", { class: "muted" }, "Todavía no estás en ningún grupo. Creá uno o pedile el código a un amigo.");
  }
  return el("ul", { class: "group-list" }, groups.map((g) => el("li", {},
    el("a", { href: `#/g/${g.code}/rankings` },
      el("span", { class: "group-name" }, g.name),
      el("span", { class: "muted small" }, `${g.members} ${g.members === 1 ? "miembro" : "miembros"}${g.is_admin ? ", sos admin" : ""}`)))));
}

function formCard(title, field, buttonText, onSubmit) {
  const button = el("button", { class: "primary big", type: "submit" }, buttonText);
  const error = el("p", { class: "error", role: "alert" });
  const form = el("form", { class: "card" }, el("h3", {}, title), field, button, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    busy(button, error, onSubmit);
  });
  return form;
}

export async function homeView(app) {
  setChrome({ heading: "Gym-bro" });
  let groups;
  let sessions;
  try {
    [groups, sessions] = await Promise.all([api.get("/me/groups"), api.get("/me/sessions?limit=14")]);
  } catch (err) {
    app.replaceChildren(errorBox(err.message));
    return;
  }

  const groupName = el("input", { required: true, maxlength: "40", placeholder: "Los del gym" });
  const code = el("input", { required: true, maxlength: "6", class: "code", autocapitalize: "characters",
    autocomplete: "off", placeholder: "ABC234" });
  const create = formCard("Crear un grupo", el("label", {}, "Nombre", groupName), "Crear", async () => {
    const group = await api.post("/groups", { name: groupName.value.trim() });
    window.location.hash = `#/g/${group.code}/grupo`;
  });
  const join = formCard("Unirme con un código", el("label", {}, "Código", code), "Unirme", async () => {
    const group = await api.post(`/groups/${code.value.trim().toUpperCase()}/join`);
    window.location.hash = `#/g/${group.code}/entrenar`;
  });

  app.replaceChildren(
    el("header", { class: "greeting" },
      el("h2", {}, `Hola, ${state.me.display_name}`),
      el("p", { class: "muted" }, "¿Qué toca hoy?")),
    weekStrip(sessions, state.me.weekly_goal),
    heroCard(groups) || "",
    el("section", { class: "card" },
      el("div", { class: "spread" }, el("h3", {}, "Tus grupos"),
        el("a", { href: "#/stats", class: "button ghost" }, icon("chart", 20), "Mis stats")),
      groupList(groups)),
    el("div", { class: "grid-2" }, join, create),
  );
}
