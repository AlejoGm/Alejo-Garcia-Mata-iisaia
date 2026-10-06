import { authMode, login } from "../auth.js";
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

  const name = el("input", { name: "name", required: true, maxlength: "30", autocomplete: "nickname" });
  const button = el("button", { class: "primary big", type: "submit" }, "Entrar");
  const form = el("form", { class: "card" },
    el("p", { class: "notice" }, "Modo desarrollo: el servidor no tiene Auth0 configurado, así que se entra solo con un nombre."),
    el("label", {}, "Tu nombre", name),
    button,
    error,
  );
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    busy(button, error, async () => {
      await login(name.value.trim());
      window.location.hash = "#/";
    });
  });
  app.replaceChildren(hero, form);
}
