// D07 — flanşlı nozul: flanged (WN), slip_on (SO), pad_reinforced (WN + ped).
// Yerel +Z'de kurulur: z=0 host İÇ yüzeyi (çıpa), dış yüzey z=et kalınlığı, uç yüzü z=et+outside_projection.
// Boru + (WN konik hub | SO düz göbek) + flanş diski + RF tek (r,z) profilinin revolve'u;
// exact'te cıvata delikleri kesilir (preview'da delik yok). Ped: pad.ts.
import { drawPolysides, makeCompound, makeCylinder, type Shape3D, type Sketch } from "replicad";
import type {
  ComponentFrame, FlangeClass, FlangeRow, PartCtx, PartModule,
} from "../../geometryContract";
import type { Nozzle } from "../../types";
import { normNps } from "../../data/catalogs";
import { orient, revolveProfile, type Pt } from "../geom";
import { buildPadExact, padDims, padInlineRing } from "./pad";

export const partIdOf = (nz: Nozzle) => `nozzle:${nz.tag}`;

/** size_designation ('4" SCH40 CL150', '1½" SCH40') → katalog NPS anahtarı ("4", "1-1/2"). */
export function parseNps(sizeDesignation: string | null | undefined): string | null {
  if (!sizeDesignation) return null;
  const m = /^\s*(\d+(?:[ -]\d+\/\d+)?(?:\/\d+)?[¼½¾]?)/.exec(sizeDesignation);
  if (!m) return null;
  return normNps(m[1]).replace(" ", "-");
}

export function flangeClassOf(nz: Nozzle): FlangeClass {
  const r = (nz.rating_class ?? "").toUpperCase();
  if (/^CL(150|300|600|900|1500|2500)$/.test(r)) return r as FlangeClass;
  const m = /CL(150|300|600|900|1500|2500)/i.exec(nz.size_designation ?? "");
  return (m ? `CL${m[1]}` : "CL150") as FlangeClass;
}

/** Tamamen sayısal flanş ölçüleri (katalog null'ları oranla tamamlanmış). */
export interface Flg {
  O: number; tf: number; Rrf: number; rf: number; hb: number; hw: number;
  lWn: number; lSo: number; bc: number; n: number; bh: number; bd: number;
  missing: string[];
}

export function resolveFlange(nz: Nozzle, ctx: PartCtx): Flg {
  const D = nz.outside_diameter;
  const nps = parseNps(nz.size_designation);
  const row: FlangeRow | undefined = nps ? ctx.catalogs.flange(nps, flangeClassOf(nz)) : undefined;
  const missing: string[] = [];
  const pick = (v: number | null | undefined, fb: number, name: string): number => {
    if (v != null && v > 0) return v;
    missing.push(name);
    return fb;
  };
  const O = pick(row?.outside_diameter, 1.9 * D + 50, "dış çap");
  const tf = pick(row?.thickness, Math.max(14, 0.07 * O), "kalınlık");
  const bhDefault = Math.max(18, 0.045 * O);
  const f: Flg = {
    O, tf,
    Rrf: pick(row?.raised_face_diameter, 1.3 * D + 20, "RF çapı") / 2,
    rf: row ? row.raised_face_height : 1.6,
    hb: pick(row?.hub_base_diameter, 1.1 * D + 10, "hub tabanı"),
    hw: pick(row?.hub_weld_diameter, D, "hub kaynak ucu"),
    lWn: pick(row?.length_wn, 2.2 * tf, "WN boyu"),
    lSo: pick(row?.length_so, 1.2 * tf, "SO boyu"),
    bc: pick(row?.bolt_circle_diameter, O - 0.22 * (O - D), "cıvata dairesi"),
    n: Math.round(pick(row?.bolt_count, 4 * Math.max(1, Math.round(O / 90)), "cıvata sayısı")),
    bh: pick(row?.bolt_hole_diameter, bhDefault, "delik çapı"),
    bd: pick(row?.bolt_diameter, bhDefault - 3, "cıvata çapı"),
    missing,
  };
  if (!row) missing.unshift("flanş satırı (katalogda yok)");
  if (missing.length) {
    ctx.warn?.({
      partId: partIdOf(nz),
      code: "CATALOG_MISS",
      message: `${nz.tag}: flanş ${nps ?? "?"} ${flangeClassOf(nz)} — eksik ölçüler oranla tamamlandı: ${missing.join(", ")}`,
    });
  }
  return f;
}

/** Cıvata delikleri (compound; delik yarım adım ofsetli — eksenleri çevreler). */
export function boltHoleTool(f: Flg, z0: number, z1: number, holeD = f.bh): Shape3D {
  const cyls: Shape3D[] = [];
  const a0 = Math.PI / f.n;
  for (let i = 0; i < f.n; i++) {
    const a = a0 + (2 * Math.PI * i) / f.n;
    cyls.push(makeCylinder(holeD / 2, z1 - z0, [(f.bc / 2) * Math.cos(a), (f.bc / 2) * Math.sin(a), z0]));
  }
  return makeCompound(cyls) as Shape3D;
}

export function hexNut(rCirc: number, z0: number, h: number, x: number, y: number): Shape3D {
  const sk = drawPolysides(rCirc, 6).sketchOnPlane("XY", z0) as Sketch;
  return sk.extrude(h).translate(x, y, 0);
}

/** Yerleşim varsa yerel şekli global çerçeveye taşır (orient girdiyi tüketir). */
export function place(shape: Shape3D, ctx: PartCtx): Shape3D {
  return ctx.placement ? orient(shape, ctx.placement) : shape;
}

