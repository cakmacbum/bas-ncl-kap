# RAPOR F12-mdmt

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:23
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F12 · Dal: ork/F12 · Taban: d647504

F12 MDMT UCS-66 — KISMİ
Dosyalar: `tools/campaign/families/f12_mdmt/{__init__.py,variants.py,oracle.py,run.py,results.json}`, `docs/validation/campaign-2026-10/F12-mdmt.md`
Test: `python -m tools.campaign.families.f12_mdmt.run` → tamamlandı; 35 varyanttan 139 API sonuç satırı üretildi.
Etiketler: KAYNAK_BEKLİYOR 136, KAPSAM_DIŞI 3; 116 REVIEW REQUIRED ve 20 FAIL satırı normal kıyaslandı.
Sözleşme: uyuldu · yasaklı paketler açılmadı; yalnız API çıktısı kullanıldı.
Açık soru / risk: coincident ratio varyantları gerçek API girdisine bağlanmadı; eşleşen K4 yayın vakaları API vakaları olarak koşturulmadı. Bu nedenle bağımsız UCS-66/66.1 eğri kıyası ve tam kabul kriteri tamamlanmadı.
```
 .../docs/validation/campaign-2026-10/F12-mdmt.md   |   32 +
 .../tools/campaign/families/f12_mdmt/__init__.py   |    1 +
 .../tools/campaign/families/f12_mdmt/oracle.py     |   21 +
 .../tools/campaign/families/f12_mdmt/results.json  | 2650 ++++++++++++++++++++
 .../tools/campaign/families/f12_mdmt/run.py        |   72 +
 .../tools/campaign/families/f12_mdmt/variants.py   |   55 +
 6 files changed, 2831 insertions(+)
```
