# RAPOR F15-ayak_govde

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F15 · Dal: ork/F15 · Taban: d647504

F15 ayak_govde — KISMİ  
Dosyalar: `tools/campaign/families/f15_ayak_govde/` (5 dosya) · `docs/validation/campaign-2026-10/F15-ayak_govde.md`  
Test: `python -m tools.campaign.families.f15_ayak_govde.run` → başarılı; `results.json` 32 vaka içeriyor, hepsi `KAPSAM_DIŞI`.  
Sözleşme: uyuldu · Temiz oda kuralına uyuldu; yasaklı paketler okunmadı.  
Açık soru / risk: API, ayak başına eksenel yük alanı döndürmediği için suite ile sayısal kıyas yapılamadı. K3 yayın vakaları bu nedenle doğrulanamadı; K3-13 moment payı içerdiğinden saf \(W/n\) ile doğrudan karşılaştırılamaz.
```
 .../validation/campaign-2026-10/F15-ayak_govde.md  |  34 +
 .../campaign/families/f15_ayak_govde/__init__.py   |   1 +
 .../campaign/families/f15_ayak_govde/oracle.py     |  29 +
 .../campaign/families/f15_ayak_govde/results.json  | 735 +++++++++++++++++++++
 .../tools/campaign/families/f15_ayak_govde/run.py  |  38 ++
 .../campaign/families/f15_ayak_govde/variants.py   |  31 +
 6 files changed, 868 insertions(+)
```
