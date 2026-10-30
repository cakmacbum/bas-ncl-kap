/** Sac açınım şablonları — nötr eksen (orta yüzey) üzerinden. Birim: mm. Saf TS. */
import type { FlatPart, Pt, Shape } from "./shapes";

const PI = Math.PI;
const deg = (r: number) => (r * 180) / PI;

export type FlatResult = { ok: true; part: FlatPart } | { ok: false; reason: string };
const fail = (reason: string): FlatResult => ({ ok: false, reason });

/** Gövde halkası: dikdörtgen π·Dm × L. weldGap: kaynak ağzı payı (boy ve çevreye eklenir). */
export function shellCourse(id: string, insideD: number, t: number, length: number, weldGap = 0): FlatResult {
  if (!(insideD > 0 && t > 0 && length > 0) || weldGap < 0) return fail("Çap, et kalınlığı ve boy pozitif olmalı.");
  const dm = insideD + t;
  const w = PI * dm + weldGap;
  const h = length + weldGap;
  return {
    ok: true,
    part: {
      id, name: `Gövde halkası ${id}`,
      shapes: [
        { k: "poly", pts: [[0, 0], [w, 0], [w, h], [0, h]], closed: true },
        { k: "text", at: [w * 0.02, h * 0.5], h: Math.max(h * 0.03, 5), s: `${id} ${w.toFixed(1)} x ${h.toFixed(1)}` },
      ],
      notes: [`Nötr eksen Dm = ${dm.toFixed(1)} mm; çevre = π·Dm${weldGap ? ` + ${weldGap} mm kaynak payı` : ""}.`],
    },
  };
}

/** Koni: halka dilimi. Çaplar iç çap, axialL eksenel boy, t et kalınlığı. */
export function coneSector(id: string, largeD: number, smallD: number, axialL: number, t: number, halfApexDeg?: number | null): FlatResult {
  if (!(largeD > smallD && smallD >= 0 && axialL > 0 && t > 0)) return fail("Büyük çap > küçük çap, boy ve et kalınlığı pozitif olmalı.");
  const alpha = Math.atan((largeD - smallD) / 2 / axialL);
  const D1 = largeD + t / Math.cos(alpha);
  const D2 = smallD + t / Math.cos(alpha);
  const slant = Math.hypot(axialL, (D1 - D2) / 2);
  const R1 = (slant * D1) / (D1 - D2);
  const R2 = R1 - slant;
  const phi = (PI * D1) / R1; // rad; = 360°·(D1/2)/R1
  if (phi > 2 * PI) return fail("Açınım açısı 360° üzerinde.");
  const a0 = 90 - deg(phi) / 2;
  const a1 = 90 + deg(phi) / 2;
  const at = (R: number, a: number): Pt => [R * Math.cos((a * PI) / 180), R * Math.sin((a * PI) / 180)];
  const shapes: Shape[] = [
    { k: "arc", c: [0, 0], r: R1, a0, a1 },
    { k: "line", a: at(R1, a0), b: at(R2, a0) },
    { k: "line", a: at(R1, a1), b: at(R2, a1) },
  ];
  if (R2 > 1e-6) shapes.push({ k: "arc", c: [0, 0], r: R2, a0, a1 });
  shapes.push({ k: "text", at: [-R1 * 0.2, R1 * 0.5], h: Math.max(R1 * 0.02, 5), s: `${id} R1=${R1.toFixed(1)} R2=${R2.toFixed(1)} fi=${deg(phi).toFixed(2)}` });
  const notes = [`Eğik boy = ${slant.toFixed(1)} mm, R1 = ${R1.toFixed(1)}, R2 = ${R2.toFixed(1)}, açınım açısı = ${deg(phi).toFixed(2)}° (nötr eksen çapları ${D1.toFixed(1)} / ${D2.toFixed(1)}).`];
  if (halfApexDeg && Math.abs(halfApexDeg - deg(alpha)) > 0.5)
    notes.push(`Uyarı: girilen yarı tepe açısı (${halfApexDeg}°) çap/boydan çıkan değerle (${deg(alpha).toFixed(2)}°) uyuşmuyor; çap/boy kullanıldı.`);
  return { ok: true, part: { id, name: `Koni ${id}`, shapes, notes } };
}

export interface HeadProfileInput {
  type: "elliptical" | "torispherical" | "hemispherical";
  insideD: number;
  t: number;
  crownR?: number | null;
  knuckleR?: number | null;
  crownDepth?: number | null;
  standardFD?: boolean;
}

/** Meridyen örnekleri (kutuptan ekvatora): s = yay boyu, r = dönme yarıçapı. Hata → mesaj string. */
export function headMeridian(h: HeadProfileInput, n = 120): { s: number; r: number }[] | string {
  const a = (h.insideD + h.t) / 2;
  const out: { s: number; r: number }[] = [];
  const acc = (r: number, ds: number) => out.push({ s: (out.length ? out[out.length - 1].s : 0) + ds, r });

  if (h.type === "torispherical") {
    let Rc = h.crownR ?? null;
    let rk = h.knuckleR ?? null;
    if ((Rc == null || rk == null) && h.standardFD) { Rc = h.insideD; rk = 0.06 * h.insideD; }
    if (Rc == null || rk == null || Rc <= 0 || rk <= 0) return "Torisferik bombe için taç ve köşe yarıçapı gerekli.";
    Rc += h.t / 2; rk += h.t / 2;
    const sinB = (a - rk) / (Rc - rk);
    if (!(sinB > 0 && sinB < 1)) return "Taç/köşe yarıçapları bu çapla geometrik olarak uyuşmuyor.";
    const beta = Math.asin(sinB);
    const nc = Math.ceil(n * 0.6);
    const nk = n - nc;
    out.push({ s: 0, r: 0 });
    for (let i = 1; i <= nc; i++) acc(Rc * Math.sin((beta * i) / nc), (Rc * beta) / nc);
    for (let i = 1; i <= nk; i++) acc(a - rk + rk * Math.sin(beta + ((PI / 2 - beta) * i) / nk), (rk * (PI / 2 - beta)) / nk);
    return out;
  }

  const b = h.type === "hemispherical" ? a : h.crownDepth && h.crownDepth > 0 ? h.crownDepth + h.t / 2 : a / 2; // elips: 2:1 varsayılan
  let prev: Pt = [0, b];
  out.push({ s: 0, r: 0 });
  for (let i = 1; i <= n; i++) {
    const u = (PI / 2) * (1 - i / n);
    const cur: Pt = [a * Math.cos(u), b * Math.sin(u)];
    acc(cur[0], Math.hypot(cur[0] - prev[0], cur[1] - prev[1]));
    prev = cur;
  }
  return out;
}

