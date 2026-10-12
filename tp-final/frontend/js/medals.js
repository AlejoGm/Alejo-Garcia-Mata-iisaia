import { icon } from "./icons.js";
import { el } from "./ui.js";

export function shortDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("es-AR", { day: "numeric", month: "short", year: "2-digit" });
}

/** Grilla de medallas: las ganadas con su día, las que faltan apagadas con lo que piden. */
export function medalsCard(achievements, title = "Medallas") {
  const earned = achievements.filter((m) => m.day).length;
  return el("section", { class: "card" },
    el("div", { class: "spread" }, el("h3", {}, title), el("span", { class: "pill accent" }, `${earned} de ${achievements.length}`)),
    el("ul", { class: "medals" }, achievements.map((m) => el("li", { class: `medal${m.day ? " earned" : ""}` },
      el("span", { class: "medal-icon" }, icon("medal", 22)),
      el("strong", {}, m.title),
      el("span", { class: "muted small" }, m.day ? shortDate(m.day) : m.description)))));
}
