import { describe, expect, it } from "vitest";
import { defaultProject } from "../store";
import type { VesselProject } from "../types";
import { componentFrames } from "../vesselModel";
import { buildStressField } from "../stress/analyticField";
import { makeKnuckleCheck, isTorisphericalHead } from "../stress/knuckleNote";
import { equivalent, equivalents, evaluateAll, linearize } from "../fea/linearize";
import { runFea } from "../fea/solver";
import { toStressField } from "../fea/toStressField";
import type { SclSample } from "../fea/types";

const T = 10, N = 41;
const make = (f: (s: number) => number, g: (s: number) => number = () => 0): SclSample[] =>
  Array.from({ length: N }, (_, i) => {
    const s = (T * i) / (N - 1);
    return { s, sr: 0, st: f(s), sz: g(s), trz: 0 };
  });

describe("linearize — el hesabı", () => {
  it("sabit alan → yalnız membran", () => {
    const l = linearize(make(() => 100))!;
    expect(l.membrane[1]).toBeCloseTo(100, 9);
    expect(Math.abs(l.bending[1])).toBeLessThan(1e-9);
    expect(Math.abs(l.peakInner[1])).toBeLessThan(1e-9);
    const e = equivalents(l);
    expect(e.membrane).toBeCloseTo(100, 6);
    expect(e.bending).toBeLessThan(1e-9);
  });

  it("lineer alan 50 → 150 : membran 100, eğilme 50 (iç yüzeyde −50), tepe 0", () => {
    const l = linearize(make((s) => 50 + (100 * s) / T))!;
    expect(l.membrane[1]).toBeCloseTo(100, 9);
    expect(l.bending[1]).toBeCloseTo(-50, 9); // iç yüzey 50 = 100 + (−50)
    expect(Math.abs(l.peakInner[1])).toBeLessThan(1e-9);
    expect(Math.abs(l.peakOuter[1])).toBeLessThan(1e-9);
    const e = equivalents(l, "tresca");
    expect(e.mbInner).toBeCloseTo(50, 9); // yalnız σθ ≠ 0 → Tresca = |σθ|
    expect(e.mbOuter).toBeCloseTo(150, 9);
  });

  it("parabol → tepe ≠ 0, membran+eğilme toplamı ortalama/ lineer kısım", () => {
    // σ(s) = 100 + 40·(s−5)² /25  : uçlarda 140, ortada 100
    const l = linearize(make((s) => 100 + (40 * (s - 5) ** 2) / 25))!;
    // ortalama = 100 + 40/25·(T²/12)= 100 + 1,6·8,333 = 113,33
    expect(l.membrane[1]).toBeCloseTo(100 + (40 / 25) * (T * T) / 12, 1);
    expect(Math.abs(l.bending[1])).toBeLessThan(1e-6); // simetrik
    expect(l.peakInner[1]).toBeGreaterThan(20);
    expect(l.peakOuter[1]).toBeCloseTo(l.peakInner[1], 6);
  });

  it("bileşenler arası: von Mises vs Tresca", () => {
    expect(equivalent([0, 100, 50, 0], "vonMises")).toBeCloseTo(Math.sqrt(100 * 100 - 100 * 50 + 50 * 50), 9);
    expect(equivalent([0, 100, 50, 0], "tresca")).toBeCloseTo(100, 9);
    expect(equivalent([0, 0, 0, 30], "tresca")).toBeCloseTo(60, 9);
  });

  it("NaN örnek → null", () => {
    const s = make(() => 1);
    s[3].st = NaN;
    expect(linearize(s)).toBeNull();
  });
});

function torisph(): VesselProject {
  const p = defaultProject();
  p.design_conditions.design_pressure = 1;
  p.shell_sections[0] = {
    ...p.shell_sections[0], inside_diameter: 1000, nominal_thickness: 10, tangent_length: 1500,
    internal_corrosion_allowance: 0, external_corrosion_allowance: 0,
  };
  p.heads = p.heads.map((h) => ({
    ...h, type: "torispherical" as const, inside_diameter: 1000, nominal_thickness: 10,
    internal_corrosion_allowance: 0, crown_depth: null, crown_radius: null, knuckle_radius: null, straight_flange_length: 0,
  }));
  p.nozzles = [];
  p.supports = [];
  return p;
}

