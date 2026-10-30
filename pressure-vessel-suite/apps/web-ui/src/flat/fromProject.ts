import type { VesselProject } from "../types";
import type { FlatPart } from "./shapes";
import { coneSector, headPetal, nozzleCut, shellCourse, type FlatResult } from "./templates";

export interface FlatOptions { weldGap: number; petals: number }
export interface FlatEntry { id: string; part?: FlatPart; skipped?: string }

const wrap = (id: string, r: FlatResult): FlatEntry => (r.ok ? { id, part: r.part } : { id, skipped: r.reason });

/** Proje → açınım parçaları. Üretilemeyen parça gizlenmez, gerekçesiyle listelenir (K4). */
export function buildFlatParts(p: VesselProject, o: FlatOptions): FlatEntry[] {
  const out: FlatEntry[] = [];
  for (const s of p.shell_sections) {
    const id = s.inside_diameter ?? (s.outside_diameter != null ? s.outside_diameter - 2 * s.nominal_thickness : null);
    out.push(id == null ? { id: s.section_id, skipped: "İç/dış çap yok." } : wrap(s.section_id, shellCourse(s.section_id, id, s.nominal_thickness, s.tangent_length, o.weldGap)));
  }
  for (const c of p.cones)
    out.push(wrap(c.cone_id, coneSector(c.cone_id, c.large_diameter, c.small_diameter, c.length, c.nominal_thickness, c.half_apex_angle)));
  for (const h of p.heads) {
    if (h.type === "flat") { out.push({ id: h.head_id, skipped: "Düz kapak: açınım gerekmez (disk)." }); continue; }
    out.push(wrap(h.head_id, headPetal(h.head_id, {
      type: h.type, insideD: h.inside_diameter, t: h.nominal_thickness,
      crownR: h.crown_radius, knuckleR: h.knuckle_radius, crownDepth: h.crown_depth,
      standardFD: h.torispherical_geometry === "standard_asme_fd",
    }, o.petals)));
  }
  for (const n of p.nozzles) {
    const host = p.shell_sections.find((s) => s.section_id === n.host_component_id);
    if (!host) { out.push({ id: n.tag, skipped: "Yalnız silindirik gövdeye bağlı nozul için şablon üretilir." }); continue; }
    if (n.inclination_angle) { out.push({ id: n.tag, skipped: "Eğimli nozul şablonu desteklenmiyor." }); continue; }
    const hid = host.inside_diameter ?? (host.outside_diameter != null ? host.outside_diameter - 2 * host.nominal_thickness : null);
    if (hid == null) { out.push({ id: n.tag, skipped: "Gövde çapı yok." }); continue; }
    out.push(wrap(n.tag, nozzleCut(n.tag, {
      runInsideD: hid, runT: host.nominal_thickness, branchOD: n.outside_diameter, branchT: n.neck_thickness,
      crownLength: n.outside_projection + host.nominal_thickness / 2,
    })));
  }
  return out;
}
