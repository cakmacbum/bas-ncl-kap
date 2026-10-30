// Analitik gerilme alanı (P03) — GÖSTERGE AMAÇLI, ASME tasarım onayı değildir.
// Sözleşme: stress/types.ts (sabit). Birimler mm, MPa. Çerçeve: vesselModel.componentFrames
// (kap ekseni +Z, θ +X'ten). Yalnız iç tasarım basıncı; ağırlık/rüzgâr/destek yükü yok.
//
// Kaynaklar (kısa):
//  - Silindir membran σθ=P·Ri/t, σz=P·Ri/(2t) (ASME VIII-1 UG-27 ince cidar; iç yarıçap korozyonlu).
//    t/Ri>0,1 → Lamé kalın cidar, iç yüzey (Roark Table 13.5 case 1c).
//  - Koni σθ=P·r/(t·cosα), σφ=P·r/(2t·cosα) (UG-32(g) membran temeli).
//  - Dönel kabuk membranı Nφ=P·R2/2, Nθ=P·R2·(1−R2/(2R1)) (Timoshenko; Div.2 Part 4.3 bombeler):
//    elipsoid R2=a²·√(r²/a⁴+z²/b⁴), R1=R2³·b²/a⁴; torisferik taç R=L (birleşimden uzakta).
//    Torisferik hamut + taç–hamut birleşim bandı: değer üretilmez (vm=NaN, zone "unknown" = düşük güven,
//    "FEA kullanın"). Gerekçe V1: docs/validation/torispherical-knuckle.md (membran R1=rk 2–3× yüksek).
//  - Düz kapak: basit mesnetli dairesel plaka (Roark Table 11.2 case 10a); UG-34 C katsayısıyla
//    ölçeklenir (C=0,309 ≡ basit mesnet).
//  - Süreksizlik: β=1,285/√(R·t) (Div.2 Part 4.3.10, uzun silindir kiriş-temel teorisi).
//    Serbest radyal yer değiştirme farkı δ iki tarafa eşit bölünür (eşit rijitlik yaklaşımı):
//    Δσθ=±E·δ/(2R), eğilme σb≈0,293·E·δ/R; düz kapak: ankastre uç σb=1,817·P·R/t.
//    Koni birleşimi: halka yükü H=P·R·tanα/2 (Div.2 4.3.11 / VIII-1 App. 1-5).
//    Ek gerilme birleşimden e^(−βx) zarfıyla sönümlenir.
//  - Nozul: çift eksenli alanda delik kenarı Kt≈2,5 (Roark Table 17.1 / Peterson),
//    kenardan 2·d mesafede membrana sönüm; ped bölgesinde etkin kalınlık t+tp.

import type { ComponentFrame, Vec3 } from "../geometryContract";
import type { Head, Nozzle, VesselProject } from "../types";
import { componentFrames, nozzlePlacement } from "../vesselModel";
import type { StressField, StressSample, StressZone } from "./types";

const NU = 0.3;
const KT_NOZZLE = 2.5;
const C_SIMPLY_SUPPORTED = (3 * (3 + NU)) / 32; // 0,309 — UG-34 C ile eşdeğer basit mesnet
const ZONE_DECAY = 0.05; // e^(−βx) bu eşiğin altındaysa bölge membran sayılır (βx≈3)
/** Torisferik taçta, taç–hamut teğet noktasından bu kadar √(L·t) içi düşük güven (βx≈3, Div.2 4.3.10 β). */
const KNUCKLE_BAND = 2.5;

type Plane = { hoop: number; axial: number };

const vonMises = (h: number, a: number) => Math.sqrt(h * h - h * a + a * a);
const sample = (hoop: number, axial: number, zone: StressZone): StressSample => ({ vm: vonMises(hoop, axial), hoop, axial, zone });
const ZERO = (zone: StressZone): StressSample => ({ vm: 0, hoop: 0, axial: 0, zone });

function cylinder(P: number, Ri: number, t: number): Plane {
  if (t / Ri > 0.1) {
    const Ro = Ri + t;
    const den = Ro * Ro - Ri * Ri;
    return { hoop: (P * (Ro * Ro + Ri * Ri)) / den, axial: (P * Ri * Ri) / den };
  }
  return { hoop: (P * Ri) / t, axial: (P * Ri) / (2 * t) };
}

