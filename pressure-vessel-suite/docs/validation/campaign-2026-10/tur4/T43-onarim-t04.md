# T43 — T04 fuzz kapsam dışı nedenleri

Ön adımda `python -m tools.campaign.tur2.t04_fuzz.run` yeniden çalıştırıldı; 300 kayıt üretildi. Eski `Project limit reached` yanıtları yenilenmiş sonuçlarda görülmedi.

## Kapsam dışı mesajları (ilk 80 karakter)

Yenilenen sonuçlarda `sonuc=KAPSAM_DIŞI` olan vaka yok (0); bu nedenle mesaj grubu yok. 300/300 vaka HTTP 200 aldı ve üst düzey sonucu `GEÇTİ` oldu.

| Sonuç | Adet |
|---|---:|
| GEÇTİ | 300 |
| BULGU | 0 |
| BLOCKED | 0 |
| KAPSAM_DIŞI | 0 |
| geçersiz_test | 0 |

## Üretici girdi denetimi

300 deterministik girdide eksik malzeme listesi, gövde iç çapını aşan nozul dış çapı, çözümlenmeyen nozul malzeme referansı veya geçersiz gövde çap sıralaması bulunmadı. Dolayısıyla geçersiz girdi için BLOCKED beklentisiyle ayrılacak vaka yoktu; üretici değişikliği gerekmedi.

Payload içindeki mühendislik kontrollerinin durum dağılımı (vaka değil kontrol satırı): PASS 882, FAIL 292, REVIEW REQUIRED 4.508, BLOCKED MISSING INPUT 200, OUT OF SCOPE 300. Harness'ın 300 vaka düzeyindeki sınıflandırması GEÇTİ olduğundan bunlar vaka düzeyindeki kapsam dışı sayısını artırmadı.

SONUÇ: vaka=300 · GEÇTİ=300 · BULGU=0 · BLOCKED=0 · KAPSAM_DIŞI=0 · geçersiz_test=0
