# D5 — EN 13445 eksikleri + eski açık işler (supervisor, 2026-11-06)
Kaynak taramalar: S01-en13445-tarama.DONUS.md, S02-eski-isler-tarama.DONUS.md (paket ajanları ilgili bölümleri okur).
Yollar `pressure-vessel-suite/` kökü. Ortak kabul (her paket): `cd apps/web-ui && npm test && npm run build` +
`python -m pytest tests/unit tests/api tests/faz4 tests/faz5 -q` yeşil; tsconfig.tsbuildinfo commit dışı; commit sonu
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; Türkçe ≤12 satır RAPOR. K4/K6: formül/katsayı bellekten emin değilse
koda gömülmez → BLOCKED_CODE_DATA veya kullanıcı girdisi; EN sonuçları `verified=False` → PASS en fazla REVIEW_REQUIRED.

## Başarı kriterleri (PASS senaryoları)
1. EN 13445 kodlu proje hesaplanınca rapordaki kontrol listesi ASME ile aynı başlıkları içerir; EN'de hesaplanmayan her kontrol
   açık bir satır olarak NOT_CALCULATED/OUT_OF_SCOPE + nedenle görünür (sessiz boşluk sıfır) — test bunu başlık başlık doğrular.
2. Dikey kapta sıvı seviyesi + kot verildiğinde hidrotest her bileşende P_test + ρ_su·g·h ile kontrol edilir; ara değerlerde h görünür.
3. Nozula "açıklık kaynak verimi E1" girildiğinde takviye hesabı E1'i kullanır (UG-37: E1=0,85 → mevcut alan A1 düşer, marj azalır; test).
4. `npm run e2e` 3 temel tankı (dikey ayaklı, yatay eyerli, etekli kolon) UI'dan açıp hesaplatır, sonuç kartı + ekran görüntüsü üretir.
5. EN 13445'te koni, düz kapak ve torisferik tam prosedür hesap satırı üretir (REVIEW_REQUIRED/BLOCKED dürüst), el hesabı testleri geçer.

## Varsayımlar
- Lisanslı EN 13445 metni yok → EN paketleri kaynak maddesini yorumda belirtir, `verified=False`; grafik/tablo verisi gereken yer BLOCKED.
- Su yoğunluğu 1000 kg/m³, g=9,81 (hidrotest varsayımı sonuca yazılır). E1 dikişten otomatik çıkarılmaz (kullanıcı girer).
- e2e: tarayıcı indirmeden sistemdeki Edge (`channel:'msedge'`) ile; yalnız `@playwright/test` npm paketi eklenir.

## Dalga A (paralel; dosya sahipliği ayrık)
| Paket | Kim | Sahip dosyalar |
|---|---|---|
| E01 EN sessiz boşluklar | Claude Sonnet | code-en-13445 `design_code.py` (override'lar), yeni `tests/faz4/test_faz4_en13445_gaps.py`, `docs/calculation-coverage.md`, `docs/limitations.md` (B-31 çelişkisi) |
| H01 Hidrotest statik basınç (T-2.8) | Claude Opus (çekirdek) | code-asme-viii-1 `design_code.py` hidrotest bölümü + `formulas.py`, `calc_core/orchestrator.py`, `calc_core/hydrostatics.py`, testler. EN hidrotestine DOKUNMA (E01 orada) — EN için yalnız rapora not |
| N01 Nozul E1 (T-2.14) | Claude Sonnet | domain `geometry.py` Nozzle alanı, ASME `design_code.py` yalnız reinforcement çağrısı (~1151), web-ui nozul formu + types.ts, test |
| X01 Playwright e2e (T-2.12) | Codex Luna | yeni `apps/web-ui/e2e/`, `playwright.config.ts`, package.json script/devDep; uygulama koduna dokunmaz |

## Dalga B (A bittikten sonra, sıralı — aynı dosyalar)
| E02 Koni + düz kapak + MAWP koni (EN) | Claude Opus | code-en-13445 `formulas.py`, `design_code.py` |
| E03 Torisferik tam prosedür + B-09 (EN) | Claude Opus | aynı |
| E04 fa/ft, kaynak sınıfı→z, pnömatik test (EN) | Claude Opus | aynı |
| E05 Dış basınç + nozul takviyesi (EN, yeni modüller) | Claude Opus | yeni modüller + design_code bağlama |
Flanş, yorulma, yük kombinasyonu (EN) → FUTURE (NOT NOW).

## Ek paket G01 — API geometri tutarlılığı (X01 bulgusu) — Claude Sonnet
Sorun: `tools/campaign/bases.py` tabanlarında HEAD-R iç çapı 800, gövde 1000 (3 tankta) ve dikey ayak 600 mm (UI min 802, LEG_TOO_SHORT).
UI geometri doğrulaması (`apps/web-ui/src/geometryValidation.ts`) bunları reddediyor, API ise hatasız hesaplıyor → kampanya sonuçları tutarsız
geometride koşmuş olabilir. Yapılacak: (1) UI'daki BLOKLAYICI geometri kurallarının (bombe/koni ucu çapı = komşu gövde çapı, ayak boyu alt sınırı vb.)
Python karşılığı — domain `VesselProject` doğrulayıcısı veya orchestrator ön kontrolü; geçersiz geometri hesap öncesi açık hata/BLOCKED (sessiz hesap yok).
Toleransı UI ile aynı tut. (2) `bases.py` verilerini düzelt; kampanya/regresyon testlerinde beklenen değerler değişirse nedenini rapora yaz (gevşetme yok).
Sahip dosyalar: packages/domain (validator), calc_core/orchestrator.py ön kontrol, tools/campaign/bases.py, ilgili testler. EN 13445 dosyalarına DOKUNMA (E03 orada).
