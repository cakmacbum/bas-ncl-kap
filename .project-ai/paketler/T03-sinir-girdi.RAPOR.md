# RAPOR T03-sinir-girdi

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:20
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T03 · Dal: ork/T03 · Taban: 63434ed

T03 sınır-girdi — TAMAM
Dosyalar: `cases.py`, `run.py`, `results.json`, `T03-sinir-girdi.md`, `__init__.py`
Test: `python -m tools.campaign.tur2.t03_sinir_girdi.run` → çıkış 0, 57 vaka
Dağılım: 32 geçti · 25 bulgu · 0 kapsam dışı; 5 vakada HTTP 500, diğer bulgularda HTTP 200 ile PASS/FAIL/REVIEW REQUIRED
Sözleşme: uyuldu
Açık soru / risk: Bulgular `apps/api/main.py:96-102`, `packages/domain/src/domain/conditions.py:24-29` ve `packages/domain/src/domain/geometry.py:22-35` çevresinde; suite koduna dokunulmadı.
```
 .../campaign-2026-10/tur2/T03-sinir-girdi.md       |   21 +
 .../campaign/tur2/t03_sinir_girdi/__init__.py      |    1 +
 .../tools/campaign/tur2/t03_sinir_girdi/cases.py   |   79 ++
 .../campaign/tur2/t03_sinir_girdi/results.json     | 1272 ++++++++++++++++++++
 .../tools/campaign/tur2/t03_sinir_girdi/run.py     |   67 ++
 5 files changed, 1440 insertions(+)
```
