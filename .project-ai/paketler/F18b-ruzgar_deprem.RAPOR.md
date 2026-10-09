# RAPOR F18b-ruzgar_deprem

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:54
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F18b · Dal: ork/F18b · Taban: 4e986f3

F18b ruzgâr-deprem — TAMAM  
Dosyalar: `oracle.py`, `variants.py`, `run.py`, `results.json`, `F18-ruzgar_deprem.md` · Test: `python -m tools.campaign.families.f18_ruzgar_deprem.run` → başarılı; 36 sayısal kıyas DOĞRULANDI · Sözleşme: uyuldu · Açık soru / risk: Rüzgâr basıncı veya deprem kuvveti hesabı katalogda yok; kıyaslar `global_load_case` yük bileşenleriyle sınırlı. K3-19 yayımlanmış ASCE vakası API’de eşleşmediği için TEK_KAYNAK kaldı.
```
 .../campaign-2026-10/F18-ruzgar_deprem.md          |  40 +-
 .../campaign/families/f18_ruzgar_deprem/oracle.py  |  26 +-
 .../families/f18_ruzgar_deprem/results.json        | 978 +++++++++++----------
 .../campaign/families/f18_ruzgar_deprem/run.py     |  36 +-
 .../families/f18_ruzgar_deprem/variants.py         |  73 +-
 5 files changed, 599 insertions(+), 554 deletions(-)
```
