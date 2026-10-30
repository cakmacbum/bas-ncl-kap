import { describe, expect, it } from "vitest";
import { buildStressField } from "../stress/analyticField";
import { defaultProject } from "../store";
import type { Cone, Nozzle, VesselProject } from "../types";
import { componentFrames, nozzlePlacement } from "../vesselModel";

/** D500 / t5 / P=1 MPa, korozyon 0, 2:1 elipsoidal bombeler, nozulsuz. */
function base(type: "elliptical" | "hemispherical" | "flat" = "elliptical"): VesselProject {
  const p = defaultProject();
  p.design_conditions.design_pressure = 1;
  p.shell_sections[0] = {
    ...p.shell_sections[0], inside_diameter: 500, nominal_thickness: 5, tangent_length: 2000,
    internal_corrosion_allowance: 0, external_corrosion_allowance: 0,
  };
  p.heads = p.heads.map((h) => ({
    ...h, type, inside_diameter: 500, nominal_thickness: 5, internal_corrosion_allowance: 0,
    crown_depth: null, crown_radius: null, knuckle_radius: null, straight_flange_length: 0,
  }));
  p.nozzles = [];
  return p;
}

function nozzle(over: Partial<Nozzle> = {}): Nozzle {
  return {
    ...defaultProject().nozzles[0], host_component_id: "SHELL-01", axial_position: 1000, circumferential_angle: 90,
    outside_diameter: 100, inside_diameter: 90, neck_thickness: 5, corrosion_allowance: 0,
    reinforcement_pad: false, reinforcement_pad_thickness: null, reinforcement_pad_od: null, ...over,
  };
}

const shellFrame = (p: VesselProject) => componentFrames(p).find((f) => f.kind === "shell")!;
const beta = (R: number, t: number) => 1.285 / Math.sqrt(R * t);

