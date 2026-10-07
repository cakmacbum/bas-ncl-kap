# F12b — MDMT UCS-66

## Özet

Sonuç satırı: 139; sayısal kıyaslanan: 0. Etiket dağılımı: KAPSAM_DIŞI=3, KAYNAK_BEKLİYOR=136

## Oracle ve sınır

Bağımsız UCS-66 grafik noktaları çıkarılmadı: katalog ve sources-K4 yalnızca seçili yayınlanmış nihai MDMT noktalarını verir; eğri/tablo değerleri ve Fig. UCS-66.1 tam verisi yoktur. Kaynak örneklerinin her birini bu API fixture'ına birebir eşleyen girdi seti de katalogda yok. Bu nedenle varyantların hesaplanan MDMT sayıları kaynaksız kıyaslanmadı; K4 noktaları yalnızca etiketli referans olarak tutuldu. Katalogdaki MDMT örneği API'de çalışır ve sonuçlar `mdmt_check` satırlarından, `mdmt` ara değeri/final sonuç sözleşmesiyle çekilir.

## SAPMA tablosu

| case_id | girdiler | suite | oracle | fark % | yön | olası neden |
|---|---|---:|---:|---:|---|---|
Sayısal kıyaslanmış SAPMA yok.

## Yayınlanmış vakalar

| Kaynak | Yayın MDMT | Durum |
|---|---:|---|
| K4-09 | -48.333 °C | Katalog girdileriyle birebir eşlenmedi; doğrulama iddiası yok |
| K4-10 | -31.111 °C | Katalog girdileriyle birebir eşlenmedi; doğrulama iddiası yok |
| K4-13 | -98.889 °C | Katalog girdileriyle birebir eşlenmedi; doğrulama iddiası yok |
| K4-16 | -19.444 °C | Katalog girdileriyle birebir eşlenmedi; doğrulama iddiası yok |

## Temiz oda

Oracle yalnızca açık yayınlanmış noktalara dayanır; eğri verisi türetilmedi. Yasaklı uygulama paketleri okunmadı. API sonuçları harness üzerinden alındı.
