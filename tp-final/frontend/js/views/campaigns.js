import { api } from "../api.js";
import { icon } from "../icons.js";
import { avatar, busy, el, errorBox, today } from "../ui.js";

const STATUS = { upcoming: "Por empezar", active: "En curso", finished: "Terminada" };

function shortDate(iso) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString("es-AR", { day: "numeric", month: "short" });
}

function standingsTable(campaign, me) {
  return el("table", {},
    el("thead", {}, el("tr", {}, el("th", { class: "num" }, "#"), el("th", {}, "Quién"),
      el("th", { class: "num" }, "Puntos"), el("th", { class: "num" }, "1ros puestos"))),
    el("tbody", {}, campaign.standings.map((s, index) => el("tr", { class: s.user_id === me ? "me" : null },
      el("td", { class: "num" }, String(index + 1)), el("td", {}, el("span", { class: "who" }, avatar(s.display_name, "sm"), s.display_name)),
      el("td", { class: "num" }, String(s.points)), el("td", { class: "num muted" }, String(s.firsts))))));
}

function campaignCard(campaign, me) {
  return el("div", { class: `card${campaign.status === "active" ? " highlight" : ""}` },
    el("div", { class: "person" }, el("span", { class: "activity-icon hot" }, icon("trophy", 24)),
      el("span", { class: "person-text" }, el("strong", {}, campaign.name), el("span", { class: "muted small" }, `Del ${shortDate(campaign.start)} al ${shortDate(campaign.end)}`)),
      el("span", { class: "pill" }, STATUS[campaign.status])),
    el("p", { class: "muted small" }, `Suman: ${campaign.table_labels.join(", ")}`),
    campaign.winner ? el("p", { class: "ok" }, `Ganó ${campaign.winner.display_name}`) : null,
    standingsTable(campaign, me),
    el("p", { class: "muted small" }, "Cada tabla reparte puntos por posición: 10 al primero, 8 al segundo, 6, 5, 4, 3, 2 y 1. Para sumar, mejorá en las tablas de la campaña. Desempatan los primeros puestos."));
}

async function createForm(group, refresh) {
  const routines = await api.get(`/groups/${group.code}/routines`);
  const name = el("input", { required: true, maxlength: "40", placeholder: "Campaña de verano" });
  const start = el("input", { type: "date", value: today(), required: true });
  const end = el("input", { type: "date", required: true });
  const options = [
    ...group.challenges.map((c) => [`dots:${c.id}`, `DOTS ${c.name}`, true]),
    ...group.challenges.map((c) => [`absolute:${c.id}`, `Absoluto ${c.name}`, false]),
    ["progress", "Progreso", true], ["consistency", "Constancia", true],
  ];
  const boxes = options.map(([key, label, checked]) => el("label", { class: "check" },
    el("input", { type: "checkbox", value: key, checked }), label));
  const routine = el("select", {}, el("option", { value: "" }, "Cualquier rutina"),
    routines.map((r) => el("option", { value: String(r.id) }, `Solo quienes siguen ${r.name}`)));
  const error = el("p", { class: "error", role: "alert" });
  const save = el("button", { type: "submit", class: "primary big" }, "Crear campaña");
  const form = el("form", { class: "card" }, el("h3", {}, "Nueva campaña"),
    el("label", {}, "Nombre", name),
    el("div", { class: "row" }, el("label", {}, "Desde", start), el("label", {}, "Hasta", end)),
    el("fieldset", {}, el("legend", {}, "Tablas que suman puntos"), el("div", { class: "checks" }, boxes)),
    el("label", {}, "Participan", routine), save, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    busy(save, error, async () => {
      const tables = boxes.map((b) => b.firstChild).filter((i) => i.checked).map((i) => i.value);
      if (!tables.length) throw new Error("Elegí al menos una tabla.");
      await api.post(`/groups/${group.code}/campaigns`, {
        name: name.value.trim(), start: start.value, end: end.value, tables,
        routine_id: routine.value ? Number(routine.value) : null,
      });
      await refresh();
    });
  });
  return el("details", { class: "card" }, el("summary", {}, "Crear una campaña"), form);
}

export async function campaignsView(app, group) {
  async function refresh() {
    try {
      const campaigns = await api.get(`/groups/${group.code}/campaigns`);
      app.replaceChildren(
        el("p", { class: "muted" }, "Una campaña es una competencia con fecha de inicio, de fin y un ganador."),
        group.is_admin ? await createForm(group, refresh) : "",
        ...(campaigns.length ? campaigns.map((c) => campaignCard(c, group.me))
          : [el("div", { class: "card" }, el("p", { class: "muted" }, group.is_admin ? "Todavía no hay campañas." : "Todavía no hay campañas. Las crea el admin del grupo."))]));
    } catch (err) {
      app.replaceChildren(errorBox(err.message));
    }
  }
  await refresh();
}
