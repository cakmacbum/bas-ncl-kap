# RAPOR T16-test-basinci-kombine

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:22
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T16 · Dal: ork/T16 · Taban: 63434ed

T16 test-basinci-kombine — TAMAM
Dosyalar: `tools/campaign/tur2/t16_test_basinci_kombine/{cases.py,run.py,oracle.py,results.json}`, `tools/campaign/tur2/__init__.py`, `docs/validation/campaign-2026-10/tur2/T16-test-basinci-kombine.md` · Test: `python -m tools.campaign.tur2.t16_test_basinci_kombine.run` → 48 vaka; 6 GEÇTİ, 42 BULGU, 0 KAPSAM_DIŞI · Sözleşme: sapma: temiz oda nedeniyle uygulama dosya:satır bilgisi belirlenemedi · Açık soru / risk: 18 MAWP vakasında statik kafa eklenmemesi emniyetsiz düşük basınca; 24 tasarım tabanı karşılaştırmasında MAWP kullanımı emniyetli yüksek basınca yol açtı.
```
 .../tur2/T16-test-basinci-kombine.md               |   14 +
 .../tools/campaign/tur2/__init__.py                |    0
 .../tur2/t16_test_basinci_kombine/cases.py         |   38 +
 .../tur2/t16_test_basinci_kombine/oracle.py        |   10 +
 .../tur2/t16_test_basinci_kombine/results.json     | 2171 ++++++++++++++++++++
 .../campaign/tur2/t16_test_basinci_kombine/run.py  |   79 +
 6 files changed, 2312 insertions(+)
```
