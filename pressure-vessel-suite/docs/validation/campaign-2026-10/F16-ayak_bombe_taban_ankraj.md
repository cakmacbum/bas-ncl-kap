# F16 — Bombe altına bağlı ayak, taban plakası ve ankraj

## 1. Özet

32 girdi varyantı çalıştırıldı; her biri 4 büyüklük için karşılaştırıldı (128 satır). Etiket dağılımı: KAPSAM_DIŞI 128; DOĞRULANDI 0; FORMÜLASYON_FARKI 0; SAPMA 0; TEK_KAYNAK 0; KAYNAK_BEKLİYOR 0. API'de base_plate_check sonuç satırı çoğu girdide NOT CALCULATED veya gerekli sonuç değeri yayımlanmıyor; bu yüzden sayısal suite/oracle farkı çıkarmak mümkün olmadı. REVIEW REQUIRED satırları normal kıyaslanacak şekilde işlendi.

## 2. Oracle formülleri

- DG1 basitleştirilmiş konsol şeridi: `t_req = l·sqrt(2 fp/(0.9 Fy))`; `l=max((L-W)/2,0)`.
- Beton: `fp=P/(L·W)`.
- Ankraj: `T=max(M/(n/4·D_bc)-W/n,0)`; kesme `V/n`.
- Bu bağımsız oracle, paket girdileri için karşılaştırma zemini üretir; suite sonuç alanları ve dayanak yükünün uyuşması doğrulanamadığından bunlar doğrulama sonucu olarak sunulmamıştır.

## 3. SAPMA tablosu

Sayısal sapma raporlanamadı. `results.json`'daki tüm ölçüm satırları `KAPSAM_DIŞI`; plaka kontrolü 104 satırda NOT CALCULATED, 16 satırda PASS durumunda sonuç değeri bulunamadı. Ankraj/beton için API sonuç alanı eşleştirilemedi. Emniyetsiz/emniyetli yön belirlemek mümkün değil.

## 4. Yayınlanmış vakalar

K3 öncelikli kaynak: AISC Steel Design Guide 1, 2. baskı (2006), Bölüm 4: K3-15 (merkezi basma), K3-16 (küçük moment), K3-17 (büyük moment ve ankraj çekmesi), K3-18 (ankraj çekmesi/kopma konisi). K3-17 en doğrudan devrilme ve çekme ankrajı referansıdır. Kaynak girdileri bu çalışmadaki SI tank geometrisi ve yükleriyle eşdeğer olmadığı için birebir yayınlanmış vaka sonucu olarak işaretlenmedi; sayılar uydurulmadı.

## 5. Kapsam dışı ve bloklanan vakalar

GRID-01…GRID-30: girdiler API'ye gönderildi; base_plate_check sonucu ya NOT CALCULATED ya da ölçüm değeri okunamadı. INVALID-ANCHORS ve MISSING-PLATE: kasıtlı geçersiz/eksik girdiler; bloke/hesaplanmayan sonuçlar KAPSAM_DIŞI tutuldu. Tüm satırların ayrıntıları ve suite durumları `tools/campaign/families/f16_ayak_bombe_taban_ankraj/results.json` içindedir.

## 6. Temiz oda beyanı

Yasaklanan implementasyon dizinleri okunmadı. Suite değerleri yalnızca `run_case` üzerinden API yanıtından alınmaya çalışıldı. Oracle, aile dosyasında bağımsız formüllerle kuruldu. Domain modelleri, kampanya harness'i, K3 kaynak notu ve etiket politikası okundu. Temiz oda kuralına uyuldu.
