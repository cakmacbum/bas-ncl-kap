// Eksenel simetrik lineer elastik FEM çözücü (P12) — saf TypeScript, bağımlılıksız.
// Eleman: 8 düğümlü serendipity dörtgen (Q8), rijitlik 3×3 Gauss, gerilme 2×2 Gauss (Barlow)
// noktalarından köşelere ekstrapolasyon + düğüm ortalaması. Çözücü: bant Cholesky (doğrudan).
// Şekil değiştirme [εr, εz, εθ, γrz]; 2π çarpanı yük ve rijitlikte sadeleşir.
// GÖSTERGE AMAÇLI — ASME onayı / mühendis değerlendirmesi değildir.

import type { VesselProject } from "../types";
import { buildFeaModel, type FeaModel } from "./mesh";
import { FEA_DISCLAIMER, type FeaOptions, type FeaResult } from "./types";

export type Progress = (phase: "mesh" | "assemble" | "factor" | "stress", fraction: number) => void;

// Q8 doğal koordinatları: 1(−1,−1) 2(1,−1) 3(1,1) 4(−1,1) 5(0,−1) 6(1,0) 7(0,1) 8(−1,0)
const XI = [-1, 1, 1, -1, 0, 1, 0, -1];
const ETA = [-1, -1, 1, 1, -1, 0, 1, 0];

export function q8Shape(xi: number, eta: number, N: Float64Array, dNdxi?: Float64Array, dNdeta?: Float64Array) {
  for (let a = 0; a < 8; a++) {
    const xa = XI[a], ea = ETA[a];
    if (a < 4) {
      N[a] = 0.25 * (1 + xi * xa) * (1 + eta * ea) * (xi * xa + eta * ea - 1);
      if (dNdxi) dNdxi[a] = 0.25 * xa * (1 + eta * ea) * (2 * xi * xa + eta * ea);
      if (dNdeta) dNdeta[a] = 0.25 * ea * (1 + xi * xa) * (xi * xa + 2 * eta * ea);
    } else if (xa === 0) {
      N[a] = 0.5 * (1 - xi * xi) * (1 + eta * ea);
      if (dNdxi) dNdxi[a] = -xi * (1 + eta * ea);
      if (dNdeta) dNdeta[a] = 0.5 * ea * (1 - xi * xi);
    } else {
      N[a] = 0.5 * (1 + xi * xa) * (1 - eta * eta);
      if (dNdxi) dNdxi[a] = 0.5 * xa * (1 - eta * eta);
      if (dNdeta) dNdeta[a] = -eta * (1 + xi * xa);
    }
  }
}

const G3 = [-Math.sqrt(0.6), 0, Math.sqrt(0.6)];
const W3 = [5 / 9, 8 / 9, 5 / 9];
const G2 = 1 / Math.sqrt(3);

function dMatrix(E: number, nu: number): Float64Array {
  const c = E / ((1 + nu) * (1 - 2 * nu));
  // sıra: εr, εz, εθ, γrz
  return new Float64Array([
    c * (1 - nu), c * nu, c * nu, 0,
    c * nu, c * (1 - nu), c * nu, 0,
    c * nu, c * nu, c * (1 - nu), 0,
    0, 0, 0, c * (1 - 2 * nu) / 2,
  ]);
}