describe("buildStressField — membran", () => {
  it("D500/t5/P=1: gövde orta noktası hoop 50±0,5, axial 25±0,5", () => {
    const p = base();
    const f = shellFrame(p);
    const s = buildStressField(p).at([0, -252.5, (f.zStart + f.zEnd) / 2]);
    expect(s.hoop).toBeCloseTo(50, 0);
    expect(Math.abs(s.hoop - 50)).toBeLessThanOrEqual(0.5);
    expect(Math.abs(s.axial - 25)).toBeLessThanOrEqual(0.5);
    expect(s.zone).toBe("membrane");
    expect(s.vm).toBeCloseTo(Math.sqrt(50 * 50 - 50 * 25 + 25 * 25), 6);
  });

  it("korozyon payı iç çapı büyütür, kalınlığı azaltır", () => {
    const p = base();
    p.shell_sections[0].internal_corrosion_allowance = 1;
    const f = shellFrame(p);
    const s = buildStressField(p).at([252.5, 0, (f.zStart + f.zEnd) / 2]);
    expect(s.hoop).toBeCloseTo((1 * 251) / 4, 6);
  });

  it("t/R>0,1 → Lamé iç yüzey", () => {
    const p = base();
    p.shell_sections[0].nominal_thickness = 50;
    const f = shellFrame(p);
    const s = buildStressField(p).at([275, 0, (f.zStart + f.zEnd) / 2]);
    const Ri = 250, Ro = 300;
    expect(s.hoop).toBeCloseTo((Ro * Ro + Ri * Ri) / (Ro * Ro - Ri * Ri), 6);
    expect(s.axial).toBeCloseTo((Ri * Ri) / (Ro * Ro - Ri * Ri), 6);
  });

  it("bombe kutbu: yarımküre PR/2t, 2:1 elipsoid P·a/t", () => {
    for (const [type, expected] of [["hemispherical", 25], ["elliptical", 50]] as const) {
      const p = base(type);
      const hr = componentFrames(p).find((f) => f.id === "HEAD-R")!;
      const s = buildStressField(p).at([0, 0, hr.zEnd + 2.5]);
      expect(s.zone).toBe("head");
      expect(s.hoop).toBeCloseTo(expected, 3);
      expect(s.axial).toBeCloseTo(expected, 3);
    }
  });

  it("torisferik: taçta P·L/2t, hamutta basma çevresel; NaN yok", () => {
    const p = base();
    p.heads = p.heads.map((h) => ({ ...h, type: "torispherical" as const, crown_radius: 500, knuckle_radius: 50 }));
    const field = buildStressField(p);
    const hr = componentFrames(p).find((f) => f.id === "HEAD-R")!;
    const crown = field.at([0, 0, hr.zEnd + 2.5]);
    expect(crown.hoop).toBeCloseTo(50, 1);
    const knuckle = field.at([252.5, 0, hr.head!.equatorZ + 1]);
    expect(knuckle.hoop).toBeLessThan(0);
    for (let i = 0; i <= 40; i++) {
      const u = (i / 40) * (Math.PI / 2);
      const s = field.at([252.5 * Math.cos(u), 0, hr.head!.equatorZ + (hr.head!.domeHeight + 2.5) * Math.sin(u)]);
      expect(Number.isFinite(s.vm)).toBe(true);
      expect(s.vm).toBeLessThanOrEqual(field.maxVm + 1e-9);
    }
  });

  it("koni membranı σθ = P·r/(t·cosα)", () => {
    const p = base();
    const c: Cone = {
      cone_id: "CONE-01", large_diameter: 500, small_diameter: 300, half_apex_angle: 0, length: 2000,
      nominal_thickness: 5, material_id: "MAT-01", weld_joint_id: null, internal_corrosion_allowance: 0, mill_tolerance: 0,
    };
    p.cones = [c];
    p.heads[1] = { ...p.heads[1], inside_diameter: 300 };
    p.component_sequence = [
      { component_type: "head", component_id: "HEAD-L" },
      { component_type: "shell", component_id: "SHELL-01" },
      { component_type: "cone", component_id: "CONE-01" },
      { component_type: "head", component_id: "HEAD-R" },
    ];
    const cf = componentFrames(p).find((f) => f.kind === "cone")!;
    const alpha = Math.atan2(100, 2000);
    const zMid = (cf.zStart + cf.zEnd) / 2;
    const s = buildStressField(p).at([200 + 2.5, 0, zMid]);
    expect(s.zone).toBe("membrane");
    expect(s.hoop).toBeCloseTo(200 / (5 * Math.cos(alpha)), 0);
  });
});

describe("buildStressField — süreksizlik", () => {
  it("bombe-gövde birleşiminde ek gerilme var, 5/β uzakta membrana döner", () => {
    const p = base();
    const field = buildStressField(p);
    const hr = componentFrames(p).find((f) => f.id === "HEAD-R")!;
    const zj = hr.head!.equatorZ;
    const atJ = field.at([252.5, 0, zj - 0.01]);
    expect(atJ.zone).toBe("discontinuity");
    expect(Math.abs(atJ.vm - 43.30127)).toBeGreaterThan(5);
    const far = field.at([252.5, 0, zj - 5 / beta(250, 5)]);
    expect(far.zone).toBe("membrane");
    expect(Math.abs(far.vm - 43.30127) / 43.30127).toBeLessThan(0.01);
  });

  it("koni birleşimi süreksizlik bölgesi üretir", () => {
    const p = base();
    p.cones = [{
      cone_id: "CONE-01", large_diameter: 500, small_diameter: 300, half_apex_angle: 30, length: 173.2,
      nominal_thickness: 5, material_id: "MAT-01", weld_joint_id: null, internal_corrosion_allowance: 0, mill_tolerance: 0,
    }];
    p.heads[1] = { ...p.heads[1], inside_diameter: 300 };
    p.component_sequence.splice(2, 0, { component_type: "cone", component_id: "CONE-01" });
    const cf = componentFrames(p).find((f) => f.kind === "cone")!;
    const s = buildStressField(p).at([252.5, 0, cf.zStart - 1]);
    expect(s.zone).toBe("discontinuity");
    expect(s.hoop).toBeLessThan(50); // büyük uçta halka yükü içe çeker
  });
});

