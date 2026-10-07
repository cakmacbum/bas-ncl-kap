# RAPOR P00b-katalog

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-07 20:41
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/P00b · Dal: ork/P00b · Taban: 1035f4e

P00b Kampanya kataloğu — KISMİ  
Dosyalar: `tools/campaign/RESULT_CATALOG.md`, `tools/campaign/examples.py`, `tests/campaign/test_examples.py` · 11 örnek çalışan; Zick saddle ve rüzgâr/deprem, flanş, koni bağlantısı, coincident ratio ile diğer kaynak türlerinde doğrulanmış örnek yok · Test: `python -m pytest tests/campaign -q --basetemp=$env:TEMP/pvtmp` → 6 passed · Sözleşme: uyuldu  
Açık soru / risk: Katalog 29 hesap türünü kapsıyor; her türün tam ara değer adları ve birimleri çıkarılamadı. Örneklerde en önemli 5 tuzak: zorunlu girdiler yüzünden BLOCKED satırlar; Zick K1–K7 ve geometri eksikleri; rüzgâr/deprem yük durumu yokluğu; flanş Y/T/U/Z/F/V/f girdilerinin fixture’da olmaması; MDMT coincident ratio ve koni junction bağlantısının kurulamaması.
```
 .../tests/campaign/test_examples.py                | 20 ++++++
 .../tools/campaign/RESULT_CATALOG.md               | 76 ++++++++++++++++++++++
 pressure-vessel-suite/tools/campaign/examples.py   | 44 +++++++++++++
 3 files changed, 140 insertions(+)
```
