import { api } from "../api.js";
import { poll, state } from "../app.js";
import { avatar, busy, el, errorBox, num, weight } from "../ui.js";

const LEVELS = { low: ["parejo", "ok"], medium: ["desbalance medio", ""], high: ["desbalance alto", "bad"], none: ["sin datos para comparar", ""] };
const MODES = [["absolute", "Absoluto"], ["dots", "DOTS"]];
const STATUS = { pending: "Pendiente", active: "En curso", finished: "Terminado", rejected: "Rechazado" };

function fmt(value, mode, unit) {
  if (value === null || value === undefined) return "—";
  return mode === "dots" ? `${num(value)} DOTS` : weight(value, unit);
}

function segmented(name, options, selected, onChange) {
  return el("div", { class: "segmented" }, options.map(([value, label]) => el("label", {},
    el("input", { type: "radio", name, value: String(value), checked: String(value) === String(selected),
      onchange: () => onChange(value) }), el("span", {}, label))));
}

function duelCard(group, duel, unit, refresh) {
  const me = group.me;
  const error = el("p", { class: "error", role: "alert" });
  const title = duel.exercise;
  const lines = [el("p", { class: "muted small" }, `${duel.mode === "dots" ? "DOTS" : "Absoluto"}, ${duel.days} días`)];
  const side = (p, value) => el("div", { class: `duel-side${duel.winner_id === p.user_id ? " leading" : ""}` },
    avatar(p.display_name, "lg"), el("strong", {}, p.display_name),
    duel.status === "active" || duel.status === "finished" ? el("span", { class: "duel-value" }, fmt(value, duel.mode, unit)) : "");
  lines.push(el("div", { class: "duel-versus" }, side(duel.challenger, duel.challenger_value), el("span", { class: "vs" }, "vs"),
    side(duel.opponent, duel.opponent_value)));
  if (duel.status === "active" || duel.status === "finished") {
    const winner = duel.winner_id === null ? (duel.status === "finished" ? "Empate" : "Parejo por ahora")
      : `${duel.winner_id === duel.challenger.user_id ? duel.challenger.display_name : duel.opponent.display_name} ${duel.status === "finished" ? "ganó" : "va ganando"}`;
    lines.push(el("p", { class: duel.winner_id === me ? "ok" : "muted" }, `${winner}${duel.end ? `, cierra el ${new Date(`${duel.end}T00:00:00`).toLocaleDateString("es-AR", { day: "numeric", month: "short" })}` : ""}`));
  }
  let actions = null;
  if (duel.status === "pending" && duel.opponent.user_id === me) {
    const accept = el("button", { type: "button", class: "primary" }, "Aceptar");
    const reject = el("button", { type: "button", class: "secondary" }, "Rechazar");
    accept.addEventListener("click", () => busy(accept, error, async () => { await api.post(`/groups/${group.code}/duels/${duel.id}/accept`); await refresh(); }));
    reject.addEventListener("click", () => busy(reject, error, async () => { await api.post(`/groups/${group.code}/duels/${duel.id}/reject`); await refresh(); }));
    actions = el("div", { class: "row" }, reject, accept);
  } else if (duel.status === "pending") {
    lines.push(el("p", { class: "muted small" }, `Esperando que ${duel.opponent.display_name} acepte.`));
    if (duel.challenger.user_id === me) {
      const cancel = el("button", { type: "button", class: "secondary" }, "Cancelar reto");
      cancel.addEventListener("click", () => busy(cancel, error, async () => { await api.del(`/groups/${group.code}/duels/${duel.id}`); await refresh(); }));
      actions = cancel;
    }
  }
  return el("div", { class: `card${duel.status === "pending" && duel.opponent.user_id === me ? " highlight" : ""}` },
    el("div", { class: "spread" }, el("h3", {}, title), el("span", { class: "pill" }, STATUS[duel.status])),
    ...lines, actions, error);
}

// El formulario sobrevive a los refrescos: no vuelve a Sentadilla/Absoluto después de retar.
let form = null;
let notice = "";

async function challengeCard(group, exercises, unit, refresh) {
  form ??= { exercise_id: group.challenges[0]?.id ?? exercises[0].id, mode: "absolute", days: 7 };
  const box = el("div", { class: "card" });
  const error = el("p", { class: "error", role: "alert" });

  async function render() {
    const select = el("select", { "aria-label": "Ejercicio" }, exercises.map((e) =>
      el("option", { value: String(e.id), selected: e.id === form.exercise_id }, e.name)));
    select.addEventListener("change", () => { form.exercise_id = Number(select.value); render(); });
    let rivals;
    try {
      rivals = await api.get(`/groups/${group.code}/duels/suggestions?exercise_id=${form.exercise_id}&mode=${form.mode}`);
    } catch (err) {
      box.replaceChildren(errorBox(err.message));
      return;
    }
    const list = rivals.rivals.map((r) => {
      const [label, cls] = LEVELS[r.level];
      const button = el("button", { type: "button", class: "primary", style: "flex:0" }, "Retar");
      button.addEventListener("click", () => {
        if (r.level === "high" && !window.confirm(`Con ${r.display_name} hay desbalance alto. ¿Retarlo igual?`)) return;
        busy(button, error, async () => {
          await api.post(`/groups/${group.code}/duels`, { opponent_id: r.user_id, ...form });
          notice = `¡Listo! Retaste a ${r.display_name}. Tiene que aceptar para que arranque.`;
          await refresh();
        });
      });
      return el("li", { class: "rival" }, avatar(r.display_name),
        el("span", { class: "person-text" }, el("strong", {}, r.display_name),
          el("span", { class: "muted small" }, `Mejor del mes: ${fmt(r.value, form.mode, unit)}`),
          el("span", { class: `pill ${cls}` }, label)),
        button);
    });
    const shown = notice;
    notice = "";
    box.replaceChildren(
      shown ? el("p", { class: "ok", role: "status" }, shown) : "",
      el("h3", {}, "Retar a alguien"),
      el("label", {}, "Ejercicio", select),
      segmented("duel-mode", MODES, form.mode, (v) => { form.mode = v; render(); }),
      segmented("duel-days", [[3, "3 días"], [7, "7 días"], [14, "14 días"]], form.days, (v) => { form.days = Number(v); }),
      el("p", { class: "muted small" }, `Tu mejor del mes: ${fmt(rivals.mine, form.mode, unit)}. Los rivales van de más parejo a menos.`),
      list.length ? el("ul", { class: "list" }, list) : el("p", { class: "muted" }, "No hay otros miembros todavía."),
      error);
  }
  await render();
  return box;
}

export async function duelsView(app, group) {
  const unit = state.me.unit;
  const exercises = await api.get("/exercises");
  const challengeIds = new Set(group.challenges.map((c) => c.id));
  exercises.sort((a, b) => Number(challengeIds.has(b.id)) - Number(challengeIds.has(a.id)));

  async function refresh() {
    let duels;
    try {
      duels = await api.get(`/groups/${group.code}/duels`);
    } catch (err) {
      app.replaceChildren(errorBox(err.message));
      return;
    }
    const cards = duels.filter((d) => d.status !== "rejected").map((d) => duelCard(group, d, unit, refresh));
    app.replaceChildren(await challengeCard(group, exercises, unit, refresh),
      el("h2", { class: "section-title" }, "Duelos"),
      cards.length ? el("div", { class: "cards-grid" }, cards) : el("p", { class: "muted" }, "Todavía no hay duelos."));
  }

  await refresh();
  poll(refresh);
}
