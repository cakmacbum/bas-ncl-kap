// SCL örnekleme + ağ içinde nokta bulma (P12). Düğüm ortalamalı gerilmeler Q8 şekil
// fonksiyonlarıyla enterpole edilir. GÖSTERGE AMAÇLI — ASME onayı değildir.

import { q8Shape } from "./solver";
import type { FeaMesh, FeaResult, SampleScl, SclSample } from "./types";

interface Grid { r0: number; z0: number; cell: number; nr: number; nz: number; bins: number[][] }
const grids = new WeakMap<FeaMesh, Grid>();

function gridOf(mesh: FeaMesh): Grid {
  const g = grids.get(mesh);
  if (g) return g;
  const nEl = mesh.elems.length / 8;
  let rMin = Infinity, rMax = -Infinity, zMin = Infinity, zMax = -Infinity;
  for (let i = 0; i < mesh.nodes.length; i += 2) {
    rMin = Math.min(rMin, mesh.nodes[i]); rMax = Math.max(rMax, mesh.nodes[i]);
    zMin = Math.min(zMin, mesh.nodes[i + 1]); zMax = Math.max(zMax, mesh.nodes[i + 1]);
  }
  const area = Math.max((rMax - rMin) * (zMax - zMin), 1);
  const cell = Math.max(Math.sqrt(area / Math.max(nEl, 1)) * 2, 1e-3);
  const nr = Math.max(1, Math.ceil((rMax - rMin) / cell) + 1);
  const nz = Math.max(1, Math.ceil((zMax - zMin) / cell) + 1);
  const bins: number[][] = Array.from({ length: nr * nz }, () => []);
  for (let e = 0; e < nEl; e++) {
    let a = Infinity, b = -Infinity, c = Infinity, d = -Infinity;
    for (let k = 0; k < 8; k++) {
      const id = mesh.elems[e * 8 + k];
      a = Math.min(a, mesh.nodes[2 * id]); b = Math.max(b, mesh.nodes[2 * id]);
      c = Math.min(c, mesh.nodes[2 * id + 1]); d = Math.max(d, mesh.nodes[2 * id + 1]);
    }
    const i0 = Math.floor((a - rMin) / cell), i1 = Math.floor((b - rMin) / cell);
    const j0 = Math.floor((c - zMin) / cell), j1 = Math.floor((d - zMin) / cell);
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) bins[i * nz + j].push(e);
  }
  const out = { r0: rMin, z0: zMin, cell, nr, nz, bins };
  grids.set(mesh, out);
  return out;
}

const N = new Float64Array(8), dxi = new Float64Array(8), deta = new Float64Array(8);

/** Q8 ters eşleme (Newton). Dönüş: doğal koordinatlar ve (kırpılmış) noktaya uzaklık. */
function invert(mesh: FeaMesh, e: number, r: number, z: number): { xi: number; eta: number; dist: number } {
  let xi = 0, eta = 0;
  for (let it = 0; it < 25; it++) {
    q8Shape(xi, eta, N, dxi, deta);
    let x = 0, y = 0, j11 = 0, j12 = 0, j21 = 0, j22 = 0;
    for (let a = 0; a < 8; a++) {
      const id = mesh.elems[e * 8 + a];
      const nr = mesh.nodes[2 * id], nz = mesh.nodes[2 * id + 1];
      x += N[a] * nr; y += N[a] * nz;
      j11 += dxi[a] * nr; j12 += dxi[a] * nz; j21 += deta[a] * nr; j22 += deta[a] * nz;
    }
    const det = j11 * j22 - j12 * j21;
    if (!(Math.abs(det) > 1e-30)) break;
    const dr = r - x, dz = z - y;
    const dXi = (j22 * dr - j21 * dz) / det;
    const dEta = (-j12 * dr + j11 * dz) / det;
    xi = Math.max(-1.5, Math.min(1.5, xi + dXi));
    eta = Math.max(-1.5, Math.min(1.5, eta + dEta));
    if (Math.abs(dXi) + Math.abs(dEta) < 1e-10) break;
  }
  const cx = Math.max(-1, Math.min(1, xi)), ce = Math.max(-1, Math.min(1, eta));
  q8Shape(cx, ce, N);
  let x = 0, y = 0;
  for (let a = 0; a < 8; a++) {
    const id = mesh.elems[e * 8 + a];
    x += N[a] * mesh.nodes[2 * id]; y += N[a] * mesh.nodes[2 * id + 1];
  }
  return { xi: cx, eta: ce, dist: Math.hypot(r - x, z - y) };
}

