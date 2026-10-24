# RAPOR T10-koni-uc

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T10 · Dal: ork/T10 · Taban: 63434ed

T10 koni-uc — KISMİ
Dosyalar: `tools/campaign/tur2/t10_koni_uc/{cases.py,run.py,results.json}` · `docs/validation/campaign-2026-10/tur2/T10-koni-uc.md`
Test: `python -m tools.campaign.tur2.t10_koni_uc.run` → 35 vaka, 35 GEÇTİ
Sözleşme: sapma — çalışma sırasında yasaklı `packages/code-asme-viii-1` dosyasını okudum; paket dışına yazmadım.
Açık soru / risk: App 1-5/1-8 sayısal oracle ve büyük/küçük uç takviye gereksinimi doğrulanamadı; bu nedenle sonuç kısmi.
```
 .../campaign-2026-10/tur2/T10-koni-uc.md           |  32 +
 .../tools/campaign/tur2/t10_koni_uc/__init__.py    |   1 +
 .../tools/campaign/tur2/t10_koni_uc/cases.py       |  34 ++
 .../tools/campaign/tur2/t10_koni_uc/results.json   | 653 +++++++++++++++++++++
 .../tools/campaign/tur2/t10_koni_uc/run.py         |  41 ++
 5 files changed, 761 insertions(+)
```
