import { describe, expect, it } from "vitest";
import { buildStressField } from "../stress/analyticField";
import { defaultProject } from "../store";
import type { VesselProject } from "../types";
import { componentFrames } from "../vesselModel";
import { buildFeaModel } from "../fea/mesh";
import { sampleScl } from "../fea/sampleScl";
import { runFea } from "../fea/solver";
import { toStressField } from "../fea/toStressField";
import { FEA_DISCLAIMER, type FeaResult } from "../fea/types";

/** Gövde + iki bombe; korozyon 0, nozulsuz, desteksiz. */
function vessel(o: { Di: number; t: number; L: number; P: number; head?: "hemispherical" | "elliptical" | "torispherical" | "flat"; th?: number }): VesselProject {
  const p = defaultProject();
  p.design_conditions.design_pressure = o.P;
  p.shell_sections[0] = {
    ...p.shell_sections[0], inside_diameter: o.Di, nominal_thickness: o.t, tangent_length: o.L,
    internal_corrosion_allowance: 0, external_corrosion_allowance: 0,
  };
  p.heads = p.heads.map((h) => ({
    ...h, type: o.head ?? "hemispherical", inside_diameter: o.Di, nominal_thickness: o.th ?? o.t,
    internal_corrosion_allowance: 0, crown_depth: null, crown_radius: null, knuckle_radius: null, straight_flange_length: 0,
  }));
  p.nozzles = [];
  p.supports = [];
  return p;
}

const shellMid = (p: VesselProject) => {
  const f = componentFrames(p).find((x) => x.kind === "shell")!;
  return { z: (f.zStart + f.zEnd) / 2, ri: f.rInStart, t: f.thickness, f };
};
const rel = (a: number, b: number) => Math.abs(a - b) / Math.abs(b);
const scl = (res: FeaResult, a: [number, number], b: [number, number]) => sampleScl(res, a, b, 21);

describe("FEA — kalın silindir (Lamé)", () => {
  it("Ri=100, t=50, P=10: σθ iç/dış %1 içinde", () => {
    const p = vessel({ Di: 200, t: 50, L: 1500, P: 10 });
    const res = runFea(p);
    expect(res.converged).toBe(true);
    const { z } = shellMid(p);
    const s = scl(res, [100, z], [150, z]);
    const Ri = 100, Ro = 150, P = 10;
    const inner = (P * (Ro * Ro + Ri * Ri)) / (Ro * Ro - Ri * Ri);
    const outer = (2 * P * Ri * Ri) / (Ro * Ro - Ri * Ri);
    console.log("Lamé", s[0].st, inner, s[20].st, outer, "σr iç", s[0].sr, "σz", s[10].sz);
    expect(rel(s[0].st, inner)).toBeLessThan(0.01);
    expect(rel(s[20].st, outer)).toBeLessThan(0.01);
    expect(Math.abs(s[0].sr + P)).toBeLessThan(0.05 * P);
    expect(rel(s[10].sz, (P * Ri * Ri) / (Ro * Ro - Ri * Ri))).toBeLessThan(0.01);
  });
});

describe("FEA — ince cidar membran", () => {
  const p = vessel({ Di: 1000, t: 10, L: 4000, P: 1 });
  const res = runFea(p);
  it("uzak alan σθ=PR/t, σz=PR/2t (%2)", () => {
    expect(res.converged).toBe(true);
    const { z } = shellMid(p);
    const s = scl(res, [500, z], [510, z]);
    const avgT = s.reduce((a, x) => a + x.st, 0) / s.length;
    const avgZ = s.reduce((a, x) => a + x.sz, 0) / s.length;
    console.log("ince", avgT, avgZ, res.mesh.elems.length / 8, res.dof, res.ms);
    expect(rel(avgT, 50)).toBeLessThan(0.02);
    expect(rel(avgZ, 25)).toBeLessThan(0.02);
  });
  it("yarımküre membran PR/2t (%2)", () => {
    const hr = componentFrames(p).find((f) => f.id === "HEAD-R")!;
    // ekvatordan 60° (birleşimden uzak)
    const ang = (60 * Math.PI) / 180;
    const a: [number, number] = [500 * Math.cos(ang), hr.head!.equatorZ + 500 * Math.sin(ang)];
    const b: [number, number] = [510 * Math.cos(ang), hr.head!.equatorZ + 510 * Math.sin(ang)];
    const s = scl(res, a, b);
    const avgT = s.reduce((x, y) => x + y.st, 0) / s.length;
    console.log("küre", avgT);
    expect(rel(avgT, 25)).toBeLessThan(0.02);
  });
});

