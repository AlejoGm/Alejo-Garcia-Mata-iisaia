// Respuesta física a lo que pasa: vibración, rebote y confeti. Con "reducir movimiento" solo queda la vibración.
import { el } from "./ui.js";

const COLORS = ["#c8f53b", "#34d399", "#ff6b4a", "#eef3ec"];

const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function vibrate(pattern) {
  if (navigator.vibrate) navigator.vibrate(pattern);
}

/** Rebote corto de un número o un botón. */
export function pop(node) {
  if (!node || reduced()) return;
  node.classList.remove("pop");
  void node.offsetWidth; // reinicia la animación si ya estaba corriendo
  node.classList.add("pop");
}

/** PR o medalla nueva: papelitos que caen y una vibración de festejo. */
export function celebrate() {
  vibrate([60, 40, 60, 40, 140]);
  if (reduced()) return;
  const layer = el("div", { class: "confetti", "aria-hidden": "true" });
  for (let i = 0; i < 40; i += 1) {
    const piece = el("span");
    piece.style.setProperty("--x", `${Math.random() * 100}vw`);
    piece.style.setProperty("--d", `${1 + Math.random()}s`);
    piece.style.setProperty("--delay", `${Math.random() * 0.3}s`);
    piece.style.setProperty("--r", `${Math.random() * 900 - 450}deg`);
    piece.style.setProperty("--c", COLORS[i % COLORS.length]);
    layer.append(piece);
  }
  document.body.append(layer);
  setTimeout(() => layer.remove(), 2600);
}
