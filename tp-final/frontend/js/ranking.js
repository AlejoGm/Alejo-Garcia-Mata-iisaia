function cell(tag, text) {
  const element = document.createElement(tag);
  element.textContent = text;
  return element;
}

function renderExercise(ranking, me) {
  const section = document.createElement("div");
  section.className = "ranking";
  section.append(cell("h3", ranking.exercise));

  const table = document.createElement("table");
  table.innerHTML = "<thead><tr><th>#</th><th>Quién</th><th>1RM est.</th><th>× peso</th></tr></thead>";
  const tbody = document.createElement("tbody");
  let position = 0;
  for (const entry of ranking.entries) {
    const row = document.createElement("tr");
    if (entry.nickname.toLowerCase() === me.toLowerCase()) row.className = "me";
    if (entry.ratio === null) {
      row.classList.add("no-data");
      row.append(cell("td", "—"), cell("td", entry.nickname), cell("td", "sin datos"), cell("td", ""));
    } else {
      position += 1;
      row.append(
        cell("td", String(position)),
        cell("td", entry.nickname),
        cell("td", `${entry.best_1rm} kg`),
        cell("td", entry.ratio.toFixed(2)),
      );
    }
    tbody.append(row);
  }
  table.append(tbody);
  section.append(table);
  return section;
}

export function renderStrength(container, strength, me) {
  container.innerHTML = "";
  if (strength.length === 0) {
    container.append(cell("p", "El grupo no tiene ejercicios de desafío."));
    return;
  }
  for (const ranking of strength) {
    container.append(renderExercise(ranking, me));
  }
}
