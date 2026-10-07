# DECISIONS

## DEC-001 — CAD dosyası hesabın kaynağı olmaz, yalnız öneri üretir (2026-10-06)
Karar: STEP → tanıma → kullanıcı onaylı form ön-doldurma; STL yalnız görüntü.
Gerekçe: K2; dosyada malzeme/P/T/E/C yok; doğrulanmış parametrik hat korunur.
Reddedilen: keyfi geometri için FEA (CalculiX yok, sorumluluk riski, "yeni özellik dur" konseyi).
Karar veren: Yusuf (plan onayı).

## DEC-002 — Yükleme ham gövde (octet-stream), multipart değil (2026-10-06)
Karar: `POST /api/import/step` ham baytları alır, ad `X-Filename` başlığında.
Gerekçe: `python-multipart` kurulu değil; yeni bağımlılık ve ayrıştırıcı saldırı yüzeyi yok.
Bedel: tarayıcı tarafında `fetch(body: file)` — sorun değil.

## DEC-003 — Münazara atlandı (2026-10-06)
Tanıyıcı hesap metodolojisi değil, girdi önerisi üretir; her değer kullanıcı onayından geçer.
Risk orta → Kademe 1 kontrol + test zorunlu, Kademe 2 gerekmez.

## DEC-004 — Ayırt edilemeyen düz flanş null döner, yer tutucu yok (2026-10-06)
Karar: `straight_flange_length` dosyada ayrı yüz yoksa `null`; sebep `warnings`'te. UI satırı göstermez.
Gerekçe: P01 `0.0`/low öneriyordu; kullanıcı işaretlerse forma 0 mm yazılırdı (K4 ihlali).
Kök neden: vessel_builder bombe eteğini gövde silindirine bindiriyor → dikiş yok.

## DEC-005 — M2 kampanya düzeni (2026-10-07, Yusuf)
Dış kaynak = web'den yayınlanmış örnek + temiz-oda oracle; 20 Codex aynı anda; bulgu yalnız raporlanır,
düzeltme Yusuf onayından sonra Claude'da. Kıyas API yolundan (`/calculate`), formül doğrudan çağrılmaz.
