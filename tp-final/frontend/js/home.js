import { createGroup, joinGroup } from "./api.js";
import { loadMembership, saveMembership } from "./membership.js";

function readMember(form) {
  return {
    nickname: form.nickname.value.trim(),
    bodyweight: Number(form.bodyweight.value),
  };
}

async function enter(code, form) {
  const { nickname, bodyweight } = readMember(form);
  await joinGroup(code, nickname, bodyweight);
  saveMembership(code, nickname);
  window.location.href = "group.html";
}

function handle(form, action) {
  const error = form.querySelector(".error");
  const button = form.querySelector("button");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    error.textContent = "";
    button.disabled = true;
    button.textContent = "Un momento...";
    try {
      await action(form);
    } catch (err) {
      error.textContent = err.message;
      button.disabled = false;
      button.textContent = form.id === "create-form" ? "Crear" : "Unirme";
    }
  });
}

handle(document.getElementById("create-form"), async (form) => {
  const group = await createGroup(form.group.value.trim());
  await enter(group.code, form);
});

handle(document.getElementById("join-form"), async (form) => {
  await enter(form.code.value.trim().toUpperCase(), form);
});

if (loadMembership()) {
  document.getElementById("resume").hidden = false;
}
