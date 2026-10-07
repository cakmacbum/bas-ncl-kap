# RAPOR F21-flans_app2

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:25
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F21 · Dal: ork/F21 · Taban: d647504

F21 Flanş Appendix 2 — KISMİ
Dosyalar: `tools/campaign/families/f21_flans_app2/` · `docs/validation/campaign-2026-10/F21-flans_app2.md`
Test: `python -m tools.campaign.families.f21_flans_app2.run` → başarılı; 32 vaka, 256 metrik satırı üretildi.
Etiketler: KAYNAK_BEKLİYOR 176 · KAPSAM_DIŞI 80 · diğerleri 0.
Sözleşme: sapma — ilk `rg` keşfinde yasaklı hesap paketlerinden satırlar terminal çıktısına geldi; ayrıntısı raporda.
Açık soru / risk: API karşılaştırılabilir Appendix 2 sonuçları üretmedi; K2-12/13 kaynak değerleri suite ile kıyaslanamadı.
```
 .../validation/campaign-2026-10/F21-flans_app2.md  |   35 +
 .../campaign/families/f21_flans_app2/__init__.py   |    3 +
 .../campaign/families/f21_flans_app2/oracle.py     |   17 +
 .../campaign/families/f21_flans_app2/results.json  | 9146 ++++++++++++++++++++
 .../tools/campaign/families/f21_flans_app2/run.py  |   51 +
 .../campaign/families/f21_flans_app2/variants.py   |   43 +
 6 files changed, 9295 insertions(+)
```
