// CAD geometri yardımcıları. Model çerçevesi D00 §1: kap ekseni +Z, z=0 sol bombe kutbu.
import { draw } from "replicad";
import type { Shape3D, Sketch } from "replicad";
import type { NozzlePlacement, Vec3 } from "../geometryContract";

export type Pt = [number, number]; // (r, z) — eksene uzaklık, eksen konumu

export const dot = (a: Vec3, b: Vec3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a: Vec3, b: Vec3): Vec3 => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0],
];
export const norm = (a: Vec3): Vec3 => {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
};

/**
 * Yerel +Z ekseninde, orijinde kurulmuş şekli `placement.axis` yönüne döndürür ve
 * `placement.position`'a taşır. replicad dönüşümleri girdiyi tüketir — dönen şekli kullan.
 */
export function orient<S extends Shape3D>(shape: S, placement: Pick<NozzlePlacement, "position" | "axis">): S {
  const z: Vec3 = [0, 0, 1];
  const a = norm(placement.axis);
  const c = Math.max(-1, Math.min(1, dot(z, a)));
  let out: Shape3D = shape;
  if (c < 1 - 1e-12) {
    const k = c > -1 + 1e-12 ? norm(cross(z, a)) : ([1, 0, 0] as Vec3);
    out = out.rotate((Math.acos(c) * 180) / Math.PI, [0, 0, 0], k);
  }
  const [px, py, pz] = placement.position;
  if (px || py || pz) out = out.translate(px, py, pz);
  return out as S;
}

/** Kapalı (r,z) profil komutu: çizgi ya da üç noktalı yay. */
export type ProfileSeg = { line: Pt } | { arc: Pt; via: Pt } | { ellipse: Pt; rx: number; rz: number; sweep: boolean };

/**
 * (r,z) düzleminde kapalı profili Z ekseni etrafında 360° döndürür (revolve).
 * 2B x → r (global X), 2B y → z (global Z): "XZ" düzlemi.
 */
export function revolveProfile(start: Pt, segs: ProfileSeg[]): Shape3D {
  let pen = draw(start);
  for (const s of segs) {
    if ("line" in s) pen = pen.lineTo(s.line);
    else if ("arc" in s) pen = pen.threePointsArcTo(s.arc, s.via);
    else pen = pen.ellipseTo(s.ellipse, s.rx, s.rz, 0, false, s.sweep);
  }
  const sketch = pen.close().sketchOnPlane("XZ") as Sketch;
  return sketch.revolve([0, 0, 1], { origin: [0, 0, 0] });
}

/** Merkez c, yarıçap R çember üzerinde a→b yayının orta noktası (kısa yay). */
export function arcMid(c: Pt, R: number, a: Pt, b: Pt): Pt {
  const ta = Math.atan2(a[1] - c[1], a[0] - c[0]);
  let tb = Math.atan2(b[1] - c[1], b[0] - c[0]);
  while (tb - ta > Math.PI) tb -= 2 * Math.PI;
  while (tb - ta < -Math.PI) tb += 2 * Math.PI;
  const tm = (ta + tb) / 2;
  return [c[0] + R * Math.cos(tm), c[1] + R * Math.sin(tm)];
}
