# P10 — 2D ölçülü imalat resmi (SVG + DXF)
Kendi başına yeterli paket. Yollar `pressure-vessel-suite/` köküne göre. Gizli bilgi yok.

## Bağlam
Basınçlı kap tasarım uygulaması (React + Vite, `apps/web-ui`). 3D model tarayıcıda replicad (OpenCascade WASM) ile bir
web worker'da üretiliyor: `apps/web-ui/src/cad/cad.worker.ts`, `buildShapes.ts`, `export.ts` (STEP/STL), istemci `cadClient.ts`.
Proje verisi tipi `apps/web-ui/src/types.ts` (`VesselProject`). Dışa aktarma menüsü `apps/web-ui/src/exportMenu.tsx`,
seçenek listesi `geometryLayout.ts` `EXPORT_OPTIONS`. Analitik profil yardımcıları `vesselModel.ts`/`geometryLayout.ts`
(`vesselProfile`, `componentFrames`, `nozzlePlacement`).

## İstenen
"Dışa aktar" menüsüne **"İmalat resmi (SVG)"** ve **"İmalat resmi (DXF)"** ekle. Tek A3 yatay pafta:
1. Ön görünüş (kap ekseni yatay), yarım kesit (üst yarı kesit, alt yarı görünüş) — iç/dış çizgi, et kalınlığı görünür.
2. Uç görünüş (nozul yönleri), nozullar etiketli (N1, N2… proje nozul id'leri).
3. Ölçüler: toplam boy (teğet-teğet ve bombe dahil), iç çap, et kalınlıkları, her nozulun eksenden konumu ve çıkıntısı,
   destek konumları. Ölçü çizgisi + ok + değer (mm).
4. Antet: proje no/adı, revizyon, kod, malzeme, ölçek, "Ön bilgi — imalat onayı değildir".
5. Nozul tablosu (id, DN, flanş sınıfı varsa, konum, açı).

Yaklaşım serbest; önerilen: geometriyi analitik profil + nozul yerleşiminden 2D çizgi/yay ilkellerine çevir (OCC gizli çizgi
projeksiyonu replicad'de varsa `drawProjection` kullanılabilir, yoksa analitik yeterli). DXF: R12 ASCII, katmanlar
(OUTLINE, HIDDEN, DIM, TEXT, TITLE), dış kütüphane ekleme. SVG ve DXF aynı ara modelden (`drawing/model.ts`) üretilsin.
Yeni dosyalar `apps/web-ui/src/drawing/` altında; mevcut dosyalarda yalnız menüye bağlama satırları.

## Kabul
- `cd apps/web-ui && npm ci` (gerekirse) `&& npm test && npm run build` yeşil; `tsconfig.tsbuildinfo` commit etme.
- vitest: örnek proje için ara modelde toplam boy ölçüsü = analitik boy, nozul sayısı = etiket sayısı, DXF'te `SECTION/ENTITIES/EOF`
  yapısı ve katman adları.
- Commit mesajı sonu: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- Kısa Türkçe rapor: dosyalar, yaklaşım, sınırlar.
