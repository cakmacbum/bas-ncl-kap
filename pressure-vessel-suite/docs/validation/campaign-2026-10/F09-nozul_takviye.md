# F09 — Nozul takviyesi UG-37/40 + UG-45

## 1. Özet

26 API vakası üretildi; geçerli API sonuçları için nozul UG-37 sonucu bulunamadı ve tüm satırlar `KAPSAM_DIŞI` kaldı. Kabul ölçütü olan 30 vaka bu çalıştırmada sağlanmadı.

## 2. Oracle formülleri

Temiz oda oracle’ı UG-37(c)’de gerekli alanı `A = d·tr`; UG-40 alan boyutlarını nozul/gövde kalınlıklarına göre sınırlandırır. Kodda kullanılan basitleştirilmiş bağımsız alan bileşenleri A1–A5’tir. UG-45 minimum boyun et kalınlığı değerlendirmesi şimdilik yalnız kaba alt sınırdır; kod tablosu terimleri tamamlanmamıştır.

## 3. SAPMA tablosu

SAPMA üretilemedi: API sonucu içinde nozul bileşenine ait hesap satırı tespit edilmedi. Bu nedenle sayısal suite/oracle farkı ve yönü raporlanamaz.

## 4. Yayınlanmış vakalar

| vaka | Kaynak | Kullanım |
|---|---|---|
| PUB-K2-02-PVE-S5 | PVE Sample 5, Nozul B, s.13 | Pedsiz silindirik gövde alanları ve UG-45 yayın değeri |
| PUB-K2-17-IJERT | IJERT/PV Elite, torisferik bombe manhole, s.3–4 | Pedli nozul ve UG-40 kırpma davranışı; tr girdisi kaynak belirsizliği taşır |

Yayınlanmış sonuçlar `sources-K2.md` içindedir; mevcut API bağlantısı hesap satırı vermediğinden sayısal karşılaştırma yapılmadı.

## 5. Kapsam dışı / bloklanan

Bütün vakalar, hesap satırı bulunmadığı için `KAPSAM_DIŞI` olarak kaydedildi. Ek geçersiz girdiler API’de BLOCKED davranışını kanıtlamak üzere eklenmedi.

## 6. Temiz oda beyanı

Yasaklı hesap implementasyonları okunmadı. Oracle, UG-37(c), UG-40 ve UG-45 alan denklemlerinin bağımsız ve kısmi uygulamasıdır; UG-45 tablosu ve detaylı A1–A5 kaynak varyantları eksiktir.
