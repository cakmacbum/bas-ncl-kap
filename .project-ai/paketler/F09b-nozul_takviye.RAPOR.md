# RAPOR F09b-nozul_takviye

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:47
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F09b · Dal: ork/F09b · Taban: ef69aa4

F09b nozul takviyesi — TAMAM  
Dosyalar: `variants.py`, `run.py`, `oracle.py`, `results.json`, `F09-nozul_takviye.md` · Test: `python -m tools.campaign.families.f09_nozul_takviye.run` → başarılı; 32 vaka, 30 sayısal kıyas, 2 KAPSAM_DIŞI · Sözleşme: uyuldu · Açık soru / risk: 30 SAPMA’nın tamamı emniyetli yönde (%1,278–%2,158); socket_weld ve threaded API’de hesap satırı üretmedi.
```
 .../campaign-2026-10/F09-nozul_takviye.md          |  86 ++--
 .../campaign/families/f09_nozul_takviye/oracle.py  |   4 +-
 .../families/f09_nozul_takviye/results.json        | 466 ++++++++++++++-------
 .../campaign/families/f09_nozul_takviye/run.py     |  13 +-
 .../families/f09_nozul_takviye/variants.py         |  20 +-
 5 files changed, 389 insertions(+), 200 deletions(-)
```
