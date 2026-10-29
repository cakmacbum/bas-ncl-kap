# U03 — Adım 03 alt adım formlarının sadeleşmesi

Kök: `pressure-vessel-suite/apps/web-ui/`. Referans: `pressure-vessel-suite/docs/rea/configurator-layout.md` (oku).
Sahip olunan dosyalar: `src/geometrySteps/**` (Step1BodyChain…Step5Supports, GeometryWizard, IssuesPanel, shared.tsx, wizard.css),
yeni `src/__tests__/stepIssueCounts.test.ts`. `pages.tsx`, `theme.css`, `viewer.tsx` BAŞKA PAKETİN — dokunma.
`GeometryWizard`'ın dış API'si (`issues` prop'u, store `geoSubStep`) değişmez.

## İstenenler
1. **Adım şeridi (GeometryWizard):** tek satır numaralı sekmeler 3.1–3.5, yükseklik ~40px; her sekmede durum rozeti
   (✓ sorun yok / ⚠n uyarı / ✕n hata). Saf yardımcı `stepIssueCounts(issues): Record<number, {error:number; warn:number}>`
   (IssuesPanel.tsx'ten export, 0..4 anahtarları hep var).
2. **Sorunlar:** hata/uyarı yoksa panel gizli (yalnız şerit rozetleri). Varsa formun üstünde daraltılmış tek satır
   "n hata · m uyarı ▸", tıklayınca liste açılır (mevcut satır tıklama → adıma git davranışı korunur). BİLGİ seviyesi
   (ör. "Destek tanımlı değil") listede kalır ama sayaca girmez.
3. **Her alt adım:** başta tek cümle "bu adımda ne yapılır" (gri, 13px). Alanlar iki gruba: **Ana ölçüler** (açık) ve
   **Ayrıntılar** (varsayılan kapalı, tıklayınca açılır). Hangi alanın hangi gruba girdiğine sen karar ver; ana ölçüler =
   kullanıcının en sık değiştirdikleri (çap, boy, kalınlık, tip, adet, konum). Ör. Step5 ayakta: Profil tipi+UPN+U yönü,
   ayak sayısı, profil boyu ana; tw/tf, açı, yarıçap, ped/sac ayrıntı.
4. **İpucu deseni:** alan altında tek satır 12px gri (birim · varsayılan · izinli aralık) — mevcut `RField` note/hint;
   uzun açıklamalar alan etiketinin yanında `?` simgesi (title tooltip). Hesaplanan salt-okunur değerler gri + "hesaplanan" rozeti.
5. **Önceki / Sonraki:** panelin altında yapışkan (sticky bottom) 56px çubuk; ortada "3.2 / 5".
6. Gereksiz kutuları sadeleştir: "Seçili halka" boşken tek satır yer tutucu; Step5'teki "hesap girdileri aşağıda…" notu →
   "Hesap ayrıntıları «Hesap girdileri» sekmesinde".
Mantık/hesap değişmez; yalnız sunum. Sessiz kırpma yok.

## Kabul
`npm test && npm run build` yeşil (mevcut testler + stepIssueCounts testi). tsbuildinfo commit dışı. Worktree dalına commit
(attribution: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). Türkçe ≤12 satır rapor: dosyalar, grup kararları, test sayısı, açıklar.
