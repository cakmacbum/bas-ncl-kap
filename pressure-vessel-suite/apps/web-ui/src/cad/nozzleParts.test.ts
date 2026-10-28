// D07 — nozul parçaları, node'da gerçek OCCT ile.
import { beforeAll, describe, expect, it } from "vitest";
import opencascade from "replicad-opencascadejs";
import { exportSTEP, measureVolume, setOC, type Shape3D } from "replicad";
import { catalogs } from "../data/catalogAdapter";
import type { BuildWarning, Level, PartCtx } from "../geometryContract";
import type { Nozzle, VesselProject } from "../types";
import { planParts } from "./parts";
import { coupling } from "./parts/coupling";

beforeAll(async () => {
  setOC(await opencascade());
}, 120_000);

const head = (id: string) => ({
  head_id: id, type: "elliptical", inside_diameter: 1000, crown_radius: null, knuckle_radius: null,
  straight_flange_length: 50, nominal_thickness: 10, material_id: "M", weld_joint_id: null,
  internal_corrosion_allowance: 0, mill_tolerance: 0, forming_thinning: 0, flat_attachment_factor: null,
});
const nozzle = (o: Partial<Nozzle>): Nozzle => ({
  tag: "N1", nozzle_type: "flanged", host_component_id: "SHELL-01", axial_position: 1000,
  circumferential_angle: 90, inclination_angle: 0, head_position_diameter: null,
  outside_diameter: 114.3, inside_diameter: 102.26, neck_thickness: 6.02, inside_projection: 0,
  outside_projection: 150, size_designation: '4" SCH40 CL150', material_id: "M", corrosion_allowance: 0,
  reinforcement_pad: false, reinforcement_pad_thickness: null, reinforcement_pad_od: null,
  rating_class: "CL150", coupling_form: null, ...o,
}) as Nozzle;

function project(nozzles: Nozzle[]): VesselProject {
  return {
    project_number: "D07", project_name: "D07", orientation: "horizontal",
    shell_sections: [{
      section_id: "SHELL-01", inside_diameter: 1000, outside_diameter: null, tangent_length: 2000,
      nominal_thickness: 10, material_id: "M", weld_joint_id: null, internal_corrosion_allowance: 0,
      external_corrosion_allowance: 0, mill_tolerance: 0, forming_thinning: 0,
    }],
    cones: [], heads: [head("HEAD-L"), head("HEAD-R")],
    component_sequence: [
      { component_type: "head", component_id: "HEAD-L" },
      { component_type: "shell", component_id: "SHELL-01" },
      { component_type: "head", component_id: "HEAD-R" },
    ],
    nozzles, supports: [], junctions: [], materials: [], welds: [],
  } as unknown as VesselProject;
}

function ctx(level: Level, warns: BuildWarning[] = []): PartCtx {
  return { level, catalogs, orientation: "horizontal", frames: [], warn: (w) => warns.push(w) };
}

function run(nz: Nozzle, level: Level) {
  const warns: BuildWarning[] = [];
  const plan = planParts(project([nz]), level);
  const job = plan.jobs.find((j) => j.partId === `nozzle:${nz.tag}`)!;
  const shape = job.build((w) => warns.push(w))!;
  return { shape, warns, plan, job };
}

describe("flanşlı nozul", () => {
  it("WN NPS4 CL150: hacim > 0, katalog bulundu", () => {
    const { shape, warns } = run(nozzle({}), "preview");
    expect(measureVolume(shape)).toBeGreaterThan(0);
    expect(warns.filter((w) => w.code === "CATALOG_MISS")).toEqual([]);
  });

  it("exact: 8 cıvata deliği (hacim farkı), preview'da delik yok", () => {
    const p = run(nozzle({}), "preview");
    const e = run(nozzle({}), "exact");
    const f = catalogs.flange("4", "CL150")!;
    expect(f.bolt_count).toBe(8);
    const holes = f.bolt_count! * Math.PI * (f.bolt_hole_diameter! / 2) ** 2 * f.thickness!;
    const diff = measureVolume(p.shape) - measureVolume(e.shape);
    expect(diff / holes).toBeCloseTo(1, 1);
  });

  it("slip_on ve pad_reinforced (exact ped host'a sarılı) kurulur", () => {
    const so = run(nozzle({ tag: "N2", nozzle_type: "slip_on" }), "exact");
    expect(measureVolume(so.shape)).toBeGreaterThan(0);
    const base = run(nozzle({ tag: "N3" }), "exact");
    const pd = run(nozzle({ tag: "N4", nozzle_type: "pad_reinforced", reinforcement_pad: true,
      reinforcement_pad_od: 250, reinforcement_pad_thickness: 10 }), "exact");
    const dv = measureVolume(pd.shape) - measureVolume(base.shape);
    const flatAnnulus = Math.PI * (125 ** 2 - 57.15 ** 2) * 10;
    expect(dv).toBeGreaterThan(0.5 * flatAnnulus);
    expect(dv).toBeLessThan(1.6 * flatAnnulus);
    expect(pd.warns.filter((w) => w.code === "BOOLEAN_FAILED")).toEqual([]);
  });

  it("host gövdesinden nozul deliği çıkar (exact)", () => {
    const withN = planParts(project([nozzle({})]), "exact").jobs.find((j) => j.partId === "shell:SHELL-01")!;
    const without = planParts(project([]), "exact").jobs.find((j) => j.partId === "shell:SHELL-01")!;
    const v1 = measureVolume(withN.build(() => {})!);
    const v0 = measureVolume(without.build(() => {})!);
    const hole = Math.PI * 51.13 ** 2 * 10;
    expect(v0 - v1).toBeGreaterThan(0.8 * hole);
    expect(v0 - v1).toBeLessThan(1.3 * hole);
  });

  it("host yoksa / dışarıdaysa uyarı, nozul atlanır", () => {
    const a = planParts(project([nozzle({ host_component_id: "YOK" })]), "preview");
    expect(a.warnings.map((w) => w.code)).toContain("HOST_NOT_FOUND");
    const b = planParts(project([nozzle({ axial_position: 99999 })]), "preview");
    expect(b.warnings.map((w) => w.code)).toContain("OUT_OF_HOST");
    expect(b.jobs.some((j) => j.kind === "nozzle")).toBe(false);
  });
});

