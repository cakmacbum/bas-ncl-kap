// D08 — destek katıları, node'da gerçek OCCT ile.
import { beforeAll, describe, expect, it } from "vitest";
import opencascade from "replicad-opencascadejs";
import { setOC, type Shape3D } from "replicad";
import type { Support, VesselProject } from "../types";
import { exportFilename, stepBlob, stlBlob } from "./export";
import { planParts } from "./parts";

beforeAll(async () => {
  setOC(await opencascade());
}, 120_000);

const head = (id: string) => ({
  head_id: id, type: "elliptical", inside_diameter: 1000, crown_radius: null, knuckle_radius: null,
  straight_flange_length: 50, nominal_thickness: 10, material_id: "M", weld_joint_id: null,
  internal_corrosion_allowance: 0, mill_tolerance: 0, forming_thinning: 0, flat_attachment_factor: null,
});

const support = (over: Partial<Support>): Support =>
  ({ support_id: "S1", host_component_id: null, type: "saddle", location_mm: 500, width_mm: 200, height_mm: 300,
    diameter_mm: null, thickness_mm: null, contact_angle_deg: null, leg_count: null, leg_diameter_mm: null,
    leg_thickness_mm: null, support_radius_mm: null, ...over }) as unknown as Support;

function project(orientation: "horizontal" | "vertical", supports: Support[]): VesselProject {
  return {
    project_number: "D08", project_name: "Eyer Test", orientation,
    shell_sections: [{ section_id: "SHELL-01", inside_diameter: 1000, outside_diameter: null, tangent_length: 3000,
      nominal_thickness: 10, material_id: "M", weld_joint_id: null, internal_corrosion_allowance: 0,
      external_corrosion_allowance: 0, mill_tolerance: 0, forming_thinning: 0 }],
    cones: [], heads: [head("HEAD-L"), head("HEAD-R")],
    component_sequence: [
      { component_type: "head", component_id: "HEAD-L" },
      { component_type: "shell", component_id: "SHELL-01" },
      { component_type: "head", component_id: "HEAD-R" },
    ],
    nozzles: [], supports, junctions: [], materials: [], welds: [],
  } as unknown as VesselProject;
}

function supportShapes(p: VesselProject, level: "preview" | "exact" = "preview") {
  const warns: string[] = [];
  const out = planParts(p, level).jobs
    .filter((j) => j.kind === "support")
    .map((j) => ({ partId: j.partId, shape: j.build((w) => warns.push(w.code)) as Shape3D }));
  return { out, warns };
}

describe("destek katıları", () => {
  it("2 eyerli yatay kap: 2 destek, alt nokta kap altından height_mm aşağıda", () => {
    const p = project("horizontal", [
      support({ support_id: "S1", location_mm: 500 }),
      support({ support_id: "S2", location_mm: 2500, height_mm: 400 }),
    ]);
    for (const level of ["preview", "exact"] as const) {
      const { out, warns } = supportShapes(p, level);
      expect(warns).toEqual([]);
      expect(out.map((s) => s.partId)).toEqual(["support:S1", "support:S2"]);
      const R = 510; // dış yarıçap
      expect(out[0].shape.boundingBox.bounds[0][0]).toBeCloseTo(-(R + 300), 0);
      expect(out[1].shape.boundingBox.bounds[0][0]).toBeCloseTo(-(R + 400), 0);
      // eksenel merkez = sol teğet (bombe 250+50=300 zEnd... frames) + location
      const [lo, hi] = [out[0].shape.boundingBox.bounds[0][2], out[0].shape.boundingBox.bounds[1][2]];
      expect((lo + hi) / 2).toBeCloseTo(300 + 500, 0);
    }
  });

  it("4 ayaklı dikey kap: 4 ayrı katı, alt yüz kap altından height_mm aşağıda", () => {
    const p = project("vertical", [support({ type: "leg", leg_count: 4, height_mm: 600, location_mm: 0 })]);
    for (const level of ["preview", "exact"] as const) {
      const { out, warns } = supportShapes(p, level);
      expect(warns).toEqual([]);
      expect(out[0].shape.solids).toHaveLength(4);
      expect(out[0].shape.boundingBox.bounds[0][2]).toBeCloseTo(-10 - 600, 0);
    }
  });

  it("profil kesitli ve yatay ayaklar kurulur", () => {
    for (const t of ["channel", "box", "angle"] as const) {
      const p = project("vertical", [support({ type: "leg", leg_count: 3, leg_section_type: t })]);
      expect(supportShapes(p).out[0].shape.solids).toHaveLength(3);
    }
    const h = supportShapes(project("horizontal", [support({ type: "leg", leg_count: 4, height_mm: 500 })]));
    expect(h.out[0].shape.solids).toHaveLength(4);
    expect(h.out[0].shape.boundingBox.bounds[0][0]).toBeCloseTo(-(510 + 500), 0);
  });

  it("etek: dikey kapta Ø ve yükseklik; yatayda uyarı + null", () => {
    const { out } = supportShapes(project("vertical", [support({ type: "skirt", height_mm: 800, thickness_mm: 12 })]), "exact");
    const b = out[0].shape.boundingBox.bounds;
    expect(b[1][2]).toBeCloseTo(300, 0); // sol bombe zEnd (250+50)
    expect(b[0][2]).toBeCloseTo(300 - 800, 0);
    const h = supportShapes(project("horizontal", [support({ type: "skirt" })]));
    expect(h.out[0].shape).toBeNull();
    expect(h.warns).toContain("OUT_OF_HOST");
  });

  it("export: STEP + STL blob, dosya adı proje adı + tarih", async () => {
    const { out } = supportShapes(project("horizontal", [support({})]), "exact");
    const step = stepBlob(out);
    const stl = stlBlob(out);
    expect(step.size).toBeGreaterThan(1000);
    expect(stl.size).toBeGreaterThan(1000);
    expect(await step.text()).toContain("support:S1");
    expect(exportFilename({ project_name: "Eyer Test", project_number: "x" }, "step", new Date("2026-10-28"))).toBe("Eyer_Test_2026-10-28.step");
  });
});