function revolution(P: number, R1: number, R2: number, t: number): Plane {
  return { hoop: ((P * R2) / t) * (1 - R2 / (2 * R1)), axial: (P * R2) / (2 * t) };
}

// ── Eleman modeli (önhesap) ────────────────────────────────────────────────

type Elem = {
  frame: ComponentFrame;
  t: number;   // korozyonlu kalınlık (≤0 → hesaplanamaz)
  ca: number;  // iç korozyon payı
  head?: Head;
  alpha: number; // koni yarı tepe açısı (rad)
};

type Side = { beta: number; hoopAdd: number; bend: number };
type Junction = { z: number; otherId: string; cyl: Side; other: Side; coneCos: number };

function headLocal(f: ComponentFrame, z: number): number {
  const h = f.head!;
  return h.side === "left" ? h.equatorZ - z : z - h.equatorZ; // >0: kubbe tarafı
}

function headRadius(f: ComponentFrame): number {
  return f.head!.side === "left" ? f.rInEnd : f.rInStart;
}

function torisphericalRadii(e: Elem, a: number): { L: number; rk: number } {
  const di = 2 * headRadius(e.frame);
  return {
    L: (e.head?.crown_radius ?? di) + e.ca,
    rk: (e.head?.knuckle_radius ?? 0.06 * di) + e.ca,
  };
}

/** Bombe ekvatorundaki membran serbest radyal yer değiştirmesi × E (E sadeleşir). */
function headEquatorDisp(P: number, e: Elem): number {
  const a = headRadius(e.frame) + e.ca;
  const t = e.t;
  const type = e.frame.head!.type;
  const b = e.frame.head!.domeHeight + e.ca;
  if (type === "hemispherical" && Math.abs(b - a) < 1e-6 * a) return ((P * a * a) / (2 * t)) * (1 - NU);
  if (type === "torispherical") {
    const { rk } = torisphericalRadii(e, a);
    return ((P * a * a) / t) * (1 - a / (2 * rk) - NU / 2);
  }
  return ((P * a * a) / t) * (1 - (a * a) / (2 * b * b) - NU / 2);
}

