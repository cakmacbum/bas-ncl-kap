// V1 — Torisferik hamut: P12 FEA ve P03 analitik alanı, bağımsız ince kabuk çözümüyle (referans B) karşılaştırma.
// Referans B: tools/verification/torispherical_shell.py (Reissner–Meissner/Love eksenel simetrik kabuk, solve_bvp),
// iç yarıçaplar verilir, orta yüzey = iç + t/2; ν=0,3; P=1 MPa; silindir yarı boyu 1500 mm (simetri düzlemi).
// Tablo: docs/validation/torispherical-knuckle.md
import { describe, expect, it } from "vitest";
import { buildStressField } from "../stress/analyticField";
import { makeKnuckleCheck } from "../stress/knuckleNote";
import { componentFrames } from "../vesselModel";
import type { StressSample } from "../stress/types";
import { defaultProject } from "../store";
import type { VesselProject } from "../types";
import { runFea } from "../fea/solver";

/** B: hamut yüzeyi en büyük von Mises (MPa), torispherical_shell.solve_torispherical(1000, 10, 1000, rk). */
const REF_B: Record<number, number> = { 60: 227.4, 100: 173.5, 170: 112.2 };
/** Düzeltme öncesi P03 (hamut membranı R1=rk) maxVm — kayıt için (commit 0d6a95e). */
const P03_OLD: Record<number, number> = { 60: 715.0, 100: 407.3, 170: 215.7 };

function vessel(rk: number): VesselProject {
  const p = defaultProject();
  p.design_conditions.design_pressure = 1;
  p.shell_sections[0] = {
    ...p.shell_sections[0], inside_diameter: 1000, nominal_thickness: 10, tangent_length: 3000,
    internal_corrosion_allowance: 0, external_corrosion_allowance: 0,
  };
  p.heads = p.heads.map((h) => ({
    ...h, type: "torispherical" as const, inside_diameter: 1000, nominal_thickness: 10,
    internal_corrosion_allowance: 0, crown_depth: null, crown_radius: 1000, knuckle_radius: rk, straight_flange_length: 0,
  }));
  p.nozzles = [];
  p.supports = [];
  return p;
}

const pct = (a: number, b: number) => ((a - b) / b) * 100;

describe("V1 torisferik hamut karşılaştırması (D=1000, t=10, Rc=D, P=1)", () => {
  const rows = Object.keys(REF_B).map(Number).map((rk) => {
    const p = vessel(rk);
    const fea = runFea(p);
    const field = buildStressField(p);
    // Hamut orta yüzeyi boyunca P03 örnekleri
    const hd = componentFrames(p).find((f) => f.id === "HEAD-R")!.head!;
    const check = makeKnuckleCheck(p);
    const knuckle: StressSample[] = [];
    for (let i = 0; i <= 400; i++) {
      const u = (i / 400) * (Math.PI / 2);
      const pt: [number, number, number] = [505 * Math.cos(u), 0, hd.equatorZ + (hd.domeHeight + 5) * Math.sin(u)];
      if (check(pt)) knuckle.push(field.at(pt));
    }
    return { rk, B: REF_B[rk], fea: fea.maxVm, p03: field.maxVm, p03old: P03_OLD[rk], knuckle, converged: fea.converged };
  });

  it("tablo", () => {
    console.log("rk/D | B kabuk | FEA P12 | FEA−B | P03 eski | eski−B | P03 yeni maxVm (hamut hariç)");
    for (const r of rows) {
      console.log(`${(r.rk / 1000).toFixed(2)} | ${r.B.toFixed(1)} | ${r.fea.toFixed(1)} | ${pct(r.fea, r.B).toFixed(1)}% | ` +
        `${r.p03old.toFixed(1)} | ${pct(r.p03old, r.B).toFixed(1)}% | ${r.p03.toFixed(1)}`);
    }
  });

  it("FEA (P12) bağımsız kabuk çözümüyle %15 içinde", () => {
    for (const r of rows) {
      expect(r.converged).toBe(true);
      expect(Math.abs(pct(r.fea, r.B))).toBeLessThan(15);
    }
  });

  it("P03 hamutta değer üretmez (NaN, düşük güven); maxVm sahte hamut tepesini taşımaz", () => {
    for (const r of rows) {
      expect(r.knuckle.length).toBeGreaterThan(5);
      for (const k of r.knuckle) {
        expect(Number.isNaN(k.vm)).toBe(true);
        expect(k.zone).toBe("unknown");
      }
      expect(Number.isFinite(r.p03)).toBe(true);
      expect(r.p03).toBeLessThan(r.B);
    }
  });
});
