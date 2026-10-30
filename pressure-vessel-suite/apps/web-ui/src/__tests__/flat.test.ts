import { describe, expect, it } from "vitest";
import { toDxf, bounds } from "../flat/shapes";
import { branchDrop, coneSector, headMeridian, headPetal, nozzleCut, shellCourse } from "../flat/templates";

describe("açınım şablonları", () => {
  it("gövde halkası: çevre π·(ID+t)", () => {
    const r = shellCourse("S1", 1000, 10, 2000);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    const b = bounds(r.part.shapes.filter((s) => s.k === "poly"));
    expect(b.x1).toBeCloseTo(Math.PI * 1010, 6);
    expect(b.y1).toBe(2000);
    const g = shellCourse("S1", 1000, 10, 2000, 3);
    if (g.ok) expect(bounds(g.part.shapes.filter((s) => s.k === "poly")).x1).toBeCloseTo(Math.PI * 1010 + 3, 6);
  });

  it("koni: açınım açısı = 360·(D1/2)/R1, yay boyu = π·D1", () => {
    // ID 1000/500, boy 500, t=0 benzeri küçük et → ölçüler el hesabı
    const r = coneSector("C1", 1000, 500, 500, 1e-9);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    const slant = Math.hypot(500, 250);
    const R1 = (slant * 1000) / 500;
    const arc = r.part.shapes.find((s) => s.k === "arc");
    expect(arc && arc.k === "arc" && arc.r).toBeCloseTo(R1, 4);
    if (arc && arc.k === "arc") expect(((arc.a1 - arc.a0) * Math.PI * R1) / 180).toBeCloseTo(Math.PI * 1000, 3);
    expect(coneSector("C", 500, 1000, 500, 5).ok).toBe(false);
  });

  it("kesişim eğrisi uç değerleri", () => {
    expect(branchDrop(500, 100, 0)).toBeCloseTo(0, 12);
    expect(branchDrop(500, 100, Math.PI / 2)).toBeCloseTo(500 - Math.sqrt(500 ** 2 - 100 ** 2), 9); // = 10.102
    expect(branchDrop(500, 100, Math.PI / 2)).toBeCloseTo(10.1021, 3);
    const r = nozzleCut("N1", { runInsideD: 1000, runT: 0, branchOD: 200, branchT: 0, crownLength: 150 });
    expect(r.ok).toBe(true);
    expect(nozzleCut("N", { runInsideD: 100, runT: 0, branchOD: 200, branchT: 0, crownLength: 10 }).ok).toBe(false);
  });

  it("yarımküre petali: meridyen = πR/2, ekvator genişliği = 2πR/n", () => {
    const m = headMeridian({ type: "hemispherical", insideD: 1000, t: 0 });
    expect(typeof m).not.toBe("string");
    if (typeof m === "string") return;
    expect(m[m.length - 1].s).toBeCloseTo((Math.PI * 500) / 2, 1);
    const p = headPetal("H", { type: "hemispherical", insideD: 1000, t: 1e-9 }, 8);
    expect(p.ok).toBe(true);
    expect(headPetal("H", { type: "torispherical", insideD: 1000, t: 10 }, 8).ok).toBe(false); // R yok → uydurma yok
    expect(headPetal("H", { type: "elliptical", insideD: 1000, t: 10 }, 2).ok).toBe(false);
  });

  it("DXF R12 yapısı", () => {
    const r = shellCourse("S1", 1000, 10, 2000);
    if (!r.ok) throw new Error();
    const d = toDxf(r.part);
    expect(d).toContain("AC1009");
    expect(d).toContain("POLYLINE");
    expect(d.trimEnd().endsWith("EOF")).toBe(true);
  });
});
