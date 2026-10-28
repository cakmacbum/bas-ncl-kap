// Kap geometrisinin paylaşılan türetimi — 2D şema, 3D önizleme, CAD worker ve ölçü
// etiketleri bu tek kaynaktan beslenir (D00 §1).
//
// K2: Ölçüler yalnızca project data'dan gelir; mesh/CAD'den ÖLÇÜLMEZ.
// K1: Burada mühendislik formülü yoktur — yalnızca görselleştirme geometrisi.
//     Kalınlık/MAWP gibi kod hesapları backend'deki `code-*` paketlerine aittir.
//
// Eksen: kap ekseni +Z; z=0 sol (ilk) bombenin kutbu; bileşenler sequence sırasıyla
// arka arkaya. θ +X'ten ölçülür.

import type {
  ComponentFrame, NozzlePlacement, PlacementResult, Vec3,
} from "./geometryContract";
import type {
  ComponentReference, Cone, Head, HeadTypeT, Nozzle, ShellSection, Support, VesselProject,
} from "./types";

export type { ComponentFrame, NozzlePlacement, PlacementResult };

/** Zincir türetimi için gereken proje alt kümesi (VesselProject de kabul edilir). */
export type ChainSource = Pick<VesselProject, "shell_sections" | "heads" | "cones" | "component_sequence">;

type HeadDims = Pick<Head, "crown_depth" | "crown_radius" | "knuckle_radius">;

/**
 * Bombenin kubbe yüksekliği (düz flanş hariç, mm) — TEK KAYNAK (D00 §1.3).
 * Öncelik: `crown_depth` → torisferik R,r → oransal (Di/4, Di/6, Di/2, 0).
 */
export function headDomeHeight(di: number, type: string, head?: HeadDims | null): number {
  if (head?.crown_depth != null && head.crown_depth > 0) return head.crown_depth;
  if (type === "torispherical" && head?.crown_radius && head?.knuckle_radius) {
    const R = head.crown_radius;
    const r = head.knuckle_radius;
    const q = (R - r) ** 2 - (di / 2 - r) ** 2;
    if (R > r && q >= 0) return R - Math.sqrt(q);
  }
  switch (type) {
    case "hemispherical": return di / 2;
    case "elliptical":    return di / 4;
    case "torispherical": return di / 6;
    case "flat":          return 0;
    default:              return di / 4;
  }
}

/** Bombe derinliği (düz flanş dahil, mm) = kubbe + sf. */
export function headDepth(di: number, type: string, sf: number, head?: HeadDims | null): number {
  return headDomeHeight(di, type, head) + sf;
}

// ── Zincir çerçeveleri ─────────────────────────────────────────────────────

export type ChainIssue = {
  code: "DIAMETER_MISMATCH" | "INTERNAL_HEAD" | "MISSING_REF";
  id: string;
  message: string;
};

function effectiveSequence(p: ChainSource): ComponentReference[] {
  const seq = p.component_sequence ?? [];
  if (seq.length > 0) return seq;
  const out: ComponentReference[] = [];
  if (p.heads[0]) out.push({ component_type: "head", component_id: p.heads[0].head_id });
  if (p.shell_sections[0]) out.push({ component_type: "shell", component_id: p.shell_sections[0].section_id });
  if (p.heads[1]) out.push({ component_type: "head", component_id: p.heads[1].head_id });
  return out;
}

type Resolved =
  | { kind: "shell"; index: number; item: ShellSection }
  | { kind: "cone"; index: number; item: Cone }
  | { kind: "head"; index: number; item: Head };

