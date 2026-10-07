# RAPOR F08-test_basinci

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:23
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F08 · Dal: ork/F08 · Taban: d647504

F08 test_basinci — KISMİ
Dosyalar: `tools/campaign/families/f08_test_basinci/{__init__.py,variants.py,oracle.py,run.py,results.json}`, `docs/validation/campaign-2026-10/F08-test_basinci.md` · Test: `python -m tools.campaign.families.f08_test_basinci.run` → başarılı, 33 sonuç · Sözleşme: uyuldu · Açık soru / risk: Temiz oda kuralına uyuldu; MAWP ve LSR için suite ara değerlerini kullanan 30 karşılaştırma yalnız test çarpanlarını doğrular, bağımsız uçtan uca oracle değildir. Statik kafa varyantı/API eşleşmesi ve pnömatik yayımlanmış vaka eksik.
```
 .../campaign-2026-10/F08-test_basinci.md           |  43 ++
 .../campaign/families/f08_test_basinci/__init__.py |   1 +
 .../campaign/families/f08_test_basinci/oracle.py   |  11 +
 .../families/f08_test_basinci/results.json         | 602 +++++++++++++++++++++
 .../campaign/families/f08_test_basinci/run.py      |  49 ++
 .../campaign/families/f08_test_basinci/variants.py |  30 +
 6 files changed, 736 insertions(+)
```
