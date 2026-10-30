// 2D imalat resmi ara modeli (A3 yatay). SVG ve DXF aynı modelden üretilir.
// K2: ölçüler yalnız project data + analitik profilden gelir (componentFrames/nozzlePlacement); CAD'den ölçülmez.
// Kâğıt koordinatı: mm, orijin sol alt, Y yukarı.
import type { Nozzle, VesselProject } from "../types";
import {
  componentFrames, nozzlePlacement, supportZ, tangentDatum, vesselProfileChain,
} from "../vesselModel";

export type Layer = "OUTLINE" | "HIDDEN" | "DIM" | "TEXT" | "TITLE";
export const LAYERS: Layer[] = ["OUTLINE", "HIDDEN", "DIM", "TEXT", "TITLE"];

export type Entity =
  | { t: "line"; layer: Layer; x1: number; y1: number; x2: number; y2: number }
  | { t: "poly"; layer: Layer; pts: [number, number][]; closed?: boolean }
  | { t: "circle"; layer: Layer; cx: number; cy: number; r: number }
  | { t: "text"; layer: Layer; x: number; y: number; h: number; s: string; anchor?: "start" | "middle" | "end"; rot?: number };

export type DimKind = "overall" | "tangent" | "inside-diameter" | "thickness" | "nozzle-pos" | "nozzle-proj" | "support";
export interface DimInfo { kind: DimKind; ref: string; value: number }

export interface DrawingModel {
  width: number;
  height: number;
  entities: Entity[];
  dimensions: DimInfo[];
  /** Çizimde etiketlenen nozul id'leri (yerleşemeyenler hariç). */
  nozzleLabels: string[];
  nozzleTable: string[][];
  overallLengthMm: number;
  tangentLengthMm: number;
  scaleText: string;
  warnings: string[];
}

export const NOT_APPROVAL = "Ön bilgi — imalat onayı değildir";
const W = 420;
const H = 297;
const SCALES = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 5000];
const niceN = (need: number) => SCALES.find((n) => n >= need) ?? Math.ceil(need);
const f = (n: number) => String(Math.round(n * 100) / 100);

class Sheet {
  e: Entity[] = [];
  dims: DimInfo[] = [];
  line(layer: Layer, x1: number, y1: number, x2: number, y2: number) { this.e.push({ t: "line", layer, x1, y1, x2, y2 }); }
  poly(layer: Layer, pts: [number, number][], closed = false) { if (pts.length > 1) this.e.push({ t: "poly", layer, pts, closed }); }
  circle(layer: Layer, cx: number, cy: number, r: number) { this.e.push({ t: "circle", layer, cx, cy, r }); }
  text(layer: Layer, x: number, y: number, s: string, h = 2.5, anchor: "start" | "middle" | "end" = "start", rot = 0) {
    this.e.push({ t: "text", layer, x, y, h, s, anchor, rot });
  }
  rect(layer: Layer, x1: number, y1: number, x2: number, y2: number) { this.poly(layer, [[x1, y1], [x2, y1], [x2, y2], [x1, y2]], true); }
  arrow(x: number, y: number, dx: number, dy: number) {
    const L = 2.5, w = 0.8, px = -dy, py = dx;
    this.line("DIM", x, y, x + dx * L + px * w, y + dy * L + py * w);
    this.line("DIM", x, y, x + dx * L - px * w, y + dy * L - py * w);
  }
  /** Yatay ölçü: x1..x2, ölçü çizgisi yLine; uzatma çizgileri yRef1/yRef2'den. */
  hDim(x1: number, x2: number, yRef1: number, yRef2: number, yLine: number, text: string) {
    const sg = (r: number) => (yLine >= r ? 1 : -1);
    this.line("DIM", x1, yRef1 + sg(yRef1), x1, yLine + sg(yRef1) * 1.5);
    this.line("DIM", x2, yRef2 + sg(yRef2), x2, yLine + sg(yRef2) * 1.5);
    this.line("DIM", x1, yLine, x2, yLine);
    const d = x2 >= x1 ? 1 : -1;
    this.arrow(x1, yLine, d, 0);
    this.arrow(x2, yLine, -d, 0);
    this.text("DIM", (x1 + x2) / 2, yLine + 1, text, 2.5, "middle");
  }
  /** Düşey ölçü: y1..y2, ölçü çizgisi xLine. */
  vDim(y1: number, y2: number, xRef1: number, xRef2: number, xLine: number, text: string) {
    const sg = (r: number) => (xLine >= r ? 1 : -1);
    this.line("DIM", xRef1 + sg(xRef1), y1, xLine + sg(xRef1) * 1.5, y1);
    this.line("DIM", xRef2 + sg(xRef2), y2, xLine + sg(xRef2) * 1.5, y2);
    this.line("DIM", xLine, y1, xLine, y2);
    const d = y2 >= y1 ? 1 : -1;
    this.arrow(xLine, y1, 0, d);
    this.arrow(xLine, y2, 0, -d);
    this.text("DIM", xLine - 0.8, (y1 + y2) / 2, text, 2.5, "middle", 90);
  }
}