/** Birleşimin gövde tarafında (±2,5√Rt) iç/orta/dış yüzey taraması: en büyük vm. */
function zoneMax(field: { at: (p: [number, number, number]) => { vm: number } }, p: VesselProject) {
  const { f, ri, t } = shellMid(p);
  const zone = 2.5 * Math.sqrt(ri * t);
  let m = 0;
  for (let i = 0; i <= 200; i++) {
    const z = f.zEnd - zone + (zone * i) / 200;
    for (const r of [ri + 0.01, ri + t / 2, ri + t - 0.01]) m = Math.max(m, field.at([r, 0, z]).vm);
  }
  return m;
}

describe("FEA — süreksizlik ve ağ yakınsaması", () => {
  for (const head of ["hemispherical", "elliptical"] as const) {
    it(`silindir-${head} birleşimi: bölge max vm analitik ile %15 içinde`, () => {
      const p = vessel({ Di: 1000, t: 10, L: 3000, P: 1, head });
      const res = runFea(p);
      const fe = zoneMax(toStressField(res), p);
      const an = zoneMax(buildStressField(p), p);
      console.log(`birleşim ${head}: FEA ${fe.toFixed(2)} analitik ${an.toFixed(2)} fark ${(rel(fe, an) * 100).toFixed(1)}%`);
      expect(rel(fe, an)).toBeLessThan(0.15);
      // birleşim bölgesi işaretlenir
      const { f, ri, t } = shellMid(p);
      expect(toStressField(res).at([ri + t / 2, 0, f.zEnd - 1]).zone).toBe("discontinuity");
    });
  }

  for (const head of ["hemispherical", "elliptical", "torispherical"] as const) {
    it(`ağ yakınsaması (${head}): kaba/ince max vm farkı < %3`, () => {
      const p = vessel({ Di: 1000, t: 10, L: 3000, P: 1, head });
      const a = runFea(p, { refine: 1 });
      const b = runFea(p, { refine: 2 });
      expect(b.mesh.elems.length).toBeGreaterThan(3 * a.mesh.elems.length);
      const d = rel(a.maxVm, b.maxVm);
      const dz = rel(zoneMax(toStressField(a), p), zoneMax(toStressField(b), p));
      console.log(`yakınsama ${head}: ${a.maxVm.toFixed(2)} → ${b.maxVm.toFixed(2)} (${(d * 100).toFixed(2)}%), bölge ${(dz * 100).toFixed(2)}%; ` +
        `${a.mesh.elems.length / 8} el/${a.dof} sd ${a.ms?.toFixed(0)} ms → ${b.mesh.elems.length / 8} el/${b.dof} sd ${b.ms?.toFixed(0)} ms`);
      expect(d).toBeLessThan(0.03);
      expect(dz).toBeLessThan(0.03);
    });
  }

  it("düz kapak: çözülür; iç köşe tekil (ağa bağlı) — orta yüzey yakınsar", () => {
    const p = vessel({ Di: 1000, t: 10, L: 3000, P: 1, head: "flat", th: 60 });
    const a = runFea(p);
    const b = runFea(p, { refine: 2 });
    expect(a.converged && b.converged).toBe(true);
    // gövde uzak alanı etkilenmez
    const { z } = shellMid(p);
    expect(rel(toStressField(a).at([505, 0, z]).hoop, 50)).toBeLessThan(0.02);
  });

  it("torisferik: hamut tepe değeri sonlu, membran teorisinden (R1=rk) düşük", () => {
    const p = vessel({ Di: 1000, t: 10, L: 3000, P: 1, head: "torispherical" });
    const res = runFea(p);
    expect(res.converged).toBe(true);
    expect(res.maxVm).toBeGreaterThan(100);
    expect(res.maxVm).toBeLessThan(buildStressField(p).maxVm);
  });
});

