# PAKET T60 — Bombe kalınlığı toplu tarama (torisferik + yarım küre, 300 vaka)

> Proje: BASINCLI-KAP · M2 Tur 5 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor
> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir.

## Görev
1. `pressure-vessel-suite/tools/campaign/tur5/bombe_tarama/` klasörüne yaz:
   - `__init__.py` (boş)
   - `run.py`: tohum 60 ile 300 vaka üret: 150 yarım küre (`hemispherical`), 150 torisferik (`torispherical`).
     Taban tank için `tools.campaign.bases.vertical_leg_tank()` kullan; `heads` içindeki bombe tipini ve
     parametrelerini (iç çap, nominal kalınlık, CA_i, mill, S, E, P) rastgele değiştir.
     Torisferik için `knuckle_radius` ve `crown_radius` değerlerini rastgele ama fiziksel makul seç (Rc ≤ D).
   - Her vaka için `tools.campaign.harness.run_case` ile API'yi çağır.
2. Bağımsız kontrol (betik içinde yaz; suite kodunu OKUMA):
   - Yarım küre: t_req = P·R_c / (2·S·E − 0.2·P), R_c = D_i/2 + CA_i (UG-32(f)).
   - Torisferik: yalnız t_req'i karşılaştır; t_req = P·L·M / (2·S·E − 0.2·P), L = Rc (crown), M = 0.25·(3 + √(L/r)) (UG-32(e)), r = knuckle.
     Bu formül yoksa (kaynak zor) torisferik kontrolü KAPSAM_DIŞI yaz.
   - API `t_required` ile ±%1 karşılaştır → UYUŞUR / UYUŞMUYOR / VERİ_YOK.
3. Çıktı `results.json` (her vaka: id, tip, girdi, api_t, t_hesap, durum). Konsola özet bas.
4. Rapor: `docs/validation/campaign-2026-10/tur5/T60-bombe-tarama.md`; son satır:
   `SONUÇ: vaka=300 · uyuşur=a · uyuşmaz=b · veri_yok=c · kapsam_dışı=d`.

## Kapsam
Yalnız `tools/campaign/tur5/bombe_tarama/` ve `docs/validation/campaign-2026-10/tur5/T60-bombe-tarama.md`.
`packages/**`, `apps/**`, `harness.py` değiştirme. Pytest varsa `--basetemp <sistem TEMP>/pv-T60 -p no:cacheprovider`.

## Kabul
`python -m tools.campaign.tur5.bombe_tarama.run` hatasız biter; `results.json` 300 satır; SONUÇ satırı var.
