# RAPOR F10-nozul_yerlesim

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F10 · Dal: ork/F10 · Taban: d647504

F10 nozul yerleşimi — KISMİ  
Dosyalar: F10 aile klasörü (5 dosya) · `F10-nozul_yerlesim.md` · `results.json`: 30 vaka, 30 KAPSAM_DIŞI  
Test: `python -m tools.campaign.families.f10_nozul_yerlesim.run` → başarılı; API nozul yerleşimi/çakışma çıktısı sunmadığından sayısal kıyas yapılamadı  
Sözleşme: uyuldu; temiz oda kuralına uyuldu, commit atılmadı  
Açık soru / risk: Yayınlanmış geometri vakası eklenemedi; mevcut API ile konum ve çakışma kıyasları kapsam dışı kaldı.
```
 .../campaign-2026-10/F10-nozul_yerlesim.md         |  28 +
 .../families/f10_nozul_yerlesim/__init__.py        |   1 +
 .../campaign/families/f10_nozul_yerlesim/oracle.py |  25 +
 .../families/f10_nozul_yerlesim/results.json       | 819 +++++++++++++++++++++
 .../campaign/families/f10_nozul_yerlesim/run.py    |  40 +
 .../families/f10_nozul_yerlesim/variants.py        |  24 +
 6 files changed, 937 insertions(+)
```
