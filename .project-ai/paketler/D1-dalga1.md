# Dalga 1 — hızlı kazançlar (P01–P05)
Yol kuralı: yollar `pressure-vessel-suite/` köküne göre. Her paket kendi worktree dalında; yalnız SAHİP dosyalarına dokunur.
Ortak kabul: `cd apps/web-ui && npm test && npm run build` + `python -m pytest tests/unit tests/api -q` yeşil; tsconfig.tsbuildinfo commit dışı;
commit sonu `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; Türkçe ≤12 satır rapor. Sessiz kırpma yok (K4). Gizli değer yok.

## P01 Kalıcı proje deposu
Sahip: `apps/api/store.py`, yeni `apps/api/storage_supabase.py`, `apps/api/main.py` (yalnız depo seçimi), `tests/api/test_store*.py`, `apps/web-ui/src/api.ts` (yalnız kaydet/aç/revizyon çağrıları), `docs/deploy-vercel.md` (env bölümü), yeni `supabase/migrations/*.sql`.
- `ProjectStore` arayüzünü koru; `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` env varsa Supabase (PostgREST, httpx/urllib — yeni ağır bağımlılık yok), yoksa bellek içi.
- Tablo `projects(id, owner, data jsonb, revision int, updated_at)` + `project_revisions(project_id, revision, data, created_at)`; RLS açık, servis anahtarı yalnız sunucuda.
- Revizyon geçmişi uçları: `GET /api/projects/{id}/revisions`, `GET /api/projects/{id}/revisions/{n}`. Sahip kontrolü (require_owner) zorunlu.
- Testler Supabase'i taklit eder (gerçek ağ yok).

## P02 PDF rapor + U-1A
Sahip: `packages/report-engine/**`, `apps/web-ui/src/pages.tsx` içinde YALNIZ `ReportPage`, yeni `apps/web-ui/src/report-print.css`.
- Rapor HTML'ine A4 baskı CSS'i (@page, sayfa sonları, tablo başlığı tekrar, koyu tema yok). ReportPage'de "PDF indir" = rapor iframe'inde `print()`.
- U-1A Manufacturer's Data Report benzeri özet sayfa (rapor sonuna): proje verisinden dolan alanlar; dolmayan alan "—", sahte değer yok. Başlıkta "U-1A biçiminde özet — resmî form değildir".

## P03 Analitik gerilme alanı (çekirdek — Opus)
Sahip: `apps/web-ui/src/stress/analyticField.ts` (iskeleti değiştir, `buildStressField(project): StressField` imzası ve `stress/types.ts` SABİT), yeni `src/__tests__/analyticField.test.ts`.
- Membran: silindir σθ=PD/2t, σz=PD/4t (iç çap + korozyon dikkate, ince cidar; t/R>0,1 ise Lamé). Koni (α), elipsoidal/torisferik/küresel bombe meridyen-çevresel membran.
- Süreksizlik: bombe-gövde ve koni birleşiminde β=1,285/√(Rt) bandı, en yüksek ek gerilme yaklaşık değerle, birleşimden e^(−βx) sönümlü.
- Nozul: nozul ekseninden uzaklığa göre Kt≈2,5 (çift eksenli) halka, 2·d mesafede membrana sönüm; takviye pedi varsa etkin kalınlık artar.
- Koordinat: `vesselModel.componentFrames`/`nozzlePlacement` ile aynı çerçeve (eksen +Z). `allowable` = gövde malzemesinin S değeri (varsa).
- Test: D500/t5/P=1 MPa → gövde orta noktası hoop 50±0,5, axial 25±0,5; nozul kenarında vm ≥ 2×membran vm; birleşimden 5/β uzakta membrana döner.

## P04 Gerilme haritası görünümü
Sahip: `apps/web-ui/src/viewer.tsx`, `src/livePreview.tsx`, yeni `src/stress/heatmap.tsx`, `src/stress/colorScale.ts`, `src/__tests__/colorScale.test.ts`, `src/theme.css` (yalnız yeni `.stress-*` sınıfları).
- Önizlemeye "Gerilme" görünüm seçeneği: `buildStressField(project)` (stress/analyticField.ts — DOKUNMA) ile mesh vertex'leri boyanır (three `Lut` 'rainbow' veya kendi skala; vertexColors). Mesh dünya dönüşümü (yatay/dikey oryantasyon) tersine çevrilerek model çerçevesindeki nokta sorulur.
- Sağda dikey renk skalası (MPa, 0…maxVm, `allowable` varsa çizgiyle işaretli), fareyle üzerine gelince noktadaki vm/hoop/axial/zone.
- Bilgi kartı: "Kap içinde basınç her yerde aynıdır (giriş jetinin etkisi ~%0,04). Renkler duvardaki gerilmeyi gösterir." + etiket "Gösterge amaçlı — ASME tasarım onayı değildir".
- Şu anki iskelet sabit değer döndürür → harita tek renk görünür; bu beklenen, P03 merge'inde gerçek alan gelir.

## P05 Zick K katsayıları otomatik
Sahip: yeni `packages/supports/src/supports/zick_tables.py`, `packages/supports/src/supports/support_calc.py` (yalnız K değerinin boşsa tablodan alınması), `tests/unit/test_zick_tables.py`, `apps/web-ui/src/geometrySteps/Step5Supports.tsx` (yalnız saddle K alanlarının ipucu: "boş = tablodan (θ=…°)").
- Zick K1…K9 (Moss PVDM / Zick 1951), eyer açısı θ (120–180°) ve A/R oranına göre ara değerleme (lineer). Tablo dışı → hata/issue, kırpma yok. Her değerde kaynak satırı + `verified:false`.
- Kullanıcı K girdiyse o kullanılır; rapor "tablodan" / "kullanıcı" kaynağını yazar.
