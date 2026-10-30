// Eksenel simetrik FEA ağı (P12). Meridyen profili componentFrames'ten türetilir; ağ yapılandırılmış
// Q8 şerididir: yol (iç yüzey) boyunca elemanlar, et boyunca nThick eleman. Korozyonlu kalınlık:
// iç yüzey normal yönde iç CA kadar ötelenir, dış yüzey t − dış CA.
// GÖSTERGE AMAÇLI — ASME onayı / mühendis değerlendirmesi değildir.
//
// Geometri notları:
//  - Bombe kubbeleri iç yüzeyden normal ofsetle (sabit et) kurulur. Elipsoid: iç elips (a, b);
//    torisferik: gerçek hamut (rk) + taç (L) yayları; düz kapak: plaka. 3D önizlemedeki dış elips
//    (a+t, b+t) yaklaşımından birkaç mm ayrışabilir.
//  - Köşeler (koni, düz kapak, kutup nozulu): kolon, iki ofset doğrunun kesişiminden geçer (tam köşe);
//    teğet sürekli kalınlık değişiminde kolon ortalama kalınlıktadır (1 elemanlık geçiş).
//  - Ağ sıklaştırma: her bölüt sınırında ±2,5·√(R·t) içinde h≈t/2, uzakta ≈0,5·√(R·t);
//    eğrilikte h ≤ 0,15·ρ.

import type { ComponentFrame } from "../geometryContract";
import type { Head, VesselProject } from "../types";
import { componentFrames, nozzlePlacement } from "../vesselModel";
import type { FeaComponentKind, FeaJunction, FeaLine, FeaMesh, FeaOptions } from "./types";

type P2 = [number, number];

interface Seg {
  id: string;
  kind: FeaComponentKind;
  f: (t: number) => P2; // iç (nominal) yüzey, yol yönünde (sol → sağ)
  dIn: number;          // iç yüzeyden korozyonlu iç yüzeye (normal boyunca)
  dOut: number;         // iç yüzeyden korozyonlu dış yüzeye
}

export interface FeaModel {
  mesh: FeaMesh;
  pressure: number;
  E: number;
  nu: number;
  /** Basınç yüklü iç kenar (ξ=−1) elemanları. */
  pressureElems: number[];
  /** Açık uç kapak itkisi: eksenel çekme, eleman kenarı η=−1 (start) / η=+1 (end). */
  endLoads: { elems: number[]; edge: "start" | "end"; rIn: number; dir: number }[];
  axisNodes: number[];
  fixUzNode: number;
  warnings: string[];
}

const E_DEFAULT = 200000;
const NU_DEFAULT = 0.3;

const sub = (a: P2, b: P2): P2 => [a[0] - b[0], a[1] - b[1]];
const len = (v: P2) => Math.hypot(v[0], v[1]);
const lerpSeg = (a: P2, b: P2) => (t: number): P2 => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];

function tangentOf(f: (t: number) => P2, t: number): P2 {
  const h = 1e-6;
  const t0 = Math.max(0, t - h);
  const t1 = Math.min(1, t + h);
  const d = sub(f(t1), f(t0));
  const l = len(d) || 1;
  return [d[0] / l, d[1] / l];
}
/** Dışa normal: teğetin −90° dönümü (r,z düzleminde). */
const normalOf = (T: P2): P2 => [T[1], -T[0]];

function restrict(f: (t: number) => P2, t0: number, t1: number) {
  return (t: number) => f(t0 + (t1 - t0) * t);
}

/** f(t) eğrisinde r(t)=r0 olan t'yi ikiye bölme ile bulur (r monoton varsayılır). */
function solveR(f: (t: number) => P2, r0: number): number {
  let lo = 0, hi = 1;
  const rLo = f(lo)[0];
  const inc = f(hi)[0] > rLo;
  for (let i = 0; i < 60; i++) {
    const m = (lo + hi) / 2;
    const r = f(m)[0];
    if ((r < r0) === inc) lo = m; else hi = m;
  }
  return (lo + hi) / 2;
}

// ── Bombe bölütleri (sağ bombe: ekvator → kutup; sol bombe yol için ters çevrilir) ──

