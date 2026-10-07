// Reordenar filas arrastrando un asa. Pointer events en vez de drag and drop de HTML5: así anda con el dedo.
// Con teclado, el asa mueve la fila con las flechas ↑ y ↓.

function move(array, from, to) {
  const [item] = array.splice(from, 1);
  array.splice(to, 0, item);
}

/**
 * Hace ordenables las filas `.sortable-row` de `list`. Cada fila tiene un `.drag-handle`.
 * `onReorder(from, to)` recibe los índices; quien llama mueve sus datos y vuelve a dibujar.
 */
export function sortable(list, onReorder) {
  const rows = () => [...list.querySelectorAll(":scope > .sortable-row")];

  list.addEventListener("pointerdown", (event) => {
    const handle = event.target.closest(".drag-handle");
    if (!handle || !list.contains(handle)) return;
    event.preventDefault();
    const items = rows();
    const row = handle.closest(".sortable-row");
    const from = items.indexOf(row);
    const rects = items.map((r) => r.getBoundingClientRect());
    const gap = rects.length > 1 ? rects[1].top - rects[0].bottom : 0;
    const step = rects[from].height + gap;
    const startY = event.clientY;
    let to = from;
    handle.setPointerCapture(event.pointerId);
    row.classList.add("dragging");

    const onMove = (e) => {
      const dy = e.clientY - startY;
      row.style.transform = `translateY(${dy}px)`;
      const center = rects[from].top + rects[from].height / 2 + dy;
      to = items.filter((_, i) => i !== from && rects[i].top + rects[i].height / 2 < center).length;
      items.forEach((other, i) => {
        if (i === from) return;
        const shift = from < to && i > from && i <= to ? -step : from > to && i >= to && i < from ? step : 0;
        other.style.transform = shift ? `translateY(${shift}px)` : "";
      });
    };
    const onUp = () => {
      handle.removeEventListener("pointermove", onMove);
      handle.removeEventListener("pointerup", onUp);
      handle.removeEventListener("pointercancel", onUp);
      items.forEach((r) => { r.style.transform = ""; });
      row.classList.remove("dragging");
      if (to !== from) onReorder(from, to);
    };
    handle.addEventListener("pointermove", onMove);
    handle.addEventListener("pointerup", onUp);
    handle.addEventListener("pointercancel", onUp);
  });

  list.addEventListener("keydown", (event) => {
    const handle = event.target.closest(".drag-handle");
    if (!handle || (event.key !== "ArrowUp" && event.key !== "ArrowDown")) return;
    event.preventDefault();
    const from = rows().indexOf(handle.closest(".sortable-row"));
    const to = from + (event.key === "ArrowUp" ? -1 : 1);
    if (to < 0 || to >= rows().length) return;
    onReorder(from, to);
    list.querySelectorAll(".drag-handle")[to]?.focus();
  });
}

export { move };
