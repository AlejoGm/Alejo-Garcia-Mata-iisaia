import { el, weight } from "../ui.js";

export const REST_SECONDS = 90;

export function stepper(label, value, step, onChange) {
  const input = el("input", { type: "number", inputmode: "decimal", value: String(value ?? ""), "aria-label": label });
  input.addEventListener("input", () => onChange(input.value === "" ? null : Number(input.value)));
  // Al tocar el campo se selecciona todo: escribir "60" reemplaza en vez de insertarse en el medio.
  input.addEventListener("focus", () => setTimeout(() => input.select(), 0));
  const bump = (delta) => {
    const next = Math.max(0, Math.round(((Number(input.value) || 0) + delta) * 100) / 100);
    input.value = String(next);
    onChange(next);
  };
  return el("div", { class: "stepper" },
    el("span", { class: "stepper-label" }, label),
    el("div", { class: "stepper-row" },
      el("button", { type: "button", class: "step", onclick: () => bump(-step), "aria-label": `Menos ${label}` }, "−"),
      input,
      el("button", { type: "button", class: "step", onclick: () => bump(step), "aria-label": `Más ${label}` }, "+")),
  );
}

export function lastLine(last, unit) {
  const parts = [];
  if (last.mine) parts.push(`vos ${weight(last.mine.weight_kg, unit)} × ${last.mine.reps}`);
  for (const other of last.others) parts.push(`${other.display_name} ${weight(other.weight_kg, unit)} × ${other.reps}`);
  return parts.length ? `La última vez: ${parts.join(" · ")}` : "Primera vez que alguien del grupo carga este ejercicio.";
}

/** Un peso sospechoso pide un segundo toque: más de 300 kg, o más de 1,5 veces tu referencia. */
export function suspicious(weightKg, referenceKg) {
  if (weightKg > 300) return true;
  return Boolean(referenceKg) && weightKg > referenceKg * 1.5 && weightKg - referenceKg > 10;
}

/** Timer de descanso: cuenta hacia atrás y vibra al terminar. */
export function restTimer(onTick) {
  let end = null;
  let handle = null;
  const tick = () => {
    if (end === null) return;
    const left = Math.max(0, Math.round((end - Date.now()) / 1000));
    onTick(left);
    if (left === 0) {
      clearInterval(handle);
      end = null;
      if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
    }
  };
  return {
    start(seconds = REST_SECONDS) {
      end = Date.now() + seconds * 1000;
      clearInterval(handle);
      handle = setInterval(tick, 1000);
      tick();
    },
    add(seconds) {
      if (end !== null) { end += seconds * 1000; tick(); }
    },
    stop() {
      clearInterval(handle);
      end = null;
      onTick(null);
    },
    running: () => end !== null,
  };
}

export function clock(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}
