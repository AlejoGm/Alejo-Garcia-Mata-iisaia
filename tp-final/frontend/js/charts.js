// Gráfico de líneas en SVG, sin librerías. Un valor null corta la línea.
const NS = "http://www.w3.org/2000/svg";
const W = 600;
const H = 280;
const PAD = { top: 20, right: 20, bottom: 44, left: 64 };

function svg(tag, attrs = {}, text) {
  const node = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
  if (text !== undefined) node.textContent = text;
  return node;
}

export function lineChart({ labels, series, label }) {
  const values = series.flatMap((s) => s.values).filter((v) => v !== null && v !== undefined);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart", role: "img", "aria-label": label });
  if (!values.length) {
    root.append(svg("text", { x: W / 2, y: H / 2, "text-anchor": "middle", class: "chart-empty" }, "Sin datos en este período"));
    return root;
  }
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (min === max) { min -= 1; max += 1; }
  const margin = (max - min) * 0.1;
  min -= margin;
  max += margin;
  const x = (i) => PAD.left + (labels.length === 1 ? (W - PAD.left - PAD.right) / 2 : (i * (W - PAD.left - PAD.right)) / (labels.length - 1));
  const y = (v) => PAD.top + ((max - v) * (H - PAD.top - PAD.bottom)) / (max - min);

  for (const v of [max - margin, (max + min) / 2, min + margin]) {
    root.append(svg("line", { x1: PAD.left, x2: W - PAD.right, y1: y(v), y2: y(v), class: "chart-grid" }));
    root.append(svg("text", { x: PAD.left - 8, y: y(v) + 7, "text-anchor": "end", class: "chart-axis" }, Math.round(v)));
  }
  const step = Math.ceil(labels.length / 6);
  labels.forEach((text, i) => {
    if (i % step === 0 || i === labels.length - 1) {
      root.append(svg("text", { x: x(i), y: H - 10, "text-anchor": "middle", class: "chart-axis" }, text));
    }
  });
  for (const s of [...series].reverse()) {
    let d = "";
    const dots = [];
    s.values.forEach((v, i) => {
      if (v === null || v === undefined) return;
      const previous = s.values[i - 1];
      d += `${previous === null || previous === undefined || i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(v).toFixed(1)} `;
      dots.push(svg("circle", { cx: x(i), cy: y(v), r: 6, class: `chart-dot ${s.className}` }));
    });
    root.append(svg("path", { d, class: `chart-line ${s.className}` }), ...dots);
  }
  return root;
}
