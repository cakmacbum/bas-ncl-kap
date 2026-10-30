// DrawingModel → SVG (A3 yatay, mm birimli viewBox).
import type { DrawingModel, Entity, Layer } from "./model";

const STROKE: Record<Layer, { color: string; w: number; dash?: string }> = {
  OUTLINE: { color: "#111", w: 0.5 },
  HIDDEN: { color: "#555", w: 0.25, dash: "3 1.5" },
  DIM: { color: "#0a4d8c", w: 0.2 },
  TEXT: { color: "#111", w: 0.2 },
  TITLE: { color: "#111", w: 0.35 },
};

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const n = (v: number) => String(Math.round(v * 1000) / 1000);

function ent(e: Entity, H: number): string {
  const st = STROKE[e.layer];
  const attr = `class="${e.layer}" fill="none" stroke="${st.color}" stroke-width="${st.w}"${st.dash ? ` stroke-dasharray="${st.dash}"` : ""}`;
  switch (e.t) {
    case "line": return `<line ${attr} x1="${n(e.x1)}" y1="${n(H - e.y1)}" x2="${n(e.x2)}" y2="${n(H - e.y2)}"/>`;
    case "poly": return `<${e.closed ? "polygon" : "polyline"} ${attr} points="${e.pts.map(([x, y]) => `${n(x)},${n(H - y)}`).join(" ")}"/>`;
    case "circle": return `<circle ${attr} cx="${n(e.cx)}" cy="${n(H - e.cy)}" r="${n(e.r)}"/>`;
    case "text": {
      const x = n(e.x), y = n(H - e.y);
      const anchor = e.anchor ?? "start";
      const rot = e.rot ? ` transform="rotate(${-e.rot} ${x} ${y})"` : "";
      return `<text class="${e.layer}" x="${x}" y="${y}" font-size="${n(e.h)}" text-anchor="${anchor}" fill="${st.color}" font-family="Arial, Helvetica, sans-serif"${rot}>${esc(e.s)}</text>`;
    }
  }
}

export function drawingToSvg(m: DrawingModel): string {
  const body = m.entities.map((e) => ent(e, m.height)).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${m.width}mm" height="${m.height}mm" viewBox="0 0 ${m.width} ${m.height}">\n<rect width="${m.width}" height="${m.height}" fill="#fff"/>\n${body}\n</svg>\n`;
}
