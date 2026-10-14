import { api } from "../api.js";
import { icon } from "../icons.js";
import { celebrate } from "../juice.js";
import { dayLabel, el, liftText, num, toDisplay, weight } from "../ui.js";
import { listNames } from "./set-feedback.js";

const PR_LABEL = { weight: "PR de peso", reps: "PR de reps", "1rm": "PR de 1RM" };

export function setLine(s, unit) {
  return el("li", {},
    el("span", {}, `${s.exercise} · ${liftText(s.weight_kg, s.load, unit)} × ${s.reps}`),
    s.pr ? el("span", { class: "pill accent" }, PR_LABEL[s.pr]) : el("span", { class: "muted small" },
      s.estimated_1rm ? `1RM ${weight(s.estimated_1rm, unit)}` : ""));
}

/** Medallas ganadas hasta ahora, por clave: se guarda al abrir la carga para festejar las nuevas al final. */
export async function earnedMedals(group) {
  const me = await api.get(`/groups/${group.code}/members/${group.me}`);
  return { profile: me, keys: me.achievements.filter((m) => m.day).map((m) => m.key) };
}

/** Un número que sube desde 0, como el puntaje al final de un nivel. */
function countUp(target, format) {
  const node = el("strong", {}, format(0));
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    node.textContent = format(target);
    return node;
  }
  const start = performance.now();
  const step = (now) => {
    const t = Math.min(1, (now - start) / 700);
    node.textContent = format(target * (1 - (1 - t) ** 3));
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
  return node;
}

function scoreRow(saved, unit) {
  const volume = saved.sets.reduce((sum, s) => sum + s.load * s.reps, 0);
  const prs = saved.sets.filter((s) => s.pr).length;
  const cell = (node, label) => el("div", { class: "score-cell" }, node, el("span", { class: "muted small" }, label));
  return el("div", { class: "score-row" },
    cell(countUp(saved.sets.length, (v) => String(Math.round(v))), "series"),
    cell(countUp(toDisplay(volume, unit), (v) => num(Math.round(v), 0)), `${unit} de volumen`),
    cell(countUp(prs, (v) => String(Math.round(v))), prs === 1 ? "PR" : "PRs"));
}

function climbCard(standings, names) {
  const rows = Object.entries(standings ?? {}).filter(([, s]) => s.after !== null).map(([id, s]) => {
    const climbed = s.before === null || s.after < s.before;
    const text = s.before === null ? `entraste ${s.after}º de ${s.total}` : climbed ? `del ${s.before}º al ${s.after}º` : `${s.after}º de ${s.total}`;
    return el("li", {}, el("span", { class: "person-text" }, el("strong", {}, names.get(Number(id)) ?? "?"),
      s.passed.length ? el("span", { class: "muted small" }, `pasaste a ${listNames(s.passed)}`) : ""),
    el("span", { class: climbed ? "accent-number" : "muted" }, text));
  });
  if (!rows.length) return "";
  return el("section", { class: "card" }, el("h3", {}, "Tu lugar en el grupo"), el("ul", { class: "list" }, rows));
}

function weekCard(profile) {
  const goal = profile.weekly_goal;
  const pct = goal ? Math.min(100, (100 * profile.week_days) / goal) : 0;
  const streak = profile.streak ? `Racha de ${profile.streak} ${profile.streak === 1 ? "semana" : "semanas"}` : "Empezá una racha cumpliendo esta semana";
  return el("section", { class: "card" },
    el("div", { class: "spread" }, el("h3", {}, goal ? `Día ${profile.week_days} de ${goal}` : `${profile.week_days} días esta semana`),
      el("span", { class: "muted small" }, streak)),
    goal ? el("div", { class: "progress" }, el("span", { style: `width:${pct}%` })) : "");
}

function medalsCard(profile, before) {
  const fresh = profile.achievements.filter((m) => m.day && !before.includes(m.key));
  if (!fresh.length) return "";
  celebrate();
  return el("section", { class: "card highlight" }, el("h3", {}, fresh.length === 1 ? "¡Medalla nueva!" : "¡Medallas nuevas!"),
    el("ul", { class: "list" }, fresh.map((m) => el("li", {},
      el("span", { class: "who" }, el("span", { class: "medal-icon earned" }, icon("medal", 22)),
        el("span", { class: "person-text" }, el("strong", {}, m.title), el("span", { class: "muted small" }, m.description)))))));
}

export async function sessionSummary(app, group, saved, unit, finished = {}) {
  const prs = saved.sets.filter((s) => s.pr).length;
  if (prs) celebrate();
  const names = new Map(saved.sets.map((s) => [s.exercise_id, s.exercise]));
  const after = await earnedMedals(group).catch(() => null);
  app.replaceChildren(
    el("div", { class: "card summary" },
      el("span", { class: `summary-icon${prs ? " hot" : ""}` }, icon(prs ? "trophy" : "train", 40)),
      el("h2", {}, prs ? `¡${prs} ${prs === 1 ? "PR" : "PRs"} hoy!` : "Sesión guardada"),
      el("p", { class: "muted" }, dayLabel(saved.date)),
      scoreRow(saved, unit)),
    after && finished.medalsBefore ? medalsCard(after.profile, finished.medalsBefore) : "",
    climbCard(finished.standings, names),
    after ? weekCard(after.profile) : "",
    el("details", { class: "card" }, el("summary", {}, "Series de la sesión"), el("ul", { class: "list" }, saved.sets.map((s) => setLine(s, unit)))),
    el("div", { class: "actions" },
      el("a", { class: "button primary big", href: `#/g/${group.code}/rankings` }, "Ver rankings"),
      el("a", { class: "button big", href: `#/g/${group.code}/entrenar` }, "Volver")),
  );
}