function elementPlane(P: number, e: Elem, r: number, z: number): { plane: Plane; inHead: boolean; offWall: boolean } {
  const f = e.frame;
  const t = e.t;
  const tol = 1.5 * f.thickness + 10;
  if (f.kind === "shell") {
    const Ri = f.rInStart + e.ca;
    return { plane: cylinder(P, Ri, t), inHead: false, offWall: Math.abs(r - (f.rInStart + f.thickness / 2)) > tol };
  }
  if (f.kind === "cone") {
    const L = f.zEnd - f.zStart;
    const ri = f.rInStart + ((f.rInEnd - f.rInStart) * (z - f.zStart)) / (L || 1);
    const c = Math.cos(e.alpha);
    const R = ri + e.ca;
    const mid = ri + f.thickness / (2 * c);
    return {
      plane: { hoop: (P * R) / (t * c), axial: (P * R) / (2 * t * c) },
      inHead: false,
      offWall: Math.abs(r - mid) * c > tol,
    };
  }
  const hd = f.head!;
  const a0 = headRadius(f);
  const a = a0 + e.ca;
  const zl = headLocal(f, z);
  if (hd.type === "flat" || hd.domeHeight <= 0) {
    if (r <= a0 && zl >= -1) {
      const C = e.head?.flat_attachment_factor ?? 0.33;
      const k = (C / C_SIMPLY_SUPPORTED) * ((3 * P) / (8 * t * t));
      const rr = Math.min(r, a);
      return {
        plane: { hoop: k * ((3 + NU) * a * a - (1 + 3 * NU) * rr * rr), axial: k * (3 + NU) * (a * a - rr * rr) },
        inHead: true,
        offWall: Math.abs(zl - f.thickness / 2) > tol,
      };
    }
    return { plane: cylinder(P, a, t), inHead: false, offWall: Math.abs(r - (a0 + f.thickness / 2)) > tol };
  }
  if (zl <= 0) {
    return { plane: cylinder(P, a, t), inHead: false, offWall: Math.abs(r - (a0 + f.thickness / 2)) > tol };
  }
  // Duvar mesafesi: mesh ile aynı elips kubbe (vesselModel.domeProfile) üzerinden.
  const b0 = hd.domeHeight;
  const u = Math.atan2(zl / b0, r / a0);
  const wall = Math.hypot(r - a0 * Math.cos(u), zl - b0 * Math.sin(u));
  const offWall = Math.abs(wall - f.thickness / 2) > tol;

  if (hd.type === "torispherical") {
    const { L, rk } = torisphericalRadii(e, a);
    const q = (L - rk) ** 2 - (a - rk) ** 2;
    if (L > rk && a > rk && q > 0) {
      const hc = L - Math.sqrt(q);
      const zc = hc - L; // taç merkezi (ekvatordan kutba doğru z)
      const sinB = (a - rk) / (L - rk);
      const zlr = (zl / b0) * hc; // geometrik kubbe yüksekliği farkı için ölçekle
      const vr = Math.hypot(r, zlr - zc);
      // V1 doğrulaması (docs/validation/torispherical-knuckle.md): hamutta membran teorisi (R1=rk) bağımsız kabuk
      // çözümünün 2–3 katı; taç–hamut birleşimine yakın taçta eğilme (≈2× membran) modellenmez. Kaynaklı kapalı
      // form yok → bu bölgede değer üretilmez (NaN, düşük güven, "FEA kullanın").
      if (vr > 0 && r / vr <= sinB) {
        const arc = L * (Math.asin(sinB) - Math.asin(Math.min(1, r / vr)));
        if (arc > KNUCKLE_BAND * Math.sqrt(L * t)) return { plane: { hoop: (P * L) / (2 * t), axial: (P * L) / (2 * t) }, inHead: true, offWall };
      }
      return { plane: { hoop: NaN, axial: NaN }, inHead: true, offWall };
    }
  }
  // Elipsoid / yarımküre (b=a → R1=R2=a).
  const b = b0 + e.ca;
  const rs = a * Math.cos(u);
  const zs = b * Math.sin(u);
  const R2 = a * a * Math.sqrt((rs * rs) / a ** 4 + (zs * zs) / b ** 4);
  const R1 = (R2 ** 3 * b * b) / a ** 4;
  return { plane: revolution(P, R1, R2, t), inHead: true, offWall };
}

// ── Nozul modeli ───────────────────────────────────────────────────────────

type NozzleModel = {
  pos: Vec3; axis: Vec3;
  rOut: number; d: number;
  tWall: number; tPad: number; rPad: number;
  neck: Plane; betaNeck: number;
  projOut: number; projIn: number;
};

function buildNozzles(project: VesselProject, frames: ComponentFrame[], P: number): NozzleModel[] {
  const out: NozzleModel[] = [];
  for (const nz of project.nozzles ?? []) {
    const pl = nozzlePlacement(project, nz as Nozzle, frames);
    if ("error" in pl) continue;
    const ca = Math.max(nz.corrosion_allowance ?? 0, 0);
    const tn = nz.neck_thickness - ca;
    const rn = nz.inside_diameter / 2 + ca;
    const hasPad = nz.reinforcement_pad && (nz.reinforcement_pad_thickness ?? 0) > 0 && (nz.reinforcement_pad_od ?? 0) > nz.outside_diameter;
    out.push({
      pos: pl.position, axis: pl.axis,
      rOut: nz.outside_diameter / 2, d: nz.outside_diameter,
      tWall: pl.frame.thickness,
      tPad: hasPad ? nz.reinforcement_pad_thickness! : 0,
      rPad: hasPad ? nz.reinforcement_pad_od! / 2 : 0,
      neck: tn > 0 && rn > 0 ? { hoop: (P * rn) / tn, axial: (P * rn) / (2 * tn) } : { hoop: 0, axial: 0 },
      betaNeck: tn > 0 && rn > 0 ? 1.285 / Math.sqrt(rn * tn) : 1,
      projOut: Math.max(nz.outside_projection ?? 0, 0) + 0.5 * nz.outside_diameter,
      projIn: Math.max(nz.inside_projection ?? 0, 0),
    });
  }
  return out;
}

