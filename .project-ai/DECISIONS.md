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

## DEC-006 — Yönetim düzeni: izole worktree + şef inceleme (2026-10-17, Yusuf)
Karar: Çekirdek koda dokunan düzeltmeler Sonnet ajanlarına ayrı bağlamla, ayrı git worktree'de (`S<n>`) verilir; ajan commit atmaz;
şef diff'i okur, YALNIZ ilgili dosyaları ana ağaca kopyalar, ana ağaçta tam paketi çalıştırır, kampanya CSV'lerini ezmez, sonra commit eder.
Gerekçe: A1'in 200 vakalık yeniden koşusu 1000 vakalık kanıt CSV'sini ezmişti; ajan worktree'leri editable kurulumda ana ağaç kodunu yüklüyordu (PYTHONPATH override şart).

## DEC-007 — Bulgu hükmü kuralı: bağımsız değer + madde kaynağı (2026-10-17)
Karar: "emniyetsiz" etiketi için bağımsız hesap yetmez; Kod maddesinin tanımı (ör. UG-37(a) t_r) ayrıca doğrulanır. Bağımsız sütun API değerinden
ÖNCE ayrı dosyaya yazılır. B-07 bu kuralla "yanlış alarm" çıktı.

## DEC-008 — Sınıflandırma kuralları (2026-10-17)
Satır durumu daima o satırın kontrollerinden türetilir. Nozul takviye `utilization_ratio = mevcut/gerekli` (PASS ⇔ ≥1); gövde/bombe PASS ⇔ ≤1.
`REVIEW REQUIRED` = SAYISAL_İNCELEME (ne geçti ne bulgu); `FAIL` = TASARIM_FAIL. T11 tek kaynak: ana daldaki `results_v2.json` (81/36/27).

## DEC-009 — Kot uydurma yok (2026-10-17)
Statik kafa için bileşen kotu güvenilir hesaplanamıyorsa (`component_sequence` yok, yatayda koni, çözülemeyen torisferik) kot atanmaz;
"Statik kafa uygulanmadı" uyarısı kalır (K4).
