# RAPOR P10-aggregate

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:07
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/P10 · Dal: ork/P10 · Taban: 2012cb4

P10 kampanya özeti — KISMİ  
Dosyalar: `tools/campaign/aggregate.py`, `tests/campaign/test_aggregate.py`, `docs/validation/campaign-2026-10/OZET.md`, `docs/validation/campaign-2026-10/ozet.csv`  
Test: `python -m tools.campaign.aggregate` → başarılı; etiketlerin tamamı kanonik  
Test: `python -m pytest tests -q -x --basetemp $env:TEMP/pv-p10` → 116 geçti, 1 kaldı; `test_examples.py` hatası: Missing or invalid X-Client-Id  
Test: `python -m pytest tests/campaign/test_aggregate.py -q` → 1 geçti  
Sözleşme: uyuldu  
Açık soru / risk: FNN-*.md ve teyit/V*.md raporları bulunamadı; KAPSAM_DIŞI nedenleri derlenemedi. SAPMA aileleri özette listeli, ancak teyitleri yapılamadı.
```
 .../docs/validation/campaign-2026-10/OZET.md       | 1361 ++++++++++++++++++++
 .../docs/validation/campaign-2026-10/ozet.csv      | 1303 +++++++++++++++++++
 .../tests/campaign/test_aggregate.py               |    9 +
 pressure-vessel-suite/tools/campaign/aggregate.py  |   61 +-
 4 files changed, 2730 insertions(+), 4 deletions(-)
```
