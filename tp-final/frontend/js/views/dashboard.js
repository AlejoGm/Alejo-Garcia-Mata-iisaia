import { api } from "../api.js";
import { poll, state } from "../app.js";
import { barChart, gauge, sparkline } from "../charts.js";
import { loadDraft } from "../draft.js";
import { icon } from "../icons.js";
import { avatar, el, errorBox, num, toDisplay } from "../ui.js";
import { campaignBanner } from "./rankings.js";
import { startDraft } from "./train.js";

const DAY_LABELS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
const PR_LABEL = { weight: "PR de peso", "1rm": "PR de 1RM" };

// La semana en curso no está terminada: se muestra la anterior completa en vez de un porcentaje que desmotiva.
const lastWeek = (text) => `semana pasada: ${text}`;

function volumeText(kg, unit) {
  const value = toDisplay(kg, unit);
  return value >= 10000 ? `${num(value / 1000)} t` : `${num(value, 0)} ${unit}`;
}

function kpi({ iconName, tone = "", label, value, note, spark }) {
  return el("section", { class: "card kpi" },
    el("div", { class: "kpi-head" }, el("span", { class: `tile-icon ${tone}` }, icon(iconName, 20)), el("span", { class: "muted small" }, label)),
    spark || "",
    el("strong", { class: "kpi-value" }, value),
    el("span", { class: "muted small" }, note));
}

function weekCard(days) {
  const today = new Date().toLocaleDateString("en-CA");
  return el("section", { class: "card span-6" },
    el("div", { class: "spread" }, el("h3", {}, "La semana del grupo"), el("span", { class: "legend" }, el("span", { class: "legend-item" }, "días tuyos"))),
    el("p", { class: "muted small" }, "Cuántos miembros entrenaron cada día."),
    barChart(days.map((d, i) => ({ label: DAY_LABELS[i], value: d.members, highlight: d.mine, today: d.day === today })), "Miembros que entrenaron por día"));
}

function goalCard(pct) {
  const text = pct === null ? "Nadie fijó objetivo todavía." : pct >= 100 ? "El grupo cumplió la semana." : "Sesiones de cada uno, hasta su objetivo, sobre el total de objetivos.";
  return el("section", { class: "card span-3 center" }, el("h3", {}, "Objetivo del grupo"), gauge(pct, "Objetivo semanal del grupo"),
    el("p", { class: "muted small" }, text));
}

async function todayCard(group) {
  const myRoutineId = group.members.find((m) => m.user_id === group.me)?.routine_id;
  const box = el("section", { class: "card span-3" }, el("h3", {}, "Hoy toca"));
  if (!myRoutineId) {
    box.append(el("p", { class: "muted small" }, "No seguís ninguna rutina."), el("a", { class: "button", href: `#/g/${group.code}/grupo` }, "Elegir rutina"));
    return box;
  }
  const [routines, sessions] = await Promise.all([api.get(`/groups/${group.code}/routines`), api.get("/me/sessions?limit=20")]);
  const routine = routines.find((r) => r.id === myRoutineId);
  if (!routine) return box;
  const dayIds = routine.days.map((d) => d.id);
  const last = sessions.find((s) => dayIds.includes(s.routine_day_id));
  // El día que sigue al último que hiciste de esta rutina; si nunca hiciste ninguno, el primero.
  const day = last ? routine.days[(dayIds.indexOf(last.routine_day_id) + 1) % routine.days.length] : routine.days[0];
  const start = el("button", { type: "button", class: "primary" }, loadDraft() ? "Seguir sesión" : `Empezar ${day.name}`);
  start.addEventListener("click", () => {
    if (loadDraft()) { window.location.hash = `#/g/${group.code}/carga`; return; }
    startDraft(group, { title: `${routine.name} · ${day.name}`, routineDayId: day.id,
      plan: day.items.map((i) => ({ exercise_id: i.exercise_id, name: i.exercise, sets: i.sets })) });
  });
  box.append(el("p", { class: "today-day" }, day.name),
    el("ul", { class: "today-list" }, day.items.slice(0, 5).map((i) => el("li", {}, el("span", {}, i.exercise), el("span", { class: "muted" }, `${i.sets} series`)))),
    day.items.length > 5 ? el("p", { class: "muted small" }, `y ${day.items.length - 5} más`) : "",
    start);
  return box;
}

function leadersCard(leaders) {
  return el("section", { class: "card span-4" }, el("h3", {}, "Líderes del mes"), el("p", { class: "muted small" }, "El primero en DOTS de cada desafío."),
    leaders.length ? el("ul", { class: "list" }, leaders.map((l) => el("li", {},
      el("span", { class: "who" }, avatar(l.display_name, "sm"), el("span", { class: "person-text" }, el("strong", {}, l.display_name), el("span", { class: "muted small" }, l.exercise))),
      el("strong", { class: "accent-number" }, num(l.value)))))
      : el("p", { class: "muted" }, "Todavía nadie cargó un desafío este mes."));
}

function prsCard(group, feed, unit) {
  return el("section", { class: "card span-4" },
    el("div", { class: "spread" }, el("h3", {}, "Últimos PRs"), el("a", { class: "button ghost", href: `#/g/${group.code}/feed` }, "Ver todo")),
    feed.length ? el("ul", { class: "list" }, feed.map((p) => el("li", {},
      el("span", { class: "who" }, avatar(p.display_name, "sm"), el("span", { class: "person-text" }, el("strong", {}, p.display_name), el("span", { class: "muted small" }, `${p.exercise}, ${PR_LABEL[p.pr]}`))),
      el("strong", { class: "accent-number" }, `${num(toDisplay(p.weight_kg, unit))}×${p.reps}`))))
      : el("p", { class: "muted" }, "Todavía no hay PRs."));
}

export async function dashboardView(app, group) {
  const unit = state.me.unit;

  async function render() {
    let data;
    let feed;
    let campaigns;
    try {
      [data, feed, campaigns] = await Promise.all([api.get(`/groups/${group.code}/dashboard`),
        api.get(`/groups/${group.code}/feed?limit=4`), api.get(`/groups/${group.code}/campaigns`).catch(() => [])]);
    } catch (err) {
      app.replaceChildren(errorBox(err.message));
      return;
    }
    const sessions = data.series.map((w) => w.sessions);
    const volumes = data.series.map((w) => w.volume);
    const campaign = campaignBanner(group, campaigns);
    app.replaceChildren(el("div", { class: "dash" },
      kpi({ iconName: "train", label: "Sesiones esta semana", value: String(data.sessions),
        note: lastWeek(String(data.sessions_prev)), spark: sparkline(sessions, "Sesiones por semana") }),
      kpi({ iconName: "bolt", tone: "mint", label: "Volumen esta semana", value: volumeText(data.volume, unit),
        note: lastWeek(volumeText(data.volume_prev, unit)), spark: sparkline(volumes, "Volumen por semana") }),
      kpi({ iconName: "trophy", tone: "ember", label: "PRs del mes", value: String(data.prs_month),
        note: `${data.prs_prev_month} el mes pasado` }),
      kpi({ iconName: "clock", label: "Mejor racha", value: data.best_streak ? `${data.best_streak.weeks} sem.` : "—",
        note: data.best_streak ? `de ${data.best_streak.display_name}` : "nadie cumplió todavía" }),
      weekCard(data.days),
      goalCard(data.goal_pct),
      await todayCard(group),
      leadersCard(data.leaders),
      el("div", { class: "span-4 stack" }, campaign),
      prsCard(group, feed, unit),
    ));
  }

  await render();
  poll(render);
}
