# RAPOR P11-harness-clientid

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:13
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/P11 · Dal: ork/P11 · Taban: fe21b34

P11 harness X-Client-Id + aggregate raporu — TAMAM  
Dosyalar: `tools/campaign/harness.py`, `tools/campaign/aggregate.py`, `docs/validation/campaign-2026-10/OZET.md`, `docs/validation/campaign-2026-10/ozet.csv`  
Test: `python -m pytest tests/campaign -q --basetemp "$env:TEMP/pv-p11" -p no:cacheprovider` → 9 geçti  
Test: `python -m pytest tests -q --basetemp "$env:TEMP/pv-p11b" -p no:cacheprovider` → 934 geçti, 1 atlandı  
Sözleşme: uyuldu  
Açık soru / risk: Yok
```
 .../docs/validation/campaign-2026-10/OZET.md       | 73 +++++++++++++-------
 .../docs/validation/campaign-2026-10/ozet.csv      | 32 ++++-----
 pressure-vessel-suite/tools/campaign/aggregate.py  | 79 +++++++++++++++-------
 pressure-vessel-suite/tools/campaign/harness.py    |  9 ++-
 4 files changed, 126 insertions(+), 67 deletions(-)
```
