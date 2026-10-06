import { api } from "../api.js";
import { setChrome, state } from "../app.js";
import { busy, el, errorBox } from "../ui.js";

function groupList(groups) {
  if (groups.length === 0) {
    return el("p", { class: "muted" }, "Todavía no estás en ningún grupo. Creá uno o pedile el código a un amigo.");
  }
  return el("ul", { class: "list" }, groups.map((g) => el("li", {},
    el("a", { href: `#/g/${g.code}/entrenar` }, g.name),
    el("span", { class: "muted small" }, `${g.members} ${g.members === 1 ? "miembro" : "miembros"}${g.is_admin ? " · admin" : ""}`),
  )));
}

function formCard(title, field, buttonText, onSubmit) {
  const button = el("button", { class: "primary big", type: "submit" }, buttonText);
  const error = el("p", { class: "error", role: "alert" });
  const form = el("form", { class: "card" }, el("h3", {}, title), field, button, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    busy(button, error, onSubmit);
  });
  return form;
}

export async function homeView(app) {
  setChrome({ heading: "Gym-bro" });
  let groups;
  try {
    groups = await api.get("/me/groups");
  } catch (err) {
    app.replaceChildren(errorBox(err.message));
    return;
  }

  const groupName = el("input", { required: true, maxlength: "40", placeholder: "Los del gym" });
  const code = el("input", { required: true, maxlength: "6", class: "code", autocapitalize: "characters",
    autocomplete: "off", placeholder: "ABC234" });

  const create = formCard("Crear un grupo", el("label", {}, "Nombre", groupName), "Crear", async () => {
    const group = await api.post("/groups", { name: groupName.value.trim() });
    window.location.hash = `#/g/${group.code}/grupo`;
  });
  const join = formCard("Unirme con un código", el("label", {}, "Código", code), "Unirme", async () => {
    const group = await api.post(`/groups/${code.value.trim().toUpperCase()}/join`);
    window.location.hash = `#/g/${group.code}/entrenar`;
  });

  app.replaceChildren(
    el("div", { class: "card" },
      el("div", { class: "spread" }, el("h2", {}, `Hola, ${state.me.display_name}`),
        el("a", { href: "#/stats", class: "button" }, "Mis stats")),
      groupList(groups),
    ),
    el("div", { class: "grid-2" }, join, create),
  );
}
