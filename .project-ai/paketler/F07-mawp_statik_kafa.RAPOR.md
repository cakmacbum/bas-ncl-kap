# RAPOR F07-mawp_statik_kafa

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:24
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F07 · Dal: ork/F07 · Taban: d647504

F07 Global MAWP + statik sıvı kafası — KISMİ  
Dosyalar: `tools/campaign/families/f07_mawp_statik_kafa/` (5 dosya) · `docs/validation/campaign-2026-10/F07-mawp_statik_kafa.md`  
Test: `python -m tools.campaign.families.f07_mawp_statik_kafa.run` → başarılı, `results.json` 30 vaka içeriyor  
Etiketler: DOĞRULANDI 4 · SAPMA 24 · TEK_KAYNAK 1 · KAPSAM_DIŞI 1  
Sözleşme: uyuldu; yasaklı paketler okunmadı, yalnızca kapsam dosyalarına yazıldı, commit atılmadı.  
Açık soru / risk: API’de sıvı yüksekliği girdisi bulunamadığından yoğunluk varyantları global MAWP’yi değiştirmedi; bileşen bazında statik kafa kıyası sınırlı kaldı.
```
 .../campaign-2026-10/F07-mawp_statik_kafa.md       |  41 ++
 .../families/f07_mawp_statik_kafa/__init__.py      |   1 +
 .../families/f07_mawp_statik_kafa/oracle.py        |  44 ++
 .../families/f07_mawp_statik_kafa/results.json     | 549 +++++++++++++++++++++
 .../campaign/families/f07_mawp_statik_kafa/run.py  |  37 ++
 .../families/f07_mawp_statik_kafa/variants.py      |  40 ++
 6 files changed, 712 insertions(+)
```
