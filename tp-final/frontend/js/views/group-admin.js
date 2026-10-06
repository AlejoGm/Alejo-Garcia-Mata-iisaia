import { api } from "../api.js";
import { forgetGroup, loadGroup } from "../group-shell.js";
import { busy, el } from "../ui.js";

function inviteCard(group) {
  const copy = el("button", { type: "button", class: "secondary" }, "Copiar invitación");
  const text = `Sumate a "${group.name}" en Gym-bro con el código ${group.code}: ${window.location.origin}/`;
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      copy.textContent = "Copiado";
    } catch {
      copy.textContent = group.code;
    }
  });
  return el("div", { class: "card" },
    el("p", { class: "muted small" }, "Código para invitar"),
    el("div", { class: "spread" }, el("span", { class: "code", style: "font-size:1.8rem" }, group.code), copy),
  );
}

function membersCard(group, rerender) {
  const error = el("p", { class: "error", role: "alert" });
  const items = group.members.map((m) => {
    const tags = el("span", { class: "row", style: "flex:0" },
      m.is_admin ? el("span", { class: "pill accent" }, "admin") : null,
      m.user_id === group.me ? el("span", { class: "pill" }, "vos") : null);
    let kick = null;
    if (group.is_admin && m.user_id !== group.me) {
      kick = el("button", { type: "button", class: "danger", style: "flex:0" }, "Sacar");
      kick.addEventListener("click", () => {
        if (!window.confirm(`¿Sacar a ${m.display_name} del grupo?`)) return;
        busy(kick, error, async () => {
          await api.del(`/groups/${group.code}/members/${m.user_id}`);
          await rerender();
        });
      });
    }
    return el("li", {}, el("span", {}, m.display_name), tags, kick);
  });
  return el("div", { class: "card" }, el("h3", {}, `Miembros (${group.members.length})`), el("ul", { class: "list" }, items), error);
}

async function challengesCard(group, rerender) {
  const names = group.challenges.map((c) => c.name).join(", ") || "ninguno";
  const card = el("div", { class: "card" }, el("h3", {}, "Ejercicios de desafío"),
    el("p", { class: "muted small" }, "Los rankings de fuerza comparan estos ejercicios. Máximo 4."),
    el("p", {}, names));
  if (!group.is_admin) return card;

  const exercises = await api.get("/exercises");
  const chosen = new Set(group.challenges.map((c) => c.id));
  const error = el("p", { class: "error", role: "alert" });
  const boxes = exercises.map((e) => el("label", { class: "check" },
    el("input", { type: "checkbox", value: String(e.id), checked: chosen.has(e.id) }), e.name));
  const save = el("button", { type: "button", class: "primary" }, "Guardar desafíos");
  save.addEventListener("click", () => busy(save, error, async () => {
    const ids = boxes.map((b) => b.firstChild).filter((i) => i.checked).map((i) => Number(i.value));
    if (ids.length > 4) throw new Error("Elegí como máximo 4.");
    await api.put(`/groups/${group.code}/challenges`, { exercise_ids: ids });
    await rerender();
  }));
  card.append(el("details", {}, el("summary", {}, "Cambiar"), el("div", { class: "checks" }, boxes), save, error));
  return card;
}

function leaveCard(group) {
  const error = el("p", { class: "error", role: "alert" });
  const leave = el("button", { type: "button", class: "danger big" }, "Salir del grupo");
  leave.addEventListener("click", () => {
    if (!window.confirm(`¿Salir de "${group.name}"? Tus sesiones no se borran.`)) return;
    busy(leave, error, async () => {
      await api.del(`/groups/${group.code}/members/me`);
      forgetGroup(group.code);
      window.location.hash = "#/";
    });
  });
  return el("div", { class: "actions" }, leave, error);
}

export async function adminView(app, group) {
  const rerender = async () => adminView(app, await loadGroup(group.code, true));
  app.replaceChildren(inviteCard(group), membersCard(group, rerender), await challengesCard(group, rerender),
    el("div", { id: "routines-slot" }), leaveCard(group));
}
