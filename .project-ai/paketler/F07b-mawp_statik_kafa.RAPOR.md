# RAPOR F07b-mawp_statik_kafa

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:46
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F07b · Dal: ork/F07b · Taban: ef69aa4

F07b statik kafa — TAMAM
Dosyalar: `oracle.py`, `run.py`, `results.json`, `F07-mawp_statik_kafa.md` · Test: `python -m tools.campaign.families.f07_mawp_statik_kafa.run` → başarılı; 30 vaka: DOĞRULANDI 28, TEK_KAYNAK 1, KAPSAM_DIŞI 1 · Sözleşme: uyuldu · Açık soru / risk: Katalogda sıvı yüksekliği/datum girdisi bulunmadığından statik kafa ekseni bağımsız doğrulanamadı.
```
 .../campaign-2026-10/F07-mawp_statik_kafa.md       |  41 ++--
 .../families/f07_mawp_statik_kafa/oracle.py        |  18 +-
 .../families/f07_mawp_statik_kafa/results.json     | 220 ++++++++++-----------
 .../campaign/families/f07_mawp_statik_kafa/run.py  |   7 +-
 4 files changed, 147 insertions(+), 139 deletions(-)
```
