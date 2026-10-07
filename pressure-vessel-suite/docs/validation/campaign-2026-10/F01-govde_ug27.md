# F01 — Gövde iç basınç UG-27

## 1. Özet

32 varyant üretildi; sonuç dosyasında 96 oracle kıyası ve 2 ayrı yayınlanmış kaynak anchor’ı bulunur. Oracle kıyaslarında: **75 DOĞRULANDI, 9 SAPMA, 12 KAPSAM_DIŞI**. Kapsam dışıların çoğu geçersiz/geçersizleşen kalın cidar girişidir; 9 satırda API sonucu bloklu veya hesaplanmadı. Yayınlanmış anchor’lar tek kaynakla sınırlı olduğundan TEK_KAYNAK olarak etiketlendi.

## 2. Oracle formülleri

- UG-27(c)(1): iç basınç gerekli cidar kalınlığı `t = P·R/(S·E − 0.6·P)`; `R` korozyonlu iç yarıçaptır (`R_i + CA_i`).
- Ters form: `MAWP = S·E·t_net/(R + 0.6·t_net)`; teslim net kalınlığı `t_nom·(1−mill)−CA_i−CA_o` alınmıştır.
- Dış çapla tarifli gövdede iç yarıçap, dış yarıçaptan minimum teslim cidarının çıkarılmasıyla kuruldu. App. 1-2 kalın cidar karşılaştırması bağımsız kaynak bulgusu olmadığından bu koşullar KAPSAM_DIŞI bırakıldı; formül doğrulaması iddia edilmedi.

## 3. SAPMA tablosu

| case_id | Girdiler | Suite (MPa) | Oracle (MPa) | Fark | Yön | Olası neden |
|---|---|---:|---:|---:|---|---|
| grid-04:mawp | D=1000, P=1.2, CAi=2, CAo=1, mill=12.5% | 4.1835 | 3.9182 | +6.77% | Suite MAWP yüksek, emniyetsiz | Tahmin: CA/teslim net cidar uygulaması farklı. |
| grid-06:mawp | D=2000, P=3, CAi=4, CAo=2, mill=12.5% | 1.4939 | 1.2741 | +17.25% | Suite MAWP yüksek, emniyetsiz | Tahmin: CA/teslim net cidar uygulaması farklı. |
| grid-08:mawp | D=3000, P=5, CAi=5, CAo=1, mill=12.5% | 1.2645 | 1.1638 | +8.65% | Suite MAWP yüksek, emniyetsiz | Tahmin: dış CA veya mill toleransı MAWP net cidarına aynı şekilde yansımıyor olabilir. |
| grid-10:mawp | D=4000, P=10, CAi=6, CAo=2, mill=12.5% | 1.1426 | 0.9445 | +20.98% | Suite MAWP yüksek, emniyetsiz | Tahmin: CA/teslim net cidar uygulaması farklı. |
| ca-16:mawp | D=900, P=2.5, CAo=6 | 5.9740 | 4.2147 | +41.74% | Suite MAWP yüksek, emniyetsiz | Tahmin: dış CA’nın iç yarıçap ve net cidara uygulanışı farklı. |
| large-21:mawp | D=4000, P=10, CAi=6, CAo=2, mill=12.5% | 0.7998 | 0.6611 | +20.98% | Suite MAWP yüksek, emniyetsiz | grid-10 ile aynı geometri/teslim cidarı etkisi. |
| outside-23:mawp | OD=1620, P=3, CAi=3, CAo=1, mill=12.5% | 2.4521 | 2.2904 | +7.06% | Suite MAWP yüksek, emniyetsiz | Tahmin: OD’den türetilen iç yarıçap veya CA dönüşümü farklı. |
| medium-25:mawp | D=1800, P=4, CAi=4, CAo=2, mill=12.5% | 1.8871 | 1.6097 | +17.24% | Suite MAWP yüksek, emniyetsiz | Tahmin: CA/teslim net cidar uygulaması farklı. |
| medium-27:mawp | D=750, P=.8, CAi=1, CAo=1, mill=12.5% | 3.2923 | 3.0976 | +6.29% | Suite MAWP yüksek, emniyetsiz | Tahmin: CA/teslim net cidar uygulaması farklı. |

SAPMA’ların tamamı MAWP satırlarında; gereken kalınlık ve kullanılan yarıçap varyantlarının sayısal sonuçları oracle ile örtüşüyor. Sonuçlar kaynak/uzman incelemesi gerektirir.

## 4. Yayınlanmış vakalar

| case_id | Atıf ve yayınlanmış değer | Kıyas durumu |
|---|---|---|
| K1-16 | PVEng, *Generic Vessel* PVE-6847, s.15–16; App.1-1(a)(1), `t_req=0.2437 in` | TEK_KAYNAK anchor; bu aile API girdileriyle aynı koşul olmadığı için doğrudan eşlenmedi. |
| K1-18 | PVEng, *Sample Vessel Calculations* PVE-3247, s.2; UG-27 çevresel, `ta=0.127 in`, CA=0.010 in | TEK_KAYNAK anchor; yayınlanan birim/girdi korunmuştur. |

Kaynak dosyası: `sources-K1.md`. K1-04’te yayınlanmış gerekli kalınlık değeri açıkça verilmediğinden vaka sayısal anchor olarak eklenmedi.

## 5. Kapsam dışı ve bloklanan vakalar

`invalid-p-29`, `invalid-d-30`, `invalid-s-31`, `missing-mat-32` ile formül paydası/uygulanabilirliği başarısız olan köşe durumları API’de BLOCKED/NOT CALCULATED oldu ve KAPSAM_DIŞI tutuldu. `P > 0.385·S·E` kalın cidar sınırındaki örneklerde suite’in API sonucu olsa da UG-27 ince cidar oracle’ıyla kıyas yapılmadı; App. 1-2 için bu kampanyada bağımsız yayınlanmış sayısal vaka bulunmadığından sonuçlar KAPSAM_DIŞI olarak işaretlendi.

## 6. Temiz oda beyanı

Oracle yalnız bağımsız UG-27(c)(1) cebiri ve ters denklemden yazıldı; yasaklı hesap implementasyonlarının içeriği okunmadı. API sonuçları yalnız kampanya harness’i üzerinden alındı. Bir ara shell araması yasaklı `code-asme-viii-1` dizin adını arama kapsamına katmıştı; dosya içeriği okunmadı. Bu arama sınırı sapması açıkça kayda geçirilmiştir.
