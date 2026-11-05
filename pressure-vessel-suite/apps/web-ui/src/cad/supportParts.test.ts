// D08 — destek katıları, node'da gerçek OCCT ile.
import { beforeAll, describe, expect, it } from "vitest";
import opencascade from "replicad-opencascadejs";
import { makeBox, measureDistanceBetween, measureShapeVolumeProperties, measureVolume, setOC, type Shape3D } from "replicad";
import type { Support, VesselProject } from "../types";
import { exportFilename, stepBlob, stlBlob } from "./export";
import { planParts } from "./parts";
import { legAssembly } from "./parts/legs";
import type { Catalogs } from "../geometryContract";

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

// OCCT boolean işlemleri tam paralel koşuda 5 s varsayılanı aşabiliyor (tek başına ~1 s).
describe("destek katıları", { timeout: 30_000 }, () => {
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

  it("4 ayaklı dikey kap: 4 kolon + 4 ped, taban sacı alt yüzü = ayak üstü − height_mm", () => {
    // location_mm = 400 → ayak üst ucu z = 300 (sol teğet) + 400
    const p = project("vertical", [support({ type: "leg", leg_count: 4, height_mm: 600, location_mm: 400 })]);
    for (const level of ["preview", "exact"] as const) {
      const { out, warns } = supportShapes(p, level);
      expect(warns).toEqual([]);
      expect(out[0].shape.solids).toHaveLength(8); // kolon(+sac) ve ped yalnız temas eder → ayrı katılar
      expect(out[0].shape.boundingBox.bounds[0][2]).toBeCloseTo(700 - 600, 3);
    }
  });

  it("profil kesitli ve yatay ayaklar kurulur", () => {
    for (const t of ["channel", "box", "angle"] as const) {
      for (const f of ["web", "flanges"] as const) {
        const p = project("vertical", [support({ type: "leg", leg_count: 3, location_mm: 400, leg_section_type: t, leg_channel_facing: f })]);
        expect(supportShapes(p).out[0].shape.solids).toHaveLength(6);
      }
    }
    const h = supportShapes(project("horizontal", [support({ type: "leg", leg_count: 4, height_mm: 500, leg_section_type: "channel" })]));
    expect(h.out[0].shape.solids).toHaveLength(8);
    expect(h.out[0].shape.boundingBox.bounds[0][0]).toBeCloseTo(-(510 + 500), 0);
  });

  describe("U-profil ayak (E01)", () => {
    const U = (over: Partial<Support>) => support({
      type: "leg", leg_count: 4, height_mm: 900, location_mm: 400, leg_section_type: "channel",
      leg_profile_height_mm: 100, leg_profile_width_mm: 50, leg_web_thickness_mm: 6, leg_flange_thickness_mm: 8.5,
      leg_pad_thickness_mm: 10, leg_pad_length_mm: 300, ...over,
    });
    const asm = (s: Support) => {
      const p = project("vertical", [s]);
      const frames = planParts(p, "exact").frames;
      return legAssembly(s, null, { level: "exact", orientation: "vertical", frames, catalogs: {} as Catalogs });
    };

    it.each(["web", "flanges", null] as const)("profil–ped: kesişim hacmi ≈ 0, temas var (facing=%s)", (f) => {
      const { columns, pads } = asm(U({ leg_channel_facing: f }));
      for (let i = 0; i < 4; i++) {
        const common = columns[i].clone().intersect(pads[i].clone());
        expect(measureVolume(common)).toBeLessThan(1e-3);
      }
      // θ=0 ayağı (n=1 → start 0): profil iç yüzü x = R + padT = 520 = ped bbox dış sınırı
      const one = asm(U({ leg_count: 1, leg_channel_facing: f }));
      // taban sacı radyalde taşar → yalnız ped kotundaki profil dilimi
      const cb = one.columns[0].clone().intersect(makeBox([-2000, -2000, 400], [2000, 2000, 750])).boundingBox.bounds;
      const pb = one.pads[0].boundingBox.bounds;
      expect(cb[0][0] - pb[1][0]).toBeCloseTo(0, 3);
      if (f !== "flanges") expect(measureDistanceBetween(one.columns[0], one.pads[0])).toBeLessThan(1e-3);
    });

    it("taban sacı alt yüzü z = üst − height_mm; ped üstü = üst + ext", () => {
      const { columns, pads } = asm(U({ leg_pad_top_extension_mm: 80 }));
      for (const c of columns) expect(c.boundingBox.bounds[0][2]).toBeCloseTo(700 - 900, 3);
      for (const c of columns) expect(c.boundingBox.bounds[1][2]).toBeCloseTo(700, 3);
      for (const pd of pads) expect(pd.boundingBox.bounds[1][2]).toBeCloseTo(780, 3);
      for (const pd of pads) expect(pd.boundingBox.bounds[0][2]).toBeCloseTo(780 - 300, 3);
    });

    it("web / flanges: kolon kütle merkezi radyalde farklı (sırt içte → merkez içeride)", () => {
      const cx = (f: "web" | "flanges") =>
        measureShapeVolumeProperties(asm(U({ leg_count: 1, leg_channel_facing: f, height_mm: 900 })).columns[0]).centerOfMass[0];
      const web = cx("web");
      const fl = cx("flanges");
      expect(Math.abs(web - fl)).toBeGreaterThan(5);
      expect(web).toBeLessThan(fl);
    });

    it("başlangıç açısı uygulanır (n=4 → 45° varsayılan, girilen değer öncelikli)", () => {
      const angle = (s: Support) => {
        const [x, y] = measureShapeVolumeProperties(asm(s).columns[0]).centerOfMass;
        return (Math.atan2(y, x) * 180) / Math.PI;
      };
      expect(angle(U({}))).toBeCloseTo(45, 1);
      expect(angle(U({ leg_start_angle_deg: 30 }))).toBeCloseTo(30, 1);
      expect(angle(U({ leg_count: 3 }))).toBeCloseTo(0, 1);
    });

    it("ankraj delikleri: anchor_bolt_count kadar delik hacmi düşer", () => {
      const vol = (n: number | null) => measureVolume(asm(U({ leg_count: 1, anchor_bolt_count: n })).columns[0]);
      const v0 = measureVolume(legAssembly(U({ leg_count: 1 }), null, {
        level: "preview", orientation: "vertical", frames: planParts(project("vertical", [U({})]), "preview").frames, catalogs: {} as Catalogs,
      }).columns[0]);
      const hole = Math.PI * 11 ** 2 * 16; // Ø(20+2), sac 16
      expect(v0 - vol(1)).toBeCloseTo(hole, 0);
      expect(v0 - vol(2)).toBeCloseTo(2 * hole, 0);
      expect(v0 - vol(null)).toBeCloseTo(4 * hole, 0);
    });
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
