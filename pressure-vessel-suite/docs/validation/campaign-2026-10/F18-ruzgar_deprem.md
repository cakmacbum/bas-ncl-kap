# F18 — Rüzgâr ve deprem yük girdileri (2026-10-07)

## Sonuç

`results.json` 37 kayıt içerir: 18 katalog `global_load_case` API vakasından türetilen 36 sayısal skaler kıyas (kesme ve devrilme momenti) ve K3-19 yayımlanmış kaynak kaydı. Etiket dağılımı: **DOĞRULANDI 36 · FORMÜLASYON_FARKI 0 · SAPMA 0 · TEK_KAYNAK 1 · KAYNAK_BEKLİYOR 0 · KAPSAM_DIŞI 0**. 36 kıyasın tamamında fark %0.

## Katalog sınırı ve oracle

Katalog rüzgâr/deprem için doğrudan bir hesaplama türü tanımlamıyor. Rüzgâr/deprem girdileri `global_load_case` içinde taşınıyor; bu sonuç `REVIEW REQUIRED` durumunda `resultant_shear`, `overturning_moment` ve diğer yük ara değerlerini sağlıyor. `global_load_combination` ise wind+seismic eşzamanlılığını kabul etmiyor. Bu nedenle 18 projede kataloğun tetikleyicisi ve alan adları aynen kullanıldı; her projeye bir açık yatay dış kuvvet (`fx_n`) ve moment (`my_nmm`) eklendi. Rüzgâr hızı ve deprem bölge katsayısı varyant eksenleri olarak saklandı, fakat API bu değerlerden rüzgâr basıncı veya deprem kuvveti türetmiyor.

Oracle sıfırdan doğrudan denge girdilerinden yazıldı: tek yatay bileşen için `V = |Fx|`, tek devrilme momenti için `M = |My|`. Bu, API'nin raporladığı yük bileşenlerinin aktarımını doğrular; rüzgâr/deprem mühendislik denklemlerini veya tasarım yeterliliğini doğrulamaz. Katalogdan edinilen yük alanları ve ara değer adları dışında hesap kodu kullanılmadı.

## SAPMA tablosu

Sayısal SAPMA bulunmadı; bu nedenle emniyetsiz/emniyetli yönlü sapma yoktur.

| case_id | API türü / ara değer | Suite | Oracle | Fark | Yön |
|---|---|---:|---:|---:|---|
| LOAD-01…18 kesme kıyasları | `global_load_case` / `resultant_shear` | 1,000 veya 2,500 N | aynı | %0 | SAPMA yok |
| LOAD-01…18 moment kıyasları | `global_load_case` / `overturning_moment` | 200,000 veya 500,000 N·mm | aynı | %0 | SAPMA yok |

## Yayımlanmış vaka

| Vaka | Kaynak değeri | API durumu |
|---|---|---|
| K3-19-PUBLISHED | ASCE Petrochemical Committee (2011), §6.4, ayrıntılı toplam taban kesmesi 58,868 lb (basit yöntem 82,496 lb) | `global_load_case` ASCE §6.4 yöntemini/çıktısını üretmediğinden TEK_KAYNAK; suite API vakası olarak sayılmadı. |

K3-03 (NBC 2005 deprem+rüzgâr), K3-09 ve K3-10 için kaynak notlarında suite'in tetikleyebileceği eşleşen hesap girdisi/çıktısı belirtilmiyor; K3-19 ise yayımlanmış ASCE toplamını verir ancak API yöntemi bu toplamı hesaplamaz. Bunları gerçek API doğrulaması gibi sunmak doğru olmayacağından kaynak kıyasları genişletilmedi.

## Temiz oda beyanı

Oracle denklemleri bu ailede açık `fx_n` ve `my_nmm` değerlerinden bağımsız olarak yazıldı. Yasaklı kod paketleri, nozzles, supports, external-pressure, mdmt, flanges ve calc-core implementasyonları okunmadı. Sonuç satırları public API harness'inden, alan sözleşmesi ise `RESULT_CATALOG.md` ve `examples.py` içeriğinden alındı. Temiz oda kuralına uyuldu.
