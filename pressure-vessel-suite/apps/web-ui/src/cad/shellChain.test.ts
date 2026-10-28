// D06 — gövde zinciri katıları, node'da gerçek OCCT (replicad-opencascadejs WASM) ile.
import { beforeAll, describe, expect, it } from "vitest";
import opencascade from "replicad-opencascadejs";
import { exportSTEP, getOC, importSTEP, measureVolume, setOC, type AnyShape, type Shape3D } from "replicad";
import type { ComponentFrame } from "../geometryContract";
import { buildChainSolid } from "./parts/shellChain";
import type { VesselProject } from "../types";
import { buildShellChainShapes, componentFrames, planParts } from "./parts";

beforeAll(async () => {
  // node: Emscripten WASM'ı kendi paketinden (import.meta.url) okur.
  const oc = await opencascade();
  setOC(oc);
}, 120_000);

const head = (id: string, type: string, di: number, t: number, sf: number, extra: object = {}) => ({
  head_id: id, type, inside_diameter: di, crown_radius: null, knuckle_radius: null,
  straight_flange_length: sf, nominal_thickness: t, material_id: "M", weld_joint_id: null,
  internal_corrosion_allowance: 0, mill_tolerance: 0, forming_thinning: 0, flat_attachment_factor: null, ...extra,
});
const shell = (id: string, di: number, L: number, t: number) => ({
  section_id: id, inside_diameter: di, outside_diameter: null, tangent_length: L, nominal_thickness: t,
  material_id: "M", weld_joint_id: null, internal_corrosion_allowance: 0, external_corrosion_allowance: 0,
  mill_tolerance: 0, forming_thinning: 0,
});

function project(leftType: string, rightType: string): VesselProject {
  return {
    project_number: "D06", project_name: "D06", orientation: "horizontal",
    shell_sections: [shell("SHELL-01", 1000, 2000, 10), shell("SHELL-02", 600, 1000, 8)],
    cones: [{ cone_id: "CONE-01", large_diameter: 1000, small_diameter: 600, half_apex_angle: 21.8, length: 500,
      nominal_thickness: 10, material_id: "M", weld_joint_id: null, internal_corrosion_allowance: 0, mill_tolerance: 0 }],
    heads: [head("HEAD-L", leftType, 1000, 10, 50), head("HEAD-R", rightType, 600, 8, 40)],
    component_sequence: [
      { component_type: "head", component_id: "HEAD-L" },
      { component_type: "shell", component_id: "SHELL-01" },
      { component_type: "cone", component_id: "CONE-01" },
      { component_type: "shell", component_id: "SHELL-02" },
      { component_type: "head", component_id: "HEAD-R" },
    ],
    nozzles: [], supports: [], junctions: [], materials: [], welds: [],
  } as unknown as VesselProject;
}

const ring = (a: number, t: number, L: number) => Math.PI * ((a + t) ** 2 - a ** 2) * L;
const halfEllipsoidShell = (a: number, b: number, t: number) =>
  (2 / 3) * Math.PI * ((a + t) ** 2 * (b + t) - a * a * b);

