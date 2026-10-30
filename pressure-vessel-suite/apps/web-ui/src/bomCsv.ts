import type { BomPayload } from "./types";

const q = (v: string | number | null | undefined) => {
  const s = v === null || v === undefined ? "" : String(v);
  return /[";\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

/** BOM + maliyet CSV (noktalı virgül ayraç — TR Excel; UTF-8 BOM). Boş kütle = üretilemedi. */
export function bomToCsv(bom: BomPayload): string {
  const rows: (string | number | null)[][] = [
    ["Parça", "Malzeme", "Ölçü", "Adet", "Birim kütle (kg)", "Toplam kütle (kg)", "Not"],
    ...bom.lines.map((l) => [l.part, l.material, l.dimensions, l.qty, l.unit_mass_kg, l.total_mass_kg, l.note]),
    ["TOPLAM", "", "", "", "", bom.total_mass_kg, bom.mass_complete ? "" : "EKSİK - bazı parçaların kütlesi üretilemedi"],
    [],
    ["Maliyet", "Dayanak", "Tutar (EUR)"],
    ...bom.cost.items.map((i) => [i.item, i.basis, i.cost_eur]),
    ["TOPLAM", bom.cost.status === "OK" ? "" : `Hesaplanmadı (${bom.cost.status})`, bom.cost.total_eur],
    ...bom.cost.missing.map((m) => ["Eksik girdi", m, ""]),
  ];
  return "﻿" + rows.map((r) => r.map(q).join(";")).join("\r\n");
}

export function downloadBomCsv(bom: BomPayload, name: string) {
  const blob = new Blob([bomToCsv(bom)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${name}-bom.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
