# PAKET V02 — 2:1 eliptik bombe UG-32(d): SAPMA teyidi (bulan ≠ doğrulayan)

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Dalga 2 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤15 satır rapor

## Bağlam
M2 doğrulama kampanyasında `f02_bombe_eliptik` ailesi suite sonuçlarını temiz-oda bir oracle ile kıyasladı.
Sonuç: 2 SAPMA (emniyetli yön bildirildi). Kaynaklar:
- `pressure-vessel-suite/tools/campaign/families/f02_bombe_eliptik/results.json` (vaka, girdi, suite, reference, diff_pct, verdict)
- `pressure-vessel-suite/tools/campaign/families/f02_bombe_eliptik/oracle.py`
- `pressure-vessel-suite/docs/validation/campaign-2026-10/F02-bombe_eliptik.md`

Sen **doğrulayan** rolündesin. Oracle'ı yazan ajan değilsin; ikisinden de bağımsız düşün.

## Görev
1. SAPMA vakalarını grupla (aynı kök neden → tek grup). Her gruptan en az 2 temsilci vaka seç.
2. Her temsilci için ASME VIII-1 (veya ilgili EN) formülünü **kendi bilginle** yaz ve elle/küçük bir
   Python betiğiyle hesapla. Ara değerleri göster (R, D, S, E, P, CA, mill tol, t_req, MAWP...).
3. Bu teyitte suite kodunu OKUYABİLİRSİN (`packages/**`). Amaç, farkın kaynağını satır düzeyinde
   bulmak. Oracle'ı da oku.
4. Her grup için hüküm ver. Hüküm şu üçünden biridir:
   - **SUITE_HATASI**: suite yanlış. Dosya:satır, yanlış formül/terim ve doğru ifade.
   - **ORACLE_HATASI**: oracle yanlış (ör. CA/mill tol uygulama sırası, iç/dış yarıçap, yuvarlama).
   - **FORMÜLASYON_FARKI**: ikisi de Kodda geçerli farklı yollar. Kod maddesini göster.
5. Her SUITE_HATASI için şunları belirt: yön (EMNİYETSİZ: suite gereken kalınlığı az/MAWP'yi fazla
   veriyorsa; EMNİYETLİ: tersi), büyüklük (%), etkilenen vaka sayısı ve önerilen düzeltme.
   Düzeltmeyi **uygulama**; yalnız öner.

## Kapsam
Yalnızca şu dosyaya yaz: `pressure-vessel-suite/docs/validation/campaign-2026-10/teyit/V02-f02_bombe_eliptik.md`.
Yardımcı betiğin varsa aynı klasöre `V02_calc.py` olarak koy. Başka hiçbir dosyayı değiştirme
(`packages/**`, `apps/**`, `tools/**` dahil). Pytest kullanacaksan `--basetemp` ile sistem TEMP dizinini
ver. K6: Kod metninden paragraf veya tablo kopyalama; yalnız madde numarası ve formül sembolleri.

## Kabul
Teyit dosyasında şunlar bulunur: grup tablosu (grup, vaka sayısı, hüküm, yön, %), temsilci vakaların
el hesabı ve SUITE_HATASI için dosya:satır kanıtı. Rapor sonunda tek satır özet:
`HÜKÜM: suite_hatası=N (emniyetsiz=a) · oracle_hatası=M · formülasyon=K`.