/** Sequence'i nesnelere çözer; bulunamayan / yinelenen referansları ayrı döner. */
function resolveSequence(p: ChainSource): { items: Resolved[]; missing: ChainIssue[] } {
  const shells = new Map(p.shell_sections.map((x) => [x.section_id, x]));
  const heads = new Map(p.heads.map((x) => [x.head_id, x]));
  const cones = new Map((p.cones ?? []).map((x) => [x.cone_id, x]));
  const seen = new Set<string>();
  const items: Resolved[] = [];
  const missing: ChainIssue[] = [];
  effectiveSequence(p).forEach((ref, index) => {
    const id = ref.component_id;
    if (seen.has(id)) {
      missing.push({ code: "MISSING_REF", id, message: `${id} sequence'te yineleniyor — atlandı.` });
      return;
    }
    const item = ref.component_type === "shell" ? shells.get(id)
      : ref.component_type === "cone" ? cones.get(id)
      : heads.get(id);
    if (!item) {
      missing.push({ code: "MISSING_REF", id, message: `${id} (${ref.component_type}) bulunamadı — atlandı.` });
      return;
    }
    seen.add(id);
    items.push({ kind: ref.component_type, index, item } as Resolved);
  });
  return { items, missing };
}

export function componentFrames(p: ChainSource): ComponentFrame[] {
  const { items } = resolveSequence(p);
  const frames: ComponentFrame[] = [];
  let z = 0;
  items.forEach((it, pos) => {
    const prev = frames[frames.length - 1];
    if (it.kind === "shell") {
      const s = it.item;
      const t = s.nominal_thickness;
      const ri = s.inside_diameter != null ? s.inside_diameter / 2
        : s.outside_diameter != null ? (s.outside_diameter - 2 * t) / 2
        : 0.5;
      const L = Math.max(s.tangent_length, 1);
      frames.push({
        kind: "shell", id: s.section_id, index: it.index,
        zStart: z, zEnd: z + L,
        rInStart: ri, rInEnd: ri, rOutStart: ri + t, rOutEnd: ri + t, thickness: t,
      });
      z += L;
    } else if (it.kind === "cone") {
      const c = it.item;
      const t = c.nominal_thickness;
      const large = c.large_diameter / 2;
      const small = c.small_diameter / 2;
      const prevR = prev?.rInEnd;
      const expanding = prevR != null && Math.abs(prevR - small) < Math.abs(prevR - large);
      const rInStart = expanding ? small : large;
      const rInEnd = expanding ? large : small;
      frames.push({
        kind: "cone", id: c.cone_id, index: it.index,
        zStart: z, zEnd: z + c.length,
        rInStart, rInEnd, rOutStart: rInStart + t, rOutEnd: rInEnd + t, thickness: t,
        cone: { largeAtStart: !expanding },
      });
      z += c.length;
    } else {
      const h = it.item;
      const t = h.nominal_thickness;
      const ri = h.inside_diameter / 2;
      const sf = Math.max(h.straight_flange_length ?? 0, 0);
      const dome = headDomeHeight(h.inside_diameter, h.type, h);
      const side = pos === 0 ? "left" : pos === items.length - 1 ? "right" : "internal";
      const rInStart = side === "left" ? 0 : ri;
      const rInEnd = side === "right" ? 0 : ri;
      const equatorZ = side === "left" ? z + dome : z + sf;
      frames.push({
        kind: "head", id: h.head_id, index: it.index,
        zStart: z, zEnd: z + dome + sf,
        rInStart, rInEnd, rOutStart: rInStart + t, rOutEnd: rInEnd + t, thickness: t,
        head: { side, type: h.type as HeadTypeT, domeHeight: dome, sf, equatorZ },
      });
      z += dome + sf;
    }
  });
  return frames;
}

/** Zincir tutarlılık uyarıları (çizimi engellemez; worker/UI uyarı olarak gösterir). */
export function chainIssues(p: ChainSource, f: ComponentFrame[]): ChainIssue[] {
  const issues: ChainIssue[] = [...resolveSequence(p).missing];
  let last: ComponentFrame | null = null;
  for (const fr of f) {
    if (fr.head?.side === "internal") {
      issues.push({ code: "INTERNAL_HEAD", id: fr.id, message: `${fr.id} zincirin ortasında — çizilmez.` });
      continue;
    }
    if (last && Math.abs(last.rInEnd - fr.rInStart) > 0.5) {
      issues.push({
        code: "DIAMETER_MISMATCH", id: fr.id,
        message: `${last.id} → ${fr.id}: iç çap ${(2 * last.rInEnd).toFixed(1)} ≠ ${(2 * fr.rInStart).toFixed(1)} mm.`,
      });
    }
    last = fr;
  }
  return issues;
}

