# RAPOR F01-govde_ug27

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:26
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F01 · Dal: ork/F01 · Taban: d647504

F01 gövde_ug27 — KISMİ  
Dosyalar: `tools/campaign/families/f01_govde_ug27/` · `docs/validation/campaign-2026-10/F01-govde_ug27.md`  
Test: `python -m tools.campaign.families.f01_govde_ug27.run` → başarılı; 98 sonuç satırı  
Etiketler: 75 DOĞRULANDI · 9 SAPMA · 12 KAPSAM_DIŞI · 2 TEK_KAYNAK  
Sözleşme: sapma: geçici aramada yasaklı paket dizin adı arama kapsamına girdi; dosya içeriği okunmadı. Raporlandı.  
Açık soru / risk: 9 MAWP farkı CA/teslim kalınlığı uygulamasından kaynaklanıyor olabilir; kalın cidar App. 1-2 için bağımsız kaynak yok. K1 anchor’ları doğrudan API eşlemesi değil.
```
 .../validation/campaign-2026-10/F01-govde_ug27.md  |   44 +
 .../campaign/families/f01_govde_ug27/__init__.py   |    1 +
 .../campaign/families/f01_govde_ug27/oracle.py     |   28 +
 .../campaign/families/f01_govde_ug27/results.json  | 1673 ++++++++++++++++++++
 .../tools/campaign/families/f01_govde_ug27/run.py  |   59 +
 .../campaign/families/f01_govde_ug27/variants.py   |   57 +
 6 files changed, 1862 insertions(+)
```
