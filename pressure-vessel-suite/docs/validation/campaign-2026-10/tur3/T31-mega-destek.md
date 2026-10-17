# T31 mega destek — dikey ayak / yatay saddle / etek taraması

Seed: 1002 · Vaka: 110 · Temel ve %20 artırılmış malzeme gerilmesi için harness çağrısı yapıldı.

| Durum | Adet |
|---|---:|
| GEÇTİ | 101 |
| BULGU | 9 |
| BLOCKED_BEKLENEN | 0 |

## BULGU kayıtları

Dokuz bulgunun tamamı tutarlılık kontrolünde: T31-001, T31-004, T31-007, T31-010, T31-013, T31-016, T31-019, T31-022, T31-025. Her birinde dikey ayak ailesi; proje tasarım basıncı 1.2 MPa, M1 izin verilebilir gerilmesi 138 MPa, SHELL-01 nominal kalınlığı 12 mm; N1 nozul girdisi (OD 60.3 mm, ID 52.5 mm, boyun et kalınlığı 3.9 mm, eksenel konum 1000 mm, takviye pedi kapalı). Gözlenen sonuç: `nozzle_reinforcement` satırı PASS ve utilization 1.58957484348321 (>1.0); beklenen FAIL. API HTTP 200. Olası kaynak: `packages/nozzles/src/nozzles/reinforcement.py` içindeki durum kararı (paket dışı, değiştirilmedi).

## Tekrar üretim

`python -m tools.campaign.tur3.mega_destek.run` → 110 vaka; dağılım yukarıdaki gibi. Tam girdiler, API sonuçları ve kontrol isimleri `tools/campaign/tur3/mega_destek/results.json` içindedir.

SONUÇ: vaka=110 · geçti=101 · bulgu=9 · blocked=0
