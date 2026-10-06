import { api } from "../api.js";
import { setChrome, state } from "../app.js";
import { lineChart } from "../charts.js";
import { icon } from "../icons.js";
import { el, errorBox, storageGet, storageSet, toDisplay, weight } from "../ui.js";

const PERIODS = [["6m", "6 meses"], ["12m", "12 meses"], ["all", "Todo"]];
const PREFS = "gymbro.statsPrefs";

function monthShort(iso) {
  const [y, m] = iso.split("-").map(Number);
  return new Date(y, m - 1, 1).toLocaleDateString("es-AR", { month: "short" });
}

function dayShort(iso) {
  const [, m, d] = iso.split("-").map(Number);
  return `${d}/${m}`;
}

function legend(items) {
  return el("div", { class: "legend" }, items.map(([cls, text]) => el("span", { class: `legend-item ${cls}` }, text)));
}

export async function statsView(app) {
  setChrome({ heading: "Mis stats", backTo: "#/" });
  const prefs = { period: "6m", exercise_id: null, ...storageGet(PREFS, {}) };
  const unit = state.me.unit;
  const conv = (v) => toDisplay(v, unit);

  async function render() {
    const query = new URLSearchParams({ period: prefs.period });
    if (prefs.exercise_id) query.set("exercise_id", prefs.exercise_id);
    let data;
    try {
      data = await api.get(`/me/stats?${query}`);
    } catch (err) {
      app.replaceChildren(errorBox(err.message));
      return;
    }
    if (!data.exercises.length) {
      app.replaceChildren(el("div", { class: "card" }, el("p", { class: "muted" }, "Cuando cargues sesiones, acá vas a ver tu progreso.")));
      return;
    }
    const select = el("select", { "aria-label": "Ejercicio" }, data.exercises.map((e) =>
      el("option", { value: String(e.id), selected: e.id === data.exercise_id }, e.name)));
    select.addEventListener("change", () => { prefs.exercise_id = Number(select.value); save(); });
    const periods = el("div", { class: "segmented" }, PERIODS.map(([value, label]) => el("label", {},
      el("input", { type: "radio", name: "stats-period", value, checked: prefs.period === value,
        onchange: () => { prefs.period = value; save(); } }), el("span", {}, label))));
    const chosen = data.exercises.find((e) => e.id === data.exercise_id);
    const name = chosen?.name ?? "";
    const bestText = data.best_weight_kg === null ? "—"
      : `${chosen?.bodyweight ? (data.best_weight_kg ? `+${weight(data.best_weight_kg, unit)}` : "Sin lastre") : weight(data.best_weight_kg, unit)} × ${data.best_reps}`;
    const thisMonth = new Date().toLocaleDateString("en-CA").slice(0, 7);

    app.replaceChildren(
      el("div", { class: "card" }, select, periods),
      el("div", { class: "stat-tiles" },
        el("div", { class: "card tile" }, el("span", { class: "tile-icon" }, icon("trophy", 22)), el("span", { class: "muted small" }, "Mejor serie"),
          el("strong", {}, bestText)),
        el("div", { class: "card tile" }, el("span", { class: "tile-icon mint" }, icon("bolt", 22)), el("span", { class: "muted small" }, "Mejor 1RM estimado"), el("strong", {}, weight(data.best_1rm, unit))),
        el("div", { class: "card tile" }, el("span", { class: "tile-icon ember" }, icon("clock", 22)), el("span", { class: "muted small" }, "Sesiones con este ejercicio"), el("strong", {}, String(data.sessions)))),
      el("div", { class: "card" }, el("h3", {}, `${name}: 1RM por mes`),
        legend([["best", "mejor"], ["avg", "promedio de sesiones"]]),
        el("p", { class: "muted small" }, "El mes en curso va marcado con * : todavía puede subir."),
        lineChart({ label: `1RM por mes de ${name}`, labels: data.months.map((p) => `${monthShort(p.month)}${p.month.startsWith(thisMonth) ? "*" : ""}`), series: [
          { className: "best", values: data.months.map((p) => conv(p.best)) },
          { className: "avg", values: data.months.map((p) => conv(p.average)) }] })),
      el("div", { class: "card" }, el("h3", {}, `${name}: semana a semana`),
        lineChart({ label: `1RM semanal de ${name}`, labels: data.weeks.map((p) => dayShort(p.week)),
          series: [{ className: "best", values: data.weeks.map((p) => conv(p.best)) }] })),
      el("div", { class: "card" }, el("h3", {}, `Peso corporal (${unit})`),
        lineChart({ label: "Peso corporal por semana", labels: data.bodyweight.map((p) => dayShort(p.week)),
          series: [{ className: "bw", values: data.bodyweight.map((p) => conv(p.kg)) }] })),
    );
  }

  function save() {
    storageSet(PREFS, prefs);
    render();
  }

  await render();
}
