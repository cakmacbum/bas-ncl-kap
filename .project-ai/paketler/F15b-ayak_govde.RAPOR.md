# RAPOR F15b-ayak_govde

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:45
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F15b · Dal: ork/F15b · Taban: ef69aa4

F15b ayak-govde — TAMAM  
Dosyalar: `tools/campaign/families/f15_ayak_govde/{oracle.py,variants.py,run.py,results.json}` · `docs/validation/campaign-2026-10/F15-ayak_govde.md`  
Test: `python -m tools.campaign.families.f15_ayak_govde.run` → başarılı; 84 sayısal kıyas, 84 DOĞRULANDI, 2 KAPSAM_DIŞI  
Sözleşme: uyuldu; temiz oda beyanı raporda, commit atılmadı  
Açık soru / risk: K3-13 ve K3-14 API satırlarında gerekli ara değerler eksik; bu vakalar kıyas dışı.
```
 .../validation/campaign-2026-10/F15-ayak_govde.md  |   43 +-
 .../campaign/families/f15_ayak_govde/oracle.py     |   34 +-
 .../campaign/families/f15_ayak_govde/results.json  | 1836 +++++++++++++++-----
 .../tools/campaign/families/f15_ayak_govde/run.py  |   42 +-
 .../campaign/families/f15_ayak_govde/variants.py   |   40 +-
 5 files changed, 1486 insertions(+), 509 deletions(-)
```
