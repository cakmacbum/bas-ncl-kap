/** Açınım şablonu çizim ilkelleri + DXF (R12 ASCII) ve SVG yazıcıları. Saf TS, bağımlılık yok. */
export type Pt = [number, number];
export type Shape =
  | { k: "line"; a: Pt; b: Pt }
  | { k: "poly"; pts: Pt[]; closed?: boolean }
  | { k: "arc"; c: Pt; r: number; a0: number; a1: number } // derece, CCW
  | { k: "text"; at: Pt; h: number; s: string };

export interface FlatPart {
  id: string;
  name: string;
  shapes: Shape[];
  notes: string[];
}

const f = (n: number) => (Math.abs(n) < 1e-9 ? 0 : n).toFixed(4);
const rad = (d: number) => (d * Math.PI) / 180;

/** Şekil sınırları (min/max) — SVG viewBox için. */
export function bounds(shapes: Shape[]): { x0: number; y0: number; x1: number; y1: number } {
  const xs: number[] = [];
  const ys: number[] = [];
  const add = (p: Pt) => { xs.push(p[0]); ys.push(p[1]); };
  for (const s of shapes) {
    if (s.k === "line") { add(s.a); add(s.b); }
    else if (s.k === "poly") s.pts.forEach(add);
    else if (s.k === "text") add(s.at);
    else {
      const n = 24;
      for (let i = 0; i <= n; i++) {
        const a = rad(s.a0 + ((s.a1 - s.a0) * i) / n);
        add([s.c[0] + s.r * Math.cos(a), s.c[1] + s.r * Math.sin(a)]);
      }
    }
  }
  if (!xs.length) return { x0: 0, y0: 0, x1: 1, y1: 1 };
  return { x0: Math.min(...xs), y0: Math.min(...ys), x1: Math.max(...xs), y1: Math.max(...ys) };
}

/** DXF R12 (AC1009) ASCII. Polilineler R12'de yerel POLYLINE/VERTEX/SEQEND ile yazılır (LWPOLYLINE R14+). */
export function toDxf(part: FlatPart): string {
  const o: (string | number)[] = [];
  const g = (code: number, v: string | number) => o.push(code, v);
  g(0, "SECTION"); g(2, "HEADER"); g(9, "$ACADVER"); g(1, "AC1009"); g(0, "ENDSEC");
  g(0, "SECTION"); g(2, "ENTITIES");
  for (const s of part.shapes) {
    if (s.k === "line") {
      g(0, "LINE"); g(8, "0"); g(10, f(s.a[0])); g(20, f(s.a[1])); g(30, 0); g(11, f(s.b[0])); g(21, f(s.b[1])); g(31, 0);
    } else if (s.k === "poly") {
      g(0, "POLYLINE"); g(8, "0"); g(66, 1); g(70, s.closed ? 1 : 0);
      for (const p of s.pts) { g(0, "VERTEX"); g(8, "0"); g(10, f(p[0])); g(20, f(p[1])); g(30, 0); }
      g(0, "SEQEND"); g(8, "0");
    } else if (s.k === "arc") {
      g(0, "ARC"); g(8, "0"); g(10, f(s.c[0])); g(20, f(s.c[1])); g(30, 0); g(40, f(s.r));
      g(50, f(((s.a0 % 360) + 360) % 360)); g(51, f(((s.a1 % 360) + 360) % 360));
    } else {
      g(0, "TEXT"); g(8, "0"); g(10, f(s.at[0])); g(20, f(s.at[1])); g(30, 0); g(40, f(s.h)); g(1, s.s.replace(/[^\x20-\x7E]/g, "?"));
    }
  }
  g(0, "ENDSEC"); g(0, "EOF");
  const lines: string[] = [];
  for (let i = 0; i < o.length; i += 2) lines.push(String(o[i]).padStart(3), String(o[i + 1]));
  return lines.join("\r\n") + "\r\n";
}

/** SVG önizleme (y ekseni çevrilir). */
export function toSvg(part: FlatPart, px = 480): string {
  const b = bounds(part.shapes);
  const w = b.x1 - b.x0 || 1;
  const h = b.y1 - b.y0 || 1;
  const m = Math.max(w, h) * 0.04;
  const Y = (y: number) => f(b.y1 - y);
  const X = (x: number) => f(x - b.x0);
  const el = part.shapes.map((s) => {
    if (s.k === "line") return `<line x1="${X(s.a[0])}" y1="${Y(s.a[1])}" x2="${X(s.b[0])}" y2="${Y(s.b[1])}"/>`;
    if (s.k === "poly") {
      const d = s.pts.map((p) => `${X(p[0])},${Y(p[1])}`).join(" ");
      return s.closed ? `<polygon points="${d}"/>` : `<polyline points="${d}"/>`;
    }
    if (s.k === "text") return `<text x="${X(s.at[0])}" y="${Y(s.at[1])}" font-size="${f(s.h)}" stroke="none" fill="currentColor">${s.s.replace(/[<>&]/g, "")}</text>`;
    const n = Math.max(2, Math.ceil(Math.abs(s.a1 - s.a0) / 3));
    const pts = Array.from({ length: n + 1 }, (_, i) => {
      const a = rad(s.a0 + ((s.a1 - s.a0) * i) / n);
      return `${X(s.c[0] + s.r * Math.cos(a))},${Y(s.c[1] + s.r * Math.sin(a))}`;
    });
    return `<polyline points="${pts.join(" ")}"/>`;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${f(-m)} ${f(-m)} ${f(w + 2 * m)} ${f(h + 2 * m)}" width="${px}" style="max-width:100%;height:auto" fill="none" stroke="currentColor" stroke-width="${f(Math.max(w, h) / 400)}" role="img" aria-label="${part.name.replace(/[<>&"]/g, "")}">${el.join("")}</svg>`;
}