export interface Located { elem: number; xi: number; eta: number; dist: number }

/** (r,z) noktasını içeren (yoksa en yakın) elemanı bulur; maxDist dışında null. */
export function locate(mesh: FeaMesh, r: number, z: number, maxDist = Infinity): Located | null {
  const g = gridOf(mesh);
  const nEl = mesh.elems.length / 8;
  if (nEl === 0) return null;
  const ci = Math.floor((r - g.r0) / g.cell), cj = Math.floor((z - g.z0) / g.cell);
  let best: Located | null = null;
  const tried = new Set<number>();
  const scan = (ring: number) => {
    for (let i = ci - ring; i <= ci + ring; i++) for (let j = cj - ring; j <= cj + ring; j++) {
      if (Math.max(Math.abs(i - ci), Math.abs(j - cj)) !== ring) continue;
      if (i < 0 || j < 0 || i >= g.nr || j >= g.nz) continue;
      for (const e of g.bins[i * g.nz + j]) {
        if (tried.has(e)) continue;
        tried.add(e);
        const v = invert(mesh, e, r, z);
        if (!best || v.dist < best.dist) best = { elem: e, ...v };
      }
    }
  };
  const maxRing = Math.max(g.nr, g.nz);
  for (let ring = 0; ring <= maxRing; ring++) {
    scan(ring);
    const b = best as Located | null;
    if (b && b.dist < 1e-9) break;
    // Bir halka daha taranmış bölge, en iyi aday uzaklığını garanti eder
    if (b && (ring - 1) * g.cell > b.dist) break;
    if ((ring - 1) * g.cell > maxDist) break;
  }
  const b = best as Located | null;
  if (!b || b.dist > maxDist) return null;
  return b;
}

/** Düğüm ortalamalı gerilmenin (e, ξ, η) noktasındaki değeri: [σr, σθ, σz, τrz]. */
export function stressAt(res: FeaResult, loc: Located): [number, number, number, number] {
  q8Shape(loc.xi, loc.eta, N);
  const out: [number, number, number, number] = [0, 0, 0, 0];
  for (let a = 0; a < 8; a++) {
    const id = res.mesh.elems[loc.elem * 8 + a];
    for (let c = 0; c < 4; c++) out[c] += N[a] * res.stress[4 * id + c];
  }
  return out;
}

/** Elemanın η (meridyen/yol) yönündeki birim teğeti. */
export function pathTangent(mesh: FeaMesh, loc: Located): [number, number] {
  q8Shape(loc.xi, loc.eta, N, dxi, deta);
  let tr = 0, tz = 0;
  for (let a = 0; a < 8; a++) {
    const id = mesh.elems[loc.elem * 8 + a];
    tr += deta[a] * mesh.nodes[2 * id]; tz += deta[a] * mesh.nodes[2 * id + 1];
  }
  const l = Math.hypot(tr, tz) || 1;
  return [tr / l, tz / l];
}

export const sampleScl: SampleScl = (res, a, b, n) => {
  const L = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const m = Math.max(2, Math.floor(n));
  const out: SclSample[] = [];
  for (let i = 0; i < m; i++) {
    const w = i / (m - 1);
    const r = a[0] + (b[0] - a[0]) * w, z = a[1] + (b[1] - a[1]) * w;
    const loc = locate(res.mesh, r, z);
    if (!loc) { out.push({ s: w * L, sr: NaN, st: NaN, sz: NaN, trz: NaN }); continue; }
    const [sr, st, sz, trz] = stressAt(res, loc);
    out.push({ s: w * L, sr, st, sz, trz });
  }
  return out;
};