describe("buildStressField — nozul", () => {
  function edgePoint(p: VesselProject): [number, number, number] {
    const pl = nozzlePlacement(p, p.nozzles[0], componentFrames(p));
    if ("error" in pl) throw new Error(pl.error);
    // θ=90° → anchor (0, 250, z); kenar: eksen boyunca değil z yönünde rOut kadar.
    return [pl.position[0], pl.position[1] + 2.5, pl.position[2] + 50.5];
  }

  it("nozul kenarında vm ≥ 2 × membran vm; 2·d ötesinde membran", () => {
    const p = base();
    p.nozzles = [nozzle()];
    const field = buildStressField(p);
    const memb = Math.sqrt(50 * 50 - 50 * 25 + 25 * 25);
    const edge = field.at(edgePoint(p));
    expect(edge.zone).toBe("nozzle");
    expect(edge.vm).toBeGreaterThanOrEqual(2 * memb);
    const [x, y, z] = edgePoint(p);
    const far = field.at([x, y, z + 2 * 100 + 1]);
    expect(far.zone).toBe("membrane");
    expect(far.vm).toBeCloseTo(memb, 6);
    expect(field.maxVm).toBeGreaterThanOrEqual(edge.vm - 1e-9);
  });

  it("takviye pedi kenar gerilmesini düşürür", () => {
    const bare = base();
    bare.nozzles = [nozzle()];
    const padded = base();
    padded.nozzles = [nozzle({ reinforcement_pad: true, reinforcement_pad_thickness: 5, reinforcement_pad_od: 200 })];
    const a = buildStressField(bare).at(edgePoint(bare)).vm;
    const b = buildStressField(padded).at(edgePoint(padded)).vm;
    expect(b).toBeLessThan(a);
    expect(b).toBeCloseTo(a / 2, 6);
  });

  it("nozul boynu: boyun membranı (P·rn/tn) uzakta", () => {
    const p = base();
    p.nozzles = [nozzle({ outside_projection: 400 })];
    const pl = nozzlePlacement(p, p.nozzles[0], componentFrames(p));
    if ("error" in pl) throw new Error(pl.error);
    const s = buildStressField(p).at([0, 250 + 350, pl.position[2] + 47.5]);
    expect(s.zone).toBe("nozzle");
    expect(s.hoop).toBeCloseTo(45 / 5, 2);
  });
});

describe("buildStressField — genel", () => {
  it("allowable = gövde malzemesi S; maxVm tüm örneklerin üstünde", () => {
    const p = defaultProject();
    const field = buildStressField(p);
    expect(field.allowable).toBe(138);
    const f = shellFrame(p);
    for (let i = 0; i <= 20; i++) {
      const z = f.zStart + ((f.zEnd - f.zStart) * i) / 20;
      expect(field.at([506, 0, z]).vm).toBeLessThanOrEqual(field.maxVm + 1e-9);
    }
    expect(Number.isFinite(field.maxVm)).toBe(true);
  });

  it("duvardan uzak nokta (destek) sıfır ve işaretli", () => {
    const p = base();
    const f = shellFrame(p);
    const s = buildStressField(p).at([0, -600, (f.zStart + f.zEnd) / 2]);
    expect(s.vm).toBe(0);
    expect(s.zone).toBe("unknown");
  });

  it("düz kapak: merkezde Roark basit mesnet × (C/0,309)", () => {
    const p = base("flat");
    p.heads = p.heads.map((h) => ({ ...h, nominal_thickness: 30, flat_attachment_factor: 0.33 }));
    const hr = componentFrames(p).find((f) => f.id === "HEAD-R")!;
    const s = buildStressField(p).at([0, 0, hr.head!.equatorZ + 15]);
    const k = (0.33 / ((3 * 3.3) / 32)) * (3 / (8 * 900));
    expect(s.zone).toBe("head");
    expect(s.axial).toBeCloseTo(k * 3.3 * 250 * 250, 6);
  });
});
