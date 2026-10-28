// GEÇİCİ SHIM (D06) — D04 `componentFrames`'i vesselModel.ts'e yazınca bu dosya silinir ve
// parts/index.ts'teki tek import satırı `from "../vesselModel"` olarak değiştirilir.
// Sözleşme D00 §1 algoritmasının birebir yerel kopyası. Birim mm.
import type { ComponentFrame } from "../geometryContract";
import type { Cone, Head, ShellSection, VesselProject } from "../types";

/** D00 §1.3 — kubbe yüksekliği tek kaynak (crown_depth → torisferik R,r → oransal). */
export function headDomeHeight(di: number, type: string, head?: Partial<Head>): number {
  if (head?.crown_depth != null && head.crown_depth > 0) return head.crown_depth;
  if (type === "torispherical" && head?.crown_radius && head?.knuckle_radius) {
    const R = head.crown_radius;
    const r = head.knuckle_radius;
    const h = R - Math.sqrt((R - r) ** 2 - (di / 2 - r) ** 2);
    if (Number.isFinite(h) && h > 0) return h;
  }
  switch (type) {
    case "hemispherical": return di / 2;
    case "torispherical": return di / 6;
    case "flat": return 0;
    default: return di / 4;
  }
}

type Resolved =
  | { kind: "shell"; id: string; index: number; c: ShellSection }
  | { kind: "cone"; id: string; index: number; c: Cone }
  | { kind: "head"; id: string; index: number; c: Head };

export function componentFrames(p: VesselProject): ComponentFrame[] {
  let seq = p.component_sequence ?? [];
  if (seq.length === 0) {
    seq = [];
    if (p.heads[0]) seq.push({ component_type: "head", component_id: p.heads[0].head_id });
    if (p.shell_sections[0]) seq.push({ component_type: "shell", component_id: p.shell_sections[0].section_id });
    if (p.heads[1]) seq.push({ component_type: "head", component_id: p.heads[1].head_id });
  }

  const seen = new Set<string>();
  const items: Resolved[] = [];
  seq.forEach((ref, index) => {
    const id = ref.component_id;
    if (seen.has(id)) return; // yinelenen → atla (MISSING_REF D04 chainIssues'ta)
    let r: Resolved | null = null;
    if (ref.component_type === "shell") {
      const c = p.shell_sections.find((s) => s.section_id === id);
      if (c) r = { kind: "shell", id, index, c };
    } else if (ref.component_type === "cone") {
      const c = p.cones.find((s) => s.cone_id === id);
      if (c) r = { kind: "cone", id, index, c };
    } else if (ref.component_type === "head") {
      const c = p.heads.find((s) => s.head_id === id);
      if (c) r = { kind: "head", id, index, c };
    }
    if (!r) return;
    seen.add(id);
    items.push(r);
  });

  const frames: ComponentFrame[] = [];
  let z = 0;
  items.forEach((it, i) => {
    const prev = frames[frames.length - 1];
    if (it.kind === "shell") {
      const s = it.c;
      const t = s.nominal_thickness;
      const ri = s.inside_diameter != null ? s.inside_diameter / 2
        : s.outside_diameter != null ? (s.outside_diameter - 2 * t) / 2 : 0.5;
      const L = Math.max(s.tangent_length, 1);
      frames.push({ kind: "shell", id: it.id, index: it.index, zStart: z, zEnd: z + L,
        rInStart: ri, rInEnd: ri, rOutStart: ri + t, rOutEnd: ri + t, thickness: t });
      z += L;
    } else if (it.kind === "cone") {
      const c = it.c;
      const t = c.nominal_thickness;
      const rs = c.small_diameter / 2;
      const rl = c.large_diameter / 2;
      const expanding = prev != null && Math.abs(prev.rInEnd - rs) < Math.abs(prev.rInEnd - rl);
      const rInStart = expanding ? rs : rl;
      const rInEnd = expanding ? rl : rs;
      frames.push({ kind: "cone", id: it.id, index: it.index, zStart: z, zEnd: z + c.length,
        rInStart, rInEnd, rOutStart: rInStart + t, rOutEnd: rInEnd + t, thickness: t,
        cone: { largeAtStart: !expanding } });
      z += c.length;
    } else {
      const hd = it.c;
      const t = hd.nominal_thickness;
      const Ri = hd.inside_diameter / 2;
      const h = headDomeHeight(hd.inside_diameter, hd.type, hd);
      const sf = hd.straight_flange_length ?? 0;
      const side: "left" | "right" | "internal" =
        i === 0 ? "left" : i === items.length - 1 ? "right" : "internal";
      const rInStart = side === "left" ? 0 : Ri;
      const rInEnd = side === "right" ? 0 : Ri;
      const equatorZ = side === "left" ? z + h : side === "right" ? z + sf : z + h;
      frames.push({ kind: "head", id: it.id, index: it.index, zStart: z, zEnd: z + h + sf,
        rInStart, rInEnd, rOutStart: rInStart + t, rOutEnd: rInEnd + t, thickness: t,
        head: { side, type: hd.type, domeHeight: h, sf, equatorZ } });
      z += h + sf;
    }
  });
  return frames;
}
