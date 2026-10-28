// geometryContract `Catalogs` arayüzünün D03 okuyucusu (catalogs.ts) üzerindeki
// uygulaması. D03 alan adları sözleşme §4'ten farklıdır; eşleme burada yapılır.
//
// K4/K6: Kaynakta olmayan ölçü uydurulmaz — null korunur. Weldolet katalogda yok → undefined.
// Tüm veriler `verified:false` (catalogsUnverified) — UI uyarı rozeti göstermelidir.

import type {
  Catalogs, CouplingForm, CouplingRating, CouplingRow, FlangeClass, FlangeRow, PipeSize,
} from "../geometryContract";
import {
  getCoupling, getFlange, normNps, pipeCatalog,
  type CouplingEntry, type FlangeClass as D03FlangeClass, type PipeSchedule,
} from "./catalogs";

/** "CL150" → 150 */
export function flangeClassNumber(cls: FlangeClass): D03FlangeClass {
  return Number(cls.slice(2)) as D03FlangeClass;
}

/** "3000#" → 3000 */
function couplingRatingNumber(r: CouplingRating): 3000 | 6000 {
  return r === "6000#" ? 6000 : 3000;
}

/** D03 anahtarı "1 1/2" → sözleşme ASCII "1-1/2". */
function contractNps(key: string): string {
  return key.replace(" ", "-");
}

const FRACTION_GLYPH: Record<string, string> = { "1/8": "⅛", "1/4": "¼", "3/8": "⅜", "1/2": "½", "3/4": "¾" };

/** "1 1/2" → `1½"`, "3/4" → `¾"` */
function npsLabel(key: string): string {
  const parts = key.split(" ");
  const frac = parts[parts.length - 1];
  if (FRACTION_GLYPH[frac]) {
    return `${parts.length > 1 ? parts[0] : ""}${FRACTION_GLYPH[frac]}"`;
  }
  return `${key}"`;
}

/** D03 seri adı ("40", "5S", "STD") → sözleşme wallSeries adı ("SCH40", "SCH5S", "STD"). */
export function contractSchedule(s: string): string {
  const u = s.trim().toUpperCase();
  if (u.startsWith("SCH")) return u;
  return /^\d/.test(u) ? `SCH${u}` : u;
}

function toPipeSize(size: (typeof pipeCatalog.sizes)[number]): PipeSize {
  const walls: Record<string, number | null> = {};
  for (const [k, v] of Object.entries(size.walls)) walls[contractSchedule(k)] = v;
  return { nps: contractNps(size.nps), label: npsLabel(size.nps), dn: size.dn, od: size.od, walls };
}

/** Katalogdaki tüm boru ölçüleri (DN sırasıyla) — UI seçim listeleri için. */
export function listPipeSizes(): PipeSize[] {
  return [...pipeCatalog.sizes].sort((a, b) => a.dn - b.dn).map(toPipeSize);
}

function mean(a: number | null, b: number | null): number | null {
  if (a != null && b != null) return +((a + b) / 2).toFixed(3);
  return a ?? b;
}

function toCouplingRow(e: CouplingEntry): CouplingRow {
  return {
    nps: contractNps(e.nps),
    dn: e.dn,
    rating: e.rating,
    form: e.kind,
    end: e.end === "socket_weld" ? "socket" : "threaded",
    body_od: e.od,
    top_od: null,
    length: e.length,
    socket_bore: mean(e.socket_bore_min, e.socket_bore_max),
    socket_depth: e.socket_depth,
    bore: mean(e.bore_min, e.bore_max),
    chamfer: null,
  };
}

export const catalogs: Catalogs = {
  pipe(nps) {
    const key = normNps(nps);
    const size = pipeCatalog.sizes.find((s) => s.nps === key);
    return size ? toPipeSize(size) : undefined;
  },
  flange(nps, cls) {
    const e = getFlange(nps, flangeClassNumber(cls));
    if (!e) return undefined;
    const row: FlangeRow = {
      nps: contractNps(e.nps),
      dn: e.dn,
      class: e.class,
      outside_diameter: e.O,
      thickness: e.tf,
      raised_face_diameter: e.R,
      raised_face_height: e.rf_height,
      hub_base_diameter: e.X,
      hub_weld_diameter: e.Ah,
      length_wn: e.Y_wn,
      length_so: e.Y_so,
      bore_so: null,
      bolt_circle_diameter: e.bolt_circle,
      bolt_count: e.bolt_count,
      bolt_hole_diameter: e.bolt_hole,
      bolt_diameter: e.bolt_dia,
    };
    return row;
  },
  coupling(nps, rating, form: CouplingForm, end = "threaded") {
    if (form === "weldolet") return undefined;
    const e = getCoupling(nps, couplingRatingNumber(rating), form, end === "socket" ? "socket_weld" : "threaded");
    return e ? toCouplingRow(e) : undefined;
  },
};

// ── Manşon nozul ölçüleri (store.addCoupling) ──────────────────────────────
// Katalog satırında boş kalan ölçüler yalnızca geometrik özdeşlik veya B16.11
// sınıf↔schedule eşlemesiyle tamamlanır; tamamlanamıyorsa null (katalogda yok).
//   threaded: bore yok → bağlanan borunun iç çapı (B16.11 Tablo 1: 3000#→SCH160, 6000#→XXS)
//   socket:   OD = soket çapı + 2·soket et kalınlığı; boy (full) = E + 2·J; half SW boy → null
const THREADED_SCHEDULE: Record<3000 | 6000, PipeSchedule> = { 3000: "160", 6000: "XXS" };

export interface CouplingNozzleDims { od: number; id: number; length: number; row: CouplingRow }

export function couplingNozzleDims(
  nps: string,
  rating: CouplingRating,
  form: CouplingForm,
  end: "socket" | "threaded",
): CouplingNozzleDims | null {
  if (form === "weldolet") return null;
  const r = couplingRatingNumber(rating);
  const e = getCoupling(nps, r, form, end === "socket" ? "socket_weld" : "threaded");
  if (!e) return null;
  const row = toCouplingRow(e);
  let od = row.body_od;
  let id = row.bore;
  let length = row.length;
  if (end === "threaded" && id == null) {
    const size = pipeCatalog.sizes.find((s) => s.nps === e.nps);
    const t = size?.walls[THREADED_SCHEDULE[r]];
    if (size && t != null) id = +(size.od - 2 * t).toFixed(2);
  }
  if (end === "socket") {
    if (od == null && row.socket_bore != null && e.socket_wall_avg != null) {
      od = +(row.socket_bore + 2 * e.socket_wall_avg).toFixed(2);
    }
    if (length == null && form === "full" && e.laying_length != null && e.socket_depth != null) {
      length = e.laying_length + 2 * e.socket_depth;
    }
  }
  if (od == null || id == null || length == null || od <= id) return null;
  return { od, id, length, row };
}
