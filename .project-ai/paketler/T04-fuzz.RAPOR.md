# RAPOR T04-fuzz

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:20
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T04 · Dal: ork/T04 · Taban: 63434ed

T04 Rastgele proje fuzz — KISMİ  
Dosyalar: `tools/campaign/tur2/t04_fuzz/{cases.py,run.py,results.json,__init__.py}`, `tools/campaign/tur2/__init__.py`, `docs/validation/campaign-2026-10/tur2/T04-fuzz.md` · Test: `python -m tools.campaign.tur2.t04_fuzz.run` → 300 vaka; 50 GEÇTİ, 250 KAPSAM_DIŞI (429 hız sınırı), 0 BULGU · Sözleşme: uyuldu · Açık soru / risk: 250 vakada hesap sonucu alınamadığı için fuzz kontrolleri tamamlanamadı.
```
 .../validation/campaign-2026-10/tur2/T04-fuzz.md   |     19 +
 .../tools/campaign/tur2/__init__.py                |      1 +
 .../tools/campaign/tur2/t04_fuzz/__init__.py       |      0
 .../tools/campaign/tur2/t04_fuzz/cases.py          |     53 +
 .../tools/campaign/tur2/t04_fuzz/results.json      | 147744 ++++++++++++++++++
 .../tools/campaign/tur2/t04_fuzz/run.py            |     54 +
 6 files changed, 147871 insertions(+)
```
