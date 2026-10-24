# RAPOR T63-tam-dongu

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-17 18:56
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/T63 · Dal: ork/T63 · Taban: ea8a3f6

T63 kampanya — TAMAM

Dosyalar: plan, kampanya kodu, `results.json` (240 vaka), `kontrol.json`, rapor · Test: `python -m tools.campaign.tur6.t63_dongu.run` → tamam · Sonuç: 231 uyuşur, 9 uyuşmaz, 0 veri_yok · Sözleşme: uyuldu · Açık risk: 9 eliptik bombe vakasında API `t_required`, bağımsız UG-32(d) hesabından %1’den fazla sapıyor.
```
 .../validation/campaign-2026-10/tur6/T63-plan.md   |     10 +
 .../docs/validation/campaign-2026-10/tur6/T63.md   |     15 +
 .../tools/campaign/tur6/t63_dongu/__init__.py      |      1 +
 .../tools/campaign/tur6/t63_dongu/cases.py         |     62 +
 .../tools/campaign/tur6/t63_dongu/kontrol.json     |     18 +
 .../tools/campaign/tur6/t63_dongu/results.json     | 441704 ++++++++++++++++++
 .../tools/campaign/tur6/t63_dongu/run.py           |     92 +
 7 files changed, 441902 insertions(+)
```
