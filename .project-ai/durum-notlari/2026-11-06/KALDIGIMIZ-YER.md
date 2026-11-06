# Kaldığımız yer — 2026-11-06

## Şu an çalışan
- ✓ BİTTİ (e210e43, 2:1 örnek 1,84 → 4,21 mm) — **E06 (ACİL):** EN 13445 elipsoidal bombe küre denklemiyle hesaplanıyor → 2:1 için gereken kalınlığın ~yarısı (emniyetsiz).
  Düzeltme: 7.5.4 eşdeğer torisferik (R = Di(0,44K+0,02), r = Di(0,5/K−0,08)) + E03 torisferik prosedürü. Ayrıca EN testlerindeki
  zincire bağlı olmayan fixture'lar geometrik olarak düzeltilecek (G01 kapısı sıkılaşabilsin). Brief: `paketler/D5-PLAN-en13445-eski-isler.md` → "Ek paket E06".

## main (GitHub'da, son push 297f11b) — canlıda DEĞİL
Canlı site en son 2026-10-31 (Dalga 4 + F4/V1). O tarihten sonra main'e girenler:
| Paket | Ne | Commit |
|---|---|---|
| E01 | EN'de hesaplanmayan her kontrol açık NOT_CALCULATED/OUT_OF_SCOPE satırı (sessiz boşluk yok) | 5d1dcbe |
| N01 | Nozul "Açıklık Kaynak Verimi E1" alanı (UG-37: A1 azalır) | 5b795a8 |
| H01 | Hidrotest UG-99 her bileşende P_test + ρ·g·h, σ ≤ Sy | 0baf19a |
| R01 | H01+E01 birleşiminden kalan 2 kırmızı test | 13ba6d0 |
| X01 | Playwright e2e — 3 temel tank 3/3 (`npm run e2e`, Edge) | merge 2303981 |
| E02 | EN koni (7.6.4) + büyük/küçük uç birleşimi + düz kapak (10.4, C kullanıcıdan) | db28b1a |
| E03 | EN torisferik tam prosedür (7.5.3: es/ey/eb, β, MAWP), B-09 kaldırıldı | 4c44f6b |
| E04 | EN f/ftest (Madde 6), test grubu→z, hidrotest Pd ile, pnömatik (k kullanıcıdan), EN emniyet ventili ASME etiketi kalktı, madde no 5.x→7.x | 3960f46 |
| G01 | API'de geometri kapısı (GEOMETRY_INVALID: çap uyuşmazlığı, kısa ayak, sıra, bombe derinliği, koni α>30°), kampanya verisi düzeltildi | merge b5dc793 |
| — | supportParts testine 30 s zaman aşımı (flaky) | e6874f7 |
Test durumu (son tam koşu): pytest 1176 geçti / 1 atlandı · vitest 164/164 · build yeşil · e2e 3/3.

## Sıradaki adımlar (sırayla)
1. E06 bitince: testler → push → **canlıya alma (Yusuf onayı)** — elipsoidal düzeltme canlıya gitmeli.
2. E05 (Opus): EN dış basınç (Part 8) + nozul takviyesi (yeni modüller).
3. Kampanyayı düzeltilmiş tabanlarla yeniden koş (`tools/campaign/`), eski 2026-10 çıktıları geçersiz (HEAD-R 800 / ayak 600 ile üretildi).
4. G01 kapısını sıkılaştır (bileşen sırası tanımsızken zincir kuralları şu an atlanıyor) — E06 fixture düzeltmesinden sonra.

## Çalışma düzeni
- Kadro: `.project-ai/KADRO.json` — kodlayıcı Claude Sonnet · ağır Codex Luna · test/tarama agy Gemini 3.8 Flash.
- Pratikte: agy headless komut iznini reddediyor → test/tarama Claude'a düştü. Codex sandbox'ında npm ağı yok → kurulum isteyen paket Claude'a.
- Disk dar (C: ~4,7 GB boş): yeni worktree + `npm ci` ≈ 0,6 GB. Main'e dokunan tek ajan varken ana checkout'ta çalıştırılıyor; bitmiş worktree'lerin node_modules'u siliniyor.
