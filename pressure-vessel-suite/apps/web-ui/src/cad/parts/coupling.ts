// D07 — dövme manşon (coupling / socket_welded). BORU YOK: yalnız gövde (revolve).
// Yerel +Z: z=0 host iç yüzeyi, dış yüzey z=et; gövde üst yüzü z=et+length (apeks).
// Dış üst/alt kenarda 45° pah, üstte soket kademesi (SW: socket_bore/depth; diş: bore ≈ diş çapı).
// preview: taban sacın içine 1·t uzar, boolean yok. exact: kaynak köşesi (üçgen dolgu profili) + host
// dış yüzeyiyle saddle-cut (host katısını çıkar); başarısızsa atlanır + BOOLEAN_FAILED.
import type { Shape3D } from "replicad";
import type { ComponentFrame, CouplingForm, CouplingRating, PartCtx, PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";
import { revolveProfile, type Pt } from "../geom";
import { boreCutter, parseNps, partIdOf, place } from "./flangedNozzle";
import { buildChainSolid } from "./shellChain";

function polygonSolid(pts: Pt[]): Shape3D {
  const clean = pts.filter((p, i) => {
    const q = pts[(i + pts.length - 1) % pts.length];
    return Math.abs(p[0] - q[0]) > 1e-6 || Math.abs(p[1] - q[1]) > 1e-6;
  });
  return revolveProfile(clean[0], clean.slice(1).map((line) => ({ line })));
}

const sagitta = (R: number, r: number) => (R > r ? R - Math.sqrt(R * R - r * r) : R);

export const coupling: PartModule<Nozzle> = {
  build(nz, frame, ctx) {
    const warn = ctx.warn;
    const pid = partIdOf(nz);
    const end = nz.nozzle_type === "socket_welded" ? "socket" : "threaded";
    const rating: CouplingRating = nz.rating_class === "6000#" ? "6000#" : "3000#";
    const form: CouplingForm = nz.coupling_form ?? "full";
    const nps = parseNps(nz.size_designation);
    const row = nps ? ctx.catalogs.coupling(nps, rating, form, end) : undefined;
    if (!row) {
      warn?.({
        partId: pid,
        code: "CATALOG_MISS",
        message: `${nz.tag}: manşon ${nps ?? "?"} ${rating} ${form} ${end} katalogda yok; soket/pah ölçüleri oranla`,
      });
    }

    const R = Math.max(nz.outside_diameter / 2, 1);
    let ri = nz.inside_diameter / 2;
    if (!(ri > 0 && ri < R)) ri = R * 0.6;
    const length = Math.max(nz.outside_projection, 1);
    const wall = frame?.thickness ?? 0;
    const chamfer = row?.chamfer ?? (wall > 0 ? 0.1 * wall : Math.min(2, 0.05 * R));
    const cc = Math.min(chamfer, 0.3 * (R - ri), 0.3 * length);

    // Taban: preview'da 1·t içeri (z=0'a kadar); exact'te saddle sagitasını kapsayacak kadar.
    let zb = 0;
    if (frame) {
      const Rh = Math.max(frame.rOutStart, frame.rOutEnd);
      zb = ctx.level === "exact"
        ? Math.max(0, wall - Math.min(sagitta(Rh, R), wall) - 1)
        : 0; // preview: wall − 1·t = 0 (taban sacın içine 1·t uzar)
    }
    const zt = wall + length;

    const Rt = row?.top_od ? Math.min(row.top_od / 2, R) : R;
    const sockR = row?.socket_bore ? row.socket_bore / 2 : 0;
    const sockD = row?.socket_depth ?? 0;

    const pts: Pt[] = [[ri, zb], [R - cc, zb], [R, zb + cc]];
    if (Rt < R - 1e-6) {
      const zTaper = Math.max(zb + cc + 1, zt - cc - (R - Rt));
      pts.push([R, zTaper], [Rt, zt - cc]);
    } else {
      pts.push([R, zt - cc]);
    }
    pts.push([Rt - cc, zt]);
    if (sockR > ri + 1e-6 && sockR < Rt - cc - 0.5 && sockD > 0) {
      const zs = Math.max(zt - Math.min(sockD, length * 0.8), zb + 1);
      pts.push([sockR, zt], [sockR, zs], [ri, zs]);
    } else {
      pts.push([ri, zt]);
    }
    let body = polygonSolid(pts);

    if (ctx.level !== "exact" || !frame || !ctx.placement) return place(body, ctx);

    // Kaynak köşesi: kaynak ayağı w'lu üçgen halka (host dışında kalan kısmı görünür).
    const w = Math.min(8, Math.max(3, 0.7 * wall));
    try {
      const Rh = Math.max(frame.rOutStart, frame.rOutEnd);
      const zLow = wall - Math.min(sagitta(Rh, R + w), wall) - 1;
      const bead = polygonSolid([[R - 0.5, wall + w], [R + w, Math.max(zLow, 0)], [R - 0.5, Math.max(zLow, 0)]]);
      const fused = body.fuse(bead);
      body.delete();
      bead.delete();
      body = fused;
    } catch (err) {
      warn?.({
        partId: pid,
        code: "BOOLEAN_FAILED",
        message: `${nz.tag}: kaynak köşesi atlandı (${err instanceof Error ? err.message : String(err)})`,
      });
    }

    const placed = place(body, ctx);
    const host = buildChainSolid(frame, undefined);
    if (!host) return placed;
    try {
      const cut = placed.cut(host);
      placed.delete();
      return cut;
    } catch (err) {
      warn?.({
        partId: pid,
        code: "BOOLEAN_FAILED",
        message: `${nz.tag}: saddle-cut uygulanamadı (${err instanceof Error ? err.message : String(err)})`,
      });
      return placed;
    } finally {
      host.delete();
    }
  },
  cutter(nz: Nozzle, frame: ComponentFrame, ctx: PartCtx) {
    return boreCutter(nz, frame, ctx);
  },
};
