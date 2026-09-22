import { getGroup, getRankings } from "./api.js";
import { clearMembership, loadMembership } from "./membership.js";
import { renderStrength } from "./ranking.js";
import { setupSessionForm } from "./session-form.js";

const membership = loadMembership();
if (!membership) {
  window.location.replace("index.html");
}

async function refreshRanking() {
  const container = document.getElementById("strength");
  try {
    renderStrength(container, (await getRankings(membership.code)).strength, membership.nickname);
  } catch (err) {
    container.innerHTML = "";
    const error = document.createElement("p");
    error.className = "error";
    error.textContent = err.message;
    container.append(error);
  }
}

async function start() {
  document.getElementById("nickname").textContent = membership.nickname;
  document.getElementById("leave").addEventListener("click", () => {
    clearMembership();
    window.location.href = "index.html";
  });

  let group;
  try {
    group = await getGroup(membership.code);
  } catch (err) {
    document.getElementById("group-name").textContent = "No se pudo abrir el grupo";
    document.getElementById("page-error").textContent = err.message;
    return;
  }
  document.getElementById("group-name").textContent = group.name;
  document.getElementById("group-code").textContent = group.code;

  setupSessionForm(document.getElementById("session-form"), group.exercises, membership, refreshRanking);
  await refreshRanking();
}

if (membership) {
  start();
}
