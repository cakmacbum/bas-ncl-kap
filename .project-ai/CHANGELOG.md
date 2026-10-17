# CHANGELOG

## 2026-10-06 — M1 STEP içe aktarma
- STEP → dönel kap tanıma (`cad_engine.step_import`), `POST /api/import/step` (ham gövde, süreç izolasyonu, 413/415/429/503/504)
- Geometri adımında "Modelden içe aktar": onay çekmecesi (güven rozetleri, seçici uygulama, nozullar hep yeni), STL görüntüleme sekmesi
- limitations B-34…B-37

## 2026-10-07…18 — M2 tank doğrulama kampanyası
- 21 aile (F01–F21) + Tur 2–7: harness (`tools/campaign/`), bağımsız oracle'lar, 2.000+ doğrulanmış vaka, `docs/validation/campaign-2026-10/`
- Düzeltmeler: dış korozyon payı MAWP/nominal (B-01/B-02) · statik kafa gerçek (B-10: `liquid_level_mm`, `component_bottom_elevations`) ·
  raporda koni (B-11) · rapor/uyumluluk HTML kaçışı (B-12/B-12b) · harness sahip tavanı (D-03)
- Test: 934 → 959 geçti
