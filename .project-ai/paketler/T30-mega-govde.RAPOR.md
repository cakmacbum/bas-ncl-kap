# RAPOR T30-mega-govde

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:23
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T30 · Dal: ork/T30 · Taban: 75a631c

T30 mega-gövde — KISMİ  
Dosyalar: `tools/campaign/tur3/mega_govde/run.py`, `results.json`, `__init__.py`; `docs/validation/campaign-2026-10/tur3/T30-mega-govde.md`  
Test: `python -m tools.campaign.tur3.mega_govde.run` → 110 vaka üretildi; 49 geçti, 1 bulgu, 60 beklenen engel  
Sözleşme: uyuldu  
Açık soru / risk: API 50 proje sınırına ulaştı; kalan çağrılar HTTP 429 “Project limit reached” ile blocked kaydedildi.
```
 .../campaign-2026-10/tur3/T30-mega-govde.md        |   15 +
 .../tools/campaign/tur3/mega_govde/__init__.py     |    1 +
 .../tools/campaign/tur3/mega_govde/results.json    | 3433 ++++++++++++++++++++
 .../tools/campaign/tur3/mega_govde/run.py          |  149 +
 4 files changed, 3598 insertions(+)
```
