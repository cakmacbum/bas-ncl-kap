# PAKET T50 — T01 ve T11 sınıflandırıcılarını onar

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 5 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

## Bağlam
- T01 (`tools/campaign/tur2/t01_metamorfik/results.json`, 240 satır): her satırın `observed` alanı None, `result` alanı KAPSAM_DIŞI. Gözlenen değer çıkarılamıyor; sınıflandırma yapılmamış.
- T11 (`tools/campaign/tur2/t11_yatay_tank_tarama/results.json`, 144 vaka): `gozlenen.support_results` içinde 216 saddle sonucu var: 216 OUT OF SCOPE, 72 REVIEW REQUIRED, 54 FAIL, 18 BLOCKED CODE DATA. Hepsi tek satırda KAPSAM_DIŞI sayılmış. Sayısal (REVIEW/FAIL) sonuçlar sınıflandırılmalı.

## Görev
1. T01: `result` ve `observed` alanlarının gerçekte nereden okunacağını bul. `tools/campaign/harness.py` `find_results`/`value_of` kullan. Her satırı GEÇTİ/BULGU/KAPSAM_DIŞI olarak yeniden etiketle; `results_v2.json` yaz. Monotonluk yönünü: P↑ → t_required↑ (artmalı), S↑ → t_required↓ olarak kontrol et.
2. T11: her vakada support_results'ı tek tek sınıflandır:
   - OUT OF SCOPE → KAPSAM_DIŞI (gerçek kapsam dışı; sayı olarak ayrı raporla)
   - BLOCKED CODE DATA → KAPSAM_DIŞI (neden: kod verisi eksik; ayrı raporla)
   - REVIEW REQUIRED / FAIL → sayısal sonuç: GEÇTİ (yalnız "tutarlılık" için, yani utilization ile durum uyumlu ise) — utilization oranı ≥1 PASS, <1 FAIL anlamına gelir (satır: `utilization_ratio = total / A_required` benzeri bir oran; dosyada hangi tanım kullanılıyorsa aynısını kullan).
   - Vaka durumu: vakadaki tüm saddle sonuçlarının en kötüsü.
   `results_v2.json` yaz.
3. Her iki koşu için dağılım tablosu ve kapsam dışı nedenleri (sayı + ilk 3 örnek) raporla.

## Kapsam
Yalnızca `tools/campaign/tur2/t01_metamorfik/` ve `tools/campaign/tur2/t11_yatay_tank_tarama/` içine `results_v2.json` ve gerekirse `classify.py`; rapor `docs/validation/campaign-2026-10/tur5/T50.md`. `packages/**`, `apps/**`, `harness.py` değiştirme. Hesap kodu okuma kısıtı yok (bu bir sınıflandırma onarımıdır).

## Kabul
İki `results_v2.json` dosyası var; her satır bir durum taşıyor; rapor son satırı: `SONUÇ: T01 geçti=a bulgu=b kapsam_dışı=c · T11 geçti=d bulgu=e kapsam_dışı=f`.
