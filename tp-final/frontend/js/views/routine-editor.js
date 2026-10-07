import { api } from "../api.js";
import { groupChrome, loadGroup } from "../group-shell.js";
import { sortable, move } from "../sortable.js";
import { busy, el } from "../ui.js";

function emptyDay(index) {
  return { name: `Día ${String.fromCharCode(65 + index)}`, items: [{ exercise_id: null, sets: 3 }] };
}

function toDraft(routine) {
  return {
    name: routine.name,
    days: routine.days.map((d) => ({ name: d.name, items: d.items.map((i) => ({ exercise_id: i.exercise_id, sets: i.sets })) })),
  };
}

export async function routineEditorView(app, { code, id }) {
  const group = await loadGroup(code.toUpperCase());
  groupChrome(group, "grupo");
  const exercises = await api.get("/exercises");
  const isNew = id === "nueva";
  const routine = isNew ? null : (await api.get(`/groups/${group.code}/routines`)).find((r) => r.id === Number(id));
  if (!isNew && !routine) {
    app.replaceChildren(el("p", { class: "error" }, "Esa rutina no existe."));
    return;
  }
  const draft = routine ? toDraft(routine) : { name: "", days: [emptyDay(0)] };
  const others = routine ? routine.followers.filter((uid) => uid !== group.me) : [];
  const names = new Map(group.members.map((m) => [m.user_id, m.display_name]));

  function exerciseSelect(item) {
    const select = el("select", { required: true, "aria-label": "Ejercicio" },
      el("option", { value: "" }, "Ejercicio"),
      exercises.map((e) => el("option", { value: String(e.id), selected: e.id === item.exercise_id }, e.name)));
    select.addEventListener("change", () => { item.exercise_id = Number(select.value) || null; });
    return select;
  }

  function setsInput(item) {
    const input = el("input", { type: "number", min: "1", max: "10", inputmode: "numeric", value: String(item.sets), "aria-label": "Series" });
    input.addEventListener("input", () => { item.sets = Number(input.value); });
    return input;
  }

  function itemRows(day) {
    return day.items.map((item, itemIndex) => el("div", { class: "item-row sortable-row" },
      el("button", { type: "button", class: "drag-handle", "aria-label": `Mover ejercicio ${itemIndex + 1}: arrastrá o usá las flechas` },
        el("span", { "aria-hidden": "true" }, "⋮⋮")),
      exerciseSelect(item), setsInput(item),
      el("button", { type: "button", class: "secondary", "aria-label": "Quitar ejercicio",
        onclick: () => { day.items.splice(itemIndex, 1); render(); } }, "×")));
  }

  function dayCard(day, dayIndex) {
    const name = el("input", { value: day.name, maxlength: "30", required: true, "aria-label": "Nombre del día" });
    name.addEventListener("input", () => { day.name = name.value; });
    const list = el("div", { class: "sortable-list" }, itemRows(day));
    // Solo se redibujan las filas: la lista sigue siendo la misma y el foco del teclado no se pierde.
    sortable(list, (from, to) => {
      move(day.items, from, to);
      list.replaceChildren(...itemRows(day));
    });
    return el("div", { class: "card" },
      el("div", { class: "spread" }, name,
        el("button", { type: "button", class: "danger", style: "flex:0",
          onclick: () => { draft.days.splice(dayIndex, 1); render(); } }, "Quitar día")),
      el("p", { class: "muted small" }, "Ejercicio y series. Arrastrá ⋮⋮ para cambiar el orden."),
      list,
      el("button", { type: "button", class: "secondary",
        onclick: () => { day.items.push({ exercise_id: null, sets: 3 }); render(); } }, "Agregar ejercicio"));
  }

  function render() {
    const name = el("input", { value: draft.name, maxlength: "40", required: true, placeholder: "Push/Pull/Legs" });
    name.addEventListener("input", () => { draft.name = name.value; });
    const error = el("p", { class: "error", role: "alert" });
    const save = el("button", { type: "button", class: "primary big" }, isNew ? "Crear rutina" : "Guardar cambios");
    save.addEventListener("click", () => {
      if (others.length && !window.confirm(`Esta rutina la siguen ${others.map((u) => names.get(u)).join(", ")}. ¿Cambiarla para todos?`)) return;
      busy(save, error, async () => {
        const body = { name: draft.name.trim(), days: draft.days.map((d) => ({ name: d.name.trim(), items: d.items.filter((i) => i.exercise_id) })) };
        if (body.days.some((d) => d.items.length === 0)) throw new Error("Cada día necesita al menos un ejercicio.");
        if (isNew) await api.post(`/groups/${group.code}/routines`, body);
        else await api.put(`/groups/${group.code}/routines/${routine.id}`, body);
        window.location.hash = `#/g/${group.code}/grupo`;
      });
    });
    const remove = isNew ? null : el("button", { type: "button", class: "danger" }, "Borrar rutina");
    remove?.addEventListener("click", () => {
      if (!window.confirm("¿Borrar la rutina? Las sesiones ya cargadas no se pierden.")) return;
      busy(remove, error, async () => {
        await api.del(`/groups/${group.code}/routines/${routine.id}`);
        window.location.hash = `#/g/${group.code}/grupo`;
      });
    });
    app.replaceChildren(
      others.length ? el("p", { class: "notice" }, `También la siguen: ${others.map((u) => names.get(u)).join(", ")}. Si la cambiás, cambia para ellos.`) : "",
      el("div", { class: "card" }, el("label", {}, "Nombre de la rutina", name)),
      ...draft.days.map(dayCard),
      draft.days.length < 7 ? el("button", { type: "button", class: "secondary big",
        onclick: () => { draft.days.push(emptyDay(draft.days.length)); render(); } }, "Agregar día") : "",
      el("div", { class: "actions" }, save, remove, error));
  }

  function renderReadOnly() {
    const follows = routine.followers.map((u) => names.get(u)).filter(Boolean).join(", ") || "nadie";
    app.replaceChildren(
      el("div", { class: "card" }, el("h2", {}, routine.name), el("p", { class: "muted small" }, `La siguen: ${follows}`)),
      ...routine.days.map((day) => el("div", { class: "card" }, el("h3", {}, day.name),
        el("ul", { class: "list" }, day.items.map((i) => el("li", {}, el("span", {}, i.exercise), el("span", { class: "muted" }, `${i.sets} series`)))))),
      el("div", { class: "actions" },
        el("button", { type: "button", class: "secondary big", onclick: render }, "Editar rutina"),
        el("a", { class: "button big", href: `#/g/${group.code}/grupo` }, "Volver")));
  }

  if (isNew) render();
  else renderReadOnly();
}
