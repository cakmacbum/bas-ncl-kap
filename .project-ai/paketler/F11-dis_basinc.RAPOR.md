# RAPOR F11-dis_basinc

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:24
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F11 · Dal: ork/F11 · Taban: d647504

F11 Dış basınç — KISMİ  
Dosyalar: `tools/campaign/families/f11_dis_basinc/` (5 dosya), `docs/validation/campaign-2026-10/F11-dis_basinc.md` · Test: `python -m tools.campaign.families.f11_dis_basinc.run` → tamamlandı, 32 vaka üretildi; hepsi DOĞRULANDI  
Sözleşme: uyuldu — yalnız kapsam içi dosyalar değişti, commit atılmadı, temiz oda kuralına uyuldu.  
Açık soru / risk: Izgara vakalarındaki B değerleri test girdisidir; bağımsız grafik doğrulaması değildir. UG-33 baş hesapları `BLOCKED CODE DATA` döndü. K2-16 tek yayın ailesinden olduğu için genel doğrulama sayılmaz.
```
 .../validation/campaign-2026-10/F11-dis_basinc.md  |  32 +
 .../campaign/families/f11_dis_basinc/__init__.py   |   1 +
 .../campaign/families/f11_dis_basinc/oracle.py     |  25 +
 .../campaign/families/f11_dis_basinc/results.json  | 713 +++++++++++++++++++++
 .../tools/campaign/families/f11_dis_basinc/run.py  |  41 ++
 .../campaign/families/f11_dis_basinc/variants.py   |  48 ++
 6 files changed, 860 insertions(+)
```
