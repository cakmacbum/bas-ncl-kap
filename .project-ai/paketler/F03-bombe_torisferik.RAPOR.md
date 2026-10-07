# RAPOR F03-bombe_torisferik

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:26
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F03 · Dal: ork/F03 · Taban: d647504

F03 torisferik bombe — KISMİ
Dosyalar: `tools/campaign/families/f03_bombe_torisferik/` · `docs/validation/campaign-2026-10/F03-bombe_torisferik.md` · Test: `python -m tools.campaign.families.f03_bombe_torisferik.run` → tamamlandı, 32 vaka / 96 karşılaştırma
Sözleşme: uyuldu · `packages/**`, harness ve diğer aile dosyalarına dokunulmadı; commit atılmadı; temiz oda kuralına uyuldu.
Açık soru / risk: Eksik büküm yarıçapında API beklenen BLOCKED yerine PASS ve varsayılan yarıçapla sonuç üretti. PVE-FD tablosu için ek yayın vakaları kampanyaya alınmadı; raporda belirtildi.
```
 .../campaign-2026-10/F03-bombe_torisferik.md       |   42 +
 .../families/f03_bombe_torisferik/__init__.py      |    2 +
 .../families/f03_bombe_torisferik/oracle.py        |   23 +
 .../families/f03_bombe_torisferik/results.json     | 2026 ++++++++++++++++++++
 .../campaign/families/f03_bombe_torisferik/run.py  |   73 +
 .../families/f03_bombe_torisferik/variants.py      |   72 +
 6 files changed, 2238 insertions(+)
```
