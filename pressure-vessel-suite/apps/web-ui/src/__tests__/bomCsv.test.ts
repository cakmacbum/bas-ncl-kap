import { describe, expect, it } from "vitest";
import { bomToCsv } from "../bomCsv";
import type { BomPayload } from "../types";

const bom: BomPayload = {
  lines: [
    { part: "Gövde S1", material_id: "M", material: "SA-516", dimensions: "Ø1000", qty: 1, unit_mass_kg: 10, total_mass_kg: 10, note: "" },
    { part: "Eyer", material_id: "M", material: "SA-516", dimensions: "W200", qty: 1, unit_mass_kg: null, total_mass_kg: null, note: "yok; \"x\"" },
  ],
  total_mass_kg: 10, mass_complete: false, warnings: [],
  cost: { status: "INCOMPLETE", total_eur: null, items: [], missing: ["NDT bedeli"] },
};

describe("bomToCsv", () => {
  const csv = bomToCsv(bom);
  it("UTF-8 BOM ve noktalı virgül", () => {
    expect(csv.startsWith("﻿Parça;")).toBe(true);
  });
  it("eksik kütle boş bırakılır, uydurulmaz; not tırnaklanır", () => {
    expect(csv).toContain('Eyer;SA-516;W200;1;;;"yok; ""x"""');
  });
  it("eksik toplam ve eksik girdi görünür", () => {
    expect(csv).toContain("EKSİK");
    expect(csv).toContain("Eksik girdi;NDT bedeli");
  });
});
