import { api } from "../api.js";
import { poll, state } from "../app.js";
import { el, errorBox, num, storageGet, storageSet, weight } from "../ui.js";

const PERIODS = [["month", "Mes"], ["6m", "6 m"], ["12m", "12 m"], ["all", "Todo"], ["custom", "Elegir"]];
const STATUS = { done: ["cumplido", "ok"], out: ["ya no llega", "bad"], on: ["", ""] };
const PREFS = "gymbro.rankingPrefs";

function currentMonth() {
  return new Date().toLocaleDateString("en-CA").slice(0, 7);
}

function shiftMonth(month, delta) {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function monthLabel(month) {
  const [y, m] = month.split("-").map(Number);
  const text = new Date(y, m - 1, 1).toLocaleDateString("es-AR", { month: "long", year: "numeric" });
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function table(headers, rows) {
  return el("table", {},
    el("thead", {}, el("tr", {}, headers.map(([text, cls]) => el("th", { class: cls }, text)))),
    el("tbody", {}, rows));
}

function rankRows(entries, me, cells) {
  let position = 0;
  return entries.map((entry) => {
    const hasData = cells.hasData(entry);
    if (hasData) position += 1;
    const cls = [entry.user_id === me ? "me" : "", hasData ? "" : "no-data"].join(" ").trim() || null;
    return el("tr", { class: cls },
      el("td", { class: "num" }, hasData ? String(position) : "—"),
      el("td", {}, entry.display_name),
      ...(hasData ? cells.render(entry) : [el("td", { class: "num", colspan: cells.span }, "sin datos")]));
  });
}

function weeklyCard(rows, me) {
  const body = rows.map((r) => {
    const [label, cls] = STATUS[r.status];
    return el("tr", { class: r.user_id === me ? "me" : null },
      el("td", {}, r.display_name),
      el("td", { class: "num" }, r.goal ? `${r.sessions} / ${r.goal}` : String(r.sessions)),
      el("td", { class: "num" }, label ? el("span", { class: `pill ${cls}` }, label) : ""));
  });
  return el("div", { class: "card" }, el("h3", {}, "La semana"),
    el("p", { class: "muted small" }, "Días que entrenó cada uno esta semana, contra su objetivo."),
    table([["Quién"], ["Días", "num"], ["", "num"]], body));
}

function strengthCard(item, mode, me, unit) {
  const rows = mode === "dots"
    ? rankRows(item.dots, me, { span: 2, hasData: (e) => e.value !== null,
      render: (e) => [el("td", { class: "num" }, num(e.value)), el("td", { class: "num muted" }, `${weight(e.weight_kg, unit)}×${e.reps}`)] })
    : rankRows(item.absolute, me, { span: 2, hasData: (e) => e.value !== null,
      render: (e) => [el("td", { class: "num" }, weight(e.value, unit)), el("td", { class: "num muted" }, `× ${e.reps}`)] });
  const head = mode === "dots" ? [["#", "num"], ["Quién"], ["DOTS", "num"], ["Serie", "num"]] : [["#", "num"], ["Quién"], ["Carga", "num"], ["Reps", "num"]];
  return el("div", { class: "card" }, el("h3", {}, item.exercise), table(head, rows));
}

function progressCard(rows, me, period) {
  const body = rankRows(rows, me, { span: 1, hasData: (e) => e.pct !== null,
    render: (e) => [el("td", { class: `num ${e.pct >= 0 ? "ok" : "error"}` }, `${e.pct >= 0 ? "+" : ""}${num(e.pct)}%`)] });
  return el("div", { class: "card" }, el("h3", {}, "Progreso"),
    el("p", { class: "muted small" }, period === "month" ? "Cuánto subió tu mejor 1RM este mes contra el anterior, en promedio entre tus ejercicios." : "Cuánto subió tu mejor 1RM desde el primer mes del período hasta el último, en promedio entre tus ejercicios."),
    table([["#", "num"], ["Quién"], ["Cambio", "num"]], body));
}

function consistencyCard(rows, me) {
  const body = rankRows(rows, me, { span: 2, hasData: (e) => e.pct !== null,
    render: (e) => [el("td", { class: "num" }, `${Math.round(e.pct)}%`), el("td", { class: "num muted" }, `racha ${e.streak}`)] });
  return el("div", { class: "card" }, el("h3", {}, "Constancia"),
    el("p", { class: "muted small" }, "Semanas cerradas en que llegaste a tu objetivo."),
    table([["#", "num"], ["Quién"], ["Semanas", "num"], ["", "num"]], body));
}

function periodControls(prefs, onChange) {
  const segmented = el("div", { class: "segmented small-seg" }, PERIODS.map(([value, label]) => el("label", {},
    el("input", { type: "radio", name: "period", value, checked: prefs.period === value,
      onchange: () => onChange({ period: value }) }), el("span", {}, label))));
  const extra = el("div", { class: "row" });
  if (prefs.period === "month") {
    extra.append(
      el("button", { type: "button", class: "secondary", onclick: () => onChange({ month: shiftMonth(prefs.month, -1) }) }, "‹"),
      el("strong", { style: "text-align:center" }, monthLabel(prefs.month)),
      el("button", { type: "button", class: "secondary", disabled: prefs.month >= currentMonth(),
        onclick: () => onChange({ month: shiftMonth(prefs.month, 1) }) }, "›"));
  } else if (prefs.period === "custom") {
    const from = el("input", { type: "month", value: prefs.from, onchange: () => onChange({ from: from.value }) });
    const to = el("input", { type: "month", value: prefs.to, onchange: () => onChange({ to: to.value }) });
    extra.append(el("label", {}, "Desde", from), el("label", {}, "Hasta", to));
  }
  return el("div", { class: "card" }, segmented, extra);
}

function modeToggle(mode, onChange) {
  return el("div", { class: "segmented" }, [["dots", "DOTS"], ["absolute", "Absoluto"]].map(([value, label]) => el("label", {},
    el("input", { type: "radio", name: "mode", value, checked: mode === value, onchange: () => onChange({ mode: value }) }),
    el("span", {}, label))));
}

export async function rankingsView(app, group) {
  const prefs = { period: "month", month: currentMonth(), from: shiftMonth(currentMonth(), -2), to: currentMonth(),
    mode: "dots", ...storageGet(PREFS, {}) };
  const unit = state.me.unit;

  async function render() {
    const query = new URLSearchParams({ period: prefs.period });
    if (prefs.period === "month") query.set("month", prefs.month);
    if (prefs.period === "custom") { query.set("from", prefs.from); query.set("to", prefs.to); }
    let data;
    try {
      data = await api.get(`/groups/${group.code}/rankings?${query}`);
    } catch (err) {
      app.replaceChildren(periodControls(prefs, update), errorBox(err.message));
      return;
    }
    const strength = data.strength.length
      ? data.strength.map((item) => strengthCard(item, prefs.mode, group.me, unit))
      : [el("p", { class: "muted" }, "El grupo no tiene ejercicios de desafío.")];
    app.replaceChildren(
      el("a", { class: "button", href: `#/g/${group.code}/campanas` }, "Campañas del grupo"),
      weeklyCard(data.weekly, group.me),
      periodControls(prefs, update),
      el("h2", { class: "section-title" }, "Fuerza"), modeToggle(prefs.mode, update),
      el("p", { class: "muted small" }, prefs.mode === "dots"
        ? "DOTS es el puntaje del powerlifting que ajusta la fuerza por peso corporal y sexo: compara justo a alguien de 65 kg con alguien de 95."
        : "Absoluto: el peso más alto que movió cada uno. A igual peso, gana el que hizo más reps."),
      ...strength,
      progressCard(data.progress, group.me, prefs.period),
      consistencyCard(data.consistency, group.me),
    );
  }

  function update(change) {
    Object.assign(prefs, change);
    storageSet(PREFS, prefs);
    render();
  }

  await render();
  poll(render);
}
