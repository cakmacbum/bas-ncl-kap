# F16 — Bombe altına bağlı ayak, taban plakası ve ankraj

## 1. Özet

30 geçerli proje varyantı FastAPI hesaplama API'sinde çalıştırıldı. Her projede doğru `base_plate_check` sonucu içinden `t_required` ve `bearing_pressure_q` ara değerleri çekildi; toplam 60 sayısal kıyasın dağılımı: DOĞRULANDI 60, FORMÜLASYON_FARKI 0, SAPMA 0, TEK_KAYNAK 0, KAYNAK_BEKLİYOR 0, KAPSAM_DIŞI 0. Sonuç satırları `tools/campaign/families/f16_ayak_bombe_taban_ankraj/results.json` içindedir.

## 2. Oracle formülleri

Oracle yalnızca API giriş/çıkış sözleşmesi ve kampanya örneği kullanılarak bağımsız yazıldı. Taban plakası hesabı için `q = N_max/(L·W)` ve konsol şeridi `c = max((L−0.8h)/2, (W−0.8b)/2, 0)`; gerekli kalınlık `t = c·sqrt(3q/(0.75Fy))` olarak hesaplandı. `h=b=114.3 mm` örnek boru ayak dış ölçüsüdür. Sonuç, API'nin açıkladığı Moss PVDM Prosedür 4-12 hesabıyla aynı varsayım ve büyüklükleri karşılaştırır.

## 3. SAPMA tablosu

SAPMA yok; dolayısıyla emniyetsiz/emniyetli yön sınıflandırması gerektiren vaka yok. 60 kıyasın tamamı sıfır farkla DOĞRULANDI. Her satırın değerleri ve durumları JSON sonuç dosyasında kayıtlıdır.

## 4. Yayınlanmış vakalar

K3-15…18, AISC Steel Design Guide 1, 2. baskı, Bölüm 4 örnekleri plaka, beton basıncı ve ankraj için kaynak dayanağıdır. K3-15'in 22×20 in plaka, W12x96 ve yayınlanmış ASD/LRFD değerleri; K3-17'nin 22×22 in plaka ve momentli ankraj çekmesi sonuçları suite örnek girdisiyle bire bir aynı değildir. Katalogdaki kullanılabilir `example_base_plate_check()` tam API vaka akışını sağladığı için bu yayınlanmış örnekler yanlış girdi/sonuç eşlemesiyle çalıştırılmadı. Bu kampanyada gerçek API üzerinden yayınlanmış K3 vakası yoktur; K3 kaynak sayıları uydurulmamıştır.

## 5. Kapsam dışı ve bloklanan vakalar

Yok. Katalogda `base_plate_check` için zorunlu girdi ve ara değer sözleşmesi mevcuttur; örnek de bu yolu tetikler. Bu sonuç ailesi taban plakası hesabını doğrular. Katalog `anchor_tension_per_bolt` ve `anchor_shear_per_bolt` değerlerini bu hesap türünün ara değerleri olarak listelemez; ankraj ve beton kopma konisi güvenliği bu 60 kıyasın kapsamına dahil değildir.

## 6. Temiz oda beyanı

`packages/code-*`, `nozzles`, `supports`, `external-pressure`, `mdmt`, `flanges` ve `calc-core` uygulamalarını okumadım. Girdiler `tools/campaign/examples.py` içindeki çalışan API örneğinden üretildi; suite sonuçları yalnızca kamu API'si yanıtındaki `base_plate_check` satırından, doğru `calculation_type` ve `intermediate_values` adlarıyla alındı. Oracle yukarıdaki formüllerden aile dosyasında bağımsız kuruldu. Temiz oda kuralına uyuldu.
