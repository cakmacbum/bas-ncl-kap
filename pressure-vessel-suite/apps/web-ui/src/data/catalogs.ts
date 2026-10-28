// Parça ölçü katalogları — B16.5 flanş, NPS boru, B16.11 manşon (coupling).
//
// K6: Lisanslı standart metni GÖMÜLMEZ. Veriler bu klasördeki JSON dosyalarındadır;
//     her dosyada `source`, `license_note` ve `verified: false` vardır — doğrulanana
//     kadar arayüz uyarı rozeti göstermelidir.
// Birim: mm. `null` = kaynakta yok / güvenle okunamadı (uydurulmadı).

import flangeRaw from "./flange-b165.json";
import pipeRaw from "./pipe-nps.json";
import couplingRaw from "./coupling-catalog.json";

export type FlangeClass = 150 | 300 | 600 | 900 | 1500 | 2500;
export type PipeSchedule = "5S" | "10" | "10S" | "40" | "STD" | "80" | "XS" | "160" | "XXS";
export type CouplingRating = 3000 | 6000;
export type CouplingKind = "full" | "half";
export type CouplingEnd = "threaded" | "socket_weld";

interface CatalogMeta {
  standard: string;
  source: string;
  license_note: string;
  verified: boolean;
  units: string;
  note: string;
}

export interface FlangeEntry {
  nps: string;
  dn: number;
  class: FlangeClass;
  O: number | null;
  tf: number | null;
  tf_lap: number | null;
  R: number | null;
  rf_height: number;
  X: number | null;
  Ah: number | null;
  Y_wn: number | null;
  Y_so: number | null;
  Y_lap: number | null;
  bolt_circle: number | null;
  bolt_count: number | null;
  bolt_hole: number | null;
  bolt_size_in: string | null;
  bolt_dia: number | null;
  src: Record<string, unknown>;
}

export interface PipeSize {
  nps: string;
  dn: number;
  od: number;
  od_in: number;
  walls: Record<PipeSchedule, number | null>;
}

export interface CouplingEntry {
  nps: string;
  dn: number;
  rating: CouplingRating;
  end: CouplingEnd;
  kind: CouplingKind;
  od: number | null;
  length: number | null;
  laying_length?: number | null;
  thread: string | null;
  thread_min_perfect: number | null;
  thread_min_useful: number | null;
  socket_bore_max: number | null;
  socket_bore_min: number | null;
  socket_depth: number | null;
  bore_max: number | null;
  bore_min: number | null;
  socket_wall_avg: number | null;
  socket_wall_min: number | null;
  src: string | null;
}

export const flangeCatalog = flangeRaw as unknown as CatalogMeta & { entries: FlangeEntry[] };
export const pipeCatalog = pipeRaw as unknown as CatalogMeta & { schedules: PipeSchedule[]; sizes: PipeSize[] };
export const couplingCatalog = couplingRaw as unknown as CatalogMeta & { entries: CouplingEntry[] };

/** "1-1/2", "1.1/2", "1½" gibi yazımları katalog anahtarına ("1 1/2") indirger. */
export function normNps(nps: string | number): string {
  return String(nps)
    .trim()
    .replace(/"/g, "")
    .replace(/¼/g, " 1/4")
    .replace(/½/g, " 1/2")
    .replace(/¾/g, " 3/4")
    .replace(/[-.](?=\d+\/)/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** B16.5 flanş satırı — bulunamazsa null. */
export function getFlange(nps: string | number, cls: FlangeClass): FlangeEntry | null {
  const key = normNps(nps);
  return flangeCatalog.entries.find((e) => e.nps === key && e.class === cls) ?? null;
}

/** Boru OD + et kalınlığı; seri tanımlı değilse null. ID = OD − 2t. */
export function getPipe(
  nps: string | number,
  sch: PipeSchedule,
): { nps: string; dn: number; od: number; t: number; id: number } | null {
  const key = normNps(nps);
  const size = pipeCatalog.sizes.find((s) => s.nps === key);
  const t = size?.walls[sch];
  if (!size || t == null) return null;
  return { nps: size.nps, dn: size.dn, od: size.od, t, id: +(size.od - 2 * t).toFixed(2) };
}

/** B16.11 coupling satırı (varsayılan uç: threaded) — bulunamazsa null. */
export function getCoupling(
  nps: string | number,
  rating: CouplingRating,
  kind: CouplingKind,
  end: CouplingEnd = "threaded",
): CouplingEntry | null {
  const key = normNps(nps);
  return (
    couplingCatalog.entries.find(
      (e) => e.nps === key && e.rating === rating && e.kind === kind && e.end === end,
    ) ?? null
  );
}

/** Üç katalogdan herhangi biri doğrulanmamışsa true (UI uyarı rozeti için). */
export const catalogsUnverified =
  !flangeCatalog.verified || !pipeCatalog.verified || !couplingCatalog.verified;
