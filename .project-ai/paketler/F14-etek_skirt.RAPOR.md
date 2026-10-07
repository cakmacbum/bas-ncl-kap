# RAPOR F14-etek_skirt

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:24
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F14 · Dal: ork/F14 · Taban: d647504

F14 etek_skirt — KISMİ  
Dosyalar: izinli aile klasörü (`__init__.py`, `variants.py`, `oracle.py`, `run.py`, `results.json`) · `F14-etek_skirt.md` · Test: `python -m tools.campaign.families.f14_etek_skirt.run` → tamamlandı, 33 vaka kimliği / 66 kıyas satırı  
Sözleşme: uyuldu; yasaklı paketler okunmadı, commit atılmadı  
Açık soru / risk: Harness etek yük ağırlığını doğrudan girdiden almıyor; K3-08 suite kıyası aynı W girdisini kullanmadığı için doğrulama sayılamaz.
```
 .../validation/campaign-2026-10/F14-etek_skirt.md  |   40 +
 .../campaign/families/f14_etek_skirt/__init__.py   |    1 +
 .../campaign/families/f14_etek_skirt/oracle.py     |   20 +
 .../campaign/families/f14_etek_skirt/results.json  | 1379 ++++++++++++++++++++
 .../tools/campaign/families/f14_etek_skirt/run.py  |   60 +
 .../campaign/families/f14_etek_skirt/variants.py   |   49 +
 6 files changed, 1549 insertions(+)
```
