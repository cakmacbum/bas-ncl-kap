# F13 — Yatay kap saddle, Zick

## 1. Özet

Katalogdaki `example_saddle_stress()` taban alınarak 30 geçerli konfigürasyon ve 2 geçersiz sınır vakası kuruldu. Her proje için iki saddle API satırı ve `S1_saddle` / `S1_midspan` nicelikleri arandı. Sonuç dosyasında 128 kayıt var; 82 sayısal eşleşme (41 satır), 46 kapsam dışı satır. API status `REVIEW REQUIRED` ve `FAIL` ile dönen sayısal değerler de karşılaştırıldı.

| Etiket | Satır |
|---|---:|
| DOĞRULANDI | 82 |
| FORMÜLASYON_FARKI | 0 |
| SAPMA | 0 |
| TEK_KAYNAK | 0 |
| KAYNAK_BEKLİYOR | 0 |
| KAPSAM_DIŞI | 46 |

Sayısal karşılaştırma en az 20 ayrı case_id için sağlandı. Katalog dışı K3 yayınına dayalı tam girdi/API eşleşmesi kurulamadığından yayınlanmış sonuçlar ayrıca doğrulanmadı.

## 2. Oracle denklemleri

API `intermediate_values` içindeki momentler N·mm, ortalama yarıçap ve korozyonlu kalınlık mm cinsindedir; N/mm² = MPa.

- Eyer kesiti: `S1_saddle = |M1| / (K1 · Rm² · t)`.
- Orta açıklık: `S1_midspan = |M2| / (π · Rm² · t)`.

K1 açık ara girdi olarak kullanıldı; oracle katsayı tablosu içermez. Bunlar boyuna eğilme kontrolleridir. K3-01'deki basınç+saddle süperpozisyonu ile S3/S4/hoop bileşenleri aynı nicelik olmadığından, yayımlanmış K3 sayılarıyla doğrudan etiketlenmedi.

## 3. SAPMA tablosu

SAPMA bulunmadı; bu nedenle yön sınıflandırması yoktur.

| case_id | Girdiler | Suite / oracle | Fark | Yön | Not |
|---|---|---|---:|---|---|
| — | — | — | — | — | Sayısal kıyas satırları eşit çıktı. |

## 4. Yayınlanmış vakalar

| Kaynak | Kullanım |
|---|---|
| K3-01, PVE-4293, PV Elite 2012, PDF s.34–37 | S1/S3/S4 ve reaksiyon yayımlanmış. Bu girdiler API örneğiyle birebir eşleşmediği ve katsayı/saha tanımları farklı olabildiği için sayısal regresyon vakası yapılmadı. |

## 5. Kapsam dışı ve bloklanan vakalar

`results.json` içindeki 46 değer üretmeyen nicelik satırı `BLOCKED CODE DATA` / `NOT CALCULATED` olarak kaldı; diğer nicelik ve destek satırları aynı vakada sayısal sonuç verebildi. Katalog, saddle için K1–K7 ve geometri/yük girdilerinin zorunlu olduğunu, eksik zorunlu verinin bloklanabileceğini bildirir. Eksik K1 ve 160° vaka istekleri de denendi; bunlar başarılı API hesabı sayılmaz. Geçersiz vakalarda kısmi diğer-support satırları olabildiğinden her satırı ayrı değerlendirdim.

## 6. Temiz oda beyanı

Oracle, bağımsız temel eğilme/kabuk denklemlerinden yazıldı. Yalnızca bu ailedeki önceki çıktılar, görevde izin verilen `RESULT_CATALOG.md`, `examples.py`, API harness/karşılaştırma arabirimi ve K3 kaynak notu okundu. Yasaklı implementasyon paketleri okunmadı. Suite değerleri yalnız public API sonucundaki `saddle_stress` satırlarından alındı.