/** Teğet datumları: sol bombe zEnd, sağ bombe zStart (bombe yoksa zincir uçları). */
export function tangentDatum(f: ComponentFrame[]): { left: number; right: number } {
  const first = f[0];
  const last = f[f.length - 1];
  return {
    left: first ? (first.head?.side === "left" ? first.zEnd : first.zStart) : 0,
    right: last ? (last.head?.side === "right" ? last.zStart : last.zEnd) : 0,
  };
}

/** Desteğin global Z'si: sol teğet datumu + location_mm (Zick). Etek location_mm kullanmaz. */
export function supportZ(sup: Pick<Support, "type" | "location_mm">, frames: ComponentFrame[]): number {
  const { left } = tangentDatum(frames);
  return sup.type === "skirt" ? left : left + sup.location_mm;
}

// ── Kesit profili ──────────────────────────────────────────────────────────

export interface Pt2 {
  r: number; // eksene uzaklık (mm)
  z: number; // eksen boyunca konum (mm)
}

/**
 * Bombe kubbesinin yarı profili — ekvatordan (r=R, z=0) kutba (r=0, z=h).
 * `dir` +1 sağ bombe (kubbe +Z), -1 sol bombe (kubbe -Z).
 */
function domeProfile(R: number, h: number, dir: 1 | -1, segments = 24): Pt2[] {
  if (h <= 0) return [{ r: R, z: 0 }, { r: 0, z: 0 }];
  const pts: Pt2[] = [];
  // Elips/küre yayı: r = R·cos(u), z = h·sin(u), u: 0 → π/2
  for (let i = 0; i <= segments; i++) {
    const u = (i / segments) * (Math.PI / 2);
    pts.push({ r: R * Math.cos(u), z: h * Math.sin(u) * dir });
  }
  return pts;
}

/**
 * Tek gövdeli kabın kesit profili (sequence boş eski çağıranlar için yedek).
 * Eksen: Z. Gövde z∈[0, L]; sol bombe z<0, sağ bombe z>L.
 */
export function vesselProfile(shell: ShellSection, leftHead: Head, rightHead: Head): Pt2[] {
  const t = Math.max(shell.nominal_thickness, 0.5);
  const ri = (shell.inside_diameter ?? 0) / 2 || 1;
  const ro = ri + t;
  const L = Math.max(shell.tangent_length, 1);
  const sfL = Math.max(leftHead.straight_flange_length ?? 0, 0);
  const sfR = Math.max(rightHead.straight_flange_length ?? 0, 0);
  const leftRi = Math.max(leftHead.inside_diameter / 2, 0.5);
  const rightRi = Math.max(rightHead.inside_diameter / 2, 0.5);
  const tL = Math.max(leftHead.nominal_thickness, 0.5);
  const tR = Math.max(rightHead.nominal_thickness, 0.5);
  const hL = headDomeHeight(leftRi * 2, leftHead.type, leftHead);
  const hR = headDomeHeight(rightRi * 2, rightHead.type, rightHead);

  const outer: Pt2[] = [
    ...domeProfile(leftRi + tL, hL + tL, -1).reverse().map((p) => ({ r: p.r, z: p.z - sfL })),
    { r: ro, z: 0 },
    { r: ro, z: L },
    ...domeProfile(rightRi + tR, hR + tR, 1).map((p) => ({ r: p.r, z: p.z + L + sfR })),
  ];
  const inner: Pt2[] = [
    ...domeProfile(leftRi, hL, -1).reverse().map((p) => ({ r: p.r, z: p.z - sfL })),
    { r: ri, z: 0 },
    { r: ri, z: L },
    ...domeProfile(rightRi, hR, 1).map((p) => ({ r: p.r, z: p.z + L + sfR })),
  ];
  return [...outer, ...inner.reverse()];
}

