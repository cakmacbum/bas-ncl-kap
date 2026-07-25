// Nozul boru ölçü kataloğu — anma çapı + et serisi seçilince OD/ID/et otomatik dolar.
//
// K6: Lisanslı standart tablosu GÖMÜLMEZ. Veriler `data/nozzle-catalog.json`
//     dosyasındadır, kaynağı "kullanıcı girişi" olarak işaretlidir ve
//     `verified: false` olduğu sürece arayüzde uyarı rozeti gösterilir.
// K5: Seçilen satır `nozzle.size_designation` alanına yazılır — raporda hangi
//     ölçünün kullanıldığı denetlenebilir olsun.

import catalogRaw from "./data/nozzle-catalog.json";

export interface CatalogSize {
  label: string;
  dn: number;
  od: number;
  walls: Record<string, number>;
}

export interface NozzleCatalog {
  source: string;
  verified: boolean;
  revision: string;
  note: string;
  wallSeries: string[];
  sizes: CatalogSize[];
}

export const catalog = catalogRaw as NozzleCatalog;

/** Ölçü seçici için "1½\" (DN40)" biçiminde etiketler. */
export const sizeOptions = catalog.sizes.map((s) => ({
  value: s.label,
  label: `${s.label} (DN${s.dn})`,
}));

export const wallOptions = catalog.wallSeries.map((w) => ({ value: w, label: w }));

/** Katalogdan tek satır — bulunamazsa null. */
export function findSize(label: string): CatalogSize | null {
  return catalog.sizes.find((s) => s.label === label) ?? null;
}

export interface NozzleDims {
  outside_diameter: number;
  inside_diameter: number;
  neck_thickness: number;
  size_designation: string;
}

/**
 * Anma çapı + et serisinden nozul boru ölçüleri.
 * İç çap = OD − 2×et (K1: mühendislik formülü değil, geometri tanımı).
 */
export function dimsFor(label: string, series: string): NozzleDims | null {
  const size = findSize(label);
  const wall = size?.walls[series];
  if (!size || wall === undefined) return null;
  return {
    outside_diameter: size.od,
    inside_diameter: +(size.od - 2 * wall).toFixed(2),
    neck_thickness: wall,
    size_designation: `${size.label} ${series}`,
  };
}

/**
 * Mevcut ölçülerin hangi katalog satırına karşılık geldiğini bul.
 * Elle değiştirilmişse null döner → arayüz "Özel ölçü" gösterir.
 */
export function matchDims(
  od: number,
  wall: number,
): { label: string; series: string } | null {
  const tol = 0.05;
  for (const s of catalog.sizes) {
    if (Math.abs(s.od - od) > tol) continue;
    for (const [series, w] of Object.entries(s.walls)) {
      if (Math.abs(w - wall) <= tol) return { label: s.label, series };
    }
  }
  return null;
}

export const CUSTOM = "__custom__";
