import { postSession } from "./api.js";

function today() {
  // en-CA formatea como YYYY-MM-DD en la zona horaria local.
  return new Date().toLocaleDateString("en-CA");
}

function addRow(tbody, exercises) {
  const row = document.getElementById("set-row").content.firstElementChild.cloneNode(true);
  const select = row.querySelector("select");
  for (const exercise of exercises) {
    select.append(new Option(exercise.name, exercise.id));
  }
  const previous = tbody.lastElementChild;
  if (previous) {
    // Lo habitual es repetir el ejercicio de la serie anterior.
    select.value = previous.querySelector("select").value;
  }
  row.querySelector(".remove").addEventListener("click", () => {
    if (tbody.children.length > 1) row.remove();
  });
  tbody.append(row);
}

function readSets(tbody) {
  return [...tbody.children].map((row) => ({
    exercise_id: Number(row.querySelector("select").value),
    weight_kg: Number(row.querySelector("[name=weight]").value),
    reps: Number(row.querySelector("[name=reps]").value),
  }));
}

function renderResult(container, session) {
  const ok = document.createElement("p");
  ok.className = "ok";
  ok.textContent = "Sesión guardada.";
  const list = document.createElement("ul");
  for (const s of session.sets) {
    const estimate = s.estimated_1rm === null ? "más de 10 reps, no estima 1RM" : `1RM estimado ${s.estimated_1rm} kg`;
    const item = document.createElement("li");
    item.textContent = `${s.exercise}: ${s.weight_kg} kg × ${s.reps} — ${estimate}`;
    list.append(item);
  }
  container.replaceChildren(ok, list);
}

export function setupSessionForm(form, exercises, membership, onSaved) {
  const tbody = form.querySelector("tbody");
  const error = form.querySelector(".error");
  const submit = form.querySelector("[type=submit]");
  const result = document.getElementById("session-result");

  form.date.value = today();
  form.date.max = today();
  addRow(tbody, exercises);
  document.getElementById("add-set").addEventListener("click", () => addRow(tbody, exercises));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    error.textContent = "";
    result.innerHTML = "";
    submit.disabled = true;
    submit.textContent = "Guardando...";
    try {
      renderResult(result, await postSession(membership.code, membership.nickname, form.date.value, readSets(tbody)));
      tbody.innerHTML = "";
      addRow(tbody, exercises);
      await onSaved();
    } catch (err) {
      error.textContent = err.message;
    } finally {
      submit.disabled = false;
      submit.textContent = "Guardar sesión";
    }
  });
}
