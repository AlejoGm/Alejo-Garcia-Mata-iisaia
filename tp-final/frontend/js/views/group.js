import { el } from "../ui.js";
import { groupChrome, loadGroup } from "../group-shell.js";
import { adminView } from "./group-admin.js";

const views = {
  grupo: adminView,
};

export async function groupView(app, { code, tab }) {
  const group = await loadGroup(code.toUpperCase(), true);
  groupChrome(group, tab);
  const view = views[tab];
  if (!view) {
    app.replaceChildren(el("div", { class: "card" }, el("p", { class: "muted" }, "Próximamente.")));
    return;
  }
  await view(app, group);
}
