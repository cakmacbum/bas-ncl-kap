# RAPOR R09-oracle-nozul

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:21
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/R09 · Dal: ork/R09 · Taban: 63434ed

R09 f09_nozul_takviye — TAMAM
Dosyalar: oracle.py, run.py, results.json, F09-nozul_takviye.md · Test: `python -m tools.campaign.families.f09_nozul_takviye.run` → hatasız; 28 DOĞRULANDI, 2 SAPMA, 2 KAPSAM_DIŞI · Sözleşme: uyuldu · Açık soru / risk: eff-0.7 ve eff-0.85 vakalarında suite alanı oracle’dan düşük; kaynak verimi girdisinin hesaba katılmaması olası, emniyetsiz yönde.
SONUÇ: DOĞRULANDI=28 · SAPMA=2 · FORMÜLASYON_FARKI=0 · KAPSAM_DIŞI=2
```
 .../campaign-2026-10/F09-nozul_takviye.md          |  82 +++----
 .../campaign/families/f09_nozul_takviye/oracle.py  |   7 +-
 .../families/f09_nozul_takviye/results.json        | 244 ++++++++++-----------
 .../campaign/families/f09_nozul_takviye/run.py     |   5 +-
 4 files changed, 157 insertions(+), 181 deletions(-)
```
