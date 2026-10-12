import { api } from "../api.js";
import { state } from "../app.js";
import { groupChrome, loadGroup } from "../group-shell.js";
import { medalsCard, shortDate } from "../medals.js";
import { avatar, el, errorBox, num, weight } from "../ui.js";

function headCard(bro) {
  const week = bro.weekly_goal ? `${bro.week_days} de ${bro.weekly_goal} días esta semana` : `${bro.week_days} días esta semana`;
  const streak = bro.streak ? `, racha de ${bro.streak} ${bro.streak === 1 ? "semana" : "semanas"}` : "";
  return el("section", { class: "card" }, el("div", { class: "person" }, avatar(bro.display_name, "lg"),
    el("span", { class: "person-text" }, el("h2", {}, bro.display_name), el("span", { class: "muted" }, `${week}${streak}`)),
    bro.is_me ? el("span", { class: "pill accent" }, "vos") : ""));
}

function faceoffCard(group, bro, unit) {
  const mine = bro.faceoff.filter((f) => f.winner === "mine").length;
  const theirs = bro.faceoff.filter((f) => f.winner === "theirs").length;
  const cell = (kg, dots, won) => el("td", { class: `num${won ? " winner" : ""}` }, weight(kg, unit),
    el("span", { class: "dots-note" }, `${num(dots)} DOTS`));
  return el("section", { class: "card" },
    el("div", { class: "spread" }, el("h3", {}, "Cara a cara"), el("a", { class: "button ghost", href: `#/g/${group.code}/duelos` }, "Retar")),
    el("p", { class: "muted small" }, "Mejor 1RM de los últimos 6 meses en lo que hicieron los dos. Gana el de más DOTS."),
    bro.faceoff.length ? [
      el("div", { class: "score" }, el("span", {}, "Vos"), el("strong", {}, `${mine} – ${theirs}`), el("span", {}, bro.display_name)),
      el("table", {}, el("thead", {}, el("tr", {}, el("th", {}, "Ejercicio"), el("th", { class: "num" }, "Vos"), el("th", { class: "num" }, bro.display_name))),
        el("tbody", {}, bro.faceoff.map((f) => el("tr", {}, el("td", {}, f.exercise),
          cell(f.mine_1rm, f.mine_dots, f.winner === "mine"), cell(f.theirs_1rm, f.theirs_dots, f.winner === "theirs"))))),
    ] : el("p", { class: "muted" }, "Todavía no hicieron un mismo ejercicio en estos 6 meses."));
}

function sessionsCard(bro) {
  return el("section", { class: "card" }, el("h3", {}, "Últimas sesiones"),
    bro.sessions.length ? el("ul", { class: "list" }, bro.sessions.map((s) => el("li", {},
      el("span", { class: "person-text" },
        el("strong", {}, `${shortDate(s.date)}${s.routine_day_name ? `, ${s.routine_day_name}` : ""}`),
        el("span", { class: "muted small" }, `${s.sets} series: ${s.exercises.join(", ")}`)),
      s.prs ? el("span", { class: "pill accent" }, `${s.prs} PR`) : "")))
      : el("p", { class: "muted" }, "Todavía no cargó sesiones."));
}

export async function broView(app, { code, id }) {
  const group = await loadGroup(code.toUpperCase());
  groupChrome(group, null, `#/g/${group.code}/panel`);
  let bro;
  try {
    bro = await api.get(`/groups/${group.code}/members/${id}`);
  } catch (err) {
    app.replaceChildren(errorBox(err.message));
    return;
  }
  app.replaceChildren(headCard(bro), el("div", { class: "cards-grid" },
    bro.is_me ? "" : faceoffCard(group, bro, state.me.unit),
    sessionsCard(bro),
    medalsCard(bro.achievements, bro.is_me ? "Tus medallas" : `Medallas de ${bro.display_name}`)));
}
