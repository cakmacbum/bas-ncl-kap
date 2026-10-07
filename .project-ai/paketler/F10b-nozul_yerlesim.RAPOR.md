# RAPOR F10b-nozul_yerlesim

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:44
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F10b · Dal: ork/F10b · Taban: ef69aa4

F10b nozul yerleşimi — KISMİ
Dosyalar: `run.py`, `results.json`, `F10-nozul_yerlesim.md` · Test: `python -m tools.campaign.families.f10_nozul_yerlesim.run` → başarılı; 30 API vakası üretildi · Sözleşme: uyuldu
Katalogdaki `clash_check` satırı bulundu; çalışan örnek yalnızca kategorik işaret verdiğinden sayısal konum/mesafe kıyası yapılamadı. Etiketler: KAPSAM_DIŞI 30; SAPMA yok.
Açık soru / risk: Katalogda vaat edilen sayısal clash mesafesi mevcut API yanıtında sunulmuyor.
```
 .../campaign-2026-10/F10-nozul_yerlesim.md         |  19 +-
 .../families/f10_nozul_yerlesim/results.json       | 366 +++++++++++----------
 .../campaign/families/f10_nozul_yerlesim/run.py    |  19 +-
 3 files changed, 218 insertions(+), 186 deletions(-)
```
