// Kap geometrisinin paylaşılan türetimi — 2D şema, 3D önizleme ve ölçü etiketleri
// bu tek kaynaktan beslenir.
//
// K2: Ölçüler yalnızca project data'dan gelir; mesh/CAD'den ÖLÇÜLMEZ.
// K1: Burada mühendislik formülü yoktur — yalnızca görselleştirme geometrisi.
//     Kalınlık/MAWP gibi kod hesapları backend'deki `code-*` paketlerine aittir.

import type { ComponentReference, Cone, Head, Nozzle, ShellSection } from "./types";

/** Bombe derinliği (düz flanş dahil, mm). */
export function headDepth(di: number, type: string, sf: number): number {
  switch (type) {
    case "hemispherical": return di / 2 + sf;
    case "elliptical":    return di / 4 + sf;
    case "torispherical": return di / 6 + sf;
    case "flat":          return sf; // düz kapak — neredeyse sıfır derinlik
    default:              return di / 4 + sf;
  }
}

/** Bombenin kubbe yüksekliği (düz flanş hariç, mm) — 3D profil için. */
export function headDomeHeight(di: number, type: string): number {
  switch (type) {
    case "hemispherical": return di / 2;
    case "elliptical":    return di / 4;
    case "torispherical": return di / 6;
    case "flat":          return 0;
    default:              return di / 4;
  }
}

export interface Pt2 {
  r: number; // eksene uzaklık (mm)
  z: number; // eksen boyunca konum (mm)
}

/**
 * Bombe kubbesinin yarı profili — ekvatordan (r=R, z=0) kutba (r=0, z=h).
 * `dir` +1 sağ bombe (kubbe +Z), -1 sol bombe (kubbe -Z).
 */
function domeProfile(
  R: number,
  type: string,
  dir: 1 | -1,
  segments = 24,
): Pt2[] {
  const h = headDomeHeight(R * 2, type);
  const pts: Pt2[] = [];

  if (h <= 0) {
    // Düz kapak: ekvatordan eksene düz plaka
    pts.push({ r: R, z: 0 });
    pts.push({ r: 0, z: 0 });
    return pts.map((p) => ({ r: p.r, z: p.z * dir }));
  }

  // Elips/küre yayı: r = R·cos(u), z = h·sin(u), u: 0 → π/2
  for (let i = 0; i <= segments; i++) {
    const u = (i / segments) * (Math.PI / 2);
    pts.push({ r: R * Math.cos(u), z: h * Math.sin(u) * dir });
  }
  return pts;
}

/**
 * Kabın tam kesit profili — LatheGeometry ile döndürülünce et kalınlıklı
 * gövde + iki bombe verir.
 *
 * Eksen: Z. Gövde z∈[0, L]; sol bombe z<0, sağ bombe z>L (CAD ile aynı yerleşim).
 * Profil kapalıdır: dış yüzey (sol kutup → sağ kutup) + iç yüzey (geri dönüş).
 */
export function vesselProfile(
  shell: ShellSection,
  leftHead: Head,
  rightHead: Head,
): Pt2[] {
  const t = Math.max(shell.nominal_thickness, 0.5);
  const ri = (shell.inside_diameter ?? 0) / 2 || 1;
  const ro = ri + t;
  const L = Math.max(shell.tangent_length, 1);
  const sfL = Math.max(leftHead.straight_flange_length ?? 0, 0);
  const sfR = Math.max(rightHead.straight_flange_length ?? 0, 0);

  // Dış yüzey: sol kutup → sol ekvator → gövde → sağ ekvator → sağ kutup
  const leftRi = Math.max(leftHead.inside_diameter / 2, 0.5);
  const rightRi = Math.max(rightHead.inside_diameter / 2, 0.5);
  const leftRo = leftRi + Math.max(leftHead.nominal_thickness, 0.5);
  const rightRo = rightRi + Math.max(rightHead.nominal_thickness, 0.5);
  const leftOuter = domeProfile(leftRo, leftHead.type, -1).reverse(); // kutuptan ekvatora
  const rightOuter = domeProfile(rightRo, rightHead.type, 1);

  const outer: Pt2[] = [
    ...leftOuter.map((p) => ({ r: p.r, z: p.z - sfL })),
    { r: ro, z: 0 },
    { r: ro, z: L },
    ...rightOuter.map((p) => ({ r: p.r, z: p.z + L + sfR })),
  ];

  // İç yüzey: aynı yol, kalınlık kadar içeride, ters yönde
  const leftInner = domeProfile(leftRi, leftHead.type, -1).reverse();
  const rightInner = domeProfile(rightRi, rightHead.type, 1);

  const inner: Pt2[] = [
    ...leftInner.map((p) => ({ r: p.r, z: p.z - sfL + Math.max(leftHead.nominal_thickness, 0.5) })),
    { r: ri, z: 0 },
    { r: ri, z: L },
    ...rightInner.map((p) => ({ r: p.r, z: p.z + L + sfR - Math.max(rightHead.nominal_thickness, 0.5) })),
  ];

  // Kapalı kesit: dış ileri + iç geri
  return [...outer, ...inner.reverse()];
}