describe("gövde zinciri katıları", () => {
  it("frames: SHELL-01 → CONE-01 (1000→600) → SHELL-02", () => {
    const f = componentFrames(project("elliptical", "elliptical"));
    expect(f.map((x) => x.id)).toEqual(["HEAD-L", "SHELL-01", "CONE-01", "SHELL-02", "HEAD-R"]);
    expect(f[2].zStart).toBeCloseTo(250 + 50 + 2000);
    expect(f[2].cone?.largeAtStart).toBe(true);
    expect(f[3].rInStart).toBe(300);
  });

  it("2:1 eliptik sol + sağ: hacimler analitik, ayrı partId'ler", () => {
    const shapes = buildShellChainShapes(project("elliptical", "elliptical"));
    expect(shapes.map((s) => s.partId)).toEqual([
      "head:HEAD-L", "shell:SHELL-01", "cone:CONE-01", "shell:SHELL-02", "head:HEAD-R",
    ]);
    const vol = Object.fromEntries(shapes.map((s) => [s.partId, measureVolume(s.shape)]));
    expect(vol["shell:SHELL-01"]).toBeCloseTo(ring(500, 10, 2000), -2);
    expect(vol["head:HEAD-L"] / (halfEllipsoidShell(500, 250, 10) + ring(500, 10, 50))).toBeCloseTo(1, 4);
    expect(vol["head:HEAD-R"] / (halfEllipsoidShell(300, 150, 8) + ring(300, 8, 40))).toBeCloseTo(1, 4);
    // Sol bombe kutbu z=0 (iç) → dış kutup −t; sağ bombe sağa bakar
    const bl = shapes[0].shape.boundingBox.bounds;
    expect(bl[0][2]).toBeCloseTo(-10, 3);
    expect(bl[1][2]).toBeCloseTo(300, 3);
    const br = shapes[4].shape.boundingBox.bounds;
    const f = componentFrames(project("elliptical", "elliptical"));
    expect(br[1][2]).toBeCloseTo(f[4].zEnd + 8, 3);
    expect(br[0][2]).toBeCloseTo(f[4].zStart, 3);
  });

  it("koni: daralan, normal kalınlık", () => {
    const [, , cone] = buildShellChainShapes(project("elliptical", "elliptical"));
    const L = 500;
    const dr = 10 / Math.cos(Math.atan(200 / L));
    const frustum = (r1: number, r2: number) => (Math.PI * L * (r1 * r1 + r1 * r2 + r2 * r2)) / 3;
    expect(measureVolume(cone.shape) / (frustum(500 + dr, 300 + dr) - frustum(500, 300))).toBeCloseTo(1, 4);
  });

  it("yarım küre, torisferik, düz kapak kurulur", () => {
    for (const [l, r] of [["hemispherical", "torispherical"], ["flat", "hemispherical"], ["torispherical", "flat"]]) {
      const shapes = buildShellChainShapes(project(l, r), "exact");
      expect(shapes).toHaveLength(5);
      for (const s of shapes) expect(measureVolume(s.shape)).toBeGreaterThan(0);
    }
    const [hl] = buildShellChainShapes(project("hemispherical", "flat"));
    const sphereShell = (2 / 3) * Math.PI * (510 ** 3 - 500 ** 3);
    expect(measureVolume(hl.shape) / (sphereShell + ring(500, 10, 50))).toBeCloseTo(1, 4);
    const shapes = buildShellChainShapes(project("elliptical", "flat"));
    const flat = shapes[4].shape;
    expect(measureVolume(flat) / (Math.PI * 308 ** 2 * 8 + ring(300, 8, 40))).toBeCloseTo(1, 4);
  });

  it("torisferik kubbe yüksekliği frame ile aynı (tek kaynak)", () => {
    const p = project("elliptical", "torispherical");
    const f = componentFrames(p);
    const [, , , , hr] = buildShellChainShapes(p);
    expect(hr.shape.boundingBox.bounds[1][2]).toBeCloseTo(f[4].zEnd + 8, 2);
  });

  it("süre + STEP (bilgi)", () => {
    for (const level of ["preview", "exact"] as const) {
      const t0 = performance.now();
      const shapes = buildShellChainShapes(project("elliptical", "torispherical"), level);
      let tris = 0;
      for (const s of shapes) tris += s.shape.mesh(level === "preview"
        ? { tolerance: 1, angularTolerance: 0.3 } : { tolerance: 0.2, angularTolerance: 0.1 }).triangles.length / 3;
      const ms = performance.now() - t0;
      if (level === "exact") {
        const blob = exportSTEP(shapes.map((s) => ({ shape: s.shape, name: s.partId })), { unit: "mm" });
        console.log(`[D06] STEP ${blob.size} B`);
      }
      console.log(`[D06] ${level}: ${shapes.length} parça, ${tris} üçgen, ${ms.toFixed(0)} ms`);
    }
    expect(planParts(project("elliptical", "elliptical"), "preview").warnings).toEqual([]);
  });
});

// ---- W4 düzeltmesi: bombe katıları geçerli + duvarlı, STEP gidiş-dönüşünde de ----
const isValid = (s: AnyShape) =>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  new (getOC() as any).BRepCheck_Analyzer(s.wrapped, true, false, false).IsValid() as boolean;

