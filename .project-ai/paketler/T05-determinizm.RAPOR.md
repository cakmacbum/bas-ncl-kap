# RAPOR T05-determinizm

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T05 · Dal: ork/T05 · Taban: 63434ed

T05 Determinizm — KISMİ
Dosyalar: `tools/campaign/tur2/t05_determinizm/{cases.py,run.py,results.json}` · `docs/validation/campaign-2026-10/tur2/T05-determinizm.md`
Test: `python -m tools.campaign.tur2.t05_determinizm.run` → tamamlandı; 20 vaka, 20 BULGU, 0 kapsam dışı.
Sözleşme: uyuldu · Açık soru / risk: Kaynak sırasını ters çevirmek `weld_validation` sonuçlarının sırasını ve değerlerini değiştirdi; raporda konum `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py:1220`. Liste sırası değişse de beklenen aynı payload’dı.
```
 .../campaign-2026-10/tur2/T05-determinizm.md       |    37 +
 .../tools/campaign/tur2/t05_determinizm/cases.py   |    24 +
 .../campaign/tur2/t05_determinizm/results.json     | 71682 +++++++++++++++++++
 .../tools/campaign/tur2/t05_determinizm/run.py     |    84 +
 4 files changed, 71827 insertions(+)
```
