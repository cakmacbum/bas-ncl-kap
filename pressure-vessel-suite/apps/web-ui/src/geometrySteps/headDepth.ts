// Eliptik bombe kubbe derinliği (h) yardımcıları: ASME 1-4(c) geçerlilik aralığı 1 ≤ D/2h ≤ 3.

import type { Head, HeadTypeT } from "../types";
import { fmt } from "./shared";

/** D/2h oranı (h ≤ 0 ise NaN). */
export const depthRatio = (di: number, h: number): number => (h > 0 ? di / (2 * h) : NaN);

/** Eliptik bombe şekil katsayısı K = (2 + (D/2h)²) / 6. */
export const ellipticalK = (ratio: number): number => (2 + ratio * ratio) / 6;

/** Alanın yazacağı yama: 0 → null (standart 2:1). */
export const crownDepthPatch = (v: number): Pick<Head, "crown_depth"> => ({ crown_depth: v > 0 ? v : null });

/** Tip değişiminde yazılacak yama: eliptik dışına geçerken crown_depth temizlenir. */
export const typeChangePatch = (t: HeadTypeT): Partial<Head> =>
  t === "elliptical" ? { type: t } : { type: t, crown_depth: null };

/** Eliptik bombe için geçersiz h mesajı; geçerli/standartsa null. Kırpma yok. */
export function headDepthIssueMessage(head: Pick<Head, "head_id" | "type" | "inside_diameter" | "crown_depth">): string | null {
  const h = head.crown_depth;
  if (head.type !== "elliptical" || h == null || !(h > 0)) return null;
  const di = head.inside_diameter;
  const r = depthRatio(di, h);
  if (r >= 1 - 1e-9 && r <= 3 + 1e-9) return null;
  return `${head.head_id}: kubbe derinliği h = ${fmt(h)} mm geçersiz — ASME 1-4(c) yalnız 1 ≤ D/2h ≤ 3 için geçerli `
    + `(şu an D/2h = ${fmt(r, 2)}); h, Di/6…Di/2 = ${fmt(di / 6)}…${fmt(di / 2)} mm aralığında olmalı. [HEAD_DEPTH_RANGE]`;
}
