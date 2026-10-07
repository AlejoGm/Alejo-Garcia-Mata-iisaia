// Íconos de trazo, en SVG inline: heredan el color con currentColor.
const PATHS = {
  rankings: "M5 20V11M12 20V4M19 20v-6",
  panel: "M4 4h7v7H4zM13 4h7v4h-7zM13 10h7v10h-7zM4 13h7v7H4z",
  feed: "M12 3c1 3 4 4.5 4 8.5a4 4 0 0 1-8 0c0-1.6.7-2.7 1.5-3.5.2 1.5 1 2.4 2 2.5C11 8 11 5.5 12 3Z",
  duels: "M5 19 15 9m-2-4 6 0 0 6M19 19 9 9m2-4H5v6",
  group: "M8.5 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM2 20c0-3.3 2.9-6 6.5-6s6.5 2.7 6.5 6M16 4.5a3.5 3.5 0 0 1 0 6.5M18 14c2.4.6 4 2.9 4 6",
  train: "M6.5 6.5v11M3.5 9v6M17.5 6.5v11M20.5 9v6M6.5 12h11",
  back: "M15 5l-7 7 7 7",
  chart: "M4 19h16M7 15l3.5-4 3 2.5L18 8",
  trophy: "M8 4h8v5a4 4 0 0 1-8 0V4ZM8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8 20h8M9.5 17h5",
  clock: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM12 7v5l3 2",
  bolt: "M13 3 5 14h6l-1 7 8-11h-6l1-7Z",
  scale: "M5 20h14M12 4v16M6 8l-3 6a3 3 0 0 0 6 0L6 8Zm12 0-3 6a3 3 0 0 0 6 0l-3-6ZM6 8h12",
  copy: "M9 9h10v10H9zM5 15V5h10",
};

export function icon(name, size = 24) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", size);
  svg.setAttribute("height", size);
  svg.setAttribute("aria-hidden", "true");
  svg.classList.add("icon");
  const path = document.createElementNS(ns, "path");
  path.setAttribute("d", PATHS[name]);
  svg.append(path);
  return svg;
}
