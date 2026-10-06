import { icon } from "../icons.js";
import { el, weight } from "../ui.js";

const PR_LABEL = { weight: "PR de peso", "1rm": "PR de 1RM" };

export function setLine(s, unit) {
  return el("li", {},
    el("span", {}, `${s.exercise} · ${weight(s.weight_kg, unit)} × ${s.reps}`),
    s.pr ? el("span", { class: "pill accent" }, PR_LABEL[s.pr]) : el("span", { class: "muted small" },
      s.estimated_1rm ? `1RM ${weight(s.estimated_1rm, unit)}` : ""));
}

export function sessionSummary(app, group, saved, unit) {
  const prs = saved.sets.filter((s) => s.pr).length;
  app.replaceChildren(
    el("div", { class: "card summary" },
      el("span", { class: `summary-icon${prs ? " hot" : ""}` }, icon(prs ? "trophy" : "train", 40)),
      el("h2", {}, prs ? `¡${prs} ${prs === 1 ? "PR" : "PRs"} hoy!` : "Sesión guardada"),
      el("p", { class: "muted" }, `${saved.sets.length} series el ${saved.date}`),
      el("ul", { class: "list" }, saved.sets.map((s) => setLine(s, unit)))),
    el("div", { class: "actions" },
      el("a", { class: "button primary big", href: `#/g/${group.code}/rankings` }, "Ver rankings"),
      el("a", { class: "button big", href: `#/g/${group.code}/entrenar` }, "Volver")),
  );
}
