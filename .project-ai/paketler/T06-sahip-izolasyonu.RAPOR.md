# RAPOR T06-sahip-izolasyonu

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T06 · Dal: ork/T06 · Taban: 63434ed

T06 sahip izolasyonu — KISMİ
Dosyalar: `tools/campaign/tur2/t06_sahip_izolasyonu/{cases.py,run.py,results.json}`, `tools/campaign/tur2/__init__.py`, `docs/validation/campaign-2026-10/tur2/T06-sahip-izolasyonu.md` · Test: `python -m tools.campaign.tur2.t06_sahip_izolasyonu.run` → 27 vaka; 17 geçti, 10 bulgu; çıkış 0 · Sözleşme: uyuldu · Açık soru / risk: `apps/api/auth.py:118` büyük harfli UUID başlığını kabul ediyor (ORTA; aynı UUID sahibine normalleşiyor). Proje silme rotası tanımlı değil.
```
 .../campaign-2026-10/tur2/T06-sahip-izolasyonu.md  |  15 +
 .../tools/campaign/tur2/__init__.py                |   1 +
 .../campaign/tur2/t06_sahip_izolasyonu/__init__.py |   1 +
 .../campaign/tur2/t06_sahip_izolasyonu/cases.py    |  47 ++
 .../tur2/t06_sahip_izolasyonu/results.json         | 628 +++++++++++++++++++++
 .../campaign/tur2/t06_sahip_izolasyonu/run.py      |  86 +++
 6 files changed, 778 insertions(+)
```
