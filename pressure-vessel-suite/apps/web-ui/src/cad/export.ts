// D08 — dışa aktarma: STEP = partId adlı katılardan oluşan compound, STL = ikili (binary).
// Worker (cad.worker.ts runExport) ve testler buradan çağırır. Dosya adı: proje adı + tarih.
import { exportSTEP, makeCompound, type Shape3D } from "replicad";
import type { VesselProject } from "../types";
import { MESH_TOLERANCE } from "./parts";

export interface NamedShape {
  partId: string;
  shape: Shape3D;
}

function safeName(s: string): string {
  return (s || "model").replace(/[^\w.-]+/g, "_").slice(0, 80);
}

/** `<proje_adi>_YYYY-AA-GG.<ext>` */
export function exportFilename(project: Pick<VesselProject, "project_name" | "project_number">, ext: "step" | "stl", now = new Date()): string {
  const base = safeName(project.project_name || project.project_number);
  return `${base}_${now.toISOString().slice(0, 10)}.${ext}`;
}

/** exportSTEP şekilleri tüketmez (yalnız XCAF belgesine referans verir). */
export function stepBlob(parts: NamedShape[]): Blob {
  return exportSTEP(
    parts.map((p) => ({ shape: p.shape, name: p.partId, color: "#9aa3ab" })),
    { unit: "mm", modelUnit: "mm" },
  );
}

export function stlBlob(parts: NamedShape[]): Blob {
  const compound = makeCompound(parts.map((p) => p.shape.clone()));
  try {
    return compound.blobSTL({ binary: true, ...MESH_TOLERANCE.exact });
  } finally {
    compound.delete();
  }
}
