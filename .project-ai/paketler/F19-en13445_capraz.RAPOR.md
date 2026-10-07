# RAPOR F19-en13445_capraz

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:25
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F19 · Dal: ork/F19 · Taban: d647504

F19 EN 13445 çapraz kontrol — KISMİ  
Dosyalar: `tools/campaign/families/f19_en13445_capraz/{__init__.py,variants.py,oracle.py,run.py,results.json}` · `docs/validation/campaign-2026-10/F19-en13445_capraz.md`  
Test: `python -m tools.campaign.families.f19_en13445_capraz.run` → başarılı; 30 vaka yazıldı.  
Sözleşme: uyuldu; yalnız Kapsam’daki dosyalara yazıldı, commit atılmadı. Temiz oda beyanı rapora eklendi.  
Açık soru / risk: Sonuç dağılımı 13 SAPMA, 17 KAPSAM_DIŞI; SAPMA’lar gerçek hata diye doğrulanmadı. API ölçüm alanı ve EN/ASME girdileri eşleşmediği için çapraz kontrol ile yayımlanmış vaka kıyasları tamamlanmış sayılmaz.
```
 .../campaign-2026-10/F19-en13445_capraz.md         |  25 +
 .../families/f19_en13445_capraz/__init__.py        |   1 +
 .../campaign/families/f19_en13445_capraz/oracle.py |  15 +
 .../families/f19_en13445_capraz/results.json       | 610 +++++++++++++++++++++
 .../campaign/families/f19_en13445_capraz/run.py    |  22 +
 .../families/f19_en13445_capraz/variants.py        |  40 ++
 6 files changed, 713 insertions(+)
```
