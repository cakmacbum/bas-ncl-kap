// Div.2 Part 5 (5.5.2.2) gerilme linearizasyonu — SCL (stress classification line) üzerinden.
// Yöntem: kalınlık boyunca parçalı-lineer enterpolantın tam integrali.
//   membran  σm = (1/t)·∫σ ds
//   eğilme   σb0 = (6/t²)·∫σ·(t/2 − s) ds   (iç yüzey s=0'da +σb0, dış yüzeyde −σb0)
//   tepe     σF(s) = σ(s) − σm − σb0·(1 − 2s/t)   (yüzeylerde raporlanır)
// Eşdeğer gerilme: von Mises (varsayılan) veya Tresca (gerilme şiddeti), tensör bileşenleri
// [σr, σθ, σz, τrz] üzerinden hesaplanır (bileşen bazlı ayrıştırma, sonra eşdeğer).
// GÖSTERGE AMAÇLI — ASME onayı / mühendis değerlendirmesi değildir.

import { sampleScl } from "./sampleScl";
import { vonMises } from "./solver";
import type { FeaResult, SclSample } from "./types";

export type Tensor = [number, number, number, number]; // σr, σθ, σz, τrz
export type EquivMethod = "vonMises" | "tresca";

export interface Linearized {
  thickness: number;
  membrane: Tensor;
  /** İç yüzeydeki (s=0) eğilme tensörü; dış yüzeyde işareti ters. */
  bending: Tensor;
  /** İç / dış yüzeydeki tepe (kalan) tensör. */
  peakInner: Tensor;
  peakOuter: Tensor;
}

export interface LinearizedEquiv {
  /** Membran eşdeğeri: Pm veya PL (sınıflandırmaya göre). */
  membrane: number;
  /** Yalnız eğilme eşdeğeri (iç yüzey). */
  bending: number;
  /** Membran + eğilme, iç ve dış yüzey (PL+Pb veya PL+Pb+Q). */
  mbInner: number;
  mbOuter: number;
  /** Toplam (tepe dahil) iç / dış yüzey. */
  totalInner: number;
  totalOuter: number;
  /** Tepe bileşeni eşdeğeri, iç / dış yüzey. */
  peakInner: number;
  peakOuter: number;
}

const pick = (s: SclSample, c: number) => (c === 0 ? s.sr : c === 1 ? s.st : c === 2 ? s.sz : s.trz);

/** ∫ f·g ds, f ve g parçalı lineer (düğüm değerleri) → segment başına tam. */
function integrate(s: number[], f: number[], g: number[]): number {
  let acc = 0;
  for (let i = 0; i + 1 < s.length; i++) {
    const h = s[i + 1] - s[i];
    acc += h * ((f[i] * g[i]) / 3 + (f[i] * g[i + 1] + f[i + 1] * g[i]) / 6 + (f[i + 1] * g[i + 1]) / 3);
  }
  return acc;
}

/** SCL örneklerini (s: 0..t) membran + eğilme + tepe tensörlerine ayırır. NaN içeren örnek → null. */
export function linearize(samples: SclSample[]): Linearized | null {
  if (samples.length < 2) return null;
  if (samples.some((x) => !Number.isFinite(x.sr + x.st + x.sz + x.trz))) return null;
  const s = samples.map((x) => x.s);
  const t = s[s.length - 1] - s[0];
  if (!(t > 0)) return null;
  const ones = s.map(() => 1);
  const arm = s.map((v) => t / 2 - (v - s[0]));
  const membrane: Tensor = [0, 0, 0, 0];
  const bending: Tensor = [0, 0, 0, 0];
  const peakInner: Tensor = [0, 0, 0, 0];
  const peakOuter: Tensor = [0, 0, 0, 0];
  const last = samples.length - 1;
  for (let c = 0; c < 4; c++) {
    const v = samples.map((x) => pick(x, c));
    membrane[c] = integrate(s, v, ones) / t;
    bending[c] = (6 / (t * t)) * integrate(s, v, arm);
    peakInner[c] = v[0] - membrane[c] - bending[c];
    peakOuter[c] = v[last] - membrane[c] + bending[c];
  }
  return { thickness: t, membrane, bending, peakInner, peakOuter };
}

/** Tensör → eşdeğer gerilme. Tresca: en büyük asal fark (σθ asal, r-z düzlemi 2B asal). */
export function equivalent(t: Tensor, method: EquivMethod = "vonMises"): number {
  const [sr, st, sz, trz] = t;
  if (method === "vonMises") return vonMises(sr, st, sz, trz);
  const mean = (sr + sz) / 2, rad = Math.hypot((sr - sz) / 2, trz);
  const p = [mean + rad, mean - rad, st];
  return Math.max(...p) - Math.min(...p);
}

const add = (a: Tensor, b: Tensor, k = 1): Tensor => [a[0] + k * b[0], a[1] + k * b[1], a[2] + k * b[2], a[3] + k * b[3]];

export function equivalents(l: Linearized, method: EquivMethod = "vonMises"): LinearizedEquiv {
  const mbI = add(l.membrane, l.bending, 1);
  const mbO = add(l.membrane, l.bending, -1);
  return {
    membrane: equivalent(l.membrane, method),
    bending: equivalent(l.bending, method),
    mbInner: equivalent(mbI, method),
    mbOuter: equivalent(mbO, method),
    totalInner: equivalent(add(mbI, l.peakInner), method),
    totalOuter: equivalent(add(mbO, l.peakOuter), method),
    peakInner: equivalent(l.peakInner, method),
    peakOuter: equivalent(l.peakOuter, method),
  };
}

// ── SCL konumları + sınıflandırma ──────────────────────────────────────────

export type SclRole = "mid" | "junctionLeft" | "junctionRight";

