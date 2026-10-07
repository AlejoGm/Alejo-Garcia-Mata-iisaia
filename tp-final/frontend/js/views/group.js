import { el } from "../ui.js";
import { groupChrome, loadGroup } from "../group-shell.js";
import { adminView } from "./group-admin.js";
import { loggerView } from "./logger.js";
import { trainView } from "./train.js";
import { rankingsView } from "./rankings.js";
import { feedView } from "./feed.js";
import { duelsView } from "./duels.js";
import { campaignsView } from "./campaigns.js";
import { dashboardView } from "./dashboard.js";

const views = {
  grupo: adminView,
  entrenar: trainView,
  carga: loggerView,
  rankings: rankingsView,
  feed: feedView,
  duelos: duelsView,
  campanas: campaignsView,
  panel: dashboardView,
};

export async function groupView(app, { code, tab }) {
  const group = await loadGroup(code.toUpperCase(), true);
  groupChrome(group, { carga: "entrenar", campanas: "rankings", feed: "panel" }[tab] || tab);
  const view = views[tab];
  if (!view) {
    app.replaceChildren(el("div", { class: "card" }, el("p", { class: "muted" }, "Próximamente.")));
    return;
  }
  await view(app, group);
}
