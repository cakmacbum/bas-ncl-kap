// D08 — eyer: aşınma plakası (contact_angle_deg boyunca kabı saran), dikey web, 4 kaburga, delikli taban plakası.
// "Aşağı" = −X (yatay kap). Eksenel merkez = supportZ (sol teğet datumu + location_mm).
// height_mm = kap dış altı → taban alt yüzü. Eyer yatay kaba aittir; dikey kapta aynı çerçevede kurulur.
import { draw } from "replicad";
import type { Shape3D, Sketch } from "replicad";
import type { PartModule } from "../../geometryContract";
import type { Support } from "../../types";
import { supportZ } from "../../vesselModel";
import { box, cyl, DEG, fuseAll, makeCylinder, outerRadiusAt } from "./supportGeom";

export const saddle: PartModule<Support> = {
  build(p, frame, ctx) {
    const partId = `support:${p.support_id}`;
    const zc = supportZ(p, ctx.frames);
    const R = outerRadiusAt(ctx.frames, zc, frame);
    const tw = Math.max(p.thickness_mm ?? 12, 1);
    const W = Math.max(p.width_mm || 200, 2 * tw);
    const H = Math.max(p.height_mm || 300, tw + 20);
    const half = Math.min(Math.max((p.contact_angle_deg ?? 120) / 2, 10), 175) * DEG;
    const zLo = zc - W / 2;
    const zHi = zc + W / 2;
    const end = ctx.frames[ctx.frames.length - 1]?.zEnd ?? Infinity;
    if (zLo < 0 || zHi > end) {
      ctx.warn?.({ partId, code: "OUT_OF_HOST", message: `${p.support_id} eyeri kap uzunluğunun dışında kalıyor` });
    }

    // Aşınma plakası: (R+tw)−R halkası ∩ −X ekseninde ±half'lık kama
    const ang0 = Math.PI - half;
    const steps = Math.max(2, Math.ceil((2 * half) / (30 * DEG)));
    let pen = draw([0, 0]);
    for (let i = 0; i <= steps; i++) {
      const a = ang0 + (2 * half * i) / steps;
      pen = pen.lineTo([3 * R * Math.cos(a), 3 * R * Math.sin(a)]);
    }
    const wedge = (pen.close().sketchOnPlane("XY", zLo) as Sketch).extrude(W);
    const wear = cyl(R + tw, zLo, zHi).cut(cyl(R, zLo - 1, zHi + 1)).intersect(wedge);

    const clip = (s: Shape3D) => s.cut(cyl(R + tw, zLo - 5, zHi + 5)); // plaka içi kısmı at
    const tb = Math.max(p.base_plate_thickness_mm ?? 20, 1);
    const xBase = -(R + H); // taban alt yüzü
    const yMax = R * Math.sin(Math.min(half, 80 * DEG));
    const web = clip(box(xBase + tb, 0, -yMax, yMax, zc - tw / 2, zc + tw / 2));
    const ribs = [yMax - tw / 2, yMax / 2]
      .flatMap((y) => [y, -y])
      .map((y) => clip(box(xBase + tb, 0, y - tw / 2, y + tw / 2, zLo, zHi)));

    const bl = Math.max(p.base_plate_length_mm ?? 2 * yMax, 2 * tw);
    const bw = Math.max(p.base_plate_width_mm ?? W, 2 * tw);
    let base = box(xBase, xBase + tb, -bl / 2, bl / 2, zc - bw / 2, zc + bw / 2);
    if (ctx.level === "exact") {
      const d = (p.anchor_bolt_diameter_mm ?? 22) + 2;
      const iy = Math.min(40, bl / 4);
      const iz = Math.min(40, bw / 4);
      for (const sy of [-1, 1]) {
        for (const sz of [-1, 1]) {
          base = base.cut(
            makeCylinder(d / 2, tb + 2, [xBase - 1, sy * (bl / 2 - iy), zc + sz * (bw / 2 - iz)], [1, 0, 0]),
          );
        }
      }
    }
    return fuseAll([base, web, ...ribs, wear]);
  },
};
