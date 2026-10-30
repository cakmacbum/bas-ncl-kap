// GEÇİCİ İSKELET — P03 bu dosyanın gövdesini gerçek analitik alanla değiştirir; imza sabit kalır.
import type { VesselProject } from "../types";
import type { StressField } from "./types";

export function buildStressField(project: VesselProject): StressField {
  const shell = project.shell_sections?.[0];
  const P = project.design_conditions?.design_pressure ?? 0;
  const D = shell?.inside_diameter ?? 1;
  const t = Math.max(0.1, shell?.nominal_thickness ?? 1);
  const hoop = (P * D) / (2 * t);
  const axial = hoop / 2;
  const vm = Math.sqrt(hoop * hoop - hoop * axial + axial * axial);
  return { at: () => ({ vm, hoop, axial, zone: "membrane" }), allowable: null, maxVm: vm };
}
