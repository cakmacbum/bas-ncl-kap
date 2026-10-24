# RAPOR C1-t63-yeniden

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-18 15:20
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/C1 · Dal: ork/C1 · Taban: cb068c8

C1 — TAMAM
Dosyalar: `tools/campaign/tur6/t63_dongu/` (vakalar, kod ve çıktılar), `docs/validation/campaign-2026-10/tur6/C1.md` · Test: `python -m tools.campaign.tur6.t63_dongu.run` → 300 vaka; 228 UYUŞUR, 72 UYUŞMUYOR, 0 VERİ_YOK · `python -m py_compile ...` → başarılı · Sözleşme: uyuldu · Açık soru / risk: Nozul sapmalarının 70'i kullanım oranı <1, 2'si bağımsız alan farkı >%1.
```
 .../docs/validation/campaign-2026-10/tur6/C1.md    |     14 +
 .../tools/campaign/tur6/t63_dongu/cases.py         |     21 +-
 .../tools/campaign/tur6/t63_dongu/kontrol.json     |     21 +-
 .../tools/campaign/tur6/t63_dongu/ref.csv          |    301 +
 .../tools/campaign/tur6/t63_dongu/results.json     | 160416 +++++++++++++++---
 .../tools/campaign/tur6/t63_dongu/run.py           |    121 +-
 6 files changed, 137030 insertions(+), 23864 deletions(-)
```
