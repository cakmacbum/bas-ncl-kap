# E02 — Step 3.5 Mesnetler: ayak ölçülerinin tek tek seçimi

Kök: `pressure-vessel-suite/apps/web-ui/`. Sahip olunan dosyalar: `src/geometrySteps/**`, `src/data/upn-catalog.json` (yeni),
`src/data/catalogs.ts` (yalnız UPN eki), `src/i18n.ts`, ilgili yeni test dosyaları. `src/cad/`, `types.ts`, `viewer.tsx`
E01'in — dokunma.

## Sözleşme (E01 types.ts'e ekliyor; sen worktree'nde types.ts'te yoksa AYNI satırları ekle, merge'de E01'inki kalır)
`Support`: `leg_channel_facing: "web" | "flanges" | null`, `leg_pad_top_extension_mm: number | null`,
`leg_start_angle_deg: number | null`. Dikey kapta `height_mm` = ayak PROFİL BOYU, `location_mm` = ayak üst ucu kotu (alt teğetten).

## Step5Supports.tsx — ayak seçiliyken editör 4 grup (her alan ayrı RField, mm, varsayılan değer görünür)
1. **Profil**: kesit tipi (yeni ayakta varsayılan "channel"), "Hazır UPN seç" (EN 10279 UPN 80…300; seçince
   leg_profile_height_mm=h, leg_profile_width_mm=b, leg_web_thickness_mm=tw, leg_flange_thickness_mm=tf doldurur; elle
   değiştirilebilir; `verified:false` rozeti — mevcut `CatalogBadge` deseni), h, b, tw, tf, **U yönü** (Sırtı pede / Kanatlar pede)
   — yalnız channel'da. Boru seçilirse çap + et kalınlığı.
2. **Ayak**: sayı (3–8), profil boyu (`height_mm`), üst ucu kotu (`location_mm`), ilk ayak açısı (°), yerleşim yarıçapı (0=otomatik).
3. **Ayak pedi**: boy (`leg_pad_length_mm`), en (`leg_pad_width_mm`), kalınlık (`leg_pad_thickness_mm`), üst taşma (`leg_pad_top_extension_mm`).
4. **Taban sacı**: boy/en/kalınlık (`base_plate_length_mm/width/thickness`), ankraj adedi, ankraj çapı.
Varsayılan göstergeler CAD varsayılanlarıyla aynı olsun: ped L=2.5·h, W=2·b, T=10; sac L=2h+40, W=2b+40, T=16; ext=50.
"3 ayak / 4 ayak" önerisi yeni ayağı channel + UPN 120 + height 1500 ile başlatsın (elle değiştirilebilir).
Kap yatayken (`project.orientation==="horizontal"`) Öneri bölümünde **"Kabı dikey yap"** düğmesi → orientation "vertical".
Hesap-only alanlar (WRC, kaynak, burkulma K) pages.tsx "Destek ayrıntıları"nda kalır — pages.tsx'e dokunma.

## IssuesPanel.computeIssues — yeni kurallar (Destek kategorisi)
- `LEG_TOO_SHORT` hata: dikey kap, taban sacı alt kotu (supportZ − height_mm) > kap altı (sol bombe dış kutbu,
  `src/cad/parts/supportGeom.ts` `vesselBottomZ` mantığı — import edebilirsin) → mesajda gereken min boy.
- `LEG_PAD_OFF_SHELL` uyarı: ped z aralığı [üst+ext−padL, üst+ext] gövde (shell/cone) çerçevelerinin dışına taşıyor.
- `LEG_PROFILE_INVALID` hata: channel'da tw ≥ h/2 veya tf ≥ b, ya da h/b ≤ 0.
## UPN katalog
`upn-catalog.json`: {source, verified:false, rows:[{name:"UPN 80", h, b, tw, tf}, …]} UPN 80,100,120,140,160,180,200,220,240,260,280,300
(EN 10279 / DIN 1026 standart değerleri). catalogs.ts'e `getUpn(name)`, `listUpn()`.
## Testler (vitest)
UPN seçimi 4 alanı doldurur; "Kabı dikey yap" orientation'ı değiştirir; 3 issue kuralı (pozitif + negatif).
## Kabul
`npm test && npm run build` yeşil. Commit (attribution: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). Rapor ≤15 satır, Türkçe.
