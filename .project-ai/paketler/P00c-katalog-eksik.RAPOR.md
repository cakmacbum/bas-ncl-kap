# RAPOR P00c-katalog-eksik

> Yürütücü: Codex gpt-6-luna·high (yaz) · 2026-10-07 20:51
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/P00c · Dal: ork/P00c · Taban: ef69aa4

P00c Sonuç kataloğu — KISMİ  
Dosyalar: `pressure-vessel-suite/tools/campaign/examples.py`, `tools/campaign/RESULT_CATALOG.md`, `tests/campaign/test_examples.py`  
Test: `python -m pytest tests/campaign -q --basetemp $env:TEMP\p00c-pytest` → 8 geçti  
ÇALIŞIYOR: saddle_stress, base_plate_check, leg_section_check, leg_weld_check, wrc_local_stress, flange_stress, junction_check (topoloji incelemesi), global_load_case, global_load_combination, external_pressure, pressure_consistency.  
ÇALIŞIYOR: MAWP örneğine sıvı yoğunluğu/seviyesi girdileri eklendi; test örneklerin harness sonuçlarını doğruluyor.  
TETİKLENEMEZ: flange ve load_combination (EN hesapları desteklenmiyor; `code-en-13445/design_code.py:709-769`); fatigue (`:749-769`).  
TETİKLENEMEZ: external_pressure_check normal akışta üretilmiyor, vacuum_stability kabuk sonucu `external_pressure` adıyla dönüyor (`code-asme-viii-1/design_code.py:2029-2041`, `external_pressure/ext_pressure.py:325-358`).  
TETİKLENEMEZ: material_check yalnız eksik malzemede `NOT CALCULATED` (`calc-core/orchestrator.py:490-507`); MDMT coincident ratio alanı solver girişinde yok (`code-asme-viii-1/design_code.py:1320-1340`).  
Sözleşme: uyuldu · Açık risk: statik kafa girdileri mevcut, ancak fixture bileşen kotu sıfır olduğundan düzeltilmiş MAWP gösterilemiyor; EN yorulma/flanş ve listelenen sonuç tipleri kaynakta desteklenmiyor.
```
 .../tests/campaign/test_examples.py                |  18 ++++
 .../tools/campaign/RESULT_CATALOG.md               |  70 ++++++++++----
 pressure-vessel-suite/tools/campaign/examples.py   | 105 ++++++++++++++++++++-
 3 files changed, 175 insertions(+), 18 deletions(-)
```
