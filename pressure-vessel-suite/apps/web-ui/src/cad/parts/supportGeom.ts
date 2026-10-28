// D08 — destek parçaları ortak yardımcıları (saddle / skirt / legs). Model çerçevesi: eksen +Z.
import { draw, makeBox, makeCylinder } from "replicad";
import type { Shape3D, Sketch } from "replicad";
import type { ComponentFrame } from "../../geometryContract";
import type { Pt } from "../geom";

export const DEG = Math.PI / 180;

/** Eksen hizalı kutu (mm). */
export function box(x0: number, x1: number, y0: number, y1: number, z0: number, z1: number): Shape3D {
  return makeBox(
    [Math.min(x0, x1), Math.min(y0, y1), Math.min(z0, z1)],
    [Math.max(x0, x1), Math.max(y0, y1), Math.max(z0, z1)],
  );
}

/** Z ekseni (ya da (cx,cy) merkezli paralel eksen) etrafında dolu silindir z0→z1. */
export function cyl(r: number, z0: number, z1: number, cx = 0, cy = 0): Shape3D {
  return makeCylinder(r, z1 - z0, [cx, cy, Math.min(z0, z1)], [0, 0, 1]);
}

/** Kapalı XY çokgenini z0'dan z1'e ekstrüde eder. */
export function prism(pts: Pt[], z0: number, z1: number): Shape3D {
  let pen = draw(pts[0]);
  for (let i = 1; i < pts.length; i++) pen = pen.lineTo(pts[i]);
  return (pen.close().sketchOnPlane("XY", z0) as Sketch).extrude(z1 - z0);
}

/** Frame içinde z'deki dış yarıçap (shell/cone doğrusal; bombe için en büyük). */
export function frameOuterRadius(f: ComponentFrame, z: number): number {
  if (f.kind === "head") return Math.max(f.rOutStart, f.rOutEnd);
  const L = f.zEnd - f.zStart;
  const s = L > 1e-9 ? Math.min(1, Math.max(0, (z - f.zStart) / L)) : 0;
  return f.rOutStart + (f.rOutEnd - f.rOutStart) * s;
}

/** z konumundaki gövde dış yarıçapı (bombe olmayan frame öncelikli; yoksa en büyük). */
export function outerRadiusAt(frames: ComponentFrame[], z: number, host: ComponentFrame | null): number {
  if (host && host.kind !== "head") return frameOuterRadius(host, z);
  const hit = frames.find((f) => f.kind !== "head" && z >= f.zStart - 1e-6 && z <= f.zEnd + 1e-6);
  if (hit) return frameOuterRadius(hit, z);
  const any = frames.find((f) => z >= f.zStart && z <= f.zEnd);
  if (any) return frameOuterRadius(any, z);
  return frames.reduce((m, f) => Math.max(m, f.rOutStart, f.rOutEnd), 0) || 500;
}

/** Sol bombe dış kutbunun z'si (dikey kapta kap altı). Sol bombe yoksa zincir başı. */
export function vesselBottomZ(frames: ComponentFrame[]): number {
  const f = frames[0];
  return f?.head?.side === "left" ? f.zStart - f.thickness : (f?.zStart ?? 0);
}

/** Birden çok katıyı birleştirir (en az bir eleman). */
export function fuseAll(parts: Shape3D[]): Shape3D {
  return parts.slice(1).reduce((acc, p) => acc.fuse(p), parts[0]);
}

/** Z yönlü dairesel delik kesicileri (plaka z0→z1). */
export function zHoles(pts: Pt[], d: number, z0: number, z1: number): Shape3D[] {
  return pts.map(([x, y]) => cyl(d / 2, z0 - 1, z1 + 1, x, y));
}

export { makeCylinder };
