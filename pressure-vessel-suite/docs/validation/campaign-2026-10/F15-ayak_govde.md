# F15 — Gövdeye bağlı ayaklar

## 1. Özet

32 varyant API üzerinden çalıştırıldı. Sayısal API karşılığı bulunmayan sonuçlar `KAPSAM_DIŞI` olarak tutuldu; yayın vakaları `TEK_KAYNAK` değildir, çünkü API kıyas değeri üretmedi. `results.json` mevcut etiket dağılımını içerir. İki yayınlanmış K3 vakası ayrı `case_id` ve `ref_source` ile kaydedilmiştir.

## 2. Bağımsız oracle

- Dairesel boru: (A=\pi(D^2-(D-2t)^2)/4), (I=\pi(D^4-(D-2t)^4)/64), (r=\sqrt{I/A}).
- Kutu kesit: içi boş kare kesit statikleri; U ve L kesitler ince cidarlı idealizasyonlardır.
- Bacak başına eksenel kuvvet (P=W/n); gerilme (P/A); narinlik (KL/r).
- AISC 360-16 E3 kolonu: (F_e=\pi^2E/(KL/r)^2); (F_{cr}=0.658^{F_y/F_e}F_y) (oran ≤2.25), aksi halde (0.877F_e). Burada açık oracle girdileri (E=200000) MPa, (F_y=250) MPa.
- Dönme momenti dağılımı, eksantrik eğilme ve birleşik yük bu basit oracle'a dahil değildir.

## 3. Sapmalar

Karşılaştırılabilir API büyüklüğü bulunmadığından sayısal sapma/yön üretilemedi. Bacak ailesi için `LEGS` bileşenindeki sonuçlar tarandı; API axial load değerini yayımlamadığı durumda suite sütunu boş ve karar `KAPSAM_DIŞI` bırakıldı. Emniyet yönü hakkında çıkarım yapılmadı.

## 4. Yayınlanmış vakalar

| case_id | Kaynak girdisi/çıktısı | Durum |
|---|---|---|
| K3-13-PVE-Sample8 | PVE Sample 8, s.22–25; 4 bacak, W=12,300 lb, yayınlanan eksenel değer f2=10,319 lb (moment payı dahil) | API kıyası yok; saf W/n oracle ile formülasyon aynı değil |
| K3-14-IJERT-2013 | IJERT 2013, s.4–5; 3 boru bacak, W=1574.2 kgf, yayınlanan Sma=3.58 MPa ve KL/r=23.68 | API kıyası yok; bağımsızca doğrudan karşılaştırılabilir alan sonuçta yok |

Kaynak künyesi ve URL'ler `sources-K3.md` K3-13/K3-14 kayıtlarındadır. Yayınlanan sayısal değerler kaynakla uyuşmayan bir ölçüte zorlanarak kıyaslanmadı.

## 5. Kapsam dışı ve bloklananlar

Geçersiz sıfır bacak sayısı ve eksik bacak sayısı vaka girdileridir. Harness/API hata çıktısı varsa suite değeri alınmadı. Geçerli varyantlarda destek hesapları `REVIEW REQUIRED` olsa da bacak axial yük alanı API sonucunda bulunmadığından `KAPSAM_DIŞI` kararı verildi. Oracle hesapları sonuç dosyasındaki parametrelerden yeniden üretilebilir.

## 6. Temiz oda beyanı

Oracle sıfırdan, kesit geometrisi ile AISC E3 eşitliklerinden yazıldı. Yasaklı kod paketleri açılmadı veya okunmadı. Suite sayıları yalnızca kampanya harness'inin API çıktısından alındı; temiz oda kuralına uyuldu.
