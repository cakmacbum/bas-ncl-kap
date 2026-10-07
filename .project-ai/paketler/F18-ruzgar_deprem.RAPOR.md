# RAPOR F18-ruzgar_deprem

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:24
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F18 · Dal: ork/F18 · Taban: d647504

F18 rüzgâr_deprem — KISMİ  
Dosyalar: `tools/campaign/families/f18_ruzgar_deprem/` · `docs/validation/campaign-2026-10/F18-ruzgar_deprem.md`  
Test: `python -m tools.campaign.families.f18_ruzgar_deprem.run` → başarılı; 31 vaka üretildi.  
Etiketler: 30 KAYNAK_BEKLİYOR · 1 TEK_KAYNAK.  
Sözleşme: uyuldu; temiz oda kuralına uyuldu, commit atılmadı, yalnız izin verilen iki yola yazıldı.  
Açık soru / risk: API payload'larında rüzgâr/deprem hesap satırı yok; geçersiz/eksik girdilerin BLOCKED davranışı doğrulanamadı. K3-19 yalnız tek kaynakla raporlandı.
```
 .../campaign-2026-10/F18-ruzgar_deprem.md          |  34 ++
 .../families/f18_ruzgar_deprem/__init__.py         |   1 +
 .../campaign/families/f18_ruzgar_deprem/oracle.py  |  19 +
 .../families/f18_ruzgar_deprem/results.json        | 670 +++++++++++++++++++++
 .../campaign/families/f18_ruzgar_deprem/run.py     |  39 ++
 .../families/f18_ruzgar_deprem/variants.py         |  58 ++
 6 files changed, 821 insertions(+)
```