/** Yerel parçaları (revolve gövde + varsa ekstra) global çerçevede tek şekle toplar; exact'te ped ekler. */
export function finish(
  parts: Shape3D[], nz: Nozzle, frame: ComponentFrame | null, ctx: PartCtx, withPad: boolean,
): Shape3D {
  const placed = parts.map((p) => place(p, ctx));
  if (withPad && ctx.level === "exact") {
    try {
      const padS = buildPadExact(nz, frame, ctx);
      if (padS) placed.push(padS);
    } catch (err) {
      ctx.warn?.({
        partId: partIdOf(nz),
        code: "BOOLEAN_FAILED",
        message: `${nz.tag}: ped kurulamadı (${err instanceof Error ? err.message : String(err)})`,
      });
    }
  }
  return placed.length === 1 ? placed[0] : (makeCompound(placed) as Shape3D);
}

export interface FlangedBody {
  body: Shape3D; // yerel, delikleri kesilmiş (exact)
  flg: Flg;
  wall: number;
  tip: number; // uç (RF) yüzü z'si
  zDisc0: number; // flanş diski alt z'si
  padInline: boolean;
}

/** Boru + hub + disk + RF gövdesi (yerel). `form`: WN konik hub, SO düz göbek. */
export function buildFlangedBody(
  nz: Nozzle, frame: ComponentFrame | null, ctx: PartCtx, form: "wn" | "so",
): FlangedBody {
  const flg = resolveFlange(nz, ctx);
  const wall = frame?.thickness ?? 0;
  const tip = wall + Math.max(nz.outside_projection, 0);
  const inside = Math.max(nz.inside_projection, 0);
  const ro = nz.outside_diameter / 2;
  let ri = nz.inside_diameter / 2;
  if (!(ri > 0 && ri < ro)) ri = Math.max(ro - Math.max(nz.neck_thickness, 1), ro * 0.5);

  const Rd = flg.O / 2;
  const zd1 = tip - flg.rf;
  const zd0 = zd1 - flg.tf;
  const Rrf = Math.min(flg.Rrf, Rd);
  const hubLen = form === "wn" ? flg.lWn : flg.lSo;
  const zhs = Math.max(tip - hubLen, -inside + 1e-3);
  const hbR = Math.max(flg.hb / 2, ro);
  const hwR = Math.max(flg.hw / 2, ro);

  const exactPad = ctx.level === "exact" && !!frame && !!ctx.placement;
  // exact ped buildPadExact'te kurulur (uyarı orada verilir); burada yalnız preview/yedek için.
  const dims = padDims(nz, frame, exactPad ? { ...ctx, warn: undefined } : ctx);
  const padInline = dims != null && !exactPad;

  const pts: Pt[] = [[ri, -inside], [ro, -inside]];
  if (padInline && dims) {
    const pr = padInlineRing(dims, frame);
    if (pr.zBottom > -inside && pr.zTop < zhs - 1e-6) {
      pts.push([ro, pr.zBottom], [pr.rOut, pr.zBottom], [pr.rOut, pr.zTop], [ro, pr.zTop]);
    }
  }
  if (zhs < zd0 - 1e-6) {
    if (form === "wn") pts.push([ro, zhs], [hwR, zhs], [hbR, zd0]);
    else pts.push([ro, zhs], [hbR, zhs], [hbR, zd0]);
  } else {
    pts.push([ro, zd0]);
  }
  pts.push([Rd, zd0], [Rd, zd1]);
  if (flg.rf > 1e-6 && Rrf < Rd) pts.push([Rrf, zd1], [Rrf, tip]);
  else pts.push([Rd, tip]);
  pts.push([ri, tip]);

  const clean = pts.filter((p, i) => {
    const q = pts[(i + pts.length - 1) % pts.length];
    return Math.abs(p[0] - q[0]) > 1e-6 || Math.abs(p[1] - q[1]) > 1e-6;
  });
  let body = revolveProfile(clean[0], clean.slice(1).map((line) => ({ line })));

  if (ctx.level === "exact") {
    const tool = boltHoleTool(flg, zd0 - 1, zd1 + 1);
    try {
      const cut = body.cut(tool);
      body.delete();
      body = cut;
    } catch (err) {
      ctx.warn?.({
        partId: partIdOf(nz),
        code: "BOOLEAN_FAILED",
        message: `${nz.tag}: cıvata delikleri açılamadı (${err instanceof Error ? err.message : String(err)})`,
      });
    } finally {
      tool.delete();
    }
  }
  return { body, flg, wall, tip, zDisc0: zd0, padInline };
}

/** Host gövdesinden çıkarılacak nozul deliği (global; placement şart). */
export function boreCutter(nz: Nozzle, frame: ComponentFrame, ctx: PartCtx): Shape3D {
  const ri = Math.max(nz.inside_diameter / 2, 1);
  const len = frame.thickness * 2 + nz.outside_diameter;
  const cyl = makeCylinder(ri, len + frame.thickness, [0, 0, -frame.thickness]);
  return place(cyl, ctx);
}

export const flangedNozzle: PartModule<Nozzle> = {
  build(nz, frame, ctx) {
    const form = nz.nozzle_type === "slip_on" ? "so" : "wn";
    const { body } = buildFlangedBody(nz, frame, ctx, form);
    return finish([body], nz, frame, ctx, nz.reinforcement_pad || nz.nozzle_type === "pad_reinforced");
  },
  cutter: boreCutter,
};
