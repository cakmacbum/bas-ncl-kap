# RAPOR P00-harness

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:03
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/P00 · Dal: ork/P00 · Taban: c6c01a8

P00 harness — TAMAM  
Dosyalar: `tools/__init__.py`, `tools/campaign/` (harness, bases, compare, aggregate, README, families init), `tests/campaign/` · Test: `python -m pytest tests/campaign -q --basetemp=.pytest-tmp` → 5 geçti; `python -m pytest tests -q -x --basetemp=.pytest-tmp` → 907 geçti, 1 atlandı · Sözleşme: uyuldu · Açık soru / risk: Yok
```
 pressure-vessel-suite/tests/campaign/__init__.py   |  0
 .../tests/campaign/test_harness.py                 | 49 +++++++++++++++++
 pressure-vessel-suite/tools/__init__.py            |  0
 pressure-vessel-suite/tools/campaign/README.md     | 62 ++++++++++++++++++++++
 pressure-vessel-suite/tools/campaign/__init__.py   |  0
 pressure-vessel-suite/tools/campaign/aggregate.py  | 29 ++++++++++
 pressure-vessel-suite/tools/campaign/bases.py      | 61 +++++++++++++++++++++
 pressure-vessel-suite/tools/campaign/compare.py    | 45 ++++++++++++++++
 .../tools/campaign/families/__init__.py            |  0
 pressure-vessel-suite/tools/campaign/harness.py    | 48 +++++++++++++++++
 10 files changed, 294 insertions(+)
```