/** Bombe taç+hamut: n petal (gore) açınımı. Yaklaşık yöntem (genişlik = 2π·r/n). */
export function headPetal(id: string, h: HeadProfileInput, petals: number): FlatResult {
  if (!(h.insideD > 0 && h.t > 0) || !Number.isInteger(petals) || petals < 3) return fail("Çap/et pozitif, petal sayısı en az 3 tam sayı olmalı.");
  const m = headMeridian(h);
  if (typeof m === "string") return fail(m);
  const half = m.map((p) => (PI * p.r) / petals);
  const left: Pt[] = m.map((p, i) => [-half[i], p.s]);
  const right: Pt[] = m.map((p, i): Pt => [half[i], p.s]).reverse();
  const L = m[m.length - 1].s;
  const wEq = 2 * half[half.length - 1];
  return {
    ok: true,
    part: {
      id, name: `Bombe petali ${id} (x${petals})`,
      shapes: [
        { k: "poly", pts: [...left, ...right], closed: true },
        { k: "line", a: [0, 0], b: [0, L] },
        { k: "text", at: [-wEq / 2, -Math.max(L * 0.06, 8)], h: Math.max(L * 0.03, 5), s: `${id} x${petals} L=${L.toFixed(1)}` },
      ],
      notes: [
        "Yaklaşık, kalıp üreticisiyle doğrula: petal genişliği 2π·r/n (nötr eksen); presle şekillendirme payı/incelme dahil değildir.",
        `Petal boyu (kutup-ekvator) = ${L.toFixed(1)} mm, ekvatorda genişlik = ${wEq.toFixed(1)} mm. Düz kenar (SFL) ayrı halka olarak açılır.`,
      ],
    },
  };
}

/**
 * Silindir-silindir kesişim: dal ucunun tepe çizgisine göre ek boyu.
 * x = e + r·sinθ; h(θ) = R − sqrt(R² − x²). e=0: θ=0 → 0, θ=90° → R − sqrt(R² − r²).
 */
export function branchDrop(R: number, r: number, theta: number, e = 0): number {
  return R - Math.sqrt(R * R - (e + r * Math.sin(theta)) ** 2);
}

export interface NozzleCutInput {
  runInsideD: number; runT: number; // ana gövde
  branchOD: number; branchT: number; // nozul borusu
  crownLength: number; // nozul borusunun θ=0 (en kısa) çizgisindeki boyu
  offset?: number; // eksen kaçıklığı (0 = radyal)
  steps?: number;
}

/** Nozul borusu açınımı (kesim eğrisi) + gövdedeki delik izi (sargı şablonu). */
export function nozzleCut(id: string, p: NozzleCutInput): FlatResult {
  const R = (p.runInsideD + p.runT) / 2;
  const r = (p.branchOD - p.branchT) / 2;
  const e = p.offset ?? 0;
  if (!(R > 0 && r > 0 && p.crownLength >= 0)) return fail("Ölçüler pozitif olmalı.");
  if (Math.abs(e) + r >= R) return fail("Nozul yarıçapı + kaçıklık gövde yarıçapını aşıyor (kesişim tanımsız).");
  const n = p.steps ?? 72;
  const W = 2 * PI * r;
  const cut: Pt[] = [];
  const hole: Pt[] = [];
  for (let i = 0; i <= n; i++) {
    const th = (2 * PI * i) / n;
    cut.push([r * th, p.crownLength + branchDrop(R, r, th, e)]);
    if (i < n) hole.push([W + 40 + R * Math.asin((e + r * Math.sin(th)) / R), r * Math.cos(th) + r]);
  }
  const H = Math.max(...cut.map((c) => c[1]));
  return {
    ok: true,
    part: {
      id, name: `Nozul ${id} açınımı`,
      shapes: [
        { k: "poly", pts: cut },
        { k: "line", a: [0, 0], b: [0, cut[0][1]] },
        { k: "line", a: [W, 0], b: [W, cut[n][1]] },
        { k: "line", a: [0, 0], b: [W, 0] },
        { k: "poly", pts: hole, closed: true },
        { k: "text", at: [0, H * 1.05], h: Math.max(H * 0.04, 4), s: `${id} cevre ${W.toFixed(1)}` },
      ],
      notes: [
        `Nötr eksen: nozul r = ${r.toFixed(1)} mm, gövde R = ${R.toFixed(1)} mm${e ? `, kaçıklık ${e} mm` : " (radyal)"}. θ = 0 gövde tepe çizgisi (en kısa boy ${p.crownLength.toFixed(1)} mm).`,
        "Sağdaki kapalı eğri gövde üzerindeki delik izidir (x: gövde çevresi boyunca yay, y: eksen). Eğimli nozul bu şablonda yoktur.",
      ],
    },
  };
}
