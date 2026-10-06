import { state } from "../app.js";
import { el } from "../ui.js";

export function homeView(app) {
  app.replaceChildren(el("div", { class: "card" },
    el("h2", {}, `Hola, ${state.me.display_name}`),
    el("p", { class: "muted" }, "Tus grupos van a aparecer acá."),
  ));
}
