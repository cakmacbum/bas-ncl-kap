// Analitik mod uyarısı: torisferik bombe hamutu (knuckle). V1 doğrulaması (docs/validation/torispherical-knuckle.md):
// D1000/t10/P1, Rc=D, rk/D=0,06/0,10/0,17 → bağımsız ince kabuk çözümü 227/174/112 MPa, P12 FEA 237/178/114 (≤%4),
// eski P03 membran (R1=rk) 715/407/216. P03 artık hamutta ve taç–hamut birleşim bandında değer üretmez (NaN, gri).
// Bu dosya yalnız bölgeyi tespit eder (geometri analyticField.ts taç/hamut ayrımıyla aynı).
import type { ComponentFrame } from "../geometryContract";
import type { VesselProject } from "../types";
import { componentFrames } from "../vesselModel";

export const KNUCKLE_WARNING = "Analitik yöntem hamutta güvenilir değer vermez (membran teorisi doğrulamada 2–3 kat yüksek; eğilme modellenmez) — FEA modunu kullanın.";

interface TorHead { zEq: number; side: "left" | "right"; L: number; hc: number; b0: number; sinB: number; id: string }

function torHeads(project: VesselProject, frames: ComponentFrame[]): TorHead[] {
  const out: TorHead[] = [];
  for (const f of frames) {
    const hd = f.head;
    if (f.kind !== "head" || !hd || hd.side === "internal" || hd.type !== "torispherical" || hd.domeHeight <= 0) continue;
    const h = project.heads.find((x) => x.head_id === f.id);
    if (!h) continue;
    const ca = Math.max(h.internal_corrosion_allowance ?? 0, 0);
    const a0 = hd.side === "left" ? f.rInEnd : f.rInStart;
    const a = a0 + ca;
    const di = 2 * a0;
    const L = (h.crown_radius ?? di) + ca, rk = (h.knuckle_radius ?? 0.06 * di) + ca;
    const q = (L - rk) ** 2 - (a - rk) ** 2;
    if (!(L > rk && a > rk && q > 0)) continue;
    out.push({ zEq: hd.equatorZ, side: hd.side, L, hc: L - Math.sqrt(q), b0: hd.domeHeight, sinB: (a - rk) / (L - rk), id: f.id });
  }
  return out;
}

/** Model çerçevesindeki nokta bir torisferik bombenin hamut bölgesinde mi? */
export function makeKnuckleCheck(project: VesselProject): (p: [number, number, number]) => boolean {
  const heads = torHeads(project, componentFrames(project));
  if (heads.length === 0) return () => false;
  return (p) => {
    const r = Math.hypot(p[0], p[1]);
    for (const h of heads) {
      const zl = h.side === "left" ? h.zEq - p[2] : p[2] - h.zEq;
      if (zl <= 0 || zl > h.b0 * 1.2 + 20) continue;
      const zc = h.hc - h.L;
      const vr = Math.hypot(r, (zl / h.b0) * h.hc - zc);
      if (vr > 0 && r / vr > h.sinB) return true;
    }
    return false;
  };
}

/** Seçili bileşen torisferik bombe mi? */
export function isTorisphericalHead(project: VesselProject, sel: { kind: string; id: string } | null | undefined): boolean {
  if (!sel || sel.kind !== "head") return false;
  return torHeads(project, componentFrames(project)).some((h) => h.id === sel.id);
}