describe("SCL konumları + FEA entegrasyonu", () => {
  const p = torisph();
  const res = runFea(p);

  it("bileşen ortası + birleşim iki yan SCL'leri üretilir, silindir ortası Pm ≈ PR/t'ye yakın", () => {
    const rows = evaluateAll(res, 138);
    expect(rows.length).toBeGreaterThanOrEqual(3 + 2 * 2);
    const mid = rows.find((r) => r.spec.role === "mid" && componentFrames(p).find((f) => f.id === r.spec.component)?.kind === "shell")!;
    // Ri=500, t=10, P=1 → σθ=50, σz=25 ⇒ vM = 43,3 MPa
    expect(mid.eq!.membrane).toBeGreaterThan(40);
    expect(mid.eq!.membrane).toBeLessThan(47);
    expect(mid.checks.map((c) => c.name)).toEqual(["Pm", "Pm+Pb"]);
    const j = rows.find((r) => r.spec.role === "junctionLeft")!;
    expect(j.checks.map((c) => c.name)).toEqual(["PL", "PL+Pb+Q"]);
    expect(j.eq!.mbInner + j.eq!.mbOuter).toBeGreaterThan(0);
  });

  it("S yoksa kontrol listesi boş", () => {
    expect(evaluateAll(res, null).every((r) => r.checks.length === 0)).toBe(true);
  });

  it("toStressField hamutta FEA < analitik membran (uyarının gerekçesi)", () => {
    const fea = toStressField(res, null);
    const ana = buildStressField(p);
    const hd = componentFrames(p).find((f) => f.kind === "head")!.head!;
    const check = makeKnuckleCheck(p);
    let maxAna = 0, maxFea = 0, n = 0;
    for (let dz = 2; dz < hd.domeHeight; dz += 4) {
      const z = hd.side === "left" ? hd.equatorZ - dz : hd.equatorZ + dz;
      for (let r = 300; r < 520; r += 2) {
        if (!check([r, 0, z])) continue;
        const a = ana.at([r, 0, z]).vm, f = fea.at([r, 0, z]).vm;
        if (a > 0 && f > 0) { n++; maxAna = Math.max(maxAna, a); maxFea = Math.max(maxFea, f); }
      }
    }
    expect(n).toBeGreaterThan(10);
    // P03 membran teorisi hamutta FEA'nın birkaç katı (D1000/t10/P1: ~715 vs ~237 MPa)
    expect(maxAna).toBeGreaterThan(1.5 * maxFea);
  });
});

describe("hamut uyarısı tespiti", () => {
  it("torisferik: tepe (taç) hamut değil, ekvatora yakın dış kenar hamut", () => {
    const p = torisph();
    const check = makeKnuckleCheck(p);
    const hd = componentFrames(p).find((f) => f.kind === "head")!.head!;
    const sign = hd.side === "left" ? -1 : 1;
    expect(check([0, 0, hd.equatorZ + sign * hd.domeHeight * 0.99])).toBe(false);
    expect(check([495, 0, hd.equatorZ + sign * 8])).toBe(true);
    expect(isTorisphericalHead(p, { kind: "head", id: p.heads[0].head_id })).toBe(true);
    expect(isTorisphericalHead(p, { kind: "shell", id: p.shell_sections[0].section_id })).toBe(false);
  });

  it("elipsoidal bombede hiç hamut uyarısı yok", () => {
    const p = torisph();
    p.heads = p.heads.map((h) => ({ ...h, type: "elliptical" as const }));
    const check = makeKnuckleCheck(p);
    expect(check([495, 0, 1600])).toBe(false);
    expect(isTorisphericalHead(p, { kind: "head", id: p.heads[0].head_id })).toBe(false);
  });
});
