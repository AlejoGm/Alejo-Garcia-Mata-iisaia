import { api, ApiError } from "../api.js";
import { logout, suggestedName } from "../auth.js";
import { loadMe, setChrome, state } from "../app.js";
import { avatar, busy, el } from "../ui.js";

function choice(name, options, selected) {
  return el("div", { class: "segmented", role: "radiogroup" },
    options.map(([value, label]) => el("label", {},
      el("input", { type: "radio", name, value, checked: value === selected, required: true }),
      el("span", {}, label),
    )),
  );
}

async function currentProfile() {
  try {
    return await loadMe(true);
  } catch (err) {
    if (err instanceof ApiError && err.status === 409) return null;
    throw err;
  }
}

export async function profileView(app) {
  const me = await currentProfile();
  setChrome({ heading: me ? "Perfil" : "Completá tu perfil", backTo: me ? "#/" : null });

  const name = el("input", { name: "name", required: true, maxlength: "30", value: me?.display_name || await suggestedName() });
  const goal = el("input", { name: "goal", type: "number", inputmode: "numeric", min: "1", max: "7", required: true,
    value: String(me?.next_week_goal ?? me?.weekly_goal ?? 3) });
  const button = el("button", { class: "primary big", type: "submit" }, me ? "Guardar" : "Empezar");
  const error = el("p", { class: "error", role: "alert" });
  const goalNote = me && me.next_week_goal !== me.weekly_goal
    ? el("p", { class: "muted small" }, `Esta semana tu objetivo es ${me.weekly_goal}; desde el lunes, ${me.next_week_goal}.`)
    : el("p", { class: "muted small" }, me ? "Si lo cambiás, rige desde el lunes." : "Cuántas veces por semana vas al gimnasio.");

  const form = el("form", { class: "card" },
    el("label", {}, "Nombre para mostrar", name),
    el("fieldset", {}, el("legend", {}, "Sexo (para comparar fuerza con DOTS)"),
      choice("sex", [["M", "Hombre"], ["F", "Mujer"]], me?.sex)),
    el("label", {}, "Objetivo semanal de sesiones", goal),
    goalNote,
    el("fieldset", {}, el("legend", {}, "Unidad"), choice("unit", [["kg", "kg"], ["lb", "lb"]], me?.unit || "kg")),
    button,
    error,
  );
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    busy(button, error, async () => {
      state.me = await api.put("/me", {
        display_name: data.get("name").trim(),
        sex: data.get("sex"),
        weekly_goal: Number(data.get("goal")),
        unit: data.get("unit"),
      });
      window.location.hash = "#/";
    });
  });

  const out = el("button", { class: "secondary", type: "button" }, "Cerrar sesión");
  out.addEventListener("click", async () => {
    await logout();
    state.me = null;
    window.location.hash = "#/login";
  });
  const header = me ? el("header", { class: "person profile-head" }, avatar(me.display_name, "lg"),
    el("span", { class: "person-text" }, el("h2", {}, me.display_name),
      el("span", { class: "muted" }, `Objetivo: ${me.weekly_goal ?? "?"} días por semana`))) : "";
  app.replaceChildren(header, form, me ? el("div", { class: "actions" }, out) : "");
}
