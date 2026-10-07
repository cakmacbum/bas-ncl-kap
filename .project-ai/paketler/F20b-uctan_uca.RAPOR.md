# RAPOR F20b-uctan_uca

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:45
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F20b · Dal: ork/F20b · Taban: ef69aa4

F20b katalog kıyası — TAMAM
Dosyalar: `variants.py`, `oracle.py`, `run.py`, `results.json`, `F20-uctan_uca.md`
Test: `python -m tools.campaign.families.f20_uctan_uca.run` → başarılı; 30 API projesinden 90 satır kıyaslandı, 90 DOĞRULANDI.
Sözleşme: uyuldu
Açık soru / risk: K1–K4 ile tam eşleşen yayınlanmış API vakası bulunamadı; katalogda çalışan örneği olmayan hesap türleri kapsanmadı. SAPMA çıkmadığı için yön tablosu boş. Temiz oda kuralına uyuldu.
```
 .../validation/campaign-2026-10/F20-uctan_uca.md   |   39 +-
 .../campaign/families/f20_uctan_uca/oracle.py      |   48 +-
 .../campaign/families/f20_uctan_uca/results.json   | 2017 ++++++++++++++++----
 .../tools/campaign/families/f20_uctan_uca/run.py   |   57 +-
 .../campaign/families/f20_uctan_uca/variants.py    |   44 +-
 5 files changed, 1686 insertions(+), 519 deletions(-)
```