export interface SclSpec {
  id: string;
  label: string;
  role: SclRole;
  component: string;
  s: number;
  a: [number, number];
  b: [number, number];
}

export interface LimitCheck {
  name: string; // ör. "Pm", "PL", "PL+Pb", "PL+Pb+Q"
  value: number;
  limit: number;
  ratio: number;
  pass: boolean;
}

export interface SclResult {
  spec: SclSpec;
  lin: Linearized | null;
  eq: LinearizedEquiv | null;
  checks: LimitCheck[];
  /** Sınıflandırma açıklaması (bu SCL'de membran/eğilme hangi kategoriye yazıldı). */
  classification: string;
}

export const CLASSIFICATION_NOTE =
  "Sınıflandırma varsayımı: bileşen ortası SCL'de membran = Pm (genel birincil membran, ≤ S), eğilme = Pb (Pm+Pb ≤ 1,5S). " +
  "Birleşim SCL'lerinde (iki yan) membran = PL (yerel birincil, ≤ 1,5S) kabul edilir; eğilme birincil/ikincil ayrıştırılmaz, " +
  "PL+Pb+Q olarak ≤ 3S (SPS) ile karşılaştırılır (muhafazakâr). Tepe (F) yorulma içindir, limit kontrolüne girmez. " +
  "Nozul/destek/eksen dışı yükler modelde yoktur. Gösterge amaçlı — ASME onayı değildir.";

const SCL_POINTS = 41;

/** Ağ bilgisinden (lines/junctions) SCL konumlarını üretir: her bileşen ortası + her birleşimin iki yanı. */
export function sclSpecs(res: FeaResult): SclSpec[] {
  const mesh = res.mesh;
  const lines = mesh.lines ?? [];
  const specs: SclSpec[] = [];
  if (lines.length < 2) return specs;
  // Çizgi k'nın ait olduğu bileşen: k < son ise lines[k].component, son çizgi için bir öncekinin bileşeni.
  const compOf = (k: number) => lines[Math.min(k, lines.length - 2)].component;
  const mk = (k: number, id: string, label: string, role: SclRole): SclSpec => ({
    id, label, role, component: compOf(k), s: lines[k].s, a: lines[k].a, b: lines[k].b,
  });
  const nearest = (target: number, ok: (k: number) => boolean): number => {
    let best = -1, bd = Infinity;
    for (let k = 0; k < lines.length; k++) {
      if (!ok(k)) continue;
      const d = Math.abs(lines[k].s - target);
      if (d < bd) { bd = d; best = k; }
    }
    return best;
  };

  const comps: string[] = [];
  for (let k = 0; k < lines.length - 1; k++) if (!comps.includes(lines[k].component)) comps.push(lines[k].component);
  for (const id of comps) {
    const idx: number[] = [];
    for (let k = 0; k < lines.length - 1; k++) if (lines[k].component === id) idx.push(k);
    const sA = lines[idx[0]].s, sB = lines[idx[idx.length - 1] + 1].s;
    const k = nearest((sA + sB) / 2, (q) => q >= idx[0] && q <= idx[idx.length - 1] + 1);
    if (k >= 0) specs.push(mk(k, `mid:${id}`, `${id} orta`, "mid"));
  }

  for (const j of mesh.junctions ?? []) {
    const thick = Math.hypot(j.b[0] - j.a[0], j.b[1] - j.a[1]);
    const d = Math.max(thick, j.zone / 5); // ≈ 0,5·√(R·t) — süreksizlik bölgesinin içinde, birleşim çizgisinin dışında
    const leftK = nearest(j.s - d, (q) => lines[q].s < j.s - 1e-6 && compOf(q) === j.left);
    const rightK = nearest(j.s + d, (q) => lines[q].s > j.s + 1e-6 && compOf(q) === j.right);
    if (leftK >= 0) specs.push(mk(leftK, `jl:${j.left}|${j.right}`, `${j.left}│${j.right} sol (${j.left})`, "junctionLeft"));
    if (rightK >= 0) specs.push(mk(rightK, `jr:${j.left}|${j.right}`, `${j.left}│${j.right} sağ (${j.right})`, "junctionRight"));
  }
  return specs;
}

const chk = (name: string, value: number, limit: number): LimitCheck => ({
  name, value, limit, ratio: limit > 0 ? value / limit : Infinity, pass: value <= limit * (1 + 1e-9),
});

/** Tek SCL için linearizasyon + sınırlar (S yoksa kontrol listesi boş). */
export function evaluateScl(
  res: FeaResult, spec: SclSpec, S: number | null, method: EquivMethod = "vonMises", n = SCL_POINTS,
): SclResult {
  const lin = linearize(sampleScl(res, spec.a, spec.b, n));
  if (!lin) return { spec, lin: null, eq: null, checks: [], classification: "SCL ağ dışında kaldı" };
  const eq = equivalents(lin, method);
  const checks: LimitCheck[] = [];
  const mbMax = Math.max(eq.mbInner, eq.mbOuter);
  let classification: string;
  if (spec.role === "mid") {
    classification = "Pm + Pb";
    if (S != null) { checks.push(chk("Pm", eq.membrane, S)); checks.push(chk("Pm+Pb", mbMax, 1.5 * S)); }
  } else {
    classification = "PL ve PL+Pb+Q";
    if (S != null) { checks.push(chk("PL", eq.membrane, 1.5 * S)); checks.push(chk("PL+Pb+Q", mbMax, 3 * S)); }
  }
  return { spec, lin, eq, checks, classification };
}

export function evaluateAll(res: FeaResult, S: number | null, method: EquivMethod = "vonMises"): SclResult[] {
  if (!res.converged) return [];
  return sclSpecs(res).map((sp) => evaluateScl(res, sp, S, method));
}
