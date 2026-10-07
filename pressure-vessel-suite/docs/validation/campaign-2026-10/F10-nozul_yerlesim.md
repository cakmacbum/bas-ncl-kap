# F10 — Nozul yerleşimi ve çakışma

## 1. Özet

30 varyant API üzerinden yeniden koşturuldu. Her birinde katalogdaki `clash_check` satırı arandı. Etiket dağılımı: KAPSAM_DIŞI 30; DOĞRULANDI / FORMÜLASYON_FARKI / SAPMA 0. Hedeflenen ≥20 sayısal kıyaslamaya ulaşılamadı: katalog `clash_check` sözleşmesi mesafe/boşluk (mm) sunacağını bildiriyor, fakat çalışan örnekteki `nozzle_nozzle_clash` ara değeri yalnızca `PASS` metni; tek nozul konum koordinatı ve sayısal mesafe alanları da yok. Bu kategorik işaret sayısal kıyas değildir.

## 2. Oracle formülleri

1. Silindirik gövdede +X'ten ölçülen açı için `x=R cos(theta)`, `y=R sin(theta)`, `z=axial_position`; `theta` 360° modunda normalize edilir.
2. İki dairesel takviye sınırı için izdüşüm uzaklığı `d <= (D1+D2)/2` ise temas/çakışma vardır; bu geometrik gösterge UG-42 uygunluk hesabı değildir.
3. 2:1 elipsoit bombe için `z=h sqrt(1-(rho/a)^2)`; bu ailede geçerli çalışan bombe örneği olmadığından sayısal test edilmedi.

## 3. SAPMA tablosu

SAPMA yok; suite sayısal konum/mesafe üretmediği için yön (emniyetsiz/emniyetli) belirlenemez. Her vakanın girdi, API durumu ve varsa `clash_marker` alanı `results.json` içinde tutulur. Sayısal fark ve yön raporlanamaz.

## 4. Yayınlanmış vakalar

Yayınlanmış `sources-K1`–`K4` içeriğinde API'nın `clash_check` sayısal mesafe alanıyla eşleştirilebilen, bu yerleşim varyantlarına uygun vaka bulunamadı; yayımlanmış vakaya dayalı ek vaka yok.

## 5. Kapsam dışı ve bloklanan vakalar

30 vakanın tümü API tarafından işlendi. Katalog `clash_check` satırı bulunmasına karşın sonuç alanı örnekte kategorik; koordinat ve sayısal nozul mesafesi mevcut değil. Bu nedenle konum/çakışma nicelikleri için kıyas KAPSAM_DIŞI. Eksik/girdi engeli nedeniyle BLOCKED vakası yok.

## 6. Temiz oda beyanı

Temiz oda kuralına uyuldu. Oracle temel geometri denklemlerinden yazıldı; yasaklı uygulama/formül kodu açılmadı. Katalog, `examples.py`, kampanya harness/karşılaştırma sözleşmesi ve önceki F10 çıktısı kullanıldı. API suite verisi yalnızca API yanıtlarından alındı.
