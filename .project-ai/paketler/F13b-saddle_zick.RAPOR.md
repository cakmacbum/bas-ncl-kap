# RAPOR F13b-saddle_zick

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:55
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/F13b · Dal: ork/F13b · Taban: c8dd38d

F13b saddle_zick — TAMAM  
Dosyalar: `f13_saddle_zick/{variants.py,oracle.py,run.py,results.json}` · `F13-saddle_zick.md`  
Test: `python -m tools.campaign.families.f13_saddle_zick.run` → başarılı; 128 satır üretildi, 32 case_id’de sayısal kıyas var  
Etiketler: DOĞRULANDI 82 · KAPSAM_DIŞI 46 · diğerleri 0  
SAPMA: yok; emniyetsiz/emniyetli yön sınıflandırması gerekmedi  
Sözleşme: uyuldu · yalnızca kapsam dosyaları değiştirildi, commit atılmadı  
Açık soru / risk: K3-01 girdileri API örneğiyle eşleşmediği için yayımlanmış vaka sayısal olarak kıyaslanmadı.
```
 .../validation/campaign-2026-10/F13-saddle_zick.md |   33 +-
 .../campaign/families/f13_saddle_zick/oracle.py    |   39 +-
 .../campaign/families/f13_saddle_zick/results.json | 3686 ++++++++------------
 .../tools/campaign/families/f13_saddle_zick/run.py |   58 +-
 .../campaign/families/f13_saddle_zick/variants.py  |   80 +-
 5 files changed, 1649 insertions(+), 2247 deletions(-)
```
