// D06 — gövde zinciri katıları: her shell / cone / head frame'i için ayrı katı.
// Hepsi (r,z) halka profilinin Z ekseni etrafında döndürülmesiyle kurulur; global çerçevede döner.
// İç profil frame'den (iç ölçü), dış yüzey normal ofset:
//   shell: dikdörtgen; koni: iç doğru + t/cosα; yarım küre ve torisferik: eş merkezli yaylar (tam ofset);
//   2:1 eliptik: (a+t, b+t) yarı eksenli elips (kutup ve ekvatorda tam, arada ölçekli yaklaşım).
// Düz kapak: t kalınlıklı plaka + sf düz flanş halkası.
import type { Shape3D } from "replicad";
import type { ComponentFrame } from "../../geometryContract";
import type { Cone, Head, ShellSection } from "../../types";
import { arcMid, revolveProfile, type ProfileSeg, type Pt } from "../geom";

export type ChainComponent = ShellSection | Cone | Head;

const EPS = 1e-6;

/** Ardışık eş noktaları ayıklayıp kapalı çizgi profili döndürür. */
function polygon(pts: Pt[]): Shape3D {
  const clean = pts.filter((p, i) => {
    const q = pts[(i + pts.length - 1) % pts.length];
    return Math.abs(p[0] - q[0]) > EPS || Math.abs(p[1] - q[1]) > EPS;
  });
  return revolveProfile(clean[0], clean.slice(1).map((line) => ({ line })));
}

function shellSolid(f: ComponentFrame): Shape3D {
  const { zStart: z0, zEnd: z1, rInStart: ri, thickness: t } = f;
  return polygon([[ri, z0], [ri, z1], [ri + t, z1], [ri + t, z0]]);
}

function coneSolid(f: ComponentFrame): Shape3D {
  const { zStart: z0, zEnd: z1, rInStart: a, rInEnd: b, thickness: t } = f;
  const L = Math.max(z1 - z0, EPS);
  const dr = t / Math.cos(Math.atan(Math.abs(b - a) / L)); // normal kalınlık → radyal ofset
  return polygon([[a, z0], [b, z1], [b + dr, z1], [a + dr, z0]]);
}

/**
 * Bombe profili yerel (r,u) koordinatında: u=0 ekvator, u>0 kubbe (kutba doğru), u<0 düz flanş.
 * Global z: sağ bombe z = E + u, sol bombe z = E − u.
 */
function headSolid(f: ComponentFrame, head: Head | undefined): Shape3D {
  const hd = f.head!;
  const t = f.thickness;
  const Ri = Math.max(f.rInStart, f.rInEnd);
  const h = hd.domeHeight;
  const sf = hd.sf;
  const E = hd.equatorZ;
  const dir = hd.side === "left" ? -1 : 1;
  const P = (p: Pt): Pt => [p[0], E + dir * p[1]];

  if (h <= EPS || hd.type === "flat") {
    // Düz kapak: plaka u∈[0,t], dış çap Ri+t (gövde dış çapıyla aynı) + flanş halkası u∈[−sf,0].
    return polygon([[Ri, -sf], [Ri, 0], [0, 0], [0, t], [Ri + t, t], [Ri + t, -sf]].map((p) => P(p as Pt)));
  }

  // Kubbe: iç eğri (Ri,0)→(0,h), dış eğri (0,h+t)→(Ri+t,0).
  let inner: ProfileSeg[];
  let outer: ProfileSeg[];
  const tori = hd.type === "torispherical" ? torisphericalArcs(Ri, h, t, head) : null;

  if (hd.type === "hemispherical" && Math.abs(h - Ri) < 1e-6 * Ri) {
    const c: Pt = [0, 0];
    inner = [{ arc: P([0, h]), via: P(arcMid(c, Ri, [Ri, 0], [0, h])) }];
    outer = [{ arc: P([Ri + t, 0]), via: P(arcMid(c, Ri + t, [0, h + t], [Ri + t, 0])) }];
  } else if (tori) {
    inner = tori.inner.map((s) => ({ arc: P(s.arc), via: P(s.via) }));
    outer = tori.outer.map((s) => ({ arc: P(s.arc), via: P(s.via) }));
  } else {
    // Elips (2:1 veya oranı farklı yarım küre/torisferik yedeği). Ayna (sol) yön değiştirir.
    const sweepIn = dir === 1;
    inner = [{ ellipse: P([0, h]), rx: Ri, rz: h, sweep: sweepIn }];
    outer = [{ ellipse: P([Ri + t, 0]), rx: Ri + t, rz: h + t, sweep: !sweepIn }];
  }

  const segs: ProfileSeg[] = [];
  const start = P([Ri, -sf]);
  if (sf > EPS) segs.push({ line: P([Ri, 0]) });
  segs.push(...inner);
  segs.push({ line: P([0, h + t]) });
  segs.push(...outer);
  if (sf > EPS) segs.push({ line: P([Ri + t, -sf]) });
  return revolveProfile(start, segs);
}

/**
 * Torisferik: knuckle r = knuckle_radius ?? 0.06·Di; crown R, frame'in domeHeight'ından çözülür
 * (h = R − √((R−r)² − (a−r)²) ⇒ R = (h² − r² + (a−r)²) / (2(h−r))) — böylece kubbe yüksekliği
 * tek kaynaktan gelir. Geçersizse null (elips yedeği).
 */
function torisphericalArcs(a: number, h: number, t: number, head: Head | undefined) {
  const r = head?.knuckle_radius && head.knuckle_radius > 0 ? head.knuckle_radius : 0.06 * 2 * a;
  if (!(h > r && r < a)) return null;
  const R = (h * h - r * r + (a - r) ** 2) / (2 * (h - r));
  if (!(R >= a) || !Number.isFinite(R)) return null;
  const kc: Pt = [a - r, 0]; // knuckle merkezi
  const cc: Pt = [0, h - R]; // crown merkezi
  const dx = kc[0] - cc[0];
  const dz = kc[1] - cc[1];
  const dl = Math.hypot(dx, dz);
  const ux = dx / dl;
  const uz = dz / dl;
  const T = (rad: number): Pt => [kc[0] + rad * ux, kc[1] + rad * uz]; // teğet noktası
  const Ti = T(r);
  const To = T(r + t);
  return {
    inner: [
      { arc: Ti, via: arcMid(kc, r, [a, 0], Ti) },
      { arc: [0, h] as Pt, via: arcMid(cc, R, Ti, [0, h]) },
    ],
    outer: [
      { arc: To, via: arcMid(cc, R + t, [0, h + t], To) },
      { arc: [a + t, 0] as Pt, via: arcMid(kc, r + t, To, [a + t, 0]) },
    ],
  };
}

/** Tek frame'in katısı. İç (internal) bombe çizilmez → null. */
export function buildChainSolid(f: ComponentFrame, comp: ChainComponent | undefined): Shape3D | null {
  if (f.kind === "shell") return shellSolid(f);
  if (f.kind === "cone") return coneSolid(f);
  if (f.head?.side === "internal") return null;
  return headSolid(f, comp as Head | undefined);
}