describe("FEA — koni, nozul, korozyon, simetri", () => {
  it("koni membranı σθ ≈ P·r/(t·cosα) (%2), 30° koni birleşimi çözülür", () => {
    const p = vessel({ Di: 500, t: 5, L: 2000, P: 1, head: "hemispherical" });
    p.cones = [{
      cone_id: "CONE-01", large_diameter: 500, small_diameter: 300, half_apex_angle: 0, length: 2000,
      nominal_thickness: 5, material_id: "MAT-01", weld_joint_id: null, internal_corrosion_allowance: 0, mill_tolerance: 0,
    }];
    p.heads[1] = { ...p.heads[1], inside_diameter: 300 };
    p.component_sequence = [
      { component_type: "head", component_id: "HEAD-L" },
      { component_type: "shell", component_id: "SHELL-01" },
      { component_type: "cone", component_id: "CONE-01" },
      { component_type: "head", component_id: "HEAD-R" },
    ];
    const res = runFea(p);
    expect(res.converged).toBe(true);
    const cf = componentFrames(p).find((f) => f.kind === "cone")!;
    const alpha = Math.atan2(100, 2000);
    const zMid = (cf.zStart + cf.zEnd) / 2;
    const n: [number, number] = [Math.cos(alpha), Math.sin(alpha)];
    const s = scl(res, [200, zMid], [200 + 5 * n[0], zMid + 5 * n[1]]);
    const avg = s.reduce((a, x) => a + x.st, 0) / s.length;
    expect(rel(avg, 200 / (5 * Math.cos(alpha)))).toBeLessThan(0.02);

    p.cones[0] = { ...p.cones[0], half_apex_angle: 30, length: 173.2 };
    const r30 = runFea(p);
    expect(r30.converged).toBe(true);
    expect(r30.mesh.junctions!.some((j) => j.right === "CONE-01")).toBe(true);
    expect(r30.maxVm).toBeGreaterThan(50); // birleşim eğilmesi membranın üstünde
  });

  it("korozyon: σθ ortalaması P·(Ri+ca)/(t−ca)", () => {
    const p = vessel({ Di: 1000, t: 10, L: 3000, P: 1 });
    p.shell_sections[0].internal_corrosion_allowance = 2;
    const res = runFea(p);
    const { z } = shellMid(p);
    const s = scl(res, [502, z], [510, z]);
    const avg = s.reduce((a, x) => a + x.st, 0) / s.length;
    expect(rel(avg, 502 / 8)).toBeLessThan(0.01);
    expect(s[0].s).toBe(0);
    expect(s[s.length - 1].s).toBeCloseTo(8, 9);
  });

  it("kutup nozulu modellenir (boyun membranı P·rn/tn), eksen dışı nozul uyarıyla atlanır", () => {
    const p = vessel({ Di: 1000, t: 10, L: 3000, P: 1, head: "elliptical" });
    const base = defaultProject().nozzles[0];
    p.nozzles = [
      { ...base, tag: "N1", host_component_id: "HEAD-R", axial_position: 0, head_position_diameter: 0, circumferential_angle: 0,
        inclination_angle: 0, outside_diameter: 116, inside_diameter: 100, neck_thickness: 8, corrosion_allowance: 0,
        inside_projection: 0, outside_projection: 300, reinforcement_pad: false, reinforcement_pad_thickness: null, reinforcement_pad_od: null },
      { ...base, tag: "N2", host_component_id: "SHELL-01", axial_position: 1000, head_position_diameter: null, circumferential_angle: 90,
        inclination_angle: 0, outside_diameter: 116, inside_diameter: 100, neck_thickness: 8, corrosion_allowance: 0,
        inside_projection: 0, outside_projection: 200, reinforcement_pad: false, reinforcement_pad_thickness: null, reinforcement_pad_od: null },
    ];
    const res = runFea(p);
    if (!res.converged) console.log(res.warnings);
    expect(res.converged).toBe(true);
    expect(res.mesh.componentKind!["N1"]).toBe("nozzle");
    expect(res.mesh.junctions!.some((j) => j.left === "HEAD-R" && j.right === "N1")).toBe(true);
    expect(res.warnings.some((w) => w.includes("1 eksen dışı nozul"))).toBe(true);
    // Boyun ortası (birleşim ve kör flanş ucundan uzak)
    const lines = res.mesh.lines!.filter((l) => l.component === "N1");
    const mid = lines[Math.floor(lines.length / 2)];
    const s = sampleScl(res, mid.a, mid.b, 11);
    const avg = s.reduce((a, x) => a + x.st, 0) / s.length;
    expect(rel(avg, 50 / 8)).toBeLessThan(0.03);
    expect(res.maxVm).toBeGreaterThan(50); // delik/boyun köşesi
  });

  it("simetrik kap: sol/sağ kutup gerilmesi eşit", () => {
    const p = vessel({ Di: 1000, t: 10, L: 2000, P: 1 });
    const res = runFea(p);
    const fs = componentFrames(p);
    const l = fs[0], r = fs[fs.length - 1];
    const f = toStressField(res);
    const a = f.at([0, 0, l.zStart - 5]);
    const b = f.at([0, 0, r.zEnd + 5]);
    expect(a.zone).toBe("head");
    expect(rel(a.vm, b.vm)).toBeLessThan(1e-3);
    expect(rel(a.hoop, 25)).toBeLessThan(0.03);
  });

  it("profil süreksizse sahte sonuç yok: converged=false", () => {
    const p = vessel({ Di: 1000, t: 10, L: 2000, P: 1 });
    p.heads[1] = { ...p.heads[1], inside_diameter: 800 };
    const res = runFea(p);
    expect(res.converged).toBe(false);
    expect(res.maxVm).toBe(0);
    expect(res.warnings[0]).toMatch(/süreksiz/);
    expect(toStressField(res).at([505, 0, 100]).vm).toBe(0);
  });

  it("ağ: et boyunca ≥4 eleman, Q8", () => {
    const m = buildFeaModel(vessel({ Di: 1000, t: 10, L: 2000, P: 1 })).mesh;
    expect(m.nodesPerElem).toBe(8);
    expect(m.nThick).toBeGreaterThanOrEqual(4);
    expect(m.elemComponent.length).toBe(m.elems.length / 8);
  });
});

