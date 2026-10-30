// DrawingModel → DXF R12 ASCII (AC1009). Katmanlar: OUTLINE, HIDDEN, DIM, TEXT, TITLE. Dış kütüphane yok.
import { LAYERS, type DrawingModel, type Entity, type Layer } from "./model";

const COLOR: Record<Layer, number> = { OUTLINE: 7, HIDDEN: 8, DIM: 5, TEXT: 7, TITLE: 3 };
const LTYPE: Record<Layer, string> = { OUTLINE: "CONTINUOUS", HIDDEN: "DASHED", DIM: "CONTINUOUS", TEXT: "CONTINUOUS", TITLE: "CONTINUOUS" };

const TR: Record<string, string> = {
  "ş": "s", "Ş": "S", "ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C",
  "—": "-", "–": "-", "Ø": "%%c", "°": "%%d",
};
/** R12 ASCII: Türkçe karakterleri sadeleştir, Ø/° için DXF kodlarını kullan. */
export function dxfText(s: string): string {
  return s.replace(/[^\x20-\x7e]/g, (c) => TR[c] ?? "?");
}

type G = (code: number, v: string | number) => void;

export function drawingToDxf(m: DrawingModel): string {
  const o: string[] = [];
  const g: G = (code, v) => { o.push(String(code), String(typeof v === "number" ? Math.round(v * 1e4) / 1e4 : v)); };

  g(0, "SECTION"); g(2, "HEADER"); g(9, "$ACADVER"); g(1, "AC1009");
  g(9, "$EXTMIN"); g(10, 0); g(20, 0); g(30, 0);
  g(9, "$EXTMAX"); g(10, m.width); g(20, m.height); g(30, 0);
  g(0, "ENDSEC");

  g(0, "SECTION"); g(2, "TABLES");
  g(0, "TABLE"); g(2, "LTYPE"); g(70, 2);
  g(0, "LTYPE"); g(2, "CONTINUOUS"); g(70, 0); g(3, "Solid line"); g(72, 65); g(73, 0); g(40, 0);
  g(0, "LTYPE"); g(2, "DASHED"); g(70, 0); g(3, "Dashed"); g(72, 65); g(73, 2); g(40, 4.5); g(49, 3); g(49, -1.5);
  g(0, "ENDTAB");
  g(0, "TABLE"); g(2, "LAYER"); g(70, LAYERS.length);
  for (const l of LAYERS) { g(0, "LAYER"); g(2, l); g(70, 0); g(62, COLOR[l]); g(6, LTYPE[l]); }
  g(0, "ENDTAB");
  g(0, "ENDSEC");

  g(0, "SECTION"); g(2, "ENTITIES");
  for (const e of m.entities) emit(e, g);
  g(0, "ENDSEC");
  g(0, "EOF");
  return o.join("\n") + "\n";
}

function emit(e: Entity, g: G) {
  switch (e.t) {
    case "line":
      g(0, "LINE"); g(8, e.layer); g(10, e.x1); g(20, e.y1); g(30, 0); g(11, e.x2); g(21, e.y2); g(31, 0); break;
    case "circle":
      g(0, "CIRCLE"); g(8, e.layer); g(10, e.cx); g(20, e.cy); g(30, 0); g(40, e.r); break;
    case "poly":
      g(0, "POLYLINE"); g(8, e.layer); g(66, 1); g(70, e.closed ? 1 : 0);
      for (const [x, y] of e.pts) { g(0, "VERTEX"); g(8, e.layer); g(10, x); g(20, y); g(30, 0); }
      g(0, "SEQEND"); g(8, e.layer); break;
    case "text":
      g(0, "TEXT"); g(8, e.layer); g(10, e.x); g(20, e.y); g(30, 0); g(40, e.h); g(1, dxfText(e.s));
      if (e.rot) g(50, e.rot);
      if (e.anchor === "middle" || e.anchor === "end") {
        g(72, e.anchor === "middle" ? 1 : 2); g(11, e.x); g(21, e.y); g(31, 0);
      }
      break;
  }
}
