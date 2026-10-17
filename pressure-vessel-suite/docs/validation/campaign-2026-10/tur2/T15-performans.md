# T15 — Performans ve eşzamanlılık

Koşum: 100 benzersiz proje, önce seri sonra 8 iş parçacığıyla eşzamanlı; her vaka/aşama için ayrı `X-Client-Id` kullanan yerel harness sarmalayıcısı. Her yanıtın hesaplama satırları seri karşılığıyla karşılaştırıldı.

| Ölçüm | Seri | 8 iş parçacığı |
|---|---:|---:|
| Toplam süre | 18.622209 sn | 4.423397 sn |
| Ortalama vaka süresi | 0.186216 sn | 0.347143 sn |
| p95 vaka süresi | 0.046822 sn | 0.418451 sn |
| Başarılı / hata | 100 / 0 | 100 / 0 |
| Yanıt karışması | — | 0 |

Bellek (tracemalloc): seri sonu canlı artış 127,298,146 bayt; tüm koşu tepe artışı 143,495,301 bayt; koşu sonu canlı artış 143,279,459 bayt.

## Bulgular

Bulgu yok. Her vakanın seri ve paralel hesaplama yanıt özeti eşleşti; hata oranı %0. 100 vaka GEÇTİ, 0 BULGU, 0 KAPSAM_DIŞI.

## Kapsam dışı

Yok.

SONUÇ: vaka=100 · geçti=100 · bulgu=0 (kritik=0, emniyetsiz=0) · kapsam_dışı=0
