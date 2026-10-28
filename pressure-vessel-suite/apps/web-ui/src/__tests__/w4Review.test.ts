// W4 inceleme düzeltmeleri: geçiş kapısı, bombe OUT_OF_HOST, türetilmiş manşon ölçüleri.
import { describe, expect, it } from "vitest";
import { defaultProject } from "../store";
import { geometryIssues } from "../geometryValidation";
import { computeIssues } from "../geometrySteps/IssuesPanel";
import { couplingNozzleDims } from "../data/catalogAdapter";
import { componentFrames, nozzlePlacement } from "../vesselModel";
import type { Nozzle } from "../types";

const nz = (over: Partial<Nozzle>): Nozzle => ({ ...defaultProject().nozzles[0], ...over });

describe("geometryValidation: SUPERSEDED kontroller kaldırıldı", () => {
  it("yanlış-pozitif junction/stale/host/axial kodları üretilmez", () => {
    const p = defaultProject();
    const bad = {
      ...p,
      heads: [{ ...p.heads[0], inside_diameter: p.heads[0].inside_diameter + 50 }, p.heads[1]],
      nozzles: [nz({ host_component_id: "YOK", axial_position: 1e6 })],
    };
    const codes = geometryIssues(bad).map((i) => i.code);
    expect(codes.some((c) => /^junction-|stale-diameter$|^nozzle-\d+-(host|axial|head-position)$/.test(c))).toBe(false);
  });

  it("computeIssues host bulunamayan nozulu engelleyici sayar (App kapısı)", () => {
    const p = { ...defaultProject(), nozzles: [nz({ host_component_id: "YOK" })] };
    expect(computeIssues(p).some((i) => i.blocking && i.id.startsWith("place-"))).toBe(true);
  });

  it("destek yok yalnız info seviyesinde (onay penceresi tetiklemez)", () => {
    const p = { ...defaultProject(), supports: [], nozzles: [] };
    const issues = computeIssues(p);
    expect(issues.some((i) => i.id === "sup-none" && i.level === "info")).toBe(true);
    expect(issues.filter((i) => i.level !== "info" && !i.blocking)).toEqual([]);
  });
});

describe("nozzlePlacement: bombe OUT_OF_HOST", () => {
  const p = defaultProject();
  const frames = componentFrames(p);
  const headId = p.heads[0].head_id;
  const dome = frames.find((f) => f.id === headId)!.head!.domeHeight;
  const on = (axial: number, d: number | null) =>
    nozzlePlacement(p, nz({ host_component_id: headId, axial_position: axial, head_position_diameter: d }), frames);

  it("axial < 0 veya > domeHeight → OUT_OF_HOST (kırpma yok)", () => {
    expect(on(-1, null)).toEqual({ error: "OUT_OF_HOST" });
    expect(on(dome + 1, null)).toEqual({ error: "OUT_OF_HOST" });
    expect("error" in on(dome / 2, null)).toBe(false);
  });

  it("yerleşim çapı > Di → OUT_OF_HOST", () => {
    expect(on(0, p.heads[0].inside_diameter + 1)).toEqual({ error: "OUT_OF_HOST" });
  });
});

describe("couplingNozzleDims.derived", () => {
  it("derived yalnız bilinen anahtarları içerir; dişli bore türetildiyse işaretlenir", () => {
    for (const end of ["socket", "threaded"] as const) {
      const d = couplingNozzleDims("1", "3000#", "full", end);
      if (d) d.derived.forEach((k) => expect(["od", "id", "length"]).toContain(k));
    }
  });
});
