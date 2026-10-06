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

/** Curva suave que pasa por todos los puntos (Catmull-Rom convertido a Bézier cúbicas). */
function smooth(points) {
  if (points.length === 1) return `M${points[0][0]},${points[0][1]}`;
  let d = `M${points[0][0].toFixed(1)},${points[0][1].toFixed(1)}`;
  for (let i = 0; i < points.length - 1; i += 1) {
    const [p0, p1, p2, p3] = [points[i - 1] || points[i], points[i], points[i + 1], points[i + 2] || points[i + 1]];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return d;
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
    root.append(svg("text", { x: PAD.left - 8, y: y(v) + 7, "text-anchor": "end", class: "chart-axis" }, max - min < 12 ? v.toLocaleString("es-AR", { maximumFractionDigits: 1 }) : Math.round(v)));
  }
  const step = Math.ceil(labels.length / 6);
  labels.forEach((text, i) => {
    if (i % step === 0 || i === labels.length - 1) {
      root.append(svg("text", { x: x(i), y: H - 10, "text-anchor": "middle", class: "chart-axis" }, text));
    }
  });
  const defs = svg("defs");
  const gradient = svg("linearGradient", { id: `fill-${label.length}-${values.length}`, x1: 0, y1: 0, x2: 0, y2: 1 });
  gradient.append(svg("stop", { offset: "0%", class: "chart-fill-top" }), svg("stop", { offset: "100%", class: "chart-fill-bottom" }));
  defs.append(gradient);
  root.prepend(defs);
  for (const [order, s] of [...series].reverse().entries()) {
    const segments = [];
    let current = [];
    s.values.forEach((v, i) => {
      if (v === null || v === undefined) {
        if (current.length) segments.push(current);
        current = [];
      } else {
        current.push([x(i), y(v)]);
      }
    });
    if (current.length) segments.push(current);
    const isMain = order === series.length - 1;
    for (const points of segments) {
      const d = smooth(points);
      if (isMain && points.length > 1) {
        const area = `${d} L${points[points.length - 1][0].toFixed(1)},${H - PAD.bottom} L${points[0][0].toFixed(1)},${H - PAD.bottom} Z`;
        root.append(svg("path", { d: area, class: "chart-area", fill: `url(#${gradient.getAttribute("id")})` }));
      }
      root.append(svg("path", { d, class: `chart-line ${s.className}` }));
      for (const [px, py] of points) root.append(svg("circle", { cx: px, cy: py, r: 6, class: `chart-dot ${s.className}` }));
    }
  }
  return root;
}
