// W4: cache anahtarı orientation içerir; uyarılar cache isabetinde kaybolmaz.
import { beforeAll, describe, expect, it } from "vitest";
import opencascade from "replicad-opencascadejs";
import { setOC, type Shape3D } from "replicad";
import type { BuildWarning } from "../geometryContract";
import type { Nozzle, Support, VesselProject } from "../types";
import { defaultProject } from "../store";
import { buildShapes, sweepWarnings } from "./buildShapes";
import { ShapeCache } from "./cache";
import { planParts } from "./parts";

beforeAll(async () => { setOC(await opencascade()); }, 120_000);

function proj(orientation: "horizontal" | "vertical", extra: Partial<VesselProject> = {}): VesselProject {
  return { ...defaultProject(), orientation, ...extra } as VesselProject;
}
const sup = {
  support_id: "S1", host_component_id: null, type: "leg", location_mm: 0, width_mm: 200, height_mm: 400,
  diameter_mm: null, thickness_mm: null, contact_angle_deg: null, leg_count: 4, leg_diameter_mm: null,
  leg_thickness_mm: null, support_radius_mm: null,
} as unknown as Support;
const jobOf = (p: VesselProject, id: string) => planParts(p, "preview").jobs.find((j) => j.partId === id)!;

describe("cache anahtarı orientation", () => {
  it("destek ve nozul anahtarı yatay→dikey geçişinde değişir; destek mesh'i farklı", () => {
    const nz = { ...defaultProject().nozzles[0], tag: "N1", axial_position: 500 } as Nozzle;
    const h = proj("horizontal", { supports: [sup], nozzles: [nz] });
    const v = proj("vertical", { supports: [sup], nozzles: [nz] });
    expect(jobOf(h, "support:S1").key).not.toBe(jobOf(v, "support:S1").key);
    expect(jobOf(h, "nozzle:N1").key).not.toBe(jobOf(v, "nozzle:N1").key);
    const bb = (p: VesselProject) => (jobOf(p, "support:S1").build(() => {}) as Shape3D).boundingBox.bounds;
    expect(bb(h)).not.toEqual(bb(v));
  });
});

describe("buildShapes uyarı kalıcılığı", () => {
  it("iki ardışık build'de CATALOG_MISS ikisinde de var; sweep temizler", async () => {
    const miss = { ...defaultProject().nozzles[0], tag: "C3", nozzle_type: "coupling", size_designation: '99" 3000#',
      axial_position: 500 } as Nozzle;
    const p = proj("horizontal", { nozzles: [miss], supports: [] });
    const caches = { shapes: new ShapeCache<Shape3D>(), warnings: new Map<string, BuildWarning[]>() };
    let used = new Set<string>();
    const run = () => buildShapes(p, "preview", () => false, caches, (u) => { used = u; });
    const a = await run();
    const b = await run();
    const count = (r: typeof a) => r!.warnings.filter((w) => w.code === "CATALOG_MISS").length;
    expect(count(a)).toBeGreaterThan(0);
    expect(count(b)).toBe(count(a));
    sweepWarnings(caches.warnings, new Set());
    expect(caches.warnings.size).toBe(0);
    expect(used.size).toBeGreaterThan(0);
  });
});
