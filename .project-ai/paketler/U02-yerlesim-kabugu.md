# U02 — Adım 03 yerleşim kabuğu (Kap Geometrisi sayfası)

YOL KURALI: tüm yollar `pressure-vessel-suite/` köküne göredir. Web uygulaması `pressure-vessel-suite/apps/web-ui/`.

## Amaç
"Kap Geometrisi" sayfasında sol parametre paneli + sağ 3D önizleme düzenini yeniden kurmak. Referans ölçüler:
`pressure-vessel-suite/docs/rea/configurator-layout.md` (önce oku; "bize uygula" listesi). Kod/CSS kopyalama yok.

## Sahip olunan dosyalar (yalnız bunlar)
- `pressure-vessel-suite/apps/web-ui/src/pages.tsx` — yalnız `GeometryPage` (satır ~470–1100) yerleşimi
- `pressure-vessel-suite/apps/web-ui/src/theme.css` — `.geo-layout`, `.geo-preview*` ve yeni sınıflar
- `pressure-vessel-suite/apps/web-ui/src/viewer.tsx`, `src/cameraToolbar.tsx` — YALNIZ yerleşim/konum (mantık değişmez)
- yeni: `pressure-vessel-suite/apps/web-ui/src/__tests__/geometryLayout.test.ts` (saf fonksiyon testleri)
`src/geometrySteps/**` BAŞKA BİR PAKETİN — dokunma.

## İstenen düzen
1. Çalışma alanı yüksekliği `calc(100vh − üst başlık)`; iki sütun grid: sol panel `480px` (≥1200px), `420px` (1000–1199),
   `360px` (769–999); sağ önizleme `1fr`. Yalnız sol panel kayar; önizleme tam yükseklik, kart çerçevesi/iç boşluk yok.
2. Sol panel en üstünde iki sekme: **Geometri | Hesap girdileri**. "Geometri" = mevcut `<GeometryWizard issues={...} />`.
   "Hesap girdileri" = şu an GeometryWizard altındaki akordeonlar (Nozul ayrıntıları, Flanşlar (Appendix 2), Destek
   ayrıntıları, Malzeme, Kaynak & NDT) — içerik/mantık AYNEN taşınır, yalnız konum değişir. Sekme seçimi yerel state
   (localStorage'a try/catch ile hatırlanabilir). Hesap girdileri sekmesi başlığında kısa açıklama: "Hesap motorunun
   kullandığı ek girdiler; geometriyi değiştirmez."
3. Önizleme (`aside.geo-preview`):
   - Görünüm sekmeleri (3D Önizleme / Ölçülü Kesit / Kesin Model) sol üstte yüzen 32px segment kontrol.
   - Kamera düğmeleri (İzo/Üst/Ön/Yan/Sığdır) alt ortada yüzen 36px çubuk.
   - STEP indir + STL indir → sağ üstte tek "Dışa aktar ▾" menü düğmesi (iki seçenek; mevcut indirme işlevleri kullanılır).
   - Uyarı rozeti ("⚠ n uyarı") sağ üstte Dışa aktar'ın yanında.
   - "Önizleme — kesin imalat modeli değildir…" ve "Modeli kullanma…" notları alt kenarda tek satır küçük metin
     (taşarsa kısaltılır, tam metin title'da).
   - Model ilk yüklemede/kap boyutu değişince alanı dolduracak şekilde sığdırılır (mevcut fit fonksiyonu).
4. ≤768px: tek sütun; önizleme üstte `position: sticky`, yükseklik `min(36vh, 300px)`; kamera çubuğu yalnız ikon; yatay kaydırma yok.
5. Koyu tema token'larıyla uyumlu (theme.css mevcut değişkenleri kullan, yeni renk sabiti yazma).

## Kabul
- `cd pressure-vessel-suite/apps/web-ui && npm test && npm run build` yeşil; mevcut testler bozulmaz.
- Hiçbir form alanı / hesap girdisi kaybolmaz (yalnız yer değişir).
- tsconfig.tsbuildinfo commit'e girmez. Commit mesajı sonu: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Dönüş formatı
Türkçe ≤15 satır: değişen dosyalar, grid/kırılma değerleri, taşınan akordeonlar listesi, test sayısı, bilinen açıklar.