/** Ekvator yerel kubbe eğrileri: dönüş [r, zl] (zl ≥ 0 kubbe yönünde), parametre ekvator→kutup. */
function domeCurves(h: Head, a: number, dome: number, warnings: string[]): { f: (t: number) => P2; tag: string }[] {
  if (h.type === "torispherical") {
    const di = 2 * a;
    const L = h.crown_radius ?? di;
    const rk = h.knuckle_radius ?? 0.06 * di;
    const q = (L - rk) ** 2 - (a - rk) ** 2;
    if (L > rk && a > rk && q > 0) {
      const zc = -Math.sqrt(q);
      const psiB = Math.acos((a - rk) / (L - rk));
      return [
        { tag: "knuckle", f: (t) => { const p = psiB * t; return [a - rk + rk * Math.cos(p), rk * Math.sin(p)]; } },
        { tag: "crown", f: (t) => { const p = psiB + (Math.PI / 2 - psiB) * t; return [L * Math.cos(p), zc + L * Math.sin(p)]; } },
      ];
    }
    warnings.push(`${h.head_id}: torisferik R/r geçersiz — elipsoid yaklaşımı kullanıldı.`);
  }
  const b = dome > 0 ? dome : a / 2;
  return [{ tag: "dome", f: (t) => { const u = (t * Math.PI) / 2; return [a * Math.cos(u), b * Math.sin(u)]; } }];
}

type PoleNozzle = { tag: string; rn: number; dIn: number; dOut: number; length: number };

function headSegments(f: ComponentFrame, h: Head, pole: PoleNozzle | null, warnings: string[]): Seg[] {
  const hd = f.head!;
  const left = hd.side === "left";
  const a = left ? f.rInEnd : f.rInStart;
  const dir = left ? -1 : 1;
  const eq = hd.equatorZ;
  const ca = Math.max(h.internal_corrosion_allowance ?? 0, 0);
  const t = h.nominal_thickness;
  const base = { id: h.head_id, kind: "head" as const, dIn: ca, dOut: t };
  // Sağ bombe sırası: düz flanş → kubbe (ekvator→kutup) → [nozul boynu]
  const out: Seg[] = [];
  if (hd.sf > 0) {
    const z0 = left ? eq + hd.sf : eq - hd.sf; // flanşın kabuk tarafı
    out.push({ ...base, f: lerpSeg([a, z0], [a, eq]) });
  }
  const toGlobal = (g: (t: number) => P2) => (t: number): P2 => { const [r, zl] = g(t); return [r, eq + dir * zl]; };
  let curves: ((t: number) => P2)[];
  if (h.type === "flat" || hd.domeHeight <= 0) {
    curves = [(t) => [a * (1 - t), 0]];
  } else {
    curves = domeCurves(h, a, hd.domeHeight, warnings).map((c) => c.f);
  }
  if (pole) {
    // Kubbeyi delik yarıçapında kes (r monoton azalır).
    const kept: ((t: number) => P2)[] = [];
    for (const c of curves) {
      const r0 = c(0)[0], r1 = c(1)[0];
      if (r1 >= pole.rn) { kept.push(c); continue; }
      if (r0 > pole.rn) kept.push(restrict(c, 0, solveR(c, pole.rn)));
      break;
    }
    curves = kept;
  }
  for (const c of curves) out.push({ ...base, f: toGlobal(c) });
  if (pole && curves.length > 0) {
    const last = out[out.length - 1].f(1);
    out.push({
      id: pole.tag, kind: "nozzle", dIn: pole.dIn, dOut: pole.dOut,
      f: lerpSeg([pole.rn, last[1]], [pole.rn, last[1] + dir * pole.length]),
    });
  }
  if (!left) return out;
  // Sol bombe: yol kutup(veya boyun ucu) → ekvator → kabuk; her bölütü ters çevir.
  return out.reverse().map((s) => ({ ...s, f: (t: number) => s.f(1 - t) }));
}