/** Eleman B matrisi (4×16) Gauss noktasında; dönüş: r ve detJ. */
function bMatrix(xr: Float64Array, xz: Float64Array, xi: number, eta: number, B: Float64Array,
  N: Float64Array, dxi: Float64Array, deta: Float64Array): { r: number; det: number } {
  q8Shape(xi, eta, N, dxi, deta);
  let j11 = 0, j12 = 0, j21 = 0, j22 = 0, r = 0;
  for (let a = 0; a < 8; a++) {
    j11 += dxi[a] * xr[a]; j12 += dxi[a] * xz[a];
    j21 += deta[a] * xr[a]; j22 += deta[a] * xz[a];
    r += N[a] * xr[a];
  }
  const det = j11 * j22 - j12 * j21;
  const inv = 1 / det;
  B.fill(0);
  for (let a = 0; a < 8; a++) {
    const dr = (j22 * dxi[a] - j12 * deta[a]) * inv;
    const dz = (-j21 * dxi[a] + j11 * deta[a]) * inv;
    const c = 2 * a;
    B[c] = dr;                       // εr
    B[16 + c + 1] = dz;              // εz
    B[32 + c] = r > 1e-12 ? N[a] / r : dr; // εθ (eksende ur/r → ∂ur/∂r)
    B[48 + c] = dz; B[48 + c + 1] = dr; // γrz
  }
  return { r, det };
}

/** Bant simetrik matris (alt üçgen): A(i, i−k) = a[i*(bw+1)+k]. */
class Band {
  a: Float64Array;
  constructor(public n: number, public bw: number) { this.a = new Float64Array(n * (bw + 1)); }
  add(i: number, j: number, v: number) { if (i >= j) this.a[i * (this.bw + 1) + (i - j)] += v; }
  get(i: number, j: number) { return i >= j ? this.a[i * (this.bw + 1) + (i - j)] : this.a[j * (this.bw + 1) + (j - i)]; }
}

function choleskyBand(A: Band, onProgress?: (f: number) => void): boolean {
  const { n, bw, a } = A;
  const w = bw + 1;
  const step = Math.max(1, Math.floor(n / 20));
  for (let i = 0; i < n; i++) {
    const j0 = Math.max(0, i - bw);
    for (let j = j0; j <= i; j++) {
      let sum = a[i * w + (i - j)];
      const k0 = Math.max(j0, j - bw);
      for (let k = k0; k < j; k++) sum -= a[i * w + (i - k)] * a[j * w + (j - k)];
      if (j === i) {
        if (!(sum > 0)) return false;
        a[i * w] = Math.sqrt(sum);
      } else {
        a[i * w + (i - j)] = sum / a[j * w];
      }
    }
    if (onProgress && i % step === 0) onProgress(i / n);
  }
  return true;
}

function solveBand(L: Band, b: Float64Array): Float64Array {
  const { n, bw, a } = L;
  const w = bw + 1;
  const y = new Float64Array(b);
  for (let i = 0; i < n; i++) {
    let s = y[i];
    for (let k = Math.max(0, i - bw); k < i; k++) s -= a[i * w + (i - k)] * y[k];
    y[i] = s / a[i * w];
  }
  for (let i = n - 1; i >= 0; i--) {
    let s = y[i];
    for (let k = i + 1; k <= Math.min(n - 1, i + bw); k++) s -= a[k * w + (k - i)] * y[k];
    y[i] = s / a[i * w];
  }
  return y;
}

