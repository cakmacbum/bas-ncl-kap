// Step 03 geometri sözleşmesi (D00) — YALNIZ tipler. Birim mm. Mantık yok.
import type { Shape3D } from "replicad";
import type { HeadTypeT, Nozzle, VesselProject } from "./types";

export type { HeadTypeT, Nozzle, VesselProject };

export type Vec3 = [number, number, number];

export type FrameKind = "head" | "shell" | "cone";

export interface ComponentFrame {
  kind: FrameKind;
  id: string;
  index: number; // sequence indeksi
  zStart: number;
  zEnd: number; // zEnd(i) === zStart(i+1)
  rInStart: number;
  rInEnd: number;
  rOutStart: number;
  rOutEnd: number;
  thickness: number;
  head?: { side: "left" | "right" | "internal"; type: HeadTypeT; domeHeight: number; sf: number; equatorZ: number };
  cone?: { largeAtStart: boolean };
}

export interface NozzlePlacement {
  position: Vec3;
  normal: Vec3;
  axis: Vec3;
  hostKind: FrameKind;
  frame: ComponentFrame;
  rAtAnchor: number;
}

export type PlacementResult =
  | NozzlePlacement
  | { error: "HOST_NOT_FOUND" | "OUT_OF_HOST" | "INTERNAL_HEAD" };

export interface Selection {
  kind: "shell" | "cone" | "head" | "nozzle" | "support";
  id: string;
}

export type Level = "preview" | "exact";

export interface MeshPart {
  partId: string; // `${kind}:${id}`
  kind: Selection["kind"];
  positions: Float32Array;
  normals: Float32Array;
  indices: Uint32Array;
  edges?: Float32Array;
}

export type BuildWarningCode =
  | "HOST_NOT_FOUND"
  | "OUT_OF_HOST"
  | "CATALOG_MISS"
  | "BOOLEAN_FAILED"
  | "INTERNAL_HEAD"
  | "DIAMETER_MISMATCH";

export interface BuildWarning {
  partId?: string;
  code: BuildWarningCode;
  message: string;
}

export type MainToWorker =
  | { type: "init" }
  | { type: "build"; reqId: number; project: VesselProject; level: Level }
  | { type: "export"; reqId: number; project: VesselProject; format: "step" | "stl" };

export type WorkerToMain =
  | { type: "ready" }
  | { type: "loading"; progress: number }
  | { type: "result"; reqId: number; level: Level; meshes: MeshPart[]; warnings: BuildWarning[]; ms: number }
  | { type: "export-result"; reqId: number; blob: Blob; filename: string }
  | { type: "error"; reqId: number; message: string };

// ---- Katalog tipleri (§4) ----
export type FlangeClass = "CL150" | "CL300" | "CL600" | "CL900" | "CL1500" | "CL2500";
export type CouplingRating = "3000#" | "6000#";
export type CouplingForm = "full" | "half" | "weldolet";

export interface PipeSize {
  nps: string;
  label: string;
  dn: number;
  od: number;
  walls: Record<string, number | null>;
}

export interface FlangeRow {
  nps: string;
  dn: number;
  class: number | string;
  outside_diameter: number;
  thickness: number;
  raised_face_diameter: number;
  raised_face_height: number;
  hub_base_diameter: number;
  hub_weld_diameter: number;
  length_wn: number;
  length_so: number;
  bore_so: number;
  bolt_circle_diameter: number;
  bolt_count: number;
  bolt_hole_diameter: number;
  bolt_diameter: number;
}

export interface CouplingRow {
  nps: string;
  dn: number;
  rating: 3000 | 6000;
  form: CouplingForm;
  end: "socket" | "threaded";
  body_od: number;
  top_od: number | null;
  length: number;
  socket_bore: number | null;
  socket_depth: number | null;
  bore: number;
  chamfer: number;
}

export interface Catalogs {
  pipe(nps: string): PipeSize | undefined;
  flange(nps: string, cls: FlangeClass): FlangeRow | undefined;
  coupling(nps: string, rating: CouplingRating, form: CouplingForm): CouplingRow | undefined;
}

// ---- Parça modülü ----
export interface PartCtx {
  level: Level;
  placement?: NozzlePlacement;
  catalogs: Catalogs;
  orientation: "horizontal" | "vertical";
  frames: ComponentFrame[];
}

export interface PartModule<P> {
  build(params: P, frame: ComponentFrame | null, ctx: PartCtx): Shape3D;
  cutter?(params: P, frame: ComponentFrame, ctx: PartCtx): Shape3D;
}
