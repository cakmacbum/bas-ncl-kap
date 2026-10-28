// D07 — takviye pedi: host dış yüzeyine sarılı halka.
//   exact:  (host dış katısının t_pad kadar kalınlaştırılmışı ∩ silindir(pad_od)) − host − silindir(OD)
//   preview: boolean yok; flangedNozzle/manway profile düz halkayı gömer (padInlineRing).
// Ayrı varlık değildir: nozul partId'si altında birleşik mesh'e girer (sözleşme).
import { makeCylinder, type Shape3D } from "replicad";
import type { ComponentFrame, PartCtx, PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";
import { orient } from "../geom";
import { buildChainSolid } from "./shellChain";

export interface PadDims {
  od: number; // pad dış çapı
  t: number; // pad kalınlığı
}

/** Pad ölçüleri; eksik alan → makul varsayılan + CATALOG_MISS. null → pad yok. */
export function padDims(nz: Nozzle, frame: ComponentFrame | null, ctx: PartCtx): PadDims | null {
  if (!nz.reinforcement_pad && nz.nozzle_type !== "pad_reinforced") return null;
  const missing: string[] = [];
  let od = nz.reinforcement_pad_od ?? 0;
  if (!(od > nz.outside_diameter)) {
    od = 2 * nz.outside_diameter;
    missing.push("pad dış çapı");
  }
  let t = nz.reinforcement_pad_thickness ?? 0;
  if (!(t > 0)) {
    t = frame?.thickness ?? 10;
    missing.push("pad kalınlığı");
  }
  if (missing.length) {
    ctx.warn?.({
      partId: `nozzle:${nz.tag}`,
      code: "CATALOG_MISS",
      message: `${nz.tag}: ${missing.join(", ")} girilmedi; varsayılan (2·OD, host et kalınlığı) kullanıldı`,
    });
  }
  return { od, t };
}

/** Preview için (r,z) profilinde gömülecek düz halka: [zBottom, zTop, rOut]. Alt yüz host sagitasına göre alçaltılır. */
export function padInlineRing(dims: PadDims, frame: ComponentFrame | null): { zBottom: number; zTop: number; rOut: number } {
  const wall = frame?.thickness ?? 0;
  const R = Math.max(frame?.rOutStart ?? 0, frame?.rOutEnd ?? 0);
  const rp = dims.od / 2;
  const sag = R > rp ? R - Math.sqrt(R * R - rp * rp) : R;
  return { zBottom: Math.max(0, wall - sag - 1), zTop: wall + dims.t, rOut: rp };
}

/**
 * Exact pad (global çerçevede, oriented). frame + placement yoksa null.
 * Host kalınlaştırması buildChainSolid ile (bombe dizi parametreleri bilinmediğinden
 * torisferik knuckle yedek oranı kullanılır — pad ile host aynı yedekle kurulur, tutarlı).
 */
export function buildPadExact(nz: Nozzle, frame: ComponentFrame | null, ctx: PartCtx): Shape3D | null {
  const dims = padDims(nz, frame, ctx);
  if (!dims || !frame || !ctx.placement) return null;
  const wall = frame.thickness;
  const ro = nz.outside_diameter / 2;
  const top = wall + dims.t + dims.od / 2;
  const thick = buildChainSolid({ ...frame, thickness: wall + dims.t }, undefined);
  const host = buildChainSolid(frame, undefined);
  if (!thick || !host) {
    thick?.delete();
    host?.delete();
    return null;
  }
  const padCyl = orient(makeCylinder(dims.od / 2, top + wall, [0, 0, -wall]), ctx.placement);
  const nozCyl = orient(makeCylinder(ro, top + wall, [0, 0, -wall]), ctx.placement);
  try {
    const a = thick.intersect(padCyl);
    const b = a.cut(host);
    const c = b.cut(nozCyl);
    a.delete();
    b.delete();
    return c;
  } finally {
    thick.delete();
    host.delete();
    padCyl.delete();
    nozCyl.delete();
  }
}

/** Kayıt defteri uyumu: pad tek başına varlık değildir; build exact pad'i (varsa) döndürür. */
export const pad: PartModule<Nozzle> = {
  build(params, frame, ctx) {
    return buildPadExact(params, frame, ctx);
  },
};
