# E01 — Dikey kap U-profil ayak CAD + şema

Kök: `pressure-vessel-suite/`. Sahip olunan dosyalar: `apps/web-ui/src/cad/**`, `apps/web-ui/src/types.ts`,
`apps/web-ui/src/viewer.tsx`, `packages/domain/**/geometry.py` (Support modeli), `tests/unit/test_support_leg_fields.py` (yeni).
Başka dosyaya dokunma (özellikle `src/geometrySteps/`, `src/data/` → E02'nin).

## Şema (sözleşme — E02 aynı isimleri kullanır)
`Support`'a opsiyonel alanlar (TS: `T | null`, Python: `Optional[...] = None`):
- `leg_channel_facing: "web" | "flanges" | null` — null = "web" (U'nun sırtı pede yaslanır). "flanges" = kanat uçları pede.
- `leg_pad_top_extension_mm: number | null` — ped üst kenarı ayak üst ucunun bu kadar üstünde (null = 50).
- `leg_start_angle_deg: number | null` — ilk ayak açısı (null → n==4 ise 45, değilse 0).
store'daki yeni-destek varsayılanında (store.ts `addSupport` varsa) bu alanlar null başlatılmalı — store.ts'e yalnız bu
3 alanı eklemek için dokunabilirsin.

## Anlam
Dikey kap: `height_mm` = ayak PROFİL BOYU (taban sacı alt yüzü → ayak üst ucu). `location_mm` = ayak üst ucu kotu
(sol/alt teğetten; `supportZ`). Backend leg_detail.py zaten height_mm'i ayak boyu sayıyor.

## legs.ts (dikey dal yeniden; yatay dal aynı kesit/facing kurallarını kullansın)
- Kesit yerel: radyal eksen = profil kanat genişliği b (`leg_profile_width_mm`), teğetsel = profil yüksekliği h
  (`leg_profile_height_mm`), sırt kalınlığı tw, kanat kalınlığı tf. `web`: sırt iç (gövdeye bakan) yüzde; `flanges`: 180° çevrili.
  Boru/kutu/köşebent de aynı "iç yüz pedin dış yüzüne değer" kuralı.
- Ayak ekseni yarıçapı `rs = R + padT + radyalDerinlik/2`; `support_radius_mm` girilmişse onu kullan.
- Kolon üst = supportZ, alt = üst − height_mm. Taban sacı L×W×T kolonun altına ortalı (sac üst yüzü = kolon altı, ya da
  kolon alt ucu sacın üstüne oturur — tutarlı seç ve testle sabitle: sac alt yüzü = üst − height_mm).
  exact seviyede ankraj delikleri: `anchor_bolt_count` (1/2/4; null=4), çap `anchor_bolt_diameter_mm+2`.
- Ped: gövde eğrisine sarılı (mevcut `pad()`), z ∈ [üst+ext−padL, üst+ext], teğetsel eni padW, kalınlık padT.
- Açılar `start + i·360/n`. Sessiz kırpma yok (K4) — geçersiz durumlar UI issue'su olur, CAD olduğu gibi çizer.
## viewer.tsx
~236: yatay kapta kesin model ekseni ekranda yatay görünmeli (livePreview.tsx ile aynı dönüşüm kuralı; incele ve eşle).
Dikeyde alt (sol) bombe aşağıda olmalı.
## Testler
`src/cad/supportParts.test.ts`'e: profil–ped kesişim hacmi ≈ 0 ama temas (bbox mesafesi ≈ 0); taban sacı alt z = üst − height_mm;
web/flanges iki yönün kütle merkezi radyalde farklı; start angle uygulanıyor. pytest: yeni alanlar kabul edilir, None varsayılan.
## Kabul
`cd apps/web-ui && npm test && npm run build` yeşil; `python -m pytest tests/unit -q` yeşil. Commit at (attribution satırı:
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). Rapor ≤15 satır, Türkçe.
