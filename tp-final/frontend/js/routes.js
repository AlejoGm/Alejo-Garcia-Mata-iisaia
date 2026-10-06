import { loginView } from "./views/login.js";
import { profileView } from "./views/profile.js";
import { homeView } from "./views/home.js";

export const routes = [
  { pattern: /^\/login$/, view: loginView, public: true },
  { pattern: /^\/perfil$/, view: profileView, path: "perfil" },
  { pattern: /^\/$/, view: homeView },
];
