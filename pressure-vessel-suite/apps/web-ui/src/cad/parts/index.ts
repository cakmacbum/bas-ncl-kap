// Parça kayıt defteri (D06 sahipliği). Projeyi varlık başına iş listesine çevirir:
// her iş = seçilebilir tek varlık (partId `${kind}:${id}`), kararlı cache anahtarı ve build kapanışı.
// Worker bu listeyi sırayla koşturur; build null dönerse parça atlanır.
import type { Shape3D } from "replicad";
import type {
  BuildWarning,
  Catalogs,
  ComponentFrame,
  Level,
  MeshPart,
  PartCtx,
  PartModule,
} from "../../geometryContract";
import type { Nozzle, Support, VesselProject } from "../../types";
import { stableHash } from "../cache";
// D04 birleşince: import { componentFrames } from "../../vesselModel";
import { componentFrames } from "../framesShim";
import { buildChainSolid, type ChainComponent } from "./shellChain";
import { flangedNozzle } from "./flangedNozzle";
import { coupling } from "./coupling";
import { manway } from "./manway";
import { saddle } from "./saddle";
import { skirt } from "./skirt";
import { legs } from "./legs";

export { componentFrames };

export const MESH_TOLERANCE: Record<Level, { tolerance: number; angularTolerance: number }> = {
  preview: { tolerance: 1.0, angularTolerance: 0.3 },
  exact: { tolerance: 0.2, angularTolerance: 0.1 },
};

/** D07 katalog adaptörü gelene kadar boş katalog (parçalar CATALOG_MISS verir). */
export const emptyCatalogs: Catalogs = {
  pipe: () => undefined,
  flange: () => undefined,
  coupling: () => undefined,
};

const NOZZLE_MODULES: Record<string, PartModule<Nozzle>> = {
  flanged: flangedNozzle,
  slip_on: flangedNozzle,
  pad_reinforced: flangedNozzle,
  coupling,
  socket_welded: coupling,
  manway,
};

const SUPPORT_MODULES: Record<Support["type"], PartModule<Support>> = {
  saddle,
  skirt,
  leg: legs,
};

export interface PartJob {
  partId: string;
  kind: MeshPart["kind"];
  /** stableHash(params + frame + level) */
  key: string;
  build(warn: (w: BuildWarning) => void): Shape3D | null;
}

export interface PartPlan {
  frames: ComponentFrame[];
  jobs: PartJob[];
  warnings: BuildWarning[];
}

function chainComponent(p: VesselProject, f: ComponentFrame): ChainComponent | undefined {
  if (f.kind === "shell") return p.shell_sections.find((s) => s.section_id === f.id);
  if (f.kind === "cone") return p.cones.find((c) => c.cone_id === f.id);
  return p.heads.find((h) => h.head_id === f.id);
}

export function planParts(project: VesselProject, level: Level, catalogs: Catalogs = emptyCatalogs): PartPlan {
  const frames = componentFrames(project);
  const warnings: BuildWarning[] = [];
  const jobs: PartJob[] = [];
  const orientation = project.orientation === "vertical" ? "vertical" : "horizontal";
  const ctxBase = { level, catalogs, orientation, frames } as const;

  for (let i = 0; i + 1 < frames.length; i++) {
    const a = frames[i];
    const b = frames[i + 1];
    if (Math.abs(a.rInEnd - b.rInStart) > 0.5) {
      warnings.push({
        partId: `${b.kind}:${b.id}`,
        code: "DIAMETER_MISMATCH",
        message: `${a.id} → ${b.id} iç çap uyuşmuyor (${(2 * a.rInEnd).toFixed(1)} ≠ ${(2 * b.rInStart).toFixed(1)} mm)`,
      });
    }
  }

  // Gövde zinciri
  for (const f of frames) {
    const partId = `${f.kind}:${f.id}`;
    if (f.head?.side === "internal") {
      warnings.push({ partId, code: "INTERNAL_HEAD", message: `${f.id} zincir içinde; çizilmedi` });
      continue;
    }
    const comp = chainComponent(project, f);
    jobs.push({
      partId,
      kind: f.kind,
      key: stableHash({ partId, comp, f, level }),
      build: () => buildChainSolid(f, comp),
    });
  }

  // Nozullar (D07). Yerleşim D04 `nozzlePlacement(project, nz, frames)` ile doldurulacak.
  for (const nz of project.nozzles ?? []) {
    const mod = NOZZLE_MODULES[nz.nozzle_type];
    if (!mod) continue;
    const frame = frames.find((f) => f.id === nz.host_component_id) ?? null;
    const partId = `nozzle:${nz.tag}`;
    jobs.push({
      partId,
      kind: "nozzle",
      key: stableHash({ partId, nz, frame, level }),
      build: (warn) => mod.build(nz, frame, { ...ctxBase, warn } satisfies PartCtx),
    });
  }

  // Destekler (D08)
  for (const s of project.supports ?? []) {
    const mod = SUPPORT_MODULES[s.type];
    if (!mod) continue;
    const frame = s.host_component_id ? frames.find((f) => f.id === s.host_component_id) ?? null : null;
    const partId = `support:${s.support_id}`;
    jobs.push({
      partId,
      kind: "support",
      key: stableHash({ partId, s, frame, frames, level }),
      build: (warn) => mod.build(s, frame, { ...ctxBase, warn } satisfies PartCtx),
    });
  }

  return { frames, jobs, warnings };
}

/** Worker dışı saf fonksiyon (test/doğrulama): gövde zinciri katıları, cache'siz. OCCT başlatılmış olmalı. */
export function buildShellChainShapes(
  project: VesselProject,
  level: Level = "preview",
): { partId: string; shape: Shape3D }[] {
  const out: { partId: string; shape: Shape3D }[] = [];
  for (const job of planParts(project, level).jobs) {
    if (job.kind === "nozzle" || job.kind === "support") continue;
    const shape = job.build(() => {});
    if (shape) out.push({ partId: job.partId, shape });
  }
  return out;
}
