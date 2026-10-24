# RAPOR T51-t04-gercek-kontrol

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:45
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T51 · Dal: ork/T51 · Taban: 6e69364

T51 T04 fuzz — KISMİ
Dosyalar: `run.py`, `results_v2.json`, `T51.md` · Test: `python -m tools.campaign.tur2.t04_fuzz.run` → tamamlandı; 300 vaka, GEÇTİ=0, BULGU=233, KAPSAM_DIŞI=67; gövde hesabı 300 uyuşan / 0 uyuşmayan · Sözleşme: sapma: sonuç özeti yazıldı, ancak başarısız vakalar var · Açık soru / risk: Kullanım kontrollerindeki BULGU’lar vaka bazında incelenmeli.
```
 docs/validation/campaign-2026-10/tur5/T51.md       |      7 +
 .../tools/campaign/tur2/t04_fuzz/results_v2.json   | 649158 ++++++++++++++++++
 .../tools/campaign/tur2/t04_fuzz/run.py            |    137 +-
 3 files changed, 649272 insertions(+), 30 deletions(-)
```
