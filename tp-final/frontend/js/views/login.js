import { authMode, login, register } from "../auth.js";
import { icon } from "../icons.js";
import { busy, el } from "../ui.js";

export function loginView(app) {
  const error = el("p", { class: "error", role: "alert" });
  const hero = el("div", { class: "hero" },
    el("span", { class: "brand-mark" }, icon("train", 34)),
    el("h2", {}, "Entrená con tus bros."),
    el("p", { class: "muted" }, "Cada uno con su rutina. Comparados de forma justa, con DOTS."),
  );

  if (authMode() === "auth0") {
    const button = el("button", { class: "primary big", type: "button" }, "Entrar con Google");
    button.addEventListener("click", () => busy(button, error, () => login()));
    app.replaceChildren(hero, el("div", { class: "card" }, button, error));
    return;
  }

  if (authMode() === "local") {
    app.replaceChildren(hero, accountForm(error));
    return;
  }

  const name = el("input", { name: "name", required: true, maxlength: "30", autocomplete: "nickname" });
  const button = el("button", { class: "primary big", type: "submit" }, "Entrar");
  const form = el("form", { class: "card" }, el("label", {}, "Tu nombre", name), button, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    busy(button, error, async () => {
      await login(name.value.trim());
      window.location.hash = "#/";
    });
  });
  app.replaceChildren(hero, form);
}

/** Entrar o crear cuenta con usuario y contraseña. Al crearla, la app sigue al perfil. */
function accountForm(error) {
  let creating = false;
  const username = el("input", { name: "username", required: true, maxlength: "30", autocomplete: "username",
    autocapitalize: "none", spellcheck: "false" });
  const password = el("input", { name: "password", type: "password", required: true, autocomplete: "current-password" });
  const repeat = el("input", { name: "repeat", type: "password", autocomplete: "new-password" });
  const repeatLabel = el("label", { hidden: true }, "Repetí la contraseña", repeat);
  const hint = el("p", { class: "muted small", hidden: true }, "Usuario de 3 a 30 letras o números, sin espacios. Contraseña de 6 caracteres o más.");
  const button = el("button", { class: "primary big", type: "submit" }, "Entrar");
  const tabs = el("div", { class: "segmented" }, [["Entrar", false], ["Crear cuenta", true]].map(([label, value]) =>
    el("label", {}, el("input", { type: "radio", name: "account-mode", checked: value === creating,
      onchange: () => { creating = value; sync(); } }), el("span", {}, label))));
  function sync() {
    repeatLabel.hidden = !creating;
    hint.hidden = !creating;
    repeat.required = creating;
    password.autocomplete = creating ? "new-password" : "current-password";
    button.textContent = creating ? "Crear cuenta" : "Entrar";
    error.textContent = "";
  }
  const form = el("form", { class: "card" }, tabs, el("label", {}, "Usuario", username), el("label", {}, "Contraseña", password),
    repeatLabel, hint, button, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    busy(button, error, async () => {
      if (creating && password.value !== repeat.value) throw new Error("Las contraseñas no coinciden.");
      await (creating ? register : login)(username.value, password.value);
      window.location.hash = "#/";
    });
  });
  return form;
}
