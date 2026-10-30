import { describe, expect, it } from "vitest";
import { defaultProject } from "../store";
import type { VesselProject } from "../types";
import { buildFeaModel } from "../fea/mesh";
import { runFea } from "../fea/solver";
import { sampleScl } from "../fea/sampleScl";
import { componentFrames } from "../vesselModel";

function vessel(): VesselProject {
  const p = defaultProject();
  p.design_conditions.design_pressure = 1;
  p.shell_sections[0] = {
    ...p.shell_sections[0], inside_diameter: 1000, nominal_thickness: 10, tangent_length: 4000,
    internal_corrosion_allowance: 0, external_corrosion_allowance: 0,
  };
  p.heads = p.heads.map((h) => ({
    ...h, type: "elliptical", inside_diameter: 1000, nominal_thickness: 10,
    internal_corrosion_allowance: 0, crown_depth: null, crown_radius: null, knuckle_radius: null, straight_flange_length: 0,
  }));
  p.nozzles = [];
  p.supports = [];
  return p;
}
const withMat = (p: VesselProject, patch: Record<string, unknown>) => {
  p.materials = p.materials.map((m, i) => (i === 0 ? { ...m, ...patch } : m));
  return p;
};
const maxU = (u: Float64Array) => u.reduce((a, b) => Math.max(a, Math.abs(b)), 0);
const hoopMid = (p: VesselProject, res: ReturnType<typeof runFea>) => {
  const f = componentFrames(p).find((x) => x.kind === "shell")!;
  const z = (f.zStart + f.zEnd) / 2;
  return sampleScl(res, [500, z], [510, z], 11)[5].st;
};

describe("FEA malzeme E/ν", () => {
  it("E iki katına → yer değiştirme yarıya, statik belirli gerilme değişmez", () => {
    const a = runFea(withMat(vessel(), { elastic_modulus: 200000, poisson_ratio: 0.3 }));
    const b = runFea(withMat(vessel(), { elastic_modulus: 400000, poisson_ratio: 0.3 }));
    expect(maxU(b.u) / maxU(a.u)).toBeCloseTo(0.5, 6);
    const pa = withMat(vessel(), { elastic_modulus: 200000, poisson_ratio: 0.3 });
    expect(hoopMid(pa, b)).toBeCloseTo(hoopMid(pa, a), 1);
    expect(b.E).toBe(400000);
    expect(a.warnings.some((w) => w.includes("E=200 GPa"))).toBe(false);
  });

  it("E/ν boşsa varsayım + uyarı; ν geçersizse de uyarı", () => {
    const r = runFea(withMat(vessel(), { elastic_modulus: null, poisson_ratio: null }));
    expect(r.warnings.some((w) => w.includes("E=200 GPa"))).toBe(true);
    const r2 = runFea(withMat(vessel(), { elastic_modulus: 200000, poisson_ratio: 0.6 }));
    expect(r2.warnings.some((w) => w.includes("E=200 GPa"))).toBe(true);
  });

  it("bileşen bazlı malzeme: uyarı yalnız varsayım kullanan bileşenler için", () => {
    const p = vessel();
    p.materials = [
      { ...p.materials[0], material_id: "MAT-01", elastic_modulus: 200000, poisson_ratio: 0.3 },
      { ...p.materials[0], material_id: "MAT-02", elastic_modulus: null, poisson_ratio: null },
    ];
    p.shell_sections[0].material_id = "MAT-01";
    p.heads = p.heads.map((h) => ({ ...h, material_id: "MAT-02" }));
    const m = buildFeaModel(p);
    const headId = p.heads[0].head_id;
    const w = m.warnings.find((x) => x.includes("E=200 GPa"))!;
    expect(w).toContain(headId);
    expect(w).not.toContain(p.shell_sections[0].section_id);

    p.materials[1] = { ...p.materials[1], elastic_modulus: 100000, poisson_ratio: 0.25 };
    const m2 = buildFeaModel(p);
    expect(m2.warnings.some((x) => x.includes("E=200 GPa"))).toBe(false);
    expect(m2.materials[headId]).toEqual({ E: 100000, nu: 0.25 });
    expect(m2.materials[p.shell_sections[0].section_id]).toEqual({ E: 200000, nu: 0.3 });
    expect(runFea(p).converged).toBe(true);
  });
});
