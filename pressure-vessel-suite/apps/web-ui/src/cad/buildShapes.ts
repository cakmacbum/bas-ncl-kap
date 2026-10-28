// Worker'dan ayrılmış saf build döngüsü (test edilebilir): cache'li katı kurulumu + kalıcı uyarılar.
// Uyarılar anahtarla cache'lenir; cache isabetinde job.build çalışmaz ama uyarı yeniden eklenir.
import type { Shape3D } from "replicad";
import type { BuildWarning, Level, MeshPart } from "../geometryContract";
import type { VesselProject } from "../types";
import type { ShapeCache } from "./cache";
import { planParts } from "./parts";

export interface BuiltPart { partId: string; kind: MeshPart["kind"]; key: string; shape: Shape3D }

export interface BuildCaches {
  shapes: ShapeCache<Shape3D>;
  warnings: Map<string, BuildWarning[]>;
}

export async function buildShapes(
  project: VesselProject,
  level: Level,
  cancelled: () => boolean,
  caches: BuildCaches,
  onUsed: (keys: Set<string>) => void,
  yieldFn: () => Promise<void> = () => Promise.resolve(),
): Promise<{ parts: BuiltPart[]; warnings: BuildWarning[] } | null> {
  const plan = planParts(project, level);
  const warnings = [...plan.warnings];
  const parts: BuiltPart[] = [];
  const used = new Set<string>();
  for (const job of plan.jobs) {
    if (cancelled()) return null;
    used.add(job.key);
    let shape = caches.shapes.get(job.key);
    if (!shape) {
      const jobWarnings: BuildWarning[] = [];
      try {
        shape = job.build((w) => jobWarnings.push(w)) ?? undefined;
      } catch (err) {
        jobWarnings.push({
          partId: job.partId,
          code: "BOOLEAN_FAILED",
          message: `${job.partId} kurulamadı: ${err instanceof Error ? err.message : String(err)}`,
        });
        shape = undefined;
      }
      if (shape) {
        caches.shapes.set(job.key, shape);
        caches.warnings.set(job.key, jobWarnings);
      }
      warnings.push(...jobWarnings);
      await yieldFn(); // daha yeni istek gelebilsin
    } else {
      warnings.push(...(caches.warnings.get(job.key) ?? []));
    }
    if (shape) parts.push({ partId: job.partId, kind: job.kind, key: job.key, shape });
  }
  onUsed(used);
  return { parts, warnings };
}

/** Katı cache'inden düşen anahtarların uyarılarını da temizler. */
export function sweepWarnings(warnings: Map<string, BuildWarning[]>, keep: Set<string>): void {
  for (const k of warnings.keys()) if (!keep.has(k)) warnings.delete(k);
}
