# Dalga 2 düzeltmeleri + Dalga 3 (imalat çıktıları)
Yol kuralı: yollar `pressure-vessel-suite/` köküne göre. Ortak kabul: `cd apps/web-ui && npm test && npm run build`
+ `python -m pytest tests/unit tests/api tests/faz5 -q` yeşil; tsconfig.tsbuildinfo commit dışı; commit sonu
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; Türkçe ≤12 satır rapor. K4/K6: uydurma katsayı/formül yok,
emin olunmayan şey BLOCKED/varsayım olarak sonuca yazılır.

## F1 — Ayak WRC moment normalizasyonu (β) — Opus, hesap çekirdeği
Sorun: `packages/supports/src/supports/wrc.py` `_moment_contribution` WRC 107/537 moment eğrilerini
N = K·M/Rm², M = K·M/Rm ile ölçekliyor; bülten normalizasyonu N·Rm²·β/M ve M·Rm·β/M → β eksik (sonuç 1/β kat büyük).
Ayak (dikdörtgen ped) için ML ve MC eğrilerinin normalizasyon β'sı C_L/Rm ya da C_C/Rm DEĞİL, bültenin eşdeğer β'sı;
formülünden emin değilsen KODA GÖMME. Yapılacak:
- `point_stress_resultants` / `evaluate_point` / `evaluate_all_points`'e `beta_ML`, `beta_MC` (Optional) ekle; ilgili moment
  yükü ≠ 0 iken β yoksa ValueError (eksik β sıfır/1 sayılmaz). Formül: N = K·M/(Rm²·β), M = K·M/(Rm·β).
- Kullanıcı girdisi: `Support`'a (domain/geometry.py) `wrc_beta_ML`, `wrc_beta_MC` Optional alanları — "katsayıyı okuduğunuz
  eğrinin β değeri". `leg_detail.py`: moment aktif ve β yoksa BLOCKED_MISSING_INPUT; mesajda β_L, β_C ve bülten ipucu.
- UI: `apps/web-ui/src/pages.tsx` ~115 civarındaki WRC katsayı girişine iki sayı alanı; `types.ts` Support tipine iki alan.
- Testleri güncelle (`tests/faz5/test_wrc_local_stress.py`, `test_leg_detail.py`): eski 1/Rm² beklentileri β'lı forma; β eksik → hata.
- `packages/nozzles/nozzle_loads.py` (P07) zaten β'lı — dokunma; tutarlılık için bir karşılaştırma testi yeterli.

## F2 — BOM: eyer ve profil ayak kütlesi — Sonnet
`packages/calc-core/src/calc_core/bom.py` eyer (saddle) ve channel/box/angle ayak için None dönüyor. Eyer: mevcut eyer geometri
alanlarından (web/taban/kanat plakası, aşınma plakası) plaka hacmi × yoğunluk. Profil ayak: `packages/supports/src/supports/sections.py`
kesit alanı (varsa) × boy × yoğunluk. Gerekli boyut yoksa yine None + uyarı (uydurma yok). Test ekle.

## P11 — Sac açınım şablonları — Sonnet
Yeni `apps/web-ui/src/flat/` (saf TS, three bağımlılığı yok) + DXF yazıcı (R12 ASCII, LINE/LWPOLYLINE/ARC/TEXT, kendin yaz, dış kütüphane yok).
- Gövde halkası: dikdörtgen (π·Dm × L), kaynak ağzı payı opsiyonel. Koni: halka dilimi (eğik boy, açınım açısı Dm farkından).
- Bombe: taç+hamut segment (petal) açınımı — yaklaşık yöntem, "yaklaşık, kalıp üreticisiyle doğrula" notu. Yarımküre/elipsoid için n petal.
- Nozul-gövde kesişim şablonu: silindir-silindir kesişim eğrisi (nozul borusu açınımı, sargı şablonu), radyal ve offset nozul.
- Nötr eksen (orta yüzey) kullan. UI: Rapor & Çıktı sayfasına "Açınım şablonları" kartı: SVG önizleme + parça başına DXF indir.
- vitest: dikdörtgen çevre, koni açısı, kesişim eğrisinin uç değerleri (θ=0 → 0, θ=90° → r²/… el hesabı).