export function buildDrawing(project: VesselProject): DrawingModel {
  const sh = new Sheet();
  const warnings: string[] = [];
  const frames = componentFrames(project);
  if (frames.length === 0) warnings.push("Bileşen zinciri boş — çizim üretilemedi.");
  const first = frames[0];
  const last = frames[frames.length - 1];
  const z0 = first?.zStart ?? 0;
  const z1 = last?.zEnd ?? 1;
  const overallLengthMm = z1 - z0;
  const datum = tangentDatum(frames);
  const tangentLengthMm = datum.right - datum.left;
  const rOutMax = Math.max(1, ...frames.map((fr) => Math.max(fr.rOutStart, fr.rOutEnd)));
  const rInRef = frames.find((fr) => fr.kind === "shell") ?? frames.find((fr) => fr.kind !== "head") ?? first;

  // Nozul yerleşimleri (K4: yerleşemeyen çizilmez, uyarı)
  const placed = project.nozzles.flatMap((nz) => {
    const pl = nozzlePlacement(project, nz, frames);
    if ("error" in pl) { warnings.push(`${nz.tag}: yerleşim yok (${pl.error}) — çizilmedi.`); return []; }
    const len = pl.frame.thickness + Math.max(nz.outside_projection, 0);
    const tip: [number, number, number] = [
      pl.position[0] + pl.axis[0] * len, pl.position[1] + pl.axis[1] * len, pl.position[2] + pl.axis[2] * len,
    ];
    return [{ nz, pl, len, tip }];
  });

  // ── Ön görünüş yerleşimi ──
  const FX0 = 45, FW = 330;
  const tipX = Math.max(0, ...placed.map((p) => Math.abs(p.tip[0])));
  const needN = Math.max(overallLengthMm / FW, Math.max(rOutMax, tipX) / 42);
  const N = niceN(needN);
  const s = 1 / N;
  const ox = FX0 + (FW - overallLengthMm * s) / 2 - z0 * s;
  const oy = 200;
  const X = (z: number) => ox + z * s;
  const Y = (x: number) => oy + x * s;

  // Profil: dış / iç yarı profil (vesselProfileChain: [...outer, ...inner.reverse()])
  const prof = vesselProfileChain(project.shell_sections, project.heads, project.cones ?? [], project.component_sequence ?? []);
  const half = Math.floor(prof.length / 2);
  const outer = prof.slice(0, half);
  const inner = prof.slice(half).reverse();
  const up = (pts: typeof outer) => pts.map((p): [number, number] => [X(p.z), Y(p.r)]);
  const dn = (pts: typeof outer) => pts.map((p): [number, number] => [X(p.z), Y(-p.r)]);
  if (outer.length > 1) {
    sh.poly("OUTLINE", up(outer));
    sh.poly("OUTLINE", up(inner));
    sh.poly("OUTLINE", dn(outer));
    sh.poly("HIDDEN", dn(inner));
    for (const [a, b] of [[outer[0], inner[0]], [outer[outer.length - 1], inner[inner.length - 1]]] as const) {
      sh.line("OUTLINE", X(a.z), Y(a.r), X(b.z), Y(b.r));
      sh.line("OUTLINE", X(a.z), Y(-a.r), X(b.z), Y(-b.r));
    }
  }
  // Eksen + teğet çizgileri
  sh.line("HIDDEN", X(z0) - 8, oy, X(z1) + 8, oy);
  for (const zt of [datum.left, datum.right]) sh.line("HIDDEN", X(zt), Y(-rOutMax) - 4, X(zt), Y(rOutMax) + 4);
  sh.text("TEXT", X(z0), oy - 4, "ÖN GÖRÜNÜŞ — YARIM KESİT", 3, "start");

  // Destekler (alt yarı, görünüş)
  let supBottom = 0;
  const supports: { id: string; z: number }[] = [];
  for (const sup of project.supports) {
    if (sup.type === "skirt") { warnings.push(`${sup.support_id}: etek konumu location_mm kullanmaz — ölçülendirilmedi.`); continue; }
    const z = supportZ(sup, frames);
    const hh = sup.height_mm > 0 ? sup.height_mm : rOutMax * 0.3;
    const w = sup.type === "saddle" ? Math.max(sup.width_mm, 20) : Math.max(sup.leg_diameter_mm ?? 60, 20);
    sh.rect("OUTLINE", X(z - w / 2), Y(-rOutMax - hh), X(z + w / 2), Y(-rOutMax));
    sh.text("TEXT", X(z), Y(-rOutMax - hh) - 3.5, sup.support_id, 2.2, "middle");
    supBottom = Math.max(supBottom, hh);
    supports.push({ id: sup.support_id, z });
  }

  // Nozullar — ön görünüş
  const drawNeck = (
    base: [number, number], tipP: [number, number], len: number, od: number, id: number, sc: number,
  ): [number, number] => {
    const dx = tipP[0] - base[0], dy = tipP[1] - base[1];
    const dl = Math.hypot(dx, dy);
    if (len <= 0 || dl / (len * sc) < 0.5) {
      sh.circle("OUTLINE", tipP[0], tipP[1], (od / 2) * sc);
      sh.circle("OUTLINE", tipP[0], tipP[1], (id / 2) * sc);
      return [0, 1];
    }
    const ux = dx / dl, uy = dy / dl, nx = -uy, ny = ux;
    for (const off of [od / 2, id / 2]) {
      sh.line("OUTLINE", base[0] + nx * off * sc, base[1] + ny * off * sc, tipP[0] + nx * off * sc, tipP[1] + ny * off * sc);
      sh.line("OUTLINE", base[0] - nx * off * sc, base[1] - ny * off * sc, tipP[0] - nx * off * sc, tipP[1] - ny * off * sc);
    }
    sh.line("OUTLINE", tipP[0] + nx * (od / 2) * sc, tipP[1] + ny * (od / 2) * sc, tipP[0] - nx * (od / 2) * sc, tipP[1] - ny * (od / 2) * sc);
    return [ux, uy];
  };
  const nozzleLabels: string[] = [];
  const topNoz: { z: number; yTip: number; tag: string }[] = [];
  const botNoz: { z: number; yTip: number; tag: string }[] = [];
  let topMax = Y(rOutMax);
  for (const { nz, pl, len, tip } of placed) {
    const base: [number, number] = [X(pl.position[2]), Y(pl.position[0])];
    const tp: [number, number] = [X(tip[2]), Y(tip[0])];
    const [ux, uy] = drawNeck(base, tp, len, nz.outside_diameter, nz.inside_diameter, s);
    const above = uy >= 0;
    sh.text("TEXT", tp[0] + (Math.abs(ux) > 0.5 ? 3 : 0), tp[1] + (above ? nz.outside_diameter * s / 2 + 2 : -nz.outside_diameter * s / 2 - 4.5), nz.tag, 2.8, Math.abs(ux) > 0.5 ? "start" : "middle");
    nozzleLabels.push(nz.tag);
    // çıkıntı ölçüsü: yalnız düşeye yakın nozullarda
    if (Math.abs(ux) < 0.3 && nz.outside_projection > 0) {
      const sgn = uy >= 0 ? 1 : -1;
      const y1 = base[1] + sgn * pl.frame.thickness * s;
      sh.vDim(y1, tp[1], tp[0], tp[0], tp[0] + (nz.outside_diameter / 2) * s + 6, f(nz.outside_projection));
      sh.dims.push({ kind: "nozzle-proj", ref: nz.tag, value: nz.outside_projection });
    }
    (pl.position[0] >= 0 ? topNoz : botNoz).push({ z: pl.position[2], yTip: tp[1], tag: nz.tag });
    topMax = Math.max(topMax, tp[1]);
  }

  // Et kalınlığı çağrıları (üst, sıra: iki kat)
  let ti = 0;
  for (const fr of frames) {
    if (fr.kind === "head" && fr.head?.side === "internal") continue;
    const zc = fr.kind === "head" && fr.head ? fr.head.equatorZ : (fr.zStart + fr.zEnd) / 2;
    const rr = fr.kind === "head" ? Math.max(fr.rOutStart, fr.rOutEnd) : (fr.rOutStart + fr.rOutEnd) / 2;
    const yText = Y(rOutMax) + 6 + (ti % 2) * 4.5;
    sh.line("DIM", X(zc), Y(rr), X(zc), yText - 0.5);
    sh.text("DIM", X(zc), yText, `t=${f(fr.thickness)}`, 2.5, "middle");
    sh.dims.push({ kind: "thickness", ref: fr.id, value: fr.thickness });
    ti++;
  }
  topMax = Math.max(topMax, Y(rOutMax) + 6 + 4.5 + 3);

  // İç çap (gövde ortasında içeriden)
  if (rInRef) {
    const di = 2 * rInRef.rInStart;
    const zm = (rInRef.zStart + rInRef.zEnd) / 2 + Math.min(rInRef.zEnd - rInRef.zStart, 4 * di) * 0.15;
    sh.vDim(Y(-rInRef.rInStart), Y(rInRef.rInStart), X(zm), X(zm), X(zm) + 0.01, `Ø${f(di)}`);
    sh.dims.push({ kind: "inside-diameter", ref: rInRef.id, value: di });
  }

  // Üst satırlar: nozul konumları (teğet-sol datumdan)
  const dY = Y(rOutMax);
  const gapRows = (n: number, avail: number) => Math.min(7, Math.max(3.5, avail / Math.max(n, 1)));
  const topRow = gapRows(topNoz.length, 285 - topMax - 4);
  topNoz.forEach((n, i) => {
    sh.hDim(X(datum.left), X(n.z), dY, n.yTip, topMax + 5 + i * topRow, `${n.tag}: ${f(n.z - datum.left)}`);
    sh.dims.push({ kind: "nozzle-pos", ref: n.tag, value: n.z - datum.left });
  });

  // Alt satırlar: teğet-teğet, toplam boy, destekler, alt nozullar
  const botY = Y(-rOutMax - supBottom);
  let row = 0;
  const rows = 2 + supports.length + botNoz.length;
  const botRow = gapRows(rows, botY - 128);
  const nextY = () => botY - 8 - row++ * botRow;
  sh.hDim(X(datum.left), X(datum.right), Y(-rOutMax), Y(-rOutMax), nextY(), `Teğet-teğet ${f(tangentLengthMm)}`);
  sh.dims.push({ kind: "tangent", ref: "T-T", value: tangentLengthMm });
  sh.hDim(X(z0), X(z1), Y(-rOutMax), Y(-rOutMax), nextY(), `Toplam boy (bombe dahil) ${f(overallLengthMm)}`);
  sh.dims.push({ kind: "overall", ref: "OA", value: overallLengthMm });
  for (const sp of supports) {
    sh.hDim(X(datum.left), X(sp.z), Y(-rOutMax), Y(-rOutMax - supBottom), nextY(), `${sp.id}: ${f(sp.z - datum.left)}`);
    sh.dims.push({ kind: "support", ref: sp.id, value: sp.z - datum.left });
  }
  for (const n of botNoz) {
    sh.hDim(X(datum.left), X(n.z), Y(-rOutMax), n.yTip, nextY(), `${n.tag}: ${f(n.z - datum.left)}`);
    sh.dims.push({ kind: "nozzle-pos", ref: n.tag, value: n.z - datum.left });
  }

  // ── Uç görünüş (z ekseni boyunca bakış; yatay = y, düşey = x) ──
  const ecx = 85, ecy = 78;
  const endExt = Math.max(rOutMax, ...placed.map((p) => Math.hypot(p.tip[0], p.tip[1])));
  const N2 = niceN(endExt / 38);
  const s2 = 1 / N2;
  sh.circle("OUTLINE", ecx, ecy, rOutMax * s2);
  sh.circle("OUTLINE", ecx, ecy, (rInRef?.rInStart ?? rOutMax) * s2);
  sh.line("HIDDEN", ecx - rOutMax * s2 - 5, ecy, ecx + rOutMax * s2 + 5, ecy);
  sh.line("HIDDEN", ecx, ecy - rOutMax * s2 - 5, ecx, ecy + rOutMax * s2 + 5);
  sh.text("TEXT", 22, 28, `UÇ GÖRÜNÜŞ (1:${N2})`, 3, "start");
  for (const { nz, pl, len, tip } of placed) {
    const b: [number, number] = [ecx + pl.position[1] * s2, ecy + pl.position[0] * s2];
    const t: [number, number] = [ecx + tip[1] * s2, ecy + tip[0] * s2];
    const [ux, uy] = drawNeck(b, t, len, nz.outside_diameter, nz.inside_diameter, s2);
    const out = Math.hypot(ux, uy) > 0 && (Math.abs(ux) > 0.5 || Math.abs(uy) < 0.99) && Math.hypot(t[0] - b[0], t[1] - b[1]) / (len * s2) >= 0.5;
    const lx = out ? t[0] + ux * 4 : t[0] + (nz.outside_diameter / 2) * s2 + 2;
    const ly = out ? t[1] + uy * 4 - 1 : t[1] + 1;
    sh.text("TEXT", lx, ly, nz.tag, 2.8, "middle");
  }

  // ── Antet ──
  sh.rect("TITLE", 10, 10, W - 10, H - 10);
  const tx = 225, ty = 10, tw = W - 10 - tx;
  sh.rect("TITLE", tx, ty, tx + tw, ty + 52);
  const mat = project.materials.find((m) => m.material_id === project.shell_sections[0]?.material_id)
    ?? project.materials[0];
  const matText = mat ? `${mat.material_designation} (${mat.material_id})` : "—";
  const rowsT: [string, string][] = [
    ["Proje no", project.project_number],
    ["Proje adı", project.project_name],
    ["Revizyon", project.revision],
    ["Kod", `${project.calculation_code} ${project.code_edition}`.trim()],
    ["Malzeme", matText],
    ["Ölçek", `Ön 1:${N} / Uç 1:${N2}  (A3, mm)`],
  ];
  rowsT.forEach(([k, v], i) => {
    const y = ty + 52 - (i + 1) * 6.2;
    sh.line("TITLE", tx, y, tx + tw, y);
    sh.text("TITLE", tx + 2, y + 1.8, k, 2.2);
    sh.text("TITLE", tx + 26, y + 1.8, v, 2.6);
  });
  sh.line("TITLE", tx + 24, ty + 52 - 6 * 6.2, tx + 24, ty + 52);
  sh.text("TITLE", tx + 2, ty + 2.2, NOT_APPROVAL, 3);

  // ── Nozul tablosu ──
  const header = ["Id", "DN / ölçü", "Flanş sınıfı", "Konum (mm)", "Açı (°)", "Çıkıntı"];
  const tableRows: string[][] = project.nozzles.map((nz) => [
    nz.tag,
    nz.size_designation ?? `Ø${f(nz.outside_diameter)}x${f(neckT(nz))}`,
    nz.rating_class ?? "—",
    posText(nz, frames, datum.left, project),
    f(nz.circumferential_angle),
    f(nz.outside_projection),
  ]);
  const cw = [18, 42, 28, 40, 18, 18];
  const nr = tableRows.length + 1;
  const rh = Math.min(6, 58 / nr);
  const tTop = ty + 52 + 4 + nr * rh;
  const colX = cw.reduce<number[]>((a, w, i) => (a.push((a[i] ?? tx) + w), a), [tx]);
  [header, ...tableRows].forEach((r, i) => {
    const y = tTop - (i + 1) * rh;
    sh.line("TITLE", tx, y, colX[colX.length - 1] ?? tx, y);
    r.forEach((c, j) => sh.text("TITLE", (colX[j] ?? tx) + 1, y + rh * 0.3, clip(c, (cw[j] ?? 20) / 1.6), Math.min(2.3, rh * 0.5)));
  });
  sh.line("TITLE", tx, tTop, colX[colX.length - 1] ?? tx, tTop);
  colX.forEach((x) => sh.line("TITLE", x, tTop - nr * rh, x, tTop));
  sh.text("TITLE", tx, tTop + 1.5, "NOZUL TABLOSU", 3);

  return {
    width: W, height: H, entities: sh.e, dimensions: sh.dims, nozzleLabels, nozzleTable: [header, ...tableRows],
    overallLengthMm, tangentLengthMm, scaleText: `1:${N}`, warnings,
  };
}

function neckT(nz: Nozzle) { return nz.neck_thickness; }
function clip(s: string, n: number) { return s.length > n ? s.slice(0, Math.max(1, Math.floor(n) - 1)) + "." : s; }
function posText(nz: Nozzle, frames: ReturnType<typeof componentFrames>, left: number, p: VesselProject): string {
  const pl = nozzlePlacement(p, nz, frames);
  return "error" in pl ? "yerleşim yok" : f(pl.position[2] - left);
}