function poleNozzle(project: VesselProject, frames: ComponentFrame[], f: ComponentFrame, warnings: string[]): PoleNozzle | null {
  const a = f.head!.side === "left" ? f.rInEnd : f.rInStart;
  for (const nz of project.nozzles ?? []) {
    if (nz.host_component_id !== f.id) continue;
    const pl = nozzlePlacement(project, nz, frames);
    if ("error" in pl) continue;
    if (pl.rAtAnchor > 0.5 || Math.abs(pl.axis[2]) < 0.9999) continue;
    const ca = Math.max(nz.corrosion_allowance ?? 0, 0);
    const rn = nz.inside_diameter / 2;
    const tn = nz.neck_thickness - ca;
    if (!(rn > 0) || !(tn > 0) || rn > 0.6 * a) {
      warnings.push(`${nz.tag}: kutup nozulu modellenemedi (çap/kalınlık) — atlandı.`);
      return null;
    }
    if ((nz.inside_projection ?? 0) > 0) warnings.push(`${nz.tag}: iç çıkıntı modellenmedi.`);
    if (nz.reinforcement_pad) warnings.push(`${nz.tag}: takviye pedi modellenmedi.`);
    const length = Math.max((nz.outside_projection ?? 0) + f.thickness, 3 * Math.sqrt((rn + ca) * tn));
    warnings.push(`${nz.tag}: kutup nozulu boyun ${length.toFixed(0)} mm, kör flanş itkisiyle modellendi.`);
    return { tag: nz.tag, rn, dIn: ca, dOut: nz.neck_thickness, length };
  }
  return null;
}

function buildSegments(project: VesselProject, warnings: string[]): Seg[] {
  const frames = componentFrames(project);
  const shells = new Map(project.shell_sections.map((s) => [s.section_id, s]));
  const heads = new Map(project.heads.map((h) => [h.head_id, h]));
  const cones = new Map((project.cones ?? []).map((c) => [c.cone_id, c]));
  const segs: Seg[] = [];
  const poleTags = new Set<string>();
  for (const f of frames) {
    if (f.kind === "shell") {
      const s = shells.get(f.id)!;
      const ca = Math.max(s.internal_corrosion_allowance ?? 0, 0);
      const ce = Math.max(s.external_corrosion_allowance ?? 0, 0);
      segs.push({ id: f.id, kind: "shell", dIn: ca, dOut: f.thickness - ce, f: lerpSeg([f.rInStart, f.zStart], [f.rInEnd, f.zEnd]) });
    } else if (f.kind === "cone") {
      const c = cones.get(f.id)!;
      const ca = Math.max(c.internal_corrosion_allowance ?? 0, 0);
      segs.push({ id: f.id, kind: "cone", dIn: ca, dOut: f.thickness, f: lerpSeg([f.rInStart, f.zStart], [f.rInEnd, f.zEnd]) });
    } else {
      if (f.head?.side === "internal") {
        warnings.push(`${f.id}: zincir ortasındaki bombe modellenmedi.`);
        continue;
      }
      const pole = poleNozzle(project, frames, f, warnings);
      if (pole) poleTags.add(pole.tag);
      segs.push(...headSegments(f, heads.get(f.id)!, pole, warnings));
    }
  }
  const offAxis = (project.nozzles ?? []).filter((n) => !poleTags.has(n.tag)).length;
  if (offAxis > 0) warnings.push(`${offAxis} eksen dışı nozul eksenel simetrik modelde atlandı.`);
  if ((project.supports ?? []).length > 0) warnings.push("Destekler ve destek yükleri modellenmedi.");
  if ((project.design_conditions?.external_pressure ?? 0) > 0) warnings.push("Dış basınç modellenmedi (yalnız iç basınç).");
  warnings.push("Yalnız iç tasarım basıncı; ağırlık, sıvı yükü, rüzgâr/deprem yok.");
  return segs;
}

// ── Ayrıklaştırma ─────────────────────────────────────────────────────────

interface Table { t: Float64Array; s: Float64Array; ang: Float64Array; L: number; }
const TABLE_N = 256;

