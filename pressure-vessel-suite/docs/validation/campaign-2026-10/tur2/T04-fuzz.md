# T04 — Rastgele proje fuzz testi

Seed 20261017 ile 300 proje üretildi: dikey ayaklı, yatay semerli ve etek destekli tanklar dengeli biçimde kullanıldı. Boyut, kalınlık, basınç, sıcaklık, destek ve nozul sayısı değiştirildi.

| Sonuç | Adet | Açıklama |
|---|---:|---|
| GEÇTİ | 50 | API 200; sonlu sayısal sonuçlar ve kontrol edilebilen kullanım oranlarında statü tutarlı. |
| BULGU | 0 | HTTP 500, sonlu olmayan sayı veya gözlenen PASS/FAIL kullanım oranı çelişkisi yok. |
| KAPSAM_DIŞI | 250 | API HTTP 429 hız sınırı; hesap sonucu alınamadı. |

## Kapsam dışı vakalar

T04-051–T04-300, paylaşılan harness istemci kimliğiyle API hız sınırına takıldı (429). Bunlar hesaplama sonucu olarak değerlendirilmedi. 429 yanıtları `results.json` içinde girdi ve gözlenen HTTP durumu ile saklandı.

## Bulgular

Bulgu yok; bu nedenle önem, yön ve kaynak satırı atanmadı.

SONUÇ: vaka=300 · geçti=50 · bulgu=0 (kritik=0, emniyetsiz=0) · kapsam_dışı=250