/** Zincirdeki tüm basınç taşıyan elemanların görsel yarı profili (componentFrames üzerinden). */
export function vesselProfileChain(
  shells: ShellSection[],
  heads: Head[],
  cones: Cone[],
  sequence: ComponentReference[],
): Pt2[] {
  const frames = componentFrames({ shell_sections: shells, heads, cones, component_sequence: sequence });
  const outer: Pt2[] = [];
  const inner: Pt2[] = [];
  for (const f of frames) {
    const t = Math.max(f.thickness, 0.5);
    if (f.kind !== "head" || !f.head) {
      outer.push({ r: f.rInStart + t, z: f.zStart }, { r: f.rInEnd + t, z: f.zEnd });
      inner.push({ r: Math.max(f.rInStart, 0.5), z: f.zStart }, { r: Math.max(f.rInEnd, 0.5), z: f.zEnd });
      continue;
    }
    const { side, domeHeight: h, sf, equatorZ } = f.head;
    if (side === "internal") continue; // çizilmez (INTERNAL_HEAD)
    const ri = Math.max(side === "left" ? f.rInEnd : f.rInStart, 0.5);
    const dir = side === "left" ? -1 : 1;
    const domeOuter = domeProfile(ri + t, h + t, dir).map((p) => ({ r: p.r, z: equatorZ + p.z }));
    const domeInner = domeProfile(ri, h, dir).map((p) => ({ r: p.r, z: equatorZ + p.z }));
    if (side === "left") {
      outer.push(...domeOuter.reverse());
      inner.push(...domeInner.reverse());
      if (sf > 0) {
        outer.push({ r: ri + t, z: f.zEnd });
        inner.push({ r: ri, z: f.zEnd });
      }
    } else {
      if (sf > 0) {
        outer.push({ r: ri + t, z: f.zStart });
        inner.push({ r: ri, z: f.zStart });
      }
      outer.push(...domeOuter);
      inner.push(...domeInner);
    }
  }
  return [...outer, ...inner.reverse()];
}

/** Kabın toplam boyu (bombeler dahil, mm). */
export function overallLength(shell: ShellSection, leftHead: Head, rightHead: Head): number {
  return (
    shell.tangent_length +
    headDepth(leftHead.inside_diameter, leftHead.type, leftHead.straight_flange_length ?? 0, leftHead) +
    headDepth(rightHead.inside_diameter, rightHead.type, rightHead.straight_flange_length ?? 0, rightHead)
  );
}

// ── Nozul yerleşimi ────────────────────────────────────────────────────────
// Backend `packages/nozzles/src/nozzles/position.py` ile aynı üç koordinat (s, θ, α).
// Çıpa iç yüzeyde; `axial_position` host zStart'ından ölçülür (bombe: tepeden).

function normalize(v: Vec3): Vec3 {
  const n = Math.hypot(v[0], v[1], v[2]);
  return n < 1e-9 ? [1, 0, 0] : [v[0] / n, v[1] / n, v[2] / n];
}

