# RAPOR T42-onarim-t11

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:40
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T42 · Dal: ork/T42 · Taban: 8a40751

T42 T11 — KISMİ
Dosyalar: `run.py`, `results.json`, `docs/validation/campaign-2026-10/tur4/T42-onarim-t11.md` · Test: `python -m tools.campaign.tur2.t11_yatay_tank_tarama.run` → başarılı; GEÇTİ=27, BULGU=36, BLOCKED=0, KAPSAM_DIŞI=81 · Sözleşme: uyuldu · Açık soru / risk: Rapor yolu paketin istediği `pressure-vessel-suite/docs/...` yerine worktree kökündeki `docs/...` konumuna yazıldı; 81 kapsam dışının nedeni raporda sınıflandırıldı.
```
 .../campaign-2026-10/tur4/T42-onarim-t11.md        |  92 ++++
 .../tur2/t11_yatay_tank_tarama/results.json        | 485 ++++++++++++++++++---
 .../campaign/tur2/t11_yatay_tank_tarama/run.py     |  31 +-
 3 files changed, 531 insertions(+), 77 deletions(-)
```
