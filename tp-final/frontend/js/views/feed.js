import { api } from "../api.js";
import { poll, state } from "../app.js";
import { broLink } from "../group-shell.js";
import { el, errorBox, num, toDisplay } from "../ui.js";

const KINDS = [["fuerza", "💪"], ["fuego", "🔥"], ["dudoso", "🤨"]];
const PR_LABEL = { weight: "PR de peso", "1rm": "PR de 1RM" };

function dateLabel(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" });
}

function reactionButtons(group, item, refresh) {
  return el("div", { class: "reactions" }, KINDS.map(([kind, icon]) => {
    const active = item.mine === kind;
    const button = el("button", { type: "button", class: `reaction${active ? " active" : ""}`,
      "aria-pressed": String(active), "aria-label": `${kind} (${item.reactions[kind]})` },
    `${icon} ${item.reactions[kind]}`);
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        if (active) await api.del(`/groups/${group.code}/feed/${item.set_id}/reaction`);
        else await api.put(`/groups/${group.code}/feed/${item.set_id}/reaction`, { kind });
        await refresh();
      } catch (err) {
        button.disabled = false;
        button.title = err.message;
      }
    });
    return button;
  }));
}

function lift(group, item, unit, refresh) {
  return el("div", { class: `feed-pr${item.excluded ? " excluded" : ""}` },
    el("div", { class: "feed-lift" },
      el("span", { class: "person-text" }, el("span", { class: "feed-exercise" }, item.exercise), el("span", { class: "muted small" }, PR_LABEL[item.pr])),
      el("span", { class: "feed-number" }, el("strong", {}, num(toDisplay(item.weight_kg, unit))), el("span", {}, `${unit} × ${item.reps}`))),
    item.excluded ? el("p", { class: "small error" }, "No cuenta para los rankings: la mayoría del grupo lo marcó como dudoso.") : null,
    reactionButtons(group, item, refresh));
}

/** Una tarjeta por sesión: los PRs de la misma persona el mismo día van juntos, cada uno con sus reacciones. */
function bySession(items) {
  const sessions = new Map();
  for (const item of items) {
    const key = `${item.user_id}|${item.date}`;
    if (!sessions.has(key)) sessions.set(key, []);
    sessions.get(key).push(item);
  }
  return [...sessions.values()];
}

function card(group, prs, unit, refresh) {
  const [first] = prs;
  return el("article", { class: "card feed-item" },
    el("div", { class: "person" }, broLink(first.user_id, first.display_name, "md",
      el("span", { class: "person-text" }, el("strong", {}, first.display_name), el("span", { class: "muted small" }, dateLabel(first.date)))),
      el("span", { class: "pill accent" }, prs.length === 1 ? "1 PR" : `${prs.length} PRs`)),
    prs.map((item) => lift(group, item, unit, refresh)));
}

export async function feedView(app, group) {
  const unit = state.me.unit;

  async function render() {
    try {
      const items = await api.get(`/groups/${group.code}/feed`);
      app.replaceChildren(items.length
        ? el("div", { class: "page-list" }, bySession(items).map((prs) => card(group, prs, unit, render)))
        : el("div", { class: "card" }, el("p", { class: "muted" }, "Todavía no hay PRs. El primero que rompa una marca aparece acá.")));
    } catch (err) {
      app.replaceChildren(errorBox(err.message));
    }
  }

  await render();
  poll(render);
}