/** Kt halkası: kenarda 1, 2·d'de 0 (yumuşak (1−s)² sönüm). */
const ringDecay = (s: number) => (s >= 1 ? 0 : s <= 0 ? 1 : (1 - s) * (1 - s));

// ── Ana fonksiyon ──────────────────────────────────────────────────────────

export function buildStressField(project: VesselProject): StressField {
  const P = Math.max(project.design_conditions?.design_pressure ?? 0, 0);
  const frames = componentFrames(project);
  const shells = new Map(project.shell_sections.map((s) => [s.section_id, s]));
  const heads = new Map(project.heads.map((h) => [h.head_id, h]));
  const cones = new Map((project.cones ?? []).map((c) => [c.cone_id, c]));

  const elems: Elem[] = frames.map((f) => {
    if (f.kind === "shell") {
      const s = shells.get(f.id)!;
      const ca = Math.max(s.internal_corrosion_allowance ?? 0, 0);
      return { frame: f, ca, t: f.thickness - ca - Math.max(s.external_corrosion_allowance ?? 0, 0), alpha: 0 };
    }
    if (f.kind === "cone") {
      const c = cones.get(f.id)!;
      const ca = Math.max(c.internal_corrosion_allowance ?? 0, 0);
      const L = f.zEnd - f.zStart;
      const alpha = c.half_apex_angle > 0 ? (c.half_apex_angle * Math.PI) / 180
        : Math.atan2(Math.abs(f.rInEnd - f.rInStart), L || 1);
      return { frame: f, ca, t: f.thickness - ca, alpha };
    }
    const h = heads.get(f.id)!;
    const ca = Math.max(h.internal_corrosion_allowance ?? 0, 0);
    return { frame: f, ca, t: f.thickness - ca, head: h, alpha: 0 };
  });

  // Süreksizlik birleşimleri
  const junctions: Junction[] = [];
  const betaOf = (R: number, t: number) => 1.285 / Math.sqrt(R * t);
  elems.forEach((e, i) => {
    const f = e.frame;
    if (e.t <= 0) return;
    if (f.kind === "head" && f.head && f.head.side !== "internal") {
      const a = headRadius(f) + e.ca;
      const nb = elems[f.head.side === "left" ? i + 1 : i - 1];
      const tc = f.head.sf > 0 || !nb || nb.frame.kind !== "shell" || nb.t <= 0 ? e.t : nb.t;
      const wc = ((P * a * a) / tc) * (1 - NU / 2);
      const cyl: Side = { beta: betaOf(a, tc), hoopAdd: 0, bend: 0 };
      const other: Side = { beta: betaOf(a, e.t), hoopAdd: 0, bend: 0 };
      if (f.head.type === "flat" || f.head.domeHeight <= 0) {
        cyl.hoopAdd = -wc / a;
        cyl.bend = (1.817 * P * a) / tc;
      } else {
        const delta = wc - headEquatorDisp(P, e);
        cyl.hoopAdd = -delta / (2 * a);
        other.hoopAdd = delta / (2 * a);
        cyl.bend = other.bend = (0.2928 * Math.abs(delta)) / a;
      }
      junctions.push({ z: f.head.equatorZ, otherId: f.id, cyl, other, coneCos: 1 });
    }
    if (f.kind === "cone" && e.alpha > 1e-6) {
      const c = Math.cos(e.alpha);
      for (const end of ["start", "end"] as const) {
        const nb = elems[end === "start" ? i - 1 : i + 1];
        if (!nb) continue;
        const R = (end === "start" ? f.rInStart : f.rInEnd) + e.ca;
        const otherR = end === "start" ? f.rInEnd : f.rInStart;
        const sign = R - e.ca >= otherR ? -1 : 1; // büyük uç: içe çekme (σθ azalır)
        const H = (P * R * Math.tan(e.alpha)) / 2;
        const tn = nb.t > 0 ? nb.t : e.t;
        const bn = betaOf(R, tn);
        const bc = betaOf(R / c, e.t);
        junctions.push({
          z: end === "start" ? f.zStart : f.zEnd,
          otherId: f.id,
          cyl: { beta: bn, hoopAdd: (sign * (H / 2) * 2 * bn * R) / tn, bend: (1.934 * (H / 2)) / (bn * tn * tn) },
          other: { beta: bc, hoopAdd: (sign * (H / 2) * 2 * bc * (R / c)) / e.t, bend: (1.934 * (H / 2)) / (bc * e.t * e.t) },
          coneCos: c,
        });
      }
    }
  });

  const nozzles = buildNozzles(project, frames, P);
  const hasSupports = (project.supports ?? []).length > 0;

  function nearestElem(z: number): Elem | null {
    let best: Elem | null = null;
    let bestD = Infinity;
    for (const e of elems) {
      if (e.frame.head?.side === "internal") continue;
      // Bombe dış yüzeyi kutup tarafında t kadar taşar (düz kapak plakası dahil).
      const side = e.frame.head?.side;
      const lo = e.frame.zStart - (side === "left" ? e.frame.thickness : 0);
      const hi = e.frame.zEnd + (side === "right" ? e.frame.thickness : 0);
      const d = z < lo ? lo - z : z > hi ? z - hi : 0;
      if (d < bestD || (d === bestD && e.frame.kind === "head")) { bestD = d; best = e; }
    }
    return best;
  }

  /** Kabuk (nozul hariç) gerilmesi: membran + süreksizlik. */
  function wall(r: number, z: number): { s: StressSample; offWall: boolean } | null {
    const e = nearestElem(z);
    if (!e) return null;
    if (e.t <= 0) return { s: ZERO("unknown"), offWall: false };
    const loc = elementPlane(P, e, r, z);
    let { hoop, axial } = loc.plane;
    if (!Number.isFinite(hoop)) return { s: { vm: NaN, hoop: NaN, axial: NaN, zone: "unknown" }, offWall: loc.offWall };
    let envelope = 0;
    const inDome = loc.inHead && e.frame.kind === "head";
    for (const j of junctions) {
      const otherSide = j.otherId === e.frame.id && (e.frame.kind === "cone" || inDome);
      const side = otherSide ? j.other : j.cyl;
      let x: number;
      if (otherSide && inDome) {
        const a = headRadius(e.frame);
        x = Math.hypot(a - r, Math.max(headLocal(e.frame, z), 0));
      } else {
        x = Math.abs(z - j.z) / (otherSide ? j.coneCos : 1);
      }
      const bx = side.beta * x;
      if (bx > 10) continue;
      const k = Math.exp(-bx);
      hoop += side.hoopAdd * k;
      axial += (axial >= 0 ? 1 : -1) * side.bend * k;
      if (side.hoopAdd !== 0 || side.bend !== 0) envelope = Math.max(envelope, k);
    }
    const zone: StressZone = envelope > ZONE_DECAY ? "discontinuity" : loc.inHead ? "head" : "membrane";
    return { s: sample(hoop, axial, zone), offWall: loc.offWall };
  }

  function at(p: [number, number, number]): StressSample {
    const [x, y, z] = p;
    const r = Math.hypot(x, y);

    // Nozul gövdesi / delik halkası
    let best: { k: number; m: number } | null = null;
    for (const n of nozzles) {
      const v: Vec3 = [x - n.pos[0], y - n.pos[1], z - n.pos[2]];
      const h = v[0] * n.axis[0] + v[1] * n.axis[1] + v[2] * n.axis[2];
      const rho = Math.hypot(v[0] - h * n.axis[0], v[1] - h * n.axis[1], v[2] - h * n.axis[2]);
      const wallTop = n.tWall + n.tPad + 2;
      const band = 2 * n.tWall + 10;
      if (rho <= n.rOut + 2 && (h > wallTop || h < -2) && h <= n.projOut && h >= -n.projIn - 2) {
        // Boyun: boyun membranı + birleşimden β_n ile sönen Kt etkisi
        const host = wall(Math.hypot(n.pos[0], n.pos[1]), n.pos[2]);
        const edge = host ? KT_NOZZLE * host.s.vm : 0;
        const dist = h > wallTop ? h - wallTop : -h;
        const f = Math.exp(-n.betaNeck * dist);
        const base = vonMises(n.neck.hoop, n.neck.axial);
        const scale = base > 0 ? Math.max(1, (base + (edge - base) * f) / base) : 1;
        return sample(n.neck.hoop * scale, n.neck.axial * scale, "nozzle");
      }
      if (h < -band || h > wallTop + band) continue;
      const s = Math.max(rho - n.rOut, 0) / (2 * n.d);
      if (s >= 1) continue;
      const m = n.tPad > 0 && rho <= n.rPad ? n.tWall / (n.tWall + n.tPad) : 1;
      const k = (1 + (KT_NOZZLE - 1) * ringDecay(s)) * m;
      if (!best || k > best.k) best = { k, m };
    }

    const w = wall(r, z);
    if (!w) return ZERO("unknown");
    if (best) return sample(w.s.hoop * best.k, w.s.axial * best.k, "nozzle");
    if (w.offWall) return ZERO(hasSupports ? "support" : "unknown");
    return w.s;
  }

  // maxVm: aynı alanın orta yüzey örneklemesi (elemanlar + birleşimler + nozul kenarları).
  let maxVm = 0;
  const probe = (pt: [number, number, number]) => {
    const v = at(pt).vm;
    if (Number.isFinite(v) && v > maxVm) maxVm = v;
  };
  for (const e of elems) {
    const f = e.frame;
    const N = f.kind === "head" ? 360 : 48; // hamut/birleşim tepeleri dar — bombede sık örnek
    for (let i = 0; i <= N; i++) {
      if (f.kind === "head" && f.head && f.head.side !== "internal" && f.head.domeHeight > 0) {
        const u = (i / N) * (Math.PI / 2);
        const a = headRadius(f) + f.thickness / 2;
        const b = f.head.domeHeight + f.thickness / 2;
        const zl = b * Math.sin(u);
        probe([a * Math.cos(u), 0, f.head.side === "left" ? f.head.equatorZ - zl : f.head.equatorZ + zl]);
      } else if (f.kind === "head" && f.head && f.head.side !== "internal") {
        const a = headRadius(f);
        const zl = f.thickness / 2;
        probe([(a * i) / N, 0, f.head.side === "left" ? f.head.equatorZ - zl : f.head.equatorZ + zl]);
      } else {
        const z = f.zStart + ((f.zEnd - f.zStart) * i) / N;
        const ri = f.rInStart + ((f.rInEnd - f.rInStart) * i) / N;
        probe([ri + f.thickness / 2, 0, z]);
      }
    }
  }
  for (const j of junctions) {
    const e = nearestElem(j.z);
    if (e) probe([(e.frame.kind === "head" ? headRadius(e.frame) : e.frame.rInStart) + e.frame.thickness / 2, 0, j.z]);
  }
  for (const n of nozzles) {
    // Delik kenarı: eksene dik yönde rOut kadar kaydırılmış nokta
    const ref: Vec3 = Math.abs(n.axis[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0];
    const dot = ref[0] * n.axis[0] + ref[1] * n.axis[1] + ref[2] * n.axis[2];
    const t = [ref[0] - dot * n.axis[0], ref[1] - dot * n.axis[1], ref[2] - dot * n.axis[2]];
    const tl = Math.hypot(t[0], t[1], t[2]) || 1;
    const o = n.rOut + 0.5;
    const hm = n.tWall / 2;
    probe([
      n.pos[0] + (t[0] / tl) * o + n.axis[0] * hm,
      n.pos[1] + (t[1] / tl) * o + n.axis[1] * hm,
      n.pos[2] + (t[2] / tl) * o + n.axis[2] * hm,
    ]);
  }

  const shell0 = project.shell_sections?.[0];
  const mat = shell0 ? project.materials?.find((m) => m.material_id === shell0.material_id) : undefined;
  const allowable = mat && Number.isFinite(mat.allowable_stress) && mat.allowable_stress > 0 ? mat.allowable_stress : null;

  return { at, allowable, maxVm };
}
