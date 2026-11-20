# Paket A1+A2 — MAWP düzeltmeleri (Gemini yazar, Claude şef test eder)

YOL KURALI: kod `pressure-vessel-suite/` altındadır; tüm yollar bu köke göredir.
KURALLAR: KOMUT (RunCommand) KULLANMA; yalnız dosya oku/düzenle. Test koşmayacaksın, şef koşar. Commit/push yok.
Yalnızca aşağıdaki dosyalara dokun. Satır numaraları kayabilir: önce fonksiyon adını ara.

## A1 — Düz kapak MAWP'de çap korozyonsuz (emniyetsiz yön)
Dosya: `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py`, `calculate_mawp`, `HeadType.FLAT` dalı (`d = D - 2 * C`).
Hata: `D` zaten korozyonlu iç çap (`inside_diameter + 2*C`); sonra `d = D - 2*C` ile korozyonsuz çapa dönülüp `flat_head_mawp`'e veriliyor,
ara değer yanlışlıkla `d_corroded` diye etiketli. Kalınlık yolu (`calculate_head_thickness`) korozyonlu D kullanıyor → tutarsız, MAWP ~%0,8 yüksek.
Yap:
1. MAWP dalında `d = D` (korozyonlu) kullan; `d_corroded` ara değeri bu olsun.
2. `formulas.flat_head_mawp` (`packages/code-asme-viii-1/src/code_asme_viii_1/formulas.py`) içindeki `CA` kullanımını oku: t'den CA düşüyor, çapa dokunmuyor olmalı; çift düşme/çift ekleme olmasın. Gerekirse yalnız yorum ekle, formülü değiştirme.
3. Yeni test dosyası `tests/` altında mevcut düz kapak/MAWP testlerinin desenini izleyerek (önce `grep -rn flat_head_mawp tests` ile bul): gidiş-dönüş testi — CA>0 iken kalınlık yolunun verdiği t_required ile MAWP hesabı ≈ P (±%0,1).
4. Dairesel olmayan kapak (`flat_z_factor`) için MAWP dalı yoksa sessiz geçme: açık `result.set_not_calculated("...")` ver.

## A2 — MAWP satırı MAWP < P iken PASS görünüyor
ASME: aynı `calculate_mawp` sonu: `result.final_result = mawp ... result.set_pass()` koşulsuz.
EN: `packages/code-en-13445/src/code_en_13445/design_code.py`, `calculate_mawp` sonu `result.set_pass()` (+ ardından `flat_review` / `_cap_unverified` mantığı KORUNACAK).
Yap:
1. Satır durumu kendi kontrolünden türesin (DEC-008): `P = dc.design_pressure` (ASME'de `dc` değişkeni fonksiyonda zaten var; yoksa `input_data["design_conditions"]`).
   `mawp < P` ise `result.set_fail(P / mawp)` (mawp<=0 ise `set_fail(0.0)` DEĞİL, utilization için büyük bir sayı yerine mevcut desene bak: `set_fail(...)` imzası `packages/calc-core/src/calc_core/result.py`); aksi `result.set_pass(P / mawp)`.
   Uyarı ekle: "MAWP (x MPa) tasarım basıncının (y MPa) altında".
2. `packages/calc-core/src/calc_core/orchestrator.py` ~446–510: statik kafa düzeltmesinde `mawp_r.final_result = corrected_mawp` sonrası, `corrected_mawp < tasarım basıncı` ise `mawp_r.set_fail(...)` + uyarı. (Bu dalda zaten `corrected_mawp <= 0` için set_fail var, onu bozma.)
3. `get_global_mawp` (orchestrator ~satır 60) ve global MAWP satırı: global MAWP < tasarım basıncı ise aynı FAIL kuralı.
4. Mevcut testlerde MAWP satırı PASS bekleyen yerleri bul (`grep -rn "mawp" tests | grep -i pass`) ve bu değişiklikle kırılacaklarsa SAYISINI ve dosyalarını raporda yaz; yalnız MAWP<P olmayan vakalar PASS kalmalı. Yeni testler: MAWP<P → FAIL (ASME gövde + EN), MAWP≥P → PASS.

## Çıktı (DONUS)
Sonunda tek mesaj: değiştirilen dosyalar, her maddenin ne yaptığı, kırılması muhtemel mevcut testler, emin olmadığın noktalar. Uydurma yok.