function tableOf(f: (t: number) => P2): Table {
  const t = new Float64Array(TABLE_N + 1);
  const s = new Float64Array(TABLE_N + 1);
  const ang = new Float64Array(TABLE_N + 1);
  let prev = f(0);
  for (let i = 0; i <= TABLE_N; i++) {
    t[i] = i / TABLE_N;
    const p = f(t[i]);
    if (i > 0) s[i] = s[i - 1] + len(sub(p, prev));
    const T = tangentOf(f, t[i]);
    ang[i] = Math.atan2(T[1], T[0]);
    prev = p;
  }
  // Açı sürekliliği
  for (let i = 1; i <= TABLE_N; i++) {
    while (ang[i] - ang[i - 1] > Math.PI) ang[i] -= 2 * Math.PI;
    while (ang[i] - ang[i - 1] < -Math.PI) ang[i] += 2 * Math.PI;
  }
  return { t, s, ang, L: s[TABLE_N] };
}

function interp(xs: Float64Array, ys: Float64Array, x: number): number {
  const n = xs.length - 1;
  if (x <= xs[0]) return ys[0];
  if (x >= xs[n]) return ys[n];
  let lo = 0, hi = n;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (xs[m] <= x) lo = m; else hi = m; }
  const w = (x - xs[lo]) / (xs[hi] - xs[lo] || 1);
  return ys[lo] + w * (ys[hi] - ys[lo]);
}

interface Col { p: P2; vIn: P2; vOut: P2; s: number; seg: number; pole: boolean }

/** İki ofset doğrunun kesişimi: v·n1=d1, v·n2=d2; paralelse ortalama. */
function cornerVec(n1: P2, d1: number, n2: P2, d2: number): P2 {
  const det = n1[0] * n2[1] - n1[1] * n2[0];
  if (Math.abs(det) < Math.sin((3 * Math.PI) / 180)) {
    const m: P2 = [n1[0] + n2[0], n1[1] + n2[1]];
    const l = len(m) || 1;
    const d = (d1 + d2) / 2;
    return [(m[0] / l) * d, (m[1] / l) * d];
  }
  return [(d1 * n2[1] - d2 * n1[1]) / det, (n1[0] * d2 - n2[0] * d1) / det];
}

