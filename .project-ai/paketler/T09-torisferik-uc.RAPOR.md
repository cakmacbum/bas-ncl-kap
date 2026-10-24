# RAPOR T09-torisferik-uc

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:19
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T09 · Dal: ork/T09 · Taban: 63434ed

T09 torisferik uç — KISMİ
Dosyalar: `cases.py`, `run.py`, `results.json` · Test: `python -m tools.campaign.tur2.t09_torisferik_uc.run` → 20 vaka üretildi; rapor ve test sonucu doğrulanamadı.
Sözleşme: sapma: sonuçlarda 60 karşılaştırmanın tamamı KAPSAM_DIŞI görünüyor; istenen `tur2/T09-torisferik-uc.md` raporu oluşmadı.
Açık soru / risk: eksik knuckle yarıçapında BLOCKED yerine varsayılanla PASS davranışı doğrulanamadı.
```
 .../campaign-2026-10/tur2/T09-torisferik-uc.md     |   78 ++
 .../campaign/tur2/t09_torisferik_uc/__init__.py    |    1 +
 .../tools/campaign/tur2/t09_torisferik_uc/cases.py |   49 +
 .../campaign/tur2/t09_torisferik_uc/results.json   | 1086 ++++++++++++++++++++
 .../tools/campaign/tur2/t09_torisferik_uc/run.py   |   66 ++
 5 files changed, 1280 insertions(+)
```
