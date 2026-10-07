# RAPOR F20-uctan_uca

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:24
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F20 · Dal: ork/F20 · Taban: d647504

F20 uctan_uca — KISMİ  
Dosyalar: `tools/campaign/families/f20_uctan_uca/{__init__.py,variants.py,oracle.py,run.py,results.json}` · `docs/validation/campaign-2026-10/F20-uctan_uca.md`  
Test: `python -m tools.campaign.families.f20_uctan_uca.run` → başarılı, 30 vaka üretildi  
Sözleşme: uyuldu; temiz oda kuralına uyuldu, yasaklı hesap paketleri okunmadı  
Açık soru / risk: Rapor HTML ve STEP üretimi koşuda doğrulanmadı; hacim oracle'ı torisferik profili/nozul katkısını kapsamıyor, dolayısıyla bazı SAPMA etiketleri kesin sapma olarak yorumlanmamalı.
```
 .../validation/campaign-2026-10/F20-uctan_uca.md   |  30 +
 .../campaign/families/f20_uctan_uca/__init__.py    |   1 +
 .../campaign/families/f20_uctan_uca/oracle.py      |  27 +
 .../campaign/families/f20_uctan_uca/results.json   | 639 +++++++++++++++++++++
 .../tools/campaign/families/f20_uctan_uca/run.py   |  36 ++
 .../campaign/families/f20_uctan_uca/variants.py    |  38 ++
 6 files changed, 771 insertions(+)
```
