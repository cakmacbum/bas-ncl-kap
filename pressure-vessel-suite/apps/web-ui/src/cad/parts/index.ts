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
  NozzlePlacement,
  PartCtx,
  PartModule,
} from "../../geometryContract";
import type { Nozzle, Support, VesselProject } from "../../types";
import { stableHash } from "../cache";
import { catalogs as defaultCatalogs } from "../../data/catalogAdapter";
import { componentFrames, nozzlePlacement } from "../../vesselModel";
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

/** Boş katalog (testler / katalogsuz kullanım); varsayılan `catalogAdapter.catalogs`. */
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

export function planParts(project: VesselProject, level: Level, catalogs: Catalogs = defaultCatalogs): PartPlan {
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

  // Nozul yerleşimleri (D04 nozzlePlacement). Hata → uyarı, nozul atlanır.
  const placed: { nz: Nozzle; mod: PartModule<Nozzle>; pl: NozzlePlacement }[] = [];
  for (const nz of project.nozzles ?? []) {
    const mod = NOZZLE_MODULES[nz.nozzle_type];
    if (!mod) continue;
    const pl = nozzlePlacement(project, nz, frames);
    const partId = `nozzle:${nz.tag}`;
    if ("error" in pl) {
      const msg: Record<typeof pl.error, string> = {
        HOST_NOT_FOUND: `${nz.tag}: host bileşen "${nz.host_component_id}" bulunamadı`,
        OUT_OF_HOST: `${nz.tag}: eksenel konum host sınırları dışında (${nz.axial_position} mm)`,
        INTERNAL_HEAD: `${nz.tag}: host zincir içi bombe; nozul çizilmedi`,
      };
      warnings.push({ partId, code: pl.error, message: msg[pl.error] });
      continue;
    }
    placed.push({ nz, mod, pl });
  }

  // Gövde zinciri
  for (const f of frames) {
    const partId = `${f.kind}:${f.id}`;
    if (f.head?.side === "internal") {
      warnings.push({ partId, code: "INTERNAL_HEAD", message: `${f.id} zincir içinde; çizilmedi` });
      continue;
    }
    const comp = chainComponent(project, f);
    // exact: bu host'taki nozul delikleri kesilir (preview'da boolean yok)
    const cuts = level === "exact" ? placed.filter((x) => x.nz.host_component_id === f.id && x.mod.cutter) : [];
    jobs.push({
      partId,
      kind: f.kind,
      key: stableHash({ partId, comp, f, level, cuts: cuts.map((c) => ({ nz: c.nz, pl: c.pl })) }),
      build: (warn) => {
        let solid = buildChainSolid(f, comp);
        if (!solid) return null;
        for (const c of cuts) {
          let tool: Shape3D | null = null;
          try {
            tool = c.mod.cutter!(c.nz, f, { ...ctxBase, placement: c.pl, warn } satisfies PartCtx);
            const next = solid.cut(tool);
            solid.delete();
            solid = next;
          } catch (err) {
            warn({
              partId,
              code: "BOOLEAN_FAILED",
              message: `${c.nz.tag} deliği ${f.id} gövdesinden çıkarılamadı: ${err instanceof Error ? err.message : String(err)}`,
            });
          } finally {
            tool?.delete();
          }
        }
        return solid;
      },
    });
  }

  // Nozullar (D07)
  for (const { nz, mod, pl } of placed) {
    const partId = `nozzle:${nz.tag}`;
    jobs.push({
      partId,
      kind: "nozzle",
      key: stableHash({ partId, nz, frame: pl.frame, pl, level }),
      build: (warn) => mod.build(nz, pl.frame, { ...ctxBase, placement: pl, warn } satisfies PartCtx),
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
