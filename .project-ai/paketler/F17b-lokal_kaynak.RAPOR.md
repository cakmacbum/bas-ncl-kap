# RAPOR F17b-lokal_kaynak

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:55
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F17b · Dal: ork/F17b · Taban: c8dd38d

F17b lokal kaynak — KISMİ
Dosyalar: F17-lokal_kaynak.md, oracle.py, results.json, run.py, variants.py · Test: `python -m tools.campaign.families.f17_lokal_kaynak.run` → başarılı; 25 vaka, 24 DOĞRULANDI, 1 TEK_KAYNAK
SAPMA: 0; yön tablosu raporda. 24 stres kıyası API’nin etkin Lw/Sw ve yük ara değerlerini kullanıyor; geometri düzeltmesi bağımsız doğrulanmadı.
Sözleşme: uyuldu · Açık soru / risk: etkin geometri düzeltmesinin dayanağı ve WRC kullanıcı katsayıları doğrulanmadı.
```
 .../campaign-2026-10/F17-lokal_kaynak.md           |  36 +-
 .../campaign/families/f17_lokal_kaynak/oracle.py   |  38 +-
 .../families/f17_lokal_kaynak/results.json         | 740 ++++++++-------------
 .../campaign/families/f17_lokal_kaynak/run.py      |  73 +-
 .../campaign/families/f17_lokal_kaynak/variants.py |  53 +-
 5 files changed, 395 insertions(+), 545 deletions(-)
```
