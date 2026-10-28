// D07 — manway: boyun (boru) + B16.5 WN flanş + kör kapak + saplama/somun dizisi + davit kolu.
// Yerel +Z; basit oranlar (ölçek: flanş dış çapı O, cıvata çapı bd). Tek mesh (compound).
import { makeBox, makeCylinder, type Shape3D } from "replicad";
import type { PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";
import {
  boltHoleTool, boreCutter, buildFlangedBody, finish, hexNut, partIdOf,
} from "./flangedNozzle";

export const manway: PartModule<Nozzle> = {
  build(nz, frame, ctx) {
    const { body, flg, tip, zDisc0 } = buildFlangedBody(nz, frame, ctx, "wn");
    const parts: Shape3D[] = [body];

    const Rd = flg.O / 2;
    const tc = flg.tf; // kapak kalınlığı = flanş kalınlığı
    const zc1 = tip + tc;

    // Kör kapak (RF yüzüne oturur); exact'te cıvata delikleri
    let cover: Shape3D = makeCylinder(Rd, tc, [0, 0, tip]);
    if (ctx.level === "exact") {
      const tool = boltHoleTool(flg, tip - 1, zc1 + 1);
      try {
        const cut = cover.cut(tool);
        cover.delete();
        cover = cut;
      } catch (err) {
        ctx.warn?.({
          partId: partIdOf(nz),
          code: "BOOLEAN_FAILED",
          message: `${nz.tag}: kapak delikleri açılamadı (${err instanceof Error ? err.message : String(err)})`,
        });
      } finally {
        tool.delete();
      }
    }
    parts.push(cover);

    // Saplama + iki somun / delik
    const nutH = 0.8 * flg.bd;
    const nutR = 0.87 * flg.bd;
    const zs0 = zDisc0 - nutH;
    const zs1 = zc1 + nutH;
    const a0 = Math.PI / flg.n;
    for (let i = 0; i < flg.n; i++) {
      const a = a0 + (2 * Math.PI * i) / flg.n;
      const x = (flg.bc / 2) * Math.cos(a);
      const y = (flg.bc / 2) * Math.sin(a);
      parts.push(
        makeCylinder(flg.bd / 2, zs1 + nutH - zs0, [x, y, zs0]),
        hexNut(nutR, zs0, nutH, x, y),
        hexNut(nutR, zc1, nutH, x, y),
      );
    }

    // Davit: kapak merkezinde dikme, üstte yatay kol, flanş dışında direk
    const armT = Math.max(0.5 * flg.bd, 6);
    const armW = Math.max(1.5 * flg.bd, 20);
    const zArm0 = zc1 + 2.2 * nutH;
    const pr = Math.max(0.7 * flg.bd, 10);
    const px = Rd + pr + 5;
    parts.push(
      makeCylinder(0.6 * flg.bd, zArm0 - zc1, [0, 0, zc1]),
      makeBox([0, -armW / 2, zArm0], [px, armW / 2, zArm0 + armT]),
      makeCylinder(pr, zArm0 + armT - zDisc0, [px, 0, zDisc0]),
    );

    return finish(parts, nz, frame, ctx, true);
  },
  cutter: boreCutter,
};