/** Zincirdeki tüm basınç taşıyan elemanların görsel yarı profilini üretir. */
export function vesselProfileChain(
  shells: ShellSection[],
  heads: Head[],
  cones: Cone[],
  sequence: ComponentReference[],
): Pt2[] {
  const byId = {
    shell: new Map(shells.map((x) => [x.section_id, x])),
    head: new Map(heads.map((x) => [x.head_id, x])),
    cone: new Map(cones.map((x) => [x.cone_id, x])),
  };
  const outer: Pt2[] = [];
  const inner: Pt2[] = [];
  let z = 0;
  sequence.forEach((ref, index) => {
    const first = index === 0;
    const last = index === sequence.length - 1;
    if (ref.component_type === "shell") {
      const item = byId.shell.get(ref.component_id);
      if (!item) return;
      const ri = Math.max(item.inside_diameter ?? 1, 1) / 2;
      const t = Math.max(item.nominal_thickness, 0.5);
      const L = Math.max(item.tangent_length, 1);
      outer.push({ r: ri + t, z }, { r: ri + t, z: z + L });
      inner.push({ r: ri, z }, { r: ri, z: z + L });
      z += L;
    } else if (ref.component_type === "cone") {
      const item = byId.cone.get(ref.component_id);
      if (!item) return;
      const t = Math.max(item.nominal_thickness, 0.5);
      const rLarge = item.large_diameter / 2 + t;
      const rSmall = item.small_diameter / 2 + t;
      outer.push({ r: rLarge, z }, { r: rSmall, z: z + item.length });
      inner.push({ r: item.large_diameter / 2, z }, { r: item.small_diameter / 2, z: z + item.length });
      z += item.length;
    } else {
      const item = byId.head.get(ref.component_id);
      if (!item) return;
      const ri = Math.max(item.inside_diameter / 2, 0.5);
      const t = Math.max(item.nominal_thickness, 0.5);
      const sf = Math.max(item.straight_flange_length ?? 0, 0);
      const h = headDomeHeight(item.inside_diameter, item.type);
      const dome = domeProfile(ri + t, item.type, first ? -1 : 1);
      const domeInner = domeProfile(ri, item.type, first ? -1 : 1);
      // Each sequence item occupies [z, z + headDepth]. The left head runs
      // pole-to-equator and then its straight flange; the right head runs
      // flange-to-equator and then pole. This keeps the following component
      // attached at the shared tangent plane instead of leaving an axial gap.
      const domeOffset = first ? h : sf;
      const shifted = dome.map((p) => ({ r: p.r, z: z + p.z + domeOffset }));
      const shiftedInner = domeInner.map((p) => ({ r: p.r, z: z + p.z + domeOffset }));
      if (first) {
        outer.push(...shifted.reverse());
        inner.push(...shiftedInner.reverse());
        if (sf > 0) {
          outer.push({ r: ri + t, z: z + h + sf });
          inner.push({ r: ri, z: z + h + sf });
        }
      } else if (last) {
        if (sf > 0) {
          outer.push({ r: ri + t, z }, { r: ri + t, z: z + sf });
          inner.push({ r: ri, z }, { r: ri, z: z + sf });
        }
        outer.push(...shifted);
        inner.push(...shiftedInner);
      }
      z += headDepth(item.inside_diameter, item.type, sf);
    }
  });
  return [...outer, ...inner.reverse()];
}

/** Kabın toplam boyu (bombeler dahil, mm). */
export function overallLength(
  shell: ShellSection,
  leftHead: Head,
  rightHead: Head,
): number {
  return (
    shell.tangent_length +
    headDepth(leftHead.inside_diameter, leftHead.type, leftHead.straight_flange_length ?? 0) +
    headDepth(rightHead.inside_diameter, rightHead.type, rightHead.straight_flange_length ?? 0)
  );
}

