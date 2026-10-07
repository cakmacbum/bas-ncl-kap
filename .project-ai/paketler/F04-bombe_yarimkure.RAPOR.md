# RAPOR F04-bombe_yarimkure

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:27
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F04 · Dal: ork/F04 · Taban: d647504

F04 yarım küre bombe — KISMİ  
Dosyalar: `tools/campaign/families/f04_bombe_yarimkure/` (varyantlar, oracle, çalıştırıcı, 70 satırlık `results.json`) · `docs/validation/campaign-2026-10/F04-bombe_yarimkure.md`  
Test: `python -m tools.campaign.families.f04_bombe_yarimkure.run` → başarılı; 35 varyant çalıştı.  
Sonuç: DOĞRULANDI 34 · SAPMA 34 · KAPSAM_DIŞI 2. Geçerli vakalarda MAWP eşleşti; kalınlıkta %14,29 sapma görüldü.  
Sözleşme: uyuldu; yalnız izinli dosyalar yazıldı, commit atılmadı ve yasaklı paketler okunmadı.  
Açık soru / risk: Kalın cidar için App. 1-3 oracle doğrulanamadı; sapmanın olası kaynağı etkin kaynak verimi farkı (tahmin).
```
 .../campaign-2026-10/F04-bombe_yarimkure.md        |   35 +
 .../families/f04_bombe_yarimkure/__init__.py       |    1 +
 .../families/f04_bombe_yarimkure/oracle.py         |   30 +
 .../families/f04_bombe_yarimkure/results.json      | 1265 ++++++++++++++++++++
 .../campaign/families/f04_bombe_yarimkure/run.py   |   51 +
 .../families/f04_bombe_yarimkure/variants.py       |   58 +
 6 files changed, 1440 insertions(+)
```
