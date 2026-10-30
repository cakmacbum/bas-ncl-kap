// İmalat resmini ana iş parçacığında üretip indirir (CAD worker gerekmez).
import type { VesselProject } from "../types";
import { drawingToDxf } from "./dxf";
import { buildDrawing } from "./model";
import { drawingToSvg } from "./svg";

export type DrawingFormat = "drawing-svg" | "drawing-dxf";
export const isDrawingFormat = (f: string): f is DrawingFormat => f === "drawing-svg" || f === "drawing-dxf";

export function exportDrawing(project: VesselProject, fmt: DrawingFormat): void {
  const m = buildDrawing(project);
  const svg = fmt === "drawing-svg";
  const blob = new Blob([svg ? drawingToSvg(m) : drawingToDxf(m)], { type: svg ? "image/svg+xml" : "application/dxf" });
  const name = (project.project_number || "kap").replace(/[^\w.-]+/g, "_");
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${name}-imalat-resmi.${svg ? "svg" : "dxf"}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