// ── Nozul yerleşimi ────────────────────────────────────────────────────────
// Backend `packages/nozzles/src/nozzles/position.py` ile AYNI üç koordinat
// (z, θ, α) ve aynı yüzey-normali mantığı. Önizleme ile kesin CAD aynı yeri
// göstersin diye buradaki formüller oradakini birebir izler.

export interface NozzlePlacement {
  /** Yüzeydeki çıpa noktası (mm) — three.js ekseni: kap ekseni Z. */
  position: [number, number, number];
  /** Nozul ekseni (birim vektör) — α eğimi dahil. */
  axis: [number, number, number];
  hostType: "shell" | "head";
}

function normalize(v: [number, number, number]): [number, number, number] {
  const n = Math.hypot(v[0], v[1], v[2]);
  return n < 1e-9 ? [1, 0, 0] : [v[0] / n, v[1] / n, v[2] / n];
}

export function nozzlePlacement(
  nozzle: Nozzle,
  shell: ShellSection,
  heads: Head[],
): NozzlePlacement | null {
  const theta = (nozzle.circumferential_angle * Math.PI) / 180;
  const alpha = (nozzle.inclination_angle * Math.PI) / 180;

  // ── Gövde üzerinde (position.py: calculate_nozzle_position_on_shell)
  if (nozzle.host_component_id === shell.section_id) {
    const R = (shell.inside_diameter ?? 0) / 2;
    return {
      position: [R * Math.cos(theta), R * Math.sin(theta), nozzle.axial_position],
      axis: normalize([
        Math.cos(theta) * Math.cos(alpha),
        Math.sin(theta) * Math.cos(alpha),
        Math.sin(alpha),
      ]),
      hostType: "shell",
    };
  }

  // ── Bombe üzerinde (position.py: calculate_nozzle_position_on_head)
  const idx = heads.findIndex((h) => h.head_id === nozzle.host_component_id);
  if (idx < 0) return null;
  const head = heads[idx];
  const isLeft = idx === 0;

  const R = head.inside_diameter / 2;
  const a = R;
  const b = headDomeHeight(head.inside_diameter, head.type) || R / 2;

  // Merkez açısı φ — position.py ile aynı iki dallı mantık:
  //   yerleşim çapı verildiyse r = d/2, φ = asin(r/a);
  //   verilmediyse axial_position bombe tepesinden mesafe.
  let phi: number;
  const dPos = nozzle.head_position_diameter ?? 0;
  if (dPos > 0) {
    const r = dPos / 2;
    // Bombe sınırının dışındaysa çizilmez (K4: sessizce kırpma yok).
    if (r > a) return null;
    phi = a > 0 ? Math.asin(Math.max(-1, Math.min(1, r / a))) : 0;
  } else {
    phi =
      b > 0 && nozzle.axial_position <= b
        ? Math.acos(Math.max(-1, Math.min(1, 1 - nozzle.axial_position / b)))
        : 0;
  }

  const x = a * Math.sin(phi) * Math.cos(theta);
  const y = a * Math.sin(phi) * Math.sin(theta);
  const zLocal = b * Math.cos(phi);

  // Elipsoid yüzey normali: (x/a², y/a², z/b²) normalize + α eğimi
  let nx = x / (a * a);
  let ny = y / (a * a);
  let nz = zLocal / (b * b);
  const nm = Math.hypot(nx, ny, nz);
  if (nm > 0) {
    nx = (nx / nm) * Math.cos(alpha);
    ny = (ny / nm) * Math.cos(alpha);
    nz = (nz / nm) * Math.cos(alpha) + Math.sin(alpha);
  } else {
    nx = 0; ny = 0; nz = 1;
  }

  // Yerel → global (vessel_builder._head_position_to_global ile aynı):
  //   sağ bombe z = L + z_local ; sol bombe z = -z_local (normal z de ters)
  const sf = head.straight_flange_length ?? 0;
  const zGlobal = isLeft ? -(zLocal + sf) : shell.tangent_length + zLocal + sf;

  return {
    position: [x, y, zGlobal],
    axis: normalize([nx, ny, isLeft ? -nz : nz]),
    hostType: "head",
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