export function buildFeaModel(project: VesselProject, opts: FeaOptions = {}): FeaModel {
  const refine = Math.max(0.25, opts.refine ?? 1);
  const warnings: string[] = [];
  const P = Math.max(project.design_conditions?.design_pressure ?? 0, 0);
  if (!(P > 0)) warnings.push("Tasarım basıncı ≤ 0 — gerilmeler sıfır.");

  // Malzeme (ilk gövde)
  const shell0 = project.shell_sections?.[0];
  const mat = shell0 ? project.materials?.find((m) => m.material_id === shell0.material_id) : undefined;
  const mAny = (mat ?? {}) as Record<string, unknown>;
  const num = (...keys: string[]) => {
    for (const k of keys) { const v = mAny[k]; if (typeof v === "number" && v > 0) return v; }
    return null;
  };
  let E = num("elastic_modulus", "elastic_modulus_mpa", "youngs_modulus", "E");
  let nu = num("poisson_ratio", "poissons_ratio", "nu");
  if (E == null || nu == null || nu >= 0.5) {
    warnings.push("E/ν malzemede yok — çelik varsayımı E=200 GPa, ν=0,3 (gerilme dağılımı E'den bağımsız, yer değiştirme bağımlı).");
    E = E ?? E_DEFAULT;
    nu = nu != null && nu < 0.5 ? nu : NU_DEFAULT;
  }

  const segs = buildSegments(project, warnings);
  if (segs.length === 0) throw new Error("Modellenecek basınç bileşeni yok.");
  for (const s of segs) {
    if (!(s.dOut - s.dIn > 0)) throw new Error(`${s.id}: korozyonlu kalınlık ≤ 0 — FEA yapılamaz.`);
  }
  for (let k = 1; k < segs.length; k++) {
    const gap = len(sub(segs[k - 1].f(1), segs[k].f(0)));
    if (gap > 0.5) throw new Error(`${segs[k - 1].id} → ${segs[k].id}: profil süreksiz (${gap.toFixed(1)} mm) — çap uyuşmazlığı.`);
  }

  const tables = segs.map((s) => tableOf(s.f));
  const offsets: number[] = [];
  let total = 0;
  for (const tb of tables) { offsets.push(total); total += tb.L; }

  // Süreksizlik noktaları (bölüt sınırları + açık uçlar)
  const thick = (k: number) => segs[k].dOut - segs[k].dIn;
  const disc: { s: number; zone: number }[] = [];
  const zoneAt = (r: number, t: number) => 2.5 * Math.sqrt(Math.max(r, t) * t);
  for (let k = 1; k < segs.length; k++) {
    const t = (thick(k - 1) + thick(k)) / 2;
    disc.push({ s: offsets[k], zone: zoneAt(segs[k].f(0)[0], t) });
  }
  const startOpen = segs[0].f(0)[0] > 1e-6;
  const endOpen = segs[segs.length - 1].f(1)[0] > 1e-6;
  if (startOpen) disc.push({ s: 0, zone: zoneAt(segs[0].f(0)[0], thick(0)) });
  if (endOpen) disc.push({ s: total, zone: zoneAt(segs[segs.length - 1].f(1)[0], thick(segs.length - 1)) });
  if (startOpen || endOpen) {
    const cyl = (startOpen && segs[0].kind !== "nozzle") || (endOpen && segs[segs.length - 1].kind !== "nozzle");
    if (cyl) warnings.push("Zincir bombesiz açık uçla bitiyor — uçta kapalı-uç itkisi uygulandı.");
  }

  // Et boyunca eleman sayısı
  let tr = 0;
  segs.forEach((s, k) => {
    const tb = tables[k];
    const rMid = Math.max(s.f(0.5)[0], 1e-6);
    tr = Math.max(tr, thick(k) / rMid);
  });
  const nT = Math.max(2, Math.round((tr > 0.1 ? 6 : 4) * refine));

  // Eleman boyu fonksiyonu h(s) (bölüt k, yerel yay s)
  function hAt(k: number, sl: number, curvH: number): number {
    const t = thick(k);
    const r = Math.max(segs[k].f(interp(tables[k].s, tables[k].t, sl))[0], t);
    const hFine = (0.5 * t) / refine;
    const hFar = Math.max(hFine, (0.5 * Math.sqrt(r * t)) / refine);
    const sg = offsets[k] + sl;
    let h = hFar;
    for (const d of disc) {
      const x = Math.abs(sg - d.s);
      const w = x <= d.zone ? 0 : x >= 2 * d.zone ? 1 : (x - d.zone) / d.zone;
      h = Math.min(h, hFine + w * (hFar - hFine));
    }
    return Math.min(h, curvH);
  }

  // Her bölüt için köşe düğüm konumları (yay boyu)
  const cornerS: number[][] = [];
  let nElemPath = 0;
  segs.forEach((s, k) => {
    const tb = tables[k];
    // yoğunluk integrali ∫ ds/h
    const dens = new Float64Array(TABLE_N + 1);
    for (let i = 1; i <= TABLE_N; i++) {
      const ds = tb.s[i] - tb.s[i - 1];
      const dAng = Math.abs(tb.ang[i] - tb.ang[i - 1]);
      const rho = dAng > 1e-12 ? ds / dAng : Infinity;
      const curvH = (0.15 * rho) / refine;
      const sm = (tb.s[i] + tb.s[i - 1]) / 2;
      dens[i] = dens[i - 1] + ds / hAt(k, sm, curvH);
    }
    const N = Math.max(1, Math.ceil(dens[TABLE_N] - 1e-9));
    const arr: number[] = [];
    for (let i = 0; i <= N; i++) arr.push(interp(dens, tb.s, (i / N) * dens[TABLE_N]));
    cornerS.push(arr);
    nElemPath += N;
  });
  if (nElemPath * nT > 60000) warnings.push(`Ağ büyük (${nElemPath * nT} eleman) — çözüm yavaş olabilir.`);

  // Kolonlar (kuadratik indeks: köşe, orta, köşe, ...)
  const cols: Col[] = [];
  const colAt = (k: number, sl: number): { p: P2; n: P2 } => {
    const t = interp(tables[k].s, tables[k].t, sl);
    return { p: segs[k].f(t), n: normalOf(tangentOf(segs[k].f, t)) };
  };
  segs.forEach((sg, k) => {
    const cs = cornerS[k];
    for (let i = 0; i < cs.length; i++) {
      if (i === 0 && k > 0) {
        // Paylaşılan sınır kolonu — önceki bölütün son kolonu köşe çözümüyle güncellenir.
        const prev = cols[cols.length - 1];
        const a = colAt(k - 1, tables[k - 1].L).n;
        const b = colAt(k, 0).n;
        prev.vIn = cornerVec(a, segs[k - 1].dIn, b, sg.dIn);
        prev.vOut = cornerVec(a, segs[k - 1].dOut, b, sg.dOut);
        prev.seg = k;
      } else {
        const c = colAt(k, cs[i]);
        cols.push({ p: c.p, vIn: [c.n[0] * sg.dIn, c.n[1] * sg.dIn], vOut: [c.n[0] * sg.dOut, c.n[1] * sg.dOut], s: offsets[k] + cs[i], seg: k, pole: false });
      }
      if (i < cs.length - 1) {
        const sm = (cs[i] + cs[i + 1]) / 2;
        const c = colAt(k, sm);
        cols.push({ p: c.p, vIn: [c.n[0] * sg.dIn, c.n[1] * sg.dIn], vOut: [c.n[0] * sg.dOut, c.n[1] * sg.dOut], s: offsets[k] + sm, seg: k, pole: false });
      }
    }
  });
  // Yakınsayan köşe (iç köşe dışbükey, dış köşe içbükey — ör. kutup nozulu): dış köşe noktası
  // komşu bölütün içine düşer; komşu kolonlar köşe vektörüne doğru harmanlanır (kolonlar kesişmez).
  for (let I = 2; I < cols.length - 1; I += 2) {
    const k = cols[I].seg;
    if (cols[I - 1].seg === k) continue;
    const c = cols[I];
    const Tp = tangentOf(segs[k - 1].f, 1);
    const Tn = tangentOf(segs[k].f, 0);
    const sides: { proj: number; dirSign: number }[] = [
      { proj: -(c.vOut[0] * Tp[0] + c.vOut[1] * Tp[1]), dirSign: -1 },
      { proj: c.vOut[0] * Tn[0] + c.vOut[1] * Tn[1], dirSign: 1 },
    ];
    for (const sd of sides) {
      if (sd.proj <= 1e-9) continue;
      const Lb = 2.5 * sd.proj;
      for (let m = I + sd.dirSign; m >= 0 && m < cols.length; m += sd.dirSign) {
        const x = Math.abs(cols[m].s - c.s);
        if (x >= Lb) break;
        const w = 1 - x / Lb;
        const o = cols[m];
        o.vIn = [(1 - w) * o.vIn[0] + w * c.vIn[0], (1 - w) * o.vIn[1] + w * c.vIn[1]];
        o.vOut = [(1 - w) * o.vOut[0] + w * c.vOut[0], (1 - w) * o.vOut[1] + w * c.vOut[1]];
      }
    }
  }
  // Köşe / kalınlık geçişi kolonuna komşu orta kolonlar: ofset vektörü iki köşe kolonunun
  // ortalaması (orta düğüm kenarın ortasında kalır → Jacobian pozitif).
  for (let I = 2; I < cols.length - 1; I += 2) {
    const c = cols[I];
    if (cols[I - 1].seg === cols[I + 1].seg) continue;
    for (const m of [I - 1, I + 1]) {
      const o = cols[m === I - 1 ? I - 2 : I + 2];
      cols[m].vIn = [(c.vIn[0] + o.vIn[0]) / 2, (c.vIn[1] + o.vIn[1]) / 2];
      cols[m].vOut = [(c.vOut[0] + o.vOut[0]) / 2, (c.vOut[1] + o.vOut[1]) / 2];
    }
  }
  if (!startOpen) cols[0].pole = true;
  if (!endOpen) cols[cols.length - 1].pole = true;

  // Düğümler
  const nCols = cols.length; // tek sayı
  const nE = (nCols - 1) / 2;
  const colStart = new Int32Array(nCols + 1);
  for (let I = 0; I < nCols; I++) colStart[I + 1] = colStart[I] + (I % 2 === 0 ? 2 * nT + 1 : nT + 1);
  const nNodes = colStart[nCols];
  const nodes = new Float64Array(2 * nNodes);
  const nodeId = (I: number, J: number) => colStart[I] + (I % 2 === 0 ? J : J / 2);
  for (let I = 0; I < nCols; I++) {
    const c = cols[I];
    const step = I % 2 === 0 ? 1 : 2;
    for (let J = 0; J <= 2 * nT; J += step) {
      const w = J / (2 * nT);
      const id = nodeId(I, J);
      let r = c.p[0] + c.vIn[0] + w * (c.vOut[0] - c.vIn[0]);
      const z = c.p[1] + c.vIn[1] + w * (c.vOut[1] - c.vIn[1]);
      if (c.pole || Math.abs(r) < 1e-9) r = 0;
      nodes[2 * id] = r;
      nodes[2 * id + 1] = z;
    }
  }

  // Elemanlar
  const elems = new Uint32Array(nE * nT * 8);
  const elemComponent: string[] = [];
  const elemColumn = new Uint32Array(nE * nT);
  for (let e = 0; e < nE; e++) {
    const I0 = 2 * e, Im = 2 * e + 1, I1 = 2 * e + 2;
    const comp = segs[cols[Im].seg].id;
    for (let j = 0; j < nT; j++) {
      const q = (e * nT + j) * 8;
      elems[q] = nodeId(I0, 2 * j);
      elems[q + 1] = nodeId(I0, 2 * j + 2);
      elems[q + 2] = nodeId(I1, 2 * j + 2);
      elems[q + 3] = nodeId(I1, 2 * j);
      elems[q + 4] = nodeId(I0, 2 * j + 1);
      elems[q + 5] = nodeId(Im, 2 * j + 2);
      elems[q + 6] = nodeId(I1, 2 * j + 1);
      elems[q + 7] = nodeId(Im, 2 * j);
      elemComponent.push(comp);
      elemColumn[e * nT + j] = e;
    }
  }

  // Çizgiler ve birleşimler
  const pt = (I: number, J: number): [number, number] => { const id = nodeId(I, J); return [nodes[2 * id], nodes[2 * id + 1]]; };
  const lines: FeaLine[] = [];
  const junctions: FeaJunction[] = [];
  for (let c = 0; c <= nE; c++) {
    const I = 2 * c;
    const segIdx = c < nE ? cols[I + 1].seg : cols[I - 1].seg;
    lines.push({ s: cols[I].s, a: pt(I, 0), b: pt(I, 2 * nT), component: segs[segIdx].id });
    if (c > 0 && c < nE) {
      const L = segs[cols[I - 1].seg], R = segs[cols[I + 1].seg];
      if (L.id !== R.id) {
        const t = ((L.dOut - L.dIn) + (R.dOut - R.dIn)) / 2;
        junctions.push({ s: cols[I].s, a: pt(I, 0), b: pt(I, 2 * nT), left: L.id, right: R.id, zone: zoneAt(cols[I].p[0], t) });
      }
    }
  }
  const componentKind: Record<string, FeaComponentKind> = {};
  for (const s of segs) componentKind[s.id] = s.kind;

  // Yükler / sınır şartları
  const pressureElems: number[] = [];
  for (let e = 0; e < nE; e++) pressureElems.push(e * nT);
  const endLoads: FeaModel["endLoads"] = [];
  if (startOpen) {
    const T = tangentOf(segs[0].f, 0);
    endLoads.push({ elems: Array.from({ length: nT }, (_, j) => j), edge: "start", rIn: pt(0, 0)[0], dir: T[1] >= 0 ? -1 : 1 });
  }
  if (endOpen) {
    const T = tangentOf(segs[segs.length - 1].f, 1);
    endLoads.push({ elems: Array.from({ length: nT }, (_, j) => (nE - 1) * nT + j), edge: "end", rIn: pt(nCols - 1, 0)[0], dir: T[1] >= 0 ? 1 : -1 });
  }
  const axisNodes: number[] = [];
  for (let i = 0; i < nNodes; i++) if (nodes[2 * i] === 0) axisNodes.push(i);
  const fixUzNode = nodeId(2 * Math.floor(nE / 2), 0);

  const mesh: FeaMesh = { nodes, elems, nodesPerElem: 8, elemComponent, lines, elemColumn, junctions, componentKind, nThick: nT };
  return { mesh, pressure: P, E, nu, pressureElems, endLoads, axisNodes, fixUzNode, warnings };
}
