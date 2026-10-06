import { api } from "../api.js";
import { busy, el } from "../ui.js";

export async function routinesCard(group, rerender) {
  const routines = await api.get(`/groups/${group.code}/routines`);
  const mine = group.members.find((m) => m.user_id === group.me)?.routine_id ?? null;
  const names = new Map(group.members.map((m) => [m.user_id, m.display_name]));
  const error = el("p", { class: "error", role: "alert" });

  const items = routines.map((r) => {
    const following = r.id === mine;
    const toggle = el("button", { type: "button", class: following ? "secondary" : "primary", style: "flex:0" },
      following ? "Dejar" : "Seguir");
    toggle.addEventListener("click", () => busy(toggle, error, async () => {
      await api.put(`/groups/${group.code}/members/me/routine`, { routine_id: following ? null : r.id });
      await rerender();
    }));
    const who = r.followers.map((id) => names.get(id)).filter(Boolean).join(", ") || "nadie todavía";
    return el("li", { class: "routine" },
      el("div", {},
        el("a", { href: `#/g/${group.code}/rutina/${r.id}` }, r.name),
        el("p", { class: "muted small" }, `${r.days.length} días · la siguen: ${who}`)),
      toggle);
  });

  return el("div", { class: "card" },
    el("h3", {}, "Rutinas"),
    el("p", { class: "muted small" }, "Son del grupo: cada uno sigue la suya o la misma que su bro."),
    items.length ? el("ul", { class: "list" }, items) : el("p", { class: "muted" }, "Todavía no hay rutinas."),
    el("a", { class: "button big", href: `#/g/${group.code}/rutina/nueva` }, "Nueva rutina"),
    error);
}
