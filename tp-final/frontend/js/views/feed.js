import { api } from "../api.js";
import { poll, state } from "../app.js";
import { avatar, el, errorBox, num, toDisplay } from "../ui.js";

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

function card(group, item, unit, refresh) {
  return el("article", { class: `card feed-item${item.excluded ? " excluded" : ""}` },
    el("div", { class: "person" }, avatar(item.display_name),
      el("span", { class: "person-text" }, el("strong", {}, item.display_name), el("span", { class: "muted small" }, dateLabel(item.date))),
      el("span", { class: "pill accent" }, PR_LABEL[item.pr])),
    el("div", { class: "feed-lift" },
      el("span", { class: "feed-exercise" }, item.exercise),
      el("span", { class: "feed-number" }, el("strong", {}, num(toDisplay(item.weight_kg, unit))), el("span", {}, `${unit} × ${item.reps}`))),
    item.excluded ? el("p", { class: "small error" }, "No cuenta para los rankings: la mayoría del grupo lo marcó como dudoso.") : null,
    reactionButtons(group, item, refresh));
}

export async function feedView(app, group) {
  const unit = state.me.unit;

  async function render() {
    try {
      const items = await api.get(`/groups/${group.code}/feed`);
      app.replaceChildren(items.length
        ? el("div", { class: "page-list" }, items.map((item) => card(group, item, unit, render)))
        : el("div", { class: "card" }, el("p", { class: "muted" }, "Todavía no hay PRs. El primero que rompa una marca aparece acá.")));
    } catch (err) {
      app.replaceChildren(errorBox(err.message));
    }
  }

  await render();
  poll(render);
}
