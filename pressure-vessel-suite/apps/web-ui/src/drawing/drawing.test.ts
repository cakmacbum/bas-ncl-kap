import { describe, expect, it } from "vitest";
import { defaultProject } from "../store";
import { overallLength } from "../vesselModel";
import { drawingToDxf, dxfText } from "./dxf";
import { buildDrawing, NOT_APPROVAL } from "./model";
import { drawingToSvg } from "./svg";

function sample() {
  const p = defaultProject();
  return {
    ...p,
    supports: [{
      ...(p.supports[0] ?? ({} as never)), support_id: "SUP-1", type: "saddle" as const, location_mm: 500,
      width_mm: 200, height_mm: 300,
    }],
  };
}

describe("imalat resmi", () => {
  const p = sample();
  const m = buildDrawing(p);

  it("toplam boy ölçüsü analitik boya eşit", () => {
    const overall = m.dimensions.find((d) => d.kind === "overall");
    expect(overall?.value).toBeCloseTo(overallLength(p.shell_sections[0]!, p.heads[0]!, p.heads[1]!), 6);
    expect(m.overallLengthMm).toBeCloseTo(overall!.value, 6);
    expect(m.dimensions.some((d) => d.kind === "tangent")).toBe(true);
    expect(m.dimensions.some((d) => d.kind === "inside-diameter")).toBe(true);
    expect(m.dimensions.some((d) => d.kind === "support")).toBe(true);
  });

  it("nozul sayısı = etiket sayısı = tablo satırı", () => {
    expect(p.nozzles.length).toBeGreaterThan(0);
    expect(m.nozzleLabels).toEqual(p.nozzles.map((n) => n.tag));
    expect(m.nozzleTable.length).toBe(p.nozzles.length + 1);
    const svg = drawingToSvg(m);
    for (const n of p.nozzles) expect(svg).toContain(`>${n.tag}</text>`);
  });

  it("antet uyarı metnini içerir", () => {
    const svg = drawingToSvg(m);
    expect(svg).toContain(NOT_APPROVAL);
    expect(svg.startsWith("<?xml")).toBe(true);
  });

  it("DXF R12 yapısı ve katmanlar", () => {
    const dxf = drawingToDxf(m);
    const lines = dxf.split("\n");
    expect(lines.slice(0, 4)).toEqual(["0", "SECTION", "2", "HEADER"]);
    expect(dxf).toContain("ENTITIES");
    expect(dxf.trimEnd().endsWith("EOF")).toBe(true);
    for (const l of ["OUTLINE", "HIDDEN", "DIM", "TEXT", "TITLE"]) expect(dxf).toContain(`\n${l}\n`);
    expect(dxf.match(/\nSECTION\n/g)?.length).toBe(3);
    expect(dxf.match(/\nENDSEC\n/g)?.length).toBe(3);
    // R12: ASCII dışı karakter olmamalı
    expect(/[^\x00-\x7f]/.test(dxf)).toBe(false);
    expect(dxfText("Ø100 90° Çıkıntı")).toBe("%%c100 90%%d Cikinti");
  });

  it("zincir boşsa çökmez", () => {
    const empty = { ...p, shell_sections: [], heads: [], cones: [], component_sequence: [], nozzles: [], supports: [] };
    expect(() => drawingToDxf(buildDrawing(empty))).not.toThrow();
  });
});
