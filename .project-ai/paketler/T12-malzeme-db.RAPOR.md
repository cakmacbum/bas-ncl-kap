# RAPOR T12-malzeme-db

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T12 · Dal: ork/T12 · Taban: 63434ed

T12 malzeme-db — KISMİ  
Dosyalar: `tools/campaign/tur2/t12_malzeme_db/{cases.py,run.py,results.json}`, `tools/campaign/tur2/__init__.py`, `docs/validation/campaign-2026-10/tur2/T12-malzeme-db.md` · Test: `python -m tools.campaign.tur2.t12_malzeme_db.run` → 20 vaka üretildi: 2 GEÇTİ, 18 KAPSAM_DIŞI, 0 BULGU · Sözleşme: uyuldu · Açık soru / risk: M1 ve M2’de sıcaklık eğrisi verisi olmadığından S(T), BLOCKED aralığı ve interpolasyon davranışları doğrulanamadı.
```
 .../campaign-2026-10/tur2/T12-malzeme-db.md        |  17 ++
 .../tools/campaign/tur2/__init__.py                |   0
 .../tools/campaign/tur2/t12_malzeme_db/cases.py    |  33 +++
 .../campaign/tur2/t12_malzeme_db/results.json      | 224 +++++++++++++++++++++
 .../tools/campaign/tur2/t12_malzeme_db/run.py      |  39 ++++
 5 files changed, 313 insertions(+)
```
