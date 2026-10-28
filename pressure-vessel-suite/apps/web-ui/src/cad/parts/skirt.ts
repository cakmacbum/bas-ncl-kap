// D08 — etek: sol bombe teğet çizgisinden (zEnd) aşağı height_mm; taban halkası + ankraj delikleri (exact).
// Yalnız dikey kap; Ø = diameter_mm ?? sol bombe dış çapı; et = thickness_mm ?? 10. Menhol açıklığı kapsam dışı.
// height_mm halkayı da içerir (alt yüz = zEnd − height_mm).
import type { PartModule } from "../../geometryContract";
import type { Support } from "../../types";
import { tangentDatum } from "../../vesselModel";
import { cyl, makeCylinder } from "./supportGeom";

export const skirt: PartModule<Support> = {
  build(p, frame, ctx) {
    const partId = `support:${p.support_id}`;
    if (ctx.orientation !== "vertical") {
      ctx.warn?.({ partId, code: "OUT_OF_HOST", message: `${p.support_id}: etek yalnız dikey kapta çizilir` });
      return null;
    }
    const zTop = tangentDatum(ctx.frames).left;
    const first = ctx.frames[0];
    const hostR = frame?.rOutStart ?? Math.max(first?.rOutStart ?? 0, first?.rOutEnd ?? 0);
    const rOut = (p.diameter_mm ?? 2 * (hostR || 500)) / 2;
    const t = Math.max(p.thickness_mm ?? 10, 1);
    const H = Math.max(p.height_mm || 1000, 50);
    const tb = Math.max(p.base_plate_thickness_mm ?? 25, 1);
    const rMid = rOut - t / 2;
    const ringW = Math.max(p.base_plate_width_mm ?? 3 * t + 60, 2 * t);
    const zBase = zTop - H; // halka alt yüzü

    const tube = cyl(rOut, zBase + tb, zTop).cut(cyl(rOut - t, zBase, zTop + 1));
    let ring = cyl(rMid + ringW / 2, zBase, zBase + tb).cut(cyl(rMid - ringW / 2, zBase - 1, zBase + tb + 1));
    if (ctx.level === "exact") {
      const n = Math.max(p.anchor_bolt_count ?? 8, 0);
      const d = (p.anchor_bolt_diameter_mm ?? 24) + 4;
      for (let i = 0; i < n; i++) {
        const a = (2 * Math.PI * i) / n;
        ring = ring.cut(makeCylinder(d / 2, tb + 2, [rMid * Math.cos(a), rMid * Math.sin(a), zBase - 1], [0, 0, 1]));
      }
    }
    return tube.fuse(ring);
  },
};
