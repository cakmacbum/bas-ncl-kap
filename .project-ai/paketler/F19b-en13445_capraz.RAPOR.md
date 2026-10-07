# RAPOR F19b-en13445_capraz

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:46
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F19b · Dal: ork/F19b · Taban: ef69aa4

F19b en13445_capraz — TAMAM
Dosyalar: [oracle.py](/C:/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F19b/pressure-vessel-suite/tools/campaign/families/f19_en13445_capraz/oracle.py), [run.py](/C:/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F19b/pressure-vessel-suite/tools/campaign/families/f19_en13445_capraz/run.py), [results.json](/C:/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F19b/pressure-vessel-suite/tools/campaign/families/f19_en13445_capraz/results.json), [rapor](/C:/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F19b/pressure-vessel-suite/docs/validation/campaign-2026-10/F19-en13445_capraz.md)
Test: `python -m tools.campaign.families.f19_en13445_capraz.run` → başarılı, 30 vaka; 26 sayısal kıyas.
Etiketler: 26 DOĞRULANDI, 4 KAPSAM_DIŞI; SAPMA yok. Rapor denklem/API uyumunu yayımlanmış kaynak teyidinden ayırıyor.
Sözleşme: uyuldu; değişiklikler yalnız kapsam dosyalarında, commit atılmadı.
Açık risk: K4 yayımlanmış vakalar bu turda API girdisi olarak koşturulmadı.
```
 .../campaign-2026-10/F19-en13445_capraz.md         |  16 +-
 .../campaign/families/f19_en13445_capraz/oracle.py |  24 +-
 .../families/f19_en13445_capraz/results.json       | 400 ++++++++++-----------
 .../campaign/families/f19_en13445_capraz/run.py    |  56 ++-
 4 files changed, 266 insertions(+), 230 deletions(-)
```
