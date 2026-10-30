# Dalga 4 — tarayıcıda eksenel simetrik FEA (P12 → P13 sıralı; P14 Yusuf onayı bekler)
Yol kuralı: `pressure-vessel-suite/` kökü. Ortak kabul: `cd apps/web-ui && npm test && npm run build` +
`python -m pytest tests/unit tests/api tests/faz5 -q` yeşil; tsconfig.tsbuildinfo commit dışı; commit sonu
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; Türkçe ≤15 satır rapor. Her sonuç "gösterge amaçlı FEA —
ASME onayı / mühendis değerlendirmesi değildir" etiketi taşır. Sahte PASS yok. Mevcut `packages/fea` (Python, CalculiX
iskeleti) P14'e aittir — dokunma.

## Sözleşme (P12 üretir, P13 tüketir) — `apps/web-ui/src/fea/types.ts`
```ts
export interface FeaMesh { nodes: Float64Array /* r,z çiftleri, mm */; elems: Uint32Array; nodesPerElem: number;
  elemComponent: string[] /* bileşen id */; }
export interface FeaResult {
  mesh: FeaMesh; u: Float64Array /* ur,uz düğüm başına, mm */;
  /** Düğümlere ortalanmış gerilme, düğüm başına [σr, σθ, σz, τrz] MPa */ stress: Float64Array;
  vm: Float64Array; maxVm: number; pressure: number; warnings: string[]; converged: boolean;
}
export interface SclSample { s: number /* 0..t */; sr: number; st: number; sz: number; trz: number }
/** Kalınlık boyunca çizgi (SCL) üzerinde n nokta örnekler; uçlar iç/dış yüzeyde. */
export type SampleScl = (res: FeaResult, a: [number, number], b: [number, number], n: number) => SclSample[];
```
Ayrıca `toStressField(res): StressField` — mevcut `src/stress/types.ts` sözleşmesine adaptör (3D noktayı r=√(x²+y²), z'ye indirger),
böylece ısı haritası FEA verisini de boyayabilir (UI modu P13'te).

## P12 — Eksenel simetrik FEM çekirdeği — Opus
- Önce kısa karşılaştırma (rapora 3 satır): saf TypeScript çözücü vs Pyodide+scikit-fem vs WASM. Öneri saf TS (bağımlılık yok,
  worker'da çalışır, paket boyutu küçük); farklı karar verirsen gerekçesini yaz.
- Meridyen profilinden (`vesselProfileChain`/`componentFrames`; korozyonlu kalınlık) yapılandırılmış ağ: et boyunca ≥4 eleman,
  meridyende süreksizlik bölgelerinde (≈ 2,5·√(Rt)) sıklaştırma. Eleman: 8 düğümlü dörtgen (Q8, 2×2 veya 3×3 Gauss) önerilir.
- Yükler: iç basınç (iç yüzeye normal). Sınır şartı: rijit hareketi önleyen tek düğüm uz=0 (yük dengeli); eksen üzerinde ur=0.
- Lineer elastik, E ve ν malzemeden (yoksa çelik 200 GPa/0,3 varsayımı + uyarı). Seyrek/bant çözücü (CG + Jacobi veya skyline Cholesky).
- Kapsam dışı (uyarıyla atla): eksen dışı nozullar, destekler, dış yükler; yalnız eksen üzerindeki (kutup) nozul modellenebilirse modelle.
- Web Worker'da çalıştır (`fea/fea.worker.ts`), istemci `useFea(project)`; büyük ağda UI donmasın.
- Doğrulama testleri (vitest): kalın silindir Lamé (σθ iç/dış %1), ince silindir uzak alan PR/t ve PR/2t (%2), yarımküre PR/2t,
  silindir-yarımküre birleşimi max gerilme analitik süreksizlik (P03 `analyticField`) ile aynı mertebe (%15), ağ yakınsama (kaba/ince fark <%3).
- Dosyalar: yeni `apps/web-ui/src/fea/` (types.ts, mesh.ts, solver.ts, sampleScl.ts, toStressField.ts, fea.worker.ts, useFea.ts) + `src/__tests__/fea*.test.ts`. Mevcut dosyalara dokunma.

## P13 — Div.2 Part 5 linearizasyon + FEA ısı haritası modu — Sonnet (P12 bittikten sonra)
- `fea/linearize.ts`: SCL örneklerinden membran (ortalama) ve eğilme (lineer) bileşenleri, tepe (peak) kalan; Pm/PL ve PL+Pb, PL+Pb+Q
  eşdeğer gerilmeleri (Tresca veya von Mises — seçilebilir, varsayılan von Mises + not). Sınırlar S, 1,5S, 3S (SPS).
- SCL konumları otomatik: her bileşen ortası (Pm) + her birleşimin iki yanı (PL+Pb+Q). Sınıflandırma varsayımını sonuca yaz.
- UI: Gerilme görünümüne "Analitik / FEA" anahtarı; FEA'da ilerleme göstergesi, `toStressField` ile boyama, SCL tablosu kartı.
- Testler: linearizasyon el hesabı (sabit → yalnız membran; lineer → membran+eğilme; parabol → tepe ≠0).
