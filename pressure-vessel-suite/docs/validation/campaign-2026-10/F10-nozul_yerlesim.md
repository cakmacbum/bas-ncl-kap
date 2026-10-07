# F10 — Nozul yerleşimi ve çakışma

## 1. Özet

30 API vakası üretildi. Yerleşim/çakışma niceliği API sonucunda bulunmadığı için 30 vaka da `KAPSAM_DIŞI`; sayısal suite-oracle farkı hesaplanamadı. Koşum sırasında API'nin döndürdüğü gerçek durum ve hata bilgisi `results.json` içinde saklanır.

## 2. Oracle formülleri

1. Silindirik gövde üzerinde açı +X ekseninden ölçülür: `x=R cos(theta)`, `y=R sin(theta)`, `z=axial_position`.
2. `theta` radyana çevrilir; 360° eşdeğeri 0° olarak normalize edilir.
3. İki dairesel takviye sınırı için izdüşüm mesafesi `d <= (D1+D2)/2` ise kesişme/temas vardır. Bu geometri tanımı UG-42'nin sınır fikrini basitleştirir; standart uygunluk hesabı değildir.
4. Eliptik bombede 2:1 elipsoid parametrelemesi `z=h sqrt(1-(rho/a)^2)` olarak ayrıca sağlanır; bu kampanya varyantlarında bombe yerleşimi API tarafından raporlanmadığından kullanılmamıştır.

## 3. SAPMA tablosu

SAPMA yok: API konum veya çakışma değeri üretmedi. Suite değerini tahmin ederek kıyas yapılmadı. Her vaka için suite durumu ve API çıktısı `results.json`'da kayıtlıdır.

## 4. Yayınlanmış vakalar

K1–K4 kaynaklarında konum/çakışma oracle'ı için doğrulanabilir yayınlanmış sayısal vaka bulunamadı. K2-09/K2-10 pedli nozul açıklık hesaplarıdır; varyant sınırları ve girdi tanımları bu geometrik konum kampanyasına doğrudan denk olmadığı için eklenmedi.

## 5. Kapsam dışı ve bloklanan vakalar

30 vaka hesaplama API'sine gönderildi. API sözleşmesi nozul konum/çakışma çıktısı içermediğinden bu nicelikler `KAPSAM_DIŞI` olarak sınıflandırıldı. Geçersiz açı (360°) da denendi; API/Harness doğrulaması sonucu varsa vaka kaydında görülebilir. Başarısız HTTP veya eksik sonuçlar ayrıca API hata alanında saklanır.

## 6. Temiz oda beyanı

Temiz oda kuralına uyuldu. Yasaklanan paketler ve uygulama hesap implementasyonları açılmadı. Oracle yalnızca temel geometri tanımlarından bağımsız olarak yazıldı; suite verisi yalnızca kampanya API'sinin çıktısından alındı.
