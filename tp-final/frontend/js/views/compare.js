// Comparar en el panel: las gráficas de mis stats, con una línea por cada miembro que elijas.
import { api } from "../api.js";
import { state } from "../app.js";
import { lineChart } from "../charts.js";
import { el, errorBox, storageGet, storageSet, toDisplay } from "../ui.js";

const COLORS = 10;  // p0..p9 en el CSS: cada miembro tiene siempre el mismo color
const PERIODS = [["6m", "6 meses"], ["12m", "12 meses"], ["all", "Todo"]];
const METRICS = [["dots", "DOTS"], ["1rm", "Kilos (1RM)"]];

function monthShort(iso) {
  const [y, m] = iso.split("-").map(Number);
  return new Date(y, m - 1, 1).toLocaleDateString("es-AR", { month: "short" });
}

function dayShort(iso) {
  const [, m, d] = iso.split("-").map(Number);
  return `${d}/${m}`;
}

function segmented(name, options, selected, onChange) {
  return el("div", { class: "segmented" }, options.map(([value, label]) => el("label", {},
    el("input", { type: "radio", name, value, checked: value === selected, onchange: () => onChange(value) }), el("span", {}, label))));
}

/** Arranca con vos y los tres que mejor vienen en el último mes con datos. */
function defaultSelection(data, me) {
  const last = (p) => [...p.months].reverse().find((v) => v !== null) ?? -1;
  const others = data.people.filter((p) => p.user_id !== me).sort((a, b) => last(b) - last(a)).slice(0, 3);
  return [me, ...others.map((p) => p.user_id)];
}

export function compareSection(group) {
  const box = el("section", { class: "card span-12 compare" }, el("p", { class: "muted" }, "Cargando..."));
  const key = `gymbro.compare.${group.code}`;
  const prefs = { metric: "dots", period: "6m", exercise_id: null, selected: null, ...storageGet(key, {}) };
  const save = () => storageSet(key, prefs);
  const color = new Map(group.members.map((m, i) => [m.user_id, `p${i % COLORS}`]));

  async function render() {
    const query = new URLSearchParams({ metric: prefs.metric, period: prefs.period });
    if (prefs.exercise_id) query.set("exercise_id", prefs.exercise_id);
    let data;
    try {
      data = await api.get(`/groups/${group.code}/compare?${query}`);
    } catch (err) {
      box.replaceChildren(errorBox(err.message));
      return;
    }
    if (!data.exercises.length) {
      box.replaceChildren(el("h3", {}, "Comparar"), el("p", { class: "muted" }, "Cuando el grupo cargue sesiones, acá van a ver sus curvas lado a lado."));
      return;
    }
    const known = new Set(data.people.map((p) => p.user_id));
    const selected = new Set((prefs.selected ?? defaultSelection(data, group.me)).filter((id) => known.has(id)));
    const shown = data.people.filter((p) => selected.has(p.user_id));
    const exercise = data.exercises.find((e) => e.id === data.exercise_id);
    const unit = state.me.unit;
    const value = (v) => (v === null ? null : prefs.metric === "1rm" ? toDisplay(v, unit) : v);

    const select = el("select", { "aria-label": "Ejercicio" }, data.exercises.map((e) =>
      el("option", { value: String(e.id), selected: e.id === data.exercise_id }, e.name)));
    select.addEventListener("change", () => { prefs.exercise_id = Number(select.value); save(); render(); });
    const people = el("div", { class: "people-chips" }, data.people.map((p) => el("button", {
      type: "button", class: `person-chip ${color.get(p.user_id)}${selected.has(p.user_id) ? " on" : ""}`,
      "aria-pressed": String(selected.has(p.user_id)),
      onclick: () => {
        if (selected.has(p.user_id)) selected.delete(p.user_id); else selected.add(p.user_id);
        prefs.selected = [...selected];
        save();
        render();
      },
    }, el("span", { class: "swatch" }), p.user_id === group.me ? "Vos" : p.display_name)));

    const what = prefs.metric === "dots" ? "DOTS del mejor 1RM" : `mejor 1RM en ${unit}`;
    box.replaceChildren(
      el("div", { class: "spread" }, el("h3", {}, "Comparar"), el("span", { class: "muted small" }, "Tocá un nombre para sumarlo o sacarlo")),
      people,
      el("div", { class: "compare-controls" }, select, segmented("compare-metric", METRICS, prefs.metric, (v) => { prefs.metric = v; save(); render(); }),
        segmented("compare-period", PERIODS, prefs.period, (v) => { prefs.period = v; save(); render(); })),
      el("div", { class: "compare-charts" },
        el("div", {}, el("h4", {}, `${exercise?.name ?? ""}: ${what}, por mes`),
          prefs.metric === "dots" ? el("p", { class: "muted small" }, "DOTS ajusta por peso corporal y sexo: compara parejo entre personas distintas.") : "",
          lineChart({ label: `${exercise?.name}, ${what} por mes`, area: false, labels: data.months.map(monthShort),
            series: shown.map((p) => ({ className: color.get(p.user_id), values: p.months.map(value) })) })),
        el("div", {}, el("h4", {}, "Días entrenados por semana"),
          el("p", { class: "muted small" }, "Las últimas 12 semanas; la actual va en curso."),
          lineChart({ label: "Días entrenados por semana", area: false, labels: data.weeks.map(dayShort),
            series: shown.map((p) => ({ className: color.get(p.user_id), values: p.days })) }))),
    );
  }

  render();
  return box;
}