export function nozzlePlacement(
  _p: ChainSource,
  nz: Nozzle,
  frames: ComponentFrame[],
): PlacementResult {
  const frame = frames.find((f) => f.id === nz.host_component_id);
  if (!frame) return { error: "HOST_NOT_FOUND" };
  const theta = (nz.circumferential_angle * Math.PI) / 180;
  const alpha = (nz.inclination_angle * Math.PI) / 180;
  const c = Math.cos(theta);
  const sn = Math.sin(theta);

  if (frame.kind === "shell" || frame.kind === "cone") {
    const L = frame.zEnd - frame.zStart;
    const s = nz.axial_position;
    if (!(s >= 0 && s <= L) || L <= 0) return { error: "OUT_OF_HOST" }; // K4: kırpma yok
    const k = (frame.rInEnd - frame.rInStart) / L;
    const r = frame.rInStart + k * s;
    const normal = normalize([c, sn, -k]);
    const tHat = normalize([k * c, k * sn, 1]);
    const ca = Math.cos(alpha);
    const sa = Math.sin(alpha);
    const axis = normalize([
      ca * normal[0] + sa * tHat[0],
      ca * normal[1] + sa * tHat[1],
      ca * normal[2] + sa * tHat[2],
    ]);
    return { position: [r * c, r * sn, frame.zStart + s], normal, axis, hostKind: frame.kind, frame, rAtAnchor: r };
  }

  const head = frame.head;
  if (!head || head.side === "internal") return { error: "INTERNAL_HEAD" };
  const isLeft = head.side === "left";
  const zSign = isLeft ? -1 : 1;
  const a = isLeft ? frame.rInEnd : frame.rInStart;
  const b = head.domeHeight;
  const dPos = nz.head_position_diameter ?? 0;

  // Düz kapak: yerleşim çapı → r, normal ±Z.
  if (b <= 0) {
    const r = dPos > 0 ? dPos / 2 : 0;
    if (r > a) return { error: "OUT_OF_HOST" };
    const normal: Vec3 = [0, 0, zSign];
    return {
      position: [r * c, r * sn, head.equatorZ], normal, axis: normal,
      hostKind: "head", frame, rAtAnchor: r,
    };
  }

  // Merkez açısı φ — position.py ile aynı iki dallı mantık.
  let phi: number;
  if (dPos > 0) {
    const r = dPos / 2;
    if (r > a) return { error: "OUT_OF_HOST" };
    phi = a > 0 ? Math.asin(Math.max(-1, Math.min(1, r / a))) : 0;
  } else {
    phi = nz.axial_position <= b
      ? Math.acos(Math.max(-1, Math.min(1, 1 - nz.axial_position / b)))
      : 0;
  }
  const x = a * Math.sin(phi) * c;
  const y = a * Math.sin(phi) * sn;
  const zLocal = b * Math.cos(phi);

  // Elipsoid yüzey normali (x/a², y/a², z/b²) + α eğimi (mevcut davranış).
  const n0 = normalize([x / (a * a), y / (a * a), zLocal / (b * b)]);
  const ca = Math.cos(alpha);
  const ax = normalize([n0[0] * ca, n0[1] * ca, n0[2] * ca + Math.sin(alpha)]);
  return {
    position: [x, y, head.equatorZ + zSign * zLocal],
    normal: [n0[0], n0[1], zSign * n0[2]],
    axis: [ax[0], ax[1], zSign * ax[2]],
    hostKind: "head",
    frame,
    rAtAnchor: a * Math.sin(phi),
  };
}

// ── Nozul tipine göre görsel oranlar ───────────────────────────────────────
// CAD'deki `_build_nozzle_type_feature` (vessel_builder.py) ile AYNI oranlar.
// K6: Flanş ölçüleri B16.5/B16.47'den DEĞİL; yalnızca görsel temsildir.

export interface NozzleVisual {
  /** Flanş/kapak dış yarıçapı — nozul dış yarıçapının katı. */
  flangeRatio: number;
  /** Flanş kalınlığı — nozul dış yarıçapının katı. */
  flangeThicknessRatio: number;
  /** Kalınlık alt sınırı (mm) — CAD'deki `max(...)` ile aynı değer. */
  minThickness: number;
  /** Flanş boru ucundan geride otursun mu (slip-on). */
  setback: boolean;
  /** Kör kapak (manway) — akış deliği kapalı. */
  blindCover: boolean;
  /** Gövdeye yakın kısa boss (socket-weld). */
  boss: boolean;
}

export const NOZZLE_VISUAL: Record<string, NozzleVisual> = {
  flanged:        { flangeRatio: 1.6,  flangeThicknessRatio: 0.26, minThickness: 10, setback: false, blindCover: false, boss: false },
  slip_on:        { flangeRatio: 1.6,  flangeThicknessRatio: 0.26, minThickness: 10, setback: true,  blindCover: false, boss: false },
  pad_reinforced: { flangeRatio: 1.6,  flangeThicknessRatio: 0.26, minThickness: 10, setback: false, blindCover: false, boss: false },
  manway:         { flangeRatio: 1.75, flangeThicknessRatio: 0.28, minThickness: 12, setback: false, blindCover: true,  boss: false },
  socket_welded:  { flangeRatio: 1.45, flangeThicknessRatio: 0.90, minThickness: 12, setback: false, blindCover: false, boss: true },
  coupling:       { flangeRatio: 1.5,  flangeThicknessRatio: 1.20, minThickness: 20, setback: false, blindCover: false, boss: true },
};

export function nozzleVisual(nozzleType: string): NozzleVisual {
  return NOZZLE_VISUAL[nozzleType] ?? NOZZLE_VISUAL.flanged;
}
