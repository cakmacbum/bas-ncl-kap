# RAPOR F06-koni

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:33
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F06 · Dal: ork/F06 · Taban: d647504

F06 koni — KISMİ  
Dosyalar: `tools/campaign/families/f06_koni/{__init__.py,variants.py,oracle.py,run.py,results.json}` · `docs/validation/campaign-2026-10/F06-koni.md`  
Test: `python -m tools.campaign.families.f06_koni.run` → başarılı; 48 kayıt üretildi (12 DOĞRULANDI, 20 FORMÜLASYON_FARKI, 16 KAPSAM_DIŞI).  
Sözleşme: uyuldu; yalnızca izin verilen dosyalar değiştirildi, commit atılmadı ve yasaklı hesap paketleri okunmadı.  
Açık soru / risk: App. 1-5 takviye alanı, API’de BLOCKED MISSING INPUT ve yayınlanmış nümerik vaka yokluğu nedeniyle bağımsız doğrulanamadı. 30° üstü vakalarda FORMÜLASYON_FARKI sonuçlarının nedenleri ayrıca mühendislik incelemesi gerektiriyor.
```
 .../docs/validation/campaign-2026-10/F06-koni.md   |  36 +
 .../tools/campaign/families/f06_koni/__init__.py   |   1 +
 .../tools/campaign/families/f06_koni/oracle.py     |  12 +
 .../tools/campaign/families/f06_koni/results.json  | 889 +++++++++++++++++++++
 .../tools/campaign/families/f06_koni/run.py        |  40 +
 .../tools/campaign/families/f06_koni/variants.py   |  28 +
 6 files changed, 1006 insertions(+)
```