export function solveFea(model: FeaModel, onProgress?: Progress): FeaResult {
  const t0 = typeof performance !== "undefined" ? performance.now() : Date.now();
  const { mesh, pressure: P, E, nu } = model;
  const warnings = [...model.warnings];
  const nNodes = mesh.nodes.length / 2;
  const nEl = mesh.elems.length / 8;
  const nDof = 2 * nNodes;
  const dCache = new Map<string, Float64Array>();
  const dOf = (e: number): Float64Array => {
    const c = mesh.elemComponent[e];
    let d = dCache.get(c);
    if (!d) { const m = model.materials[c] ?? { E, nu }; d = dMatrix(m.E, m.nu); dCache.set(c, d); }
    return d;
  };
  let D = dOf(0);

  // Bant genişliği
  let bw = 0;
  for (let e = 0; e < nEl; e++) {
    let lo = Infinity, hi = -Infinity;
    for (let a = 0; a < 8; a++) { const id = mesh.elems[e * 8 + a]; lo = Math.min(lo, id); hi = Math.max(hi, id); }
    bw = Math.max(bw, 2 * (hi - lo) + 1);
  }
  const K = new Band(nDof, bw);
  const F = new Float64Array(nDof);

  const xr = new Float64Array(8), xz = new Float64Array(8);
  const N = new Float64Array(8), dxi = new Float64Array(8), deta = new Float64Array(8);
  const B = new Float64Array(64), DB = new Float64Array(64), ke = new Float64Array(256);
  const dofs = new Int32Array(16);
  let badElems = 0;
  const loadEl = (e: number) => {
    for (let a = 0; a < 8; a++) {
      const id = mesh.elems[e * 8 + a];
      xr[a] = mesh.nodes[2 * id]; xz[a] = mesh.nodes[2 * id + 1];
      dofs[2 * a] = 2 * id; dofs[2 * a + 1] = 2 * id + 1;
    }
  };

  const aStep = Math.max(1, Math.floor(nEl / 10));
  for (let e = 0; e < nEl; e++) {
    loadEl(e);
    D = dOf(e);
    ke.fill(0);
    let bad = false;
    for (let gi = 0; gi < 3; gi++) for (let gj = 0; gj < 3; gj++) {
      const { r, det } = bMatrix(xr, xz, G3[gi], G3[gj], B, N, dxi, deta);
      if (!(det > 0)) bad = true;
      const w = W3[gi] * W3[gj] * r * det;
      // DB = D·B
      for (let i = 0; i < 4; i++) for (let c = 0; c < 16; c++) {
        let s = 0;
        for (let k = 0; k < 4; k++) s += D[i * 4 + k] * B[k * 16 + c];
        DB[i * 16 + c] = s;
      }
      for (let p = 0; p < 16; p++) for (let q = 0; q <= p; q++) {
        let s = 0;
        for (let k = 0; k < 4; k++) s += B[k * 16 + p] * DB[k * 16 + q];
        ke[p * 16 + q] += s * w;
      }
    }
    if (bad) badElems++;
    for (let p = 0; p < 16; p++) for (let q = 0; q <= p; q++) {
      const gp = dofs[p], gq = dofs[q];
      const v = ke[p * 16 + q];
      if (gp >= gq) K.add(gp, gq, v); else K.add(gq, gp, v);
      if (p !== q && gp === gq) K.add(gp, gq, v); // aynı serbestlik (olmaz) güvenlik
    }
    if (onProgress && e % aStep === 0) onProgress("assemble", e / nEl);
  }
  if (badElems > 0) warnings.push(`${badElems} elemanda Jacobian ≤ 0 (bozuk geometri) — sonuç güvenilmez.`);

  // İç basınç: ξ=−1 kenarı (düğüm 1, 8, 4), η boyunca
  const g3e = G3, w3e = W3;
  for (const e of model.pressureElems) {
    loadEl(e);
    const ids = [0, 7, 3];
    for (let g = 0; g < 3; g++) {
      const et = g3e[g];
      const n1 = (et * (et - 1)) / 2, n8 = 1 - et * et, n4 = (et * (et + 1)) / 2;
      const d1 = et - 0.5, d8 = -2 * et, d4 = et + 0.5;
      const sh = [n1, n8, n4], ds = [d1, d8, d4];
      let r = 0, dr = 0, dz = 0;
      for (let k = 0; k < 3; k++) { r += sh[k] * xr[ids[k]]; dr += ds[k] * xr[ids[k]]; dz += ds[k] * xz[ids[k]]; }
      for (let k = 0; k < 3; k++) {
        const f = sh[k] * P * r * w3e[g];
        F[dofs[2 * ids[k]]] += f * dz;
        F[dofs[2 * ids[k] + 1]] += -f * dr;
      }
    }
  }
  // Açık uç kapak itkisi (eksenel düzgün çekme, toplam P·ri²/2 — 2π sadeleşmiş)
  for (const el of model.endLoads) {
    const ids = el.edge === "start" ? [0, 4, 1] : [3, 6, 2];
    const contrib: { dof: number; v: number }[] = [];
    let area = 0;
    for (const e of el.elems) {
      loadEl(e);
      for (let g = 0; g < 3; g++) {
        const x = g3e[g];
        const sh = [(x * (x - 1)) / 2, 1 - x * x, (x * (x + 1)) / 2];
        const ds = [x - 0.5, -2 * x, x + 0.5];
        let r = 0, dr = 0, dz = 0;
        for (let k = 0; k < 3; k++) { r += sh[k] * xr[ids[k]]; dr += ds[k] * xr[ids[k]]; dz += ds[k] * xz[ids[k]]; }
        const dG = Math.hypot(dr, dz) * w3e[g] * r;
        area += dG;
        for (let k = 0; k < 3; k++) contrib.push({ dof: dofs[2 * ids[k] + 1], v: sh[k] * dG });
      }
    }
    const q = (P * el.rIn * el.rIn) / 2 / (area || 1);
    for (const c of contrib) F[c.dof] += c.v * q * el.dir;
  }

  // Denge kontrolü (eksenel)
  let fz = 0, fzAbs = 0;
  for (let i = 1; i < nDof; i += 2) { fz += F[i]; fzAbs += Math.abs(F[i]); }
  if (fzAbs > 0 && Math.abs(fz) > 1e-6 * fzAbs) warnings.push(`Eksenel yük dengesizliği ${(Math.abs(fz) / fzAbs * 100).toExponential(1)} %.`);

  // Sınır şartları: eksende ur=0, tek düğümde uz=0
  const fixed = new Uint8Array(nDof);
  for (const n of model.axisNodes) fixed[2 * n] = 1;
  fixed[2 * model.fixUzNode + 1] = 1;
  const Korig = new Band(nDof, bw);
  Korig.a.set(K.a);
  const w = bw + 1;
  for (let i = 0; i < nDof; i++) {
    if (!fixed[i]) continue;
    for (let k = 0; k <= bw; k++) {
      K.a[i * w + k] = 0;
      if (i + k < nDof) K.a[(i + k) * w + k] = 0;
    }
    K.a[i * w] = 1;
    F[i] = 0;
  }

  const ok = choleskyBand(K, onProgress ? (f) => onProgress("factor", f) : undefined);
  let u: Float64Array = new Float64Array(nDof);
  let converged = ok;
  if (!ok) warnings.push("Rijitlik matrisi pozitif tanımlı değil (mekanizma / bozuk ağ) — çözüm yok.");
  else {
    u = solveBand(K, F);
    // Artık kontrolü (serbest dereceler)
    let rn = 0, fn = 0;
    for (let i = 0; i < nDof; i++) {
      if (fixed[i]) continue;
      let s = 0;
      for (let j = Math.max(0, i - bw); j <= Math.min(nDof - 1, i + bw); j++) s += Korig.get(i, j) * u[j];
      rn += (s - F[i]) ** 2;
      fn += F[i] * F[i];
    }
    const rel = fn > 0 ? Math.sqrt(rn / fn) : 0;
    converged = Number.isFinite(rel) && rel < 1e-6 && u.every(Number.isFinite);
    if (!converged) warnings.push(`Çözüm artığı yüksek (${rel.toExponential(2)}).`);
  }

  // Gerilme: 2×2 Gauss → köşe ekstrapolasyonu → düğüm ortalaması
  const stress = new Float64Array(4 * nNodes);
  const count = new Float64Array(nNodes);
  const gp = [[-G2, -G2], [G2, -G2], [G2, G2], [-G2, G2]];
  const sg = new Float64Array(16); // 4 nokta × [σr, σθ, σz, τ]
  const sStep = Math.max(1, Math.floor(nEl / 10));
  for (let e = 0; e < nEl; e++) {
    loadEl(e);
    D = dOf(e);
    for (let g = 0; g < 4; g++) {
      bMatrix(xr, xz, gp[g][0], gp[g][1], B, N, dxi, deta);
      const eps = [0, 0, 0, 0];
      for (let k = 0; k < 4; k++) { let s = 0; for (let c = 0; c < 16; c++) s += B[k * 16 + c] * u[dofs[c]]; eps[k] = s; }
      const sig = [0, 0, 0, 0];
      for (let i = 0; i < 4; i++) { let s = 0; for (let k = 0; k < 4; k++) s += D[i * 4 + k] * eps[k]; sig[i] = s; }
      sg[g * 4] = sig[0]; sg[g * 4 + 1] = sig[2]; sg[g * 4 + 2] = sig[1]; sg[g * 4 + 3] = sig[3];
    }
    const corner: number[][] = [];
    for (let a = 0; a < 4; a++) {
      const X = XI[a] * Math.sqrt(3), Y = ETA[a] * Math.sqrt(3);
      const L = [0.25 * (1 - X) * (1 - Y), 0.25 * (1 + X) * (1 - Y), 0.25 * (1 + X) * (1 + Y), 0.25 * (1 - X) * (1 + Y)];
      const v = [0, 0, 0, 0];
      for (let g = 0; g < 4; g++) for (let c = 0; c < 4; c++) v[c] += L[g] * sg[g * 4 + c];
      corner.push(v);
    }
    const mid = [[0, 1], [1, 2], [2, 3], [3, 0]];
    for (let a = 0; a < 8; a++) {
      const v = a < 4 ? corner[a] : corner[mid[a - 4][0]].map((x, c) => (x + corner[mid[a - 4][1]][c]) / 2);
      const id = mesh.elems[e * 8 + a];
      for (let c = 0; c < 4; c++) stress[4 * id + c] += v[c];
      count[id]++;
    }
    if (onProgress && e % sStep === 0) onProgress("stress", e / nEl);
  }
  const vm = new Float64Array(nNodes);
  let maxVm = 0;
  for (let i = 0; i < nNodes; i++) {
    const k = count[i] || 1;
    for (let c = 0; c < 4; c++) stress[4 * i + c] /= k;
    vm[i] = vonMises(stress[4 * i], stress[4 * i + 1], stress[4 * i + 2], stress[4 * i + 3]);
    if (Number.isFinite(vm[i]) && vm[i] > maxVm) maxVm = vm[i];
  }
  const t1 = typeof performance !== "undefined" ? performance.now() : Date.now();
  return {
    mesh, u, stress, vm, maxVm, pressure: P, warnings, converged,
    disclaimer: FEA_DISCLAIMER, E, nu, dof: nDof, ms: t1 - t0,
  };
}

export function vonMises(sr: number, st: number, sz: number, trz: number): number {
  return Math.sqrt(0.5 * ((sr - st) ** 2 + (st - sz) ** 2 + (sz - sr) ** 2) + 3 * trz * trz);
}

/** Proje → ağ → çözüm. Ağ kurulamazsa boş, converged=false sonuç döner (sahte sonuç yok). */
export function runFea(project: VesselProject, opts: FeaOptions = {}, onProgress?: Progress): FeaResult {
  let model: FeaModel;
  try {
    onProgress?.("mesh", 0);
    model = buildFeaModel(project, opts);
  } catch (err) {
    const empty = { nodes: new Float64Array(0), elems: new Uint32Array(0), nodesPerElem: 8, elemComponent: [] };
    return {
      mesh: empty, u: new Float64Array(0), stress: new Float64Array(0), vm: new Float64Array(0), maxVm: 0,
      pressure: Math.max(project.design_conditions?.design_pressure ?? 0, 0),
      warnings: [err instanceof Error ? err.message : String(err)], converged: false, disclaimer: FEA_DISCLAIMER,
    };
  }
  return solveFea(model, onProgress);
}
