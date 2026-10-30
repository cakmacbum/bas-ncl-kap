// FeaResult → StressField adaptörü (P12). 3D nokta (x,y,z) → r=√(x²+y²), z; ısı haritası FEA
// sonucunu da boyayabilir. hoop=σθ, axial=meridyen gerilmesi (yol teğeti yönünde), vm tam 3B von Mises.
// Ağ dışındaki noktalar (eksen dışı nozul, destek) sıfır / "unknown" döner — uydurma değer yok.
// GÖSTERGE AMAÇLI — ASME onayı / mühendis değerlendirmesi değildir.

import type { StressField, StressSample, StressZone } from "../stress/types";
import { locate, pathTangent, stressAt } from "./sampleScl";
import { vonMises } from "./solver";
import type { FeaResult } from "./types";

export function toStressField(res: FeaResult, allowable: number | null = null): StressField {
  const mesh = res.mesh;
  const lines = mesh.lines ?? [];
  const junctions = mesh.junctions ?? [];
  const kinds = mesh.componentKind ?? {};
  const thick = (c: number) => {
    const l = lines[c];
    return l ? Math.hypot(l.b[0] - l.a[0], l.b[1] - l.a[1]) : 10;
  };
  // Yüzey toleransı: CAD dış yüzeyi FEA ofset yüzeyinden birkaç mm ayrışabilir.
  let tMax = 0;
  for (let c = 0; c < lines.length; c++) tMax = Math.max(tMax, thick(c));
  const searchTol = Math.max(5, tMax);

  function at(p: [number, number, number]): StressSample {
    const zero = (zone: StressZone): StressSample => ({ vm: 0, hoop: 0, axial: 0, zone });
    if (!res.converged || mesh.elems.length === 0) return zero("unknown");
    const r = Math.hypot(p[0], p[1]);
    const loc = locate(mesh, r, p[2], searchTol);
    if (!loc) return zero("unknown");
    const col = mesh.elemColumn?.[loc.elem] ?? 0;
    if (loc.dist > Math.max(3, 0.6 * thick(col))) return zero("unknown");
    const [sr, st, sz, trz] = stressAt(res, loc);
    const [tr, tz] = pathTangent(mesh, loc);
    const meridional = tr * tr * sr + tz * tz * sz + 2 * tr * tz * trz;
    const comp = mesh.elemComponent[loc.elem];
    let zone: StressZone = kinds[comp] === "head" ? "head" : kinds[comp] === "nozzle" ? "nozzle" : "membrane";
    if (lines[col] && lines[col + 1]) {
      const s = lines[col].s + ((loc.eta + 1) / 2) * (lines[col + 1].s - lines[col].s);
      if (junctions.some((j) => Math.abs(s - j.s) <= j.zone)) zone = kinds[comp] === "nozzle" ? "nozzle" : "discontinuity";
    }
    return { vm: vonMises(sr, st, sz, trz), hoop: st, axial: meridional, zone };
  }

  return { at, allowable, maxVm: res.maxVm };
}
