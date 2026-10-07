# PAKET P00c — Sonuç kataloğunun eksik tipleri (derin)

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 1b · Yürütücü: codex:yaz (reasoning high) · 2026-10-07

## Durum
P00b, `tools/campaign/RESULT_CATALOG.md` ve `tools/campaign/examples.py` dosyalarını yazdı. Ancak
yalnızca şu tipler için çalışan örnek var: thickness, mawp, nozzle_reinforcement, clash_check,
weld_validation, hydrotest, pneumatic_test, mdmt_check, leg_stress, skirt_stress.

## Görev
Aşağıdaki tiplerin her biri için `examples.py`'ye `example_<tip>()` ekle. Örnek, `harness.run_case`
ile koşunca o tipte **BLOCKED / NOT CALCULATED olmayan** en az bir satır üretmeli. Katalogda da her
tip için tetikleyen girdileri, zorunlu alanları, intermediate_values adlarını ve birimleri tamamla.
Tipler: saddle_stress (Zick K1..K7 ve geometri girdileri), base_plate_check, leg_section_check,
leg_weld_check, wrc_local_stress, flange_stress ve flange (Y/T/U/Z/F/V/f girdileri), junction_check
(koni-silindir), global_load_case ve global_load_combination ve load_combination (rüzgâr ve deprem yük
durumu), external_pressure ve external_pressure_check ve vacuum_stability, MDMT coincident ratio
girdisi, statik kafa için sıvı yüksekliği/yoğunluk girdisi, pressure_consistency, material_check,
fatigue.

**Nasıl yapılır:** suite kodunu (`packages/**`, `apps/**`) OKU. Hangi koşulun BLOCKED ürettiğini
koddan bul ve gereken girdiyi ver. Tahminle uğraşma. Bir tip fiziksel olarak tetiklenemiyorsa (örn.
koda bağlı değilse), dosya:satır kanıtıyla katalogda "tetiklenemez" diye yaz.

## Kural
- Katalog FORMÜL İÇERMEZ: yalnızca girdi/çıktı sözleşmesi yazılır (aileler temiz oda kalmalı).
- `packages/**` ve `apps/**` DEĞİŞTİRİLMEZ.
- Pytest için `--basetemp` olarak sistem TEMP dizinini ver.

## Kapsam
Yazacağın dosyalar: `pressure-vessel-suite/tools/campaign/examples.py`,
`tools/campaign/RESULT_CATALOG.md`, `tests/campaign/test_examples.py`.

## Kabul
`python -m pytest tests/campaign -q` yeşil ve her yeni example testte doğrulanmış olmalı. Raporda
tip bazında ÇALIŞIYOR / TETİKLENEMEZ (+kanıt) listesi olmalı.
