// Eksenel simetrik FEA sözleşmesi (P12 üretir, P13 tüketir). Birimler: mm, MPa.
// Düzlem: meridyen (r, z); kap ekseni +Z (vesselModel.componentFrames ile aynı).
// GÖSTERGE AMAÇLI — ASME onayı / mühendis değerlendirmesi değildir.
import type { VesselProject } from "../types";

export interface FeaMesh {
  nodes: Float64Array /* r,z çiftleri, mm */;
  elems: Uint32Array;
  nodesPerElem: number;
  elemComponent: string[] /* bileşen id */;
  // ── P12 ekleri (isteğe bağlı; sözleşmeyi değiştirmez) ──
  /** Köşe kolonları: et boyunca düz çizgi (iç → dış, korozyonlu yüzeyler), meridyen konumu s. */
  lines?: FeaLine[];
  /** Eleman → başlangıç köşe kolonu indeksi (eleman lines[c]..lines[c+1] arasında). */
  elemColumn?: Uint32Array;
  /** Bileşen birleşimleri (bileşen id değişen kolonlar). */
  junctions?: FeaJunction[];
  /** Bileşen id → tür. */
  componentKind?: Record<string, FeaComponentKind>;
  /** Et boyunca eleman sayısı. */
  nThick?: number;
}

export type FeaComponentKind = "shell" | "cone" | "head" | "nozzle";

export interface FeaLine {
  s: number;             // meridyen yol koordinatı (iç yüzey yay boyu, mm)
  a: [number, number];   // iç yüzey (r,z)
  b: [number, number];   // dış yüzey (r,z)
  component: string;     // bu kolondan başlayan elemanın bileşeni
}

export interface FeaJunction {
  s: number;
  a: [number, number];
  b: [number, number];
  left: string;  // yol yönünde önceki bileşen
  right: string; // sonraki bileşen
  /** Süreksizlik bölgesi yarı genişliği ≈ 2,5·√(R·t), mm. */
  zone: number;
}

export interface FeaResult {
  mesh: FeaMesh; u: Float64Array /* ur,uz düğüm başına, mm */;
  /** Düğümlere ortalanmış gerilme, düğüm başına [σr, σθ, σz, τrz] MPa */ stress: Float64Array;
  vm: Float64Array; maxVm: number; pressure: number; warnings: string[]; converged: boolean;
  // ── P12 ekleri ──
  disclaimer?: string;
  E?: number;
  nu?: number;
  dof?: number;
  ms?: number;
}

export interface SclSample { s: number /* 0..t */; sr: number; st: number; sz: number; trz: number }
/** Kalınlık boyunca çizgi (SCL) üzerinde n nokta örnekler; uçlar iç/dış yüzeyde. */
export type SampleScl = (res: FeaResult, a: [number, number], b: [number, number], n: number) => SclSample[];

export const FEA_DISCLAIMER = "Gösterge amaçlı FEA — ASME onayı / mühendis değerlendirmesi değildir.";

export interface FeaOptions {
  /** Ağ yoğunluk çarpanı (1 = varsayılan, 2 = iki kat ince). */
  refine?: number;
}

// ── Worker mesajları ──
export type FeaMainToWorker = { type: "solve"; reqId: number; project: VesselProject; options?: FeaOptions };
export type FeaWorkerToMain =
  | { type: "progress"; reqId: number; phase: "mesh" | "assemble" | "factor" | "stress"; fraction: number }
  | { type: "result"; reqId: number; result: FeaResult }
  | { type: "error"; reqId: number; message: string };