function simpson(f: (x: number) => number, x0: number, x1: number, n = 2000): number {
  const hh = (x1 - x0) / n;
  let s = f(x0) + f(x1);
  for (let i = 1; i < n; i++) s += (i % 2 ? 4 : 2) * f(x0 + i * hh);
  return (s * hh) / 3;
}
/** Torisferik kubbe boşluk hacmi (ekvatordan kutba): knuckle rk, crown R, yükseklik h. */
function toriCavity(a: number, rk: number, R: number, h: number): number {
  const zT = (rk * (R - h)) / (R - rk);
  const knuckle = simpson((z) => (a - rk + Math.sqrt(Math.max(0, rk * rk - z * z))) ** 2, 0, zT);
  const crown = simpson((z) => Math.max(0, R * R - (z - (h - R)) ** 2), zT, h);
  return Math.PI * (knuckle + crown);
}

type HT = "elliptical" | "torispherical" | "hemispherical" | "flat";

describe("bombe katıları: her tip, sol ve sağ ayrı", () => {
  const a = 500, t = 10, sf = 50, Di = 1000;
  const ringSf = ring(a, t, sf);
  const hT = Di / 6, rk = 0.06 * Di;
  const R = (hT * hT - rk * rk + (a - rk) ** 2) / (2 * (hT - rk));
  const cases: { type: HT; h: number; wall: number }[] = [
    { type: "elliptical", h: 250, wall: halfEllipsoidShell(a, 250, t) + ringSf },
    { type: "torispherical", h: hT, wall: toriCavity(a + t, rk + t, R + t, hT + t) - toriCavity(a, rk, R, hT) + ringSf },
    { type: "hemispherical", h: 500, wall: (2 / 3) * Math.PI * ((a + t) ** 3 - a ** 3) + ringSf },
    { type: "flat", h: 0, wall: Math.PI * (a + t) ** 2 * t + ringSf },
  ];

  const frame = (type: HT, h: number, side: "left" | "right"): ComponentFrame =>
    side === "left"
      ? { kind: "head", id: "H", index: 0, zStart: 0, zEnd: h + sf, rInStart: 0, rInEnd: a, rOutStart: t, rOutEnd: a + t,
          thickness: t, head: { side, type, domeHeight: h, sf, equatorZ: h } }
      : { kind: "head", id: "H", index: 4, zStart: 3000, zEnd: 3000 + h + sf, rInStart: a, rInEnd: 0, rOutStart: a + t,
          rOutEnd: t, thickness: t, head: { side, type, domeHeight: h, sf, equatorZ: 3000 + sf } };

  for (const c of cases) {
    for (const side of ["left", "right"] as const) {
      it(`${c.type} ${side}: geçerli, duvar hacmi ±%2, STEP gidiş-dönüş`, async () => {
        const s = buildChainSolid(frame(c.type, c.h, side), undefined) as Shape3D;
        expect(isValid(s)).toBe(true);
        expect(Math.abs(measureVolume(s) / c.wall - 1)).toBeLessThan(0.02);
        const back = (await importSTEP(exportSTEP([{ shape: s, name: `head:${side}` }], { unit: "mm" }))) as Shape3D;
        expect(isValid(back)).toBe(true);
        expect(Math.abs(measureVolume(back) / c.wall - 1)).toBeLessThan(0.02);
      });
    }
  }

  it("zincir STEP'i: 5 katı geçerli, toplam hacim korunur, bombeler duvarlı", async () => {
    const shapes = buildShellChainShapes(project("elliptical", "elliptical"), "exact");
    const back = (await importSTEP(
      exportSTEP(shapes.map((s) => ({ shape: s.shape, name: s.partId })), { unit: "mm" }),
    )) as Shape3D;
    const solids = back.solids;
    expect(solids).toHaveLength(5);
    for (const so of solids) expect(isValid(so)).toBe(true);
    const total = shapes.reduce((acc, s) => acc + measureVolume(s.shape), 0);
    expect(Math.abs(solids.reduce((acc, so) => acc + measureVolume(so), 0) / total - 1)).toBeLessThan(1e-3);
    // Katı katı eşleşme (dolu bombe hatasında HEAD-L 140e6 / HEAD-R 33e6 çıkıyordu)
    const vIn = shapes.map((s) => measureVolume(s.shape)).sort((x, y) => x - y);
    const vBack = solids.map((so) => measureVolume(so)).sort((x, y) => x - y);
    vIn.forEach((v, i) => expect(Math.abs(vBack[i] / v - 1)).toBeLessThan(1e-3));
  });
});
