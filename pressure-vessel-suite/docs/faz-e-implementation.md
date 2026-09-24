# Faz E — Doğrulama ve ürünleştirme

Bu belge Faz E altyapısının çalışma sözleşmesidir.

## E1 — Verification & validation

- `calc_core.verification.validate_result()` her sonucu NaN/inf, eksik `final_result`, negatif kullanım oranı ve uyarılı `PASS` açısından tarar.
- `GoldenCase` ve `verify_golden_case()` bağımsız referans değerlerini mutlak + bağıl toleransla karşılaştırır.
- `assert_monotonic()` property/regression testlerinde basınç–kalınlık gibi beklenen yönleri kilitler.
- `validate_suite()` bir koşunun tüm sonuçları için yayınlanabilirlik özeti üretir.

## E2 — Kalıcı ürün altyapısı

- `domain.run_store.CalculationRunStore` SQLite transaction kullanır.
- Calculation run payload'ı SHA-256 ile mühürlenir; mevcut run güncellenmez, yeni revision/run eklenir.
- Audit olayları, rol bazlı approval/sign-off ve attachment hash metadata'sı transaction içinde saklanır.
- SQLite online backup API ile tutarlı yedek alınabilir.
- JSON proje yazımı geçici dosya + `fsync` + atomic replace kullanır.

## E3 — Raporlama

Raporun 24. bölümü yöneten sonuçları, durumları, madde referanslarını ve tüm `FAIL`/
`REVIEW REQUIRED`/`BLOCKED`/`NOT CALCULATED` eksiklerini listeler. Böylece eksik kapsam
raporda sessizce PASS olarak görünmez; rapor hash'i ve mevcut traceability bloğu korunur.

## CI regression lock

Faz E testleri `tests/faz_e/test_faz_e_productization.py` altındadır. Tam suite çalıştırması
CI'da zorunludur; CAD/WeasyPrint gibi opsiyonel native bağımlılıklar yoksa ilgili testler
skip edilir, hesap doğrulama testleri skip edilmez.
