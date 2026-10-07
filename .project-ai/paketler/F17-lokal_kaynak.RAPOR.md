# RAPOR F17-lokal_kaynak

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:25
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F17 · Dal: ork/F17 · Taban: d647504

F17 lokal_kaynak — KISMİ  
Dosyalar: `tools/campaign/families/f17_lokal_kaynak/` (5 dosya) · `docs/validation/campaign-2026-10/F17-lokal_kaynak.md`  
Test: `python -m tools.campaign.families.f17_lokal_kaynak.run` → başarılı; `results.json` 31 vaka  
Etiketler: 27 KAYNAK_BEKLİYOR · 3 KAPSAM_DIŞI · 1 TEK_KAYNAK  
Sözleşme: uyuldu; temiz oda sınırına uyuldu, commit atılmadı.  
Açık soru / risk: API lokal kaynak gerilmesi, Lw/Sw/Jw veya WRC sonucu üretmiyor; sayısal suite kıyası yapılamadı. `.project-ai/ORKESTRA.md` bu worktree'de bulunmadığından C-1/C-2 incelenemedi.
```
 .../campaign-2026-10/F17-lokal_kaynak.md           |  41 ++
 .../campaign/families/f17_lokal_kaynak/__init__.py |   2 +
 .../campaign/families/f17_lokal_kaynak/oracle.py   |  21 +
 .../families/f17_lokal_kaynak/results.json         | 662 +++++++++++++++++++++
 .../campaign/families/f17_lokal_kaynak/run.py      |  50 ++
 .../campaign/families/f17_lokal_kaynak/variants.py |  39 ++
 6 files changed, 815 insertions(+)
```