describe("dövme manşon", () => {
  const cp = (o: Partial<Nozzle> = {}) => nozzle({
    tag: "C1", nozzle_type: "coupling", size_designation: '1" 3000#', rating_class: "3000#",
    coupling_form: "full", outside_diameter: 44.5, inside_diameter: 26, outside_projection: 57, ...o,
  });

  it("borusuz: bbox boyu = length ± 0.5 (host'suz yerel)", () => {
    const shape = coupling.build(cp(), null, ctx("preview"))!;
    const [[x0, , z0], [x1, , z1]] = shape.boundingBox.bounds;
    expect(Math.abs(z1 - z0 - 57)).toBeLessThanOrEqual(0.5);
    expect(x1 - x0).toBeCloseTo(44.5, 1);
  });

  it("exact saddle-cut: kurulur, BOOLEAN_FAILED yok", () => {
    const p = run(cp(), "preview");
    const e = run(cp(), "exact");
    expect(measureVolume(e.shape)).toBeGreaterThan(0);
    expect(e.warns.filter((w) => w.code === "BOOLEAN_FAILED")).toEqual([]);
    expect(measureVolume(p.shape)).toBeGreaterThan(0);
  });

  it("SW manşon + katalogsuz yedek", () => {
    const sw = run(cp({ tag: "C2", nozzle_type: "socket_welded", size_designation: '1/2" 3000#' }), "exact");
    expect(measureVolume(sw.shape)).toBeGreaterThan(0);
    const miss = run(cp({ tag: "C3", size_designation: '99" 3000#' }), "preview");
    expect(miss.warns.some((w) => w.code === "CATALOG_MISS")).toBe(true);
  });
});

describe("manway + süre/STEP", () => {
  const mw = (o: Partial<Nozzle> = {}) => nozzle({ tag: "M1", nozzle_type: "manway", size_designation: '20" CL150',
    outside_diameter: 508, inside_diameter: 488, outside_projection: 200, ...o });

  it("manway NPS20 CL150 kurulur", () => {
    expect(measureVolume(run(mw(), "preview").shape)).toBeGreaterThan(0);
    expect(measureVolume(run(mw(), "exact").shape)).toBeGreaterThan(0);
  });

  it("proje süreleri + STEP boyutu (bilgi)", () => {
    const nzs = [
      nozzle({ tag: "N1", axial_position: 400 }),
      nozzle({ tag: "N2", axial_position: 800, nozzle_type: "slip_on" }),
      nozzle({ tag: "N3", axial_position: 1200, nozzle_type: "pad_reinforced", reinforcement_pad: true,
        reinforcement_pad_od: 250, reinforcement_pad_thickness: 10 }),
      nozzle({ tag: "C1", axial_position: 1600, nozzle_type: "coupling", size_designation: '1" 3000#',
        rating_class: "3000#", coupling_form: "full", outside_diameter: 44.5, inside_diameter: 26, outside_projection: 57 }),
      mw({ axial_position: 1000, circumferential_angle: 0 }),
    ];
    for (const level of ["preview", "exact"] as const) {
      const t0 = performance.now();
      const shapes: { partId: string; shape: Shape3D }[] = [];
      const plan = planParts(project(nzs), level);
      for (const j of plan.jobs) {
        const s = j.build(() => {});
        if (s) shapes.push({ partId: j.partId, shape: s });
      }
      let tris = 0;
      const tol = level === "preview" ? { tolerance: 1, angularTolerance: 0.3 } : { tolerance: 0.2, angularTolerance: 0.1 };
      for (const s of shapes) tris += s.shape.mesh(tol).triangles.length / 3;
      const ms = performance.now() - t0;
      console.log(`[D07] ${level}: ${shapes.length} parça, ${tris} üçgen, ${ms.toFixed(0)} ms, uyarı ${plan.warnings.length}`);
      if (level === "exact") {
        const blob = exportSTEP(shapes.map((s) => ({ shape: s.shape, name: s.partId })), { unit: "mm" });
        console.log(`[D07] STEP ${blob.size} B`);
      }
    }
  }, 120_000);
});