describe("varsayılan proje", () => {
  it("defaultProject (CA, nozul, destek) çözülür, uyarılar listelenir", () => {
    const p = defaultProject();
    const res = runFea(p);
    console.log(`defaultProject: ${res.mesh.elems.length / 8} el, ${res.dof} sd, ${res.ms?.toFixed(0)} ms, maxVm ${res.maxVm.toFixed(1)}`, res.warnings);
    expect(res.converged).toBe(true);
    expect(res.maxVm).toBeGreaterThan(0);
    expect(Number.isFinite(res.maxVm)).toBe(true);
  });
});

describe("sözleşme", () => {
  it("etiket, uyarılar, toStressField", () => {
    const p = vessel({ Di: 1000, t: 10, L: 2000, P: 1, head: "elliptical" });
    const res = runFea(p);
    expect(res.disclaimer).toBe(FEA_DISCLAIMER);
    expect(res.warnings.some((w) => w.includes("E=200 GPa"))).toBe(true);
    const { z } = shellMid(p);
    const f = toStressField(res, 138);
    const s = f.at([0, 505, z]);
    expect(s.zone).toBe("membrane");
    expect(rel(s.hoop, 50)).toBeLessThan(0.02);
    expect(rel(s.axial, 25)).toBeLessThan(0.02);
    expect(f.at([0, 900, z]).vm).toBe(0);
    expect(f.allowable).toBe(138);
  });
});
