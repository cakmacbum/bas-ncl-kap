# PAKET P00b — Kampanya sonuç kataloğu + çalışan örnekler

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 1b · Yürütücü: codex:yaz
> Mod: yaz → ≤15 satır rapor · Tarih: 2026-10-07

## Neden
21 aile ajanı suite'i `tools/campaign/harness.py` ile koşturdu ama çoğu ilgili sonuç satırını bulamadı
ya da eksik girdiyle BLOCKED aldı: nozul, ayak, taban plakası, ankraj, kaynak, WRC, Zick saddle,
rüzgâr/deprem, flanş, koni bağlantısı, sıvı yüksekliği/statik kafa, MDMT coincident ratio.
Aile ajanları hesap kodunu okuyamıyor (temiz oda). **Sen okuyabilirsin.** Bu paket temiz oda dışıdır.

## Görev
Suite'in ürettiği HER `calculation_type` için (bul: `grep -rn "calculation_type=" packages apps`,
~30 tip; örn. thickness, mawp, nozzle_reinforcement, clash_check, weld_validation, hydrotest,
pneumatic_test, mdmt_check, external_pressure, external_pressure_check, vacuum_stability,
flange_stress, flange, saddle_stress, skirt_stress, leg_stress, leg_section_check, leg_weld_check,
base_plate_check, wrc_local_stress, junction_check, global_load_case, global_load_combination,
load_combination, pressure_consistency, material_check, fatigue) şunları çıkar:
(a) Hangi proje girdileri onu tetikler ve BLOCKED olmaması için hangileri zorunlu (alan adları + birimler).
(b) Dönen satır: component_type, clause_reference, status anlamı, intermediate_values adları (+birim),
    final_result anlamı.
(c) ÇALIŞAN örnek: `tools/campaign/examples.py` içinde `example_<calculation_type>() -> dict`
    (bases.py tabanlarını override ederek). `harness.run_case` ile koşunca o tip için BLOCKED /
    NOT CALCULATED olmayan en az bir satır üretmeli. Fiziksel olarak mümkün değilse nedenini katalogda yaz.
    Özellikle göster: sıvı yüksekliği/statik kafa, rüzgâr/deprem yük durumu, Zick K1..K7 girdisi, flanş
    Y/T/U/Z/F/V/f girdileri, koni junction girdileri, MDMT coincident ratio girdisi.

## Kural
- Katalog **FORMÜL İÇERMEZ.** Yalnızca girdi/çıktı sözleşmesi, alan adları, birimler ve durum anlamları
  yazılır, çünkü aileler temiz oda kalmalı.
- Hesap kodunu (`packages/**`, `apps/**`) DEĞİŞTİRME. `bases.py`'de gerçek bir hata görürsen düzelt
  ve raporla.

## Kapsam
Yazacağın dosyalar: `pressure-vessel-suite/tools/campaign/RESULT_CATALOG.md` (yeni),
`tools/campaign/examples.py` (yeni), `tests/campaign/test_examples.py` (yeni: her example_* çalışır ve
hedef tip BLOCKED değil), gerekirse `tools/campaign/bases.py`.

## Kabul
`python -m pytest tests/campaign -q --basetemp=%TEMP%/pvtmp` yeşil. Raporda şunlar olsun: tip sayısı,
örneği çalışan ve çalışmayan tipler (neden), aileleri en çok ilgilendiren 5 tuzak.
