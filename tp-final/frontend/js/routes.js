import { loginView } from "./views/login.js";
import { profileView } from "./views/profile.js";
import { homeView } from "./views/home.js";
import { groupView } from "./views/group.js";
import { routineEditorView } from "./views/routine-editor.js";

export const routes = [
  { pattern: /^\/login$/, view: loginView, public: true },
  { pattern: /^\/perfil$/, view: profileView, path: "perfil" },
  { pattern: /^\/$/, view: homeView },
  { pattern: /^\/g\/(?<code>[A-Za-z0-9]{6})\/rutina\/(?<id>nueva|\d+)$/, view: routineEditorView },
  { pattern: /^\/g\/(?<code>[A-Za-z0-9]{6})\/(?<tab>[a-z]+)$/, view: groupView },
];
