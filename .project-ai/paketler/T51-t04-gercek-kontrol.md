# PAKET T51 — T04 fuzz'a gerçek bağımsız kontroller

> Proje: BASINCLI-KAP · M2 Tur 5 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor
> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir.

## Bağlam
`pressure-vessel-suite/tools/campaign/tur2/t04_fuzz/results.json` 300 vakanın 300'ünü GEÇTİ diyor, ama
hiçbir bağımsız kontrol yapılmamış (yalnız HTTP 200). Bu sonuç güvenilir değil.

## Görev
1. `tools/campaign/tur2/t04_fuzz/run.py` içine aşağıdaki kontrolleri ekle (mevcut vakaları yeniden kullan,
   yeni vaka üretme):
   a. Sonlu sayı: sonuçta NaN/inf yok (BULGU: varsa).
   b. Kullanım tutarlılığı: PASS olan her bileşende utilization ≤ 1.0; FAIL olanda > 1.0. Takviye (nozzle
      reinforcement) için oran tanımı farklıdır: `available/required` ≥ 1 PASS, < 1 FAIL.
   c. Gövde bağımsız kalınlık: UG-27(c)(1) t_req = P·R_c / (S·E − 0.6·P), R_c = D_i/2 + CA_i. API `t_required`
      ile ±%1 uyumlu olmalı (yalnız gövde vakaları için).
   d. Kapsam: sonuç yoksa KAPSAM_DIŞI (sayı olarak ayrı raporla), sonuç varsa karşılaştırılmış say.
2. Her vaka için: `kontroller` listesi (ad, durum, gözlenen). Satır durumu = kontrollerden türet
   (herhangi biri BULGU → BULGU; hepsi GEÇTİ → GEÇTİ; yalnız KAPSAM → KAPSAM_DIŞI).
3. `results_v2.json` yaz; eski `results.json`'a dokunma.
4. Çalıştır ve özet bas: vaka, GEÇTİ, BULGU, KAPSAM_DIŞI, kontrol başına sayılar.

## Kapsam
Yalnızca `tools/campaign/tur2/t04_fuzz/run.py` ve `tools/campaign/tur2/t04_fuzz/results_v2.json` ve
`docs/validation/campaign-2026-10/tur5/T51.md`. `packages/**`, `apps/**`, `harness.py` değiştirme.
Pytest: `--basetemp <sistem TEMP>/pv-T51 -p no:cacheprovider`.

## Kabul
`python -m tools.campaign.tur2.t04_fuzz.run` hatasız biter; `results_v2.json` 300 satır; rapor son satırı:
`SONUÇ: T04 vaka=300 · GEÇTİ=a · BULGU=b · KAPSAM_DIŞI=c · kontrol_gövde_bağımsız=d (uyuşan) / e (uyuşmayan)`.
