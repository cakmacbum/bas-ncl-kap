# F11 — Dış basınç / vakum UG-28 + UG-33

## 1. Özet

32 vaka çalıştırıldı. `results.json` etiket dağılımı: DOĞRULANDI 32; FORMÜLASYON_FARKI 0; SAPMA 0; TEK_KAYNAK 0; KAYNAK_BEKLİYOR 0; KAPSAM_DIŞI 0. Bu etiketler, girilen B ile hesaplanan dış basınç aritmetiğinin karşılaştırmasıdır; A için bağımsız grafik değerleri üretilmedi.

## 2. Oracle formülleri

- UG-28(c)(1): silindirik gövde izin verilen dış basıncı `Pa = 4B / (3·Do/t)`. B, dışarıdan sağlanan kullanıcı girdisidir; grafik okunmadı.
- UG-28(c)(2): A parametresi chart prosedürünün girdisidir. Kampanyada A kullanıcı girdisi olarak taşındı; grafik tablosu yeniden üretilmedi.
- UG-33: başlık hesabı için aynı dış basınç kontrolü beklendi; fixture başlarında gerekli kod verileri API tarafından sağlanmadığı için hesap bloke oldu.

## 3. SAPMA tablosu

Yok. 32 gövde sonucu verilen A/B değerleriyle aritmetik olarak ±%1 içindedir. Bu, UG-28 grafik A/B seçimlerinin bağımsız doğrulaması değildir.

## 4. Yayınlanmış vakalar

| case_id | Kaynak girdisi / yayınlanan sonuç | Suite | Oracle | Fark |
|---|---|---:|---:|---:|
| K2-16-EMA-WP | PVE Firetube, s.24–26; Do=14 in, t=.3281 in, L=120 in, B=8157.3491 psi; EMAWP 254.92 psi | 0.0121187025 MPa | 0.0121187025 MPa | 0.000% |
| K2-16-THICKNESS | Aynı kaynak, TCA=.2566 in, B=5115.9312 psi; EMAWP 125.01 psi | 0.0059314284 MPa | 0.0059314284 MPa | 0.000% |

Basınç ve geometri girdileri SI birimlerine dönüştürülmüştür. K2-16 tek yayın ailesidir; bu sonuç DOĞRULANDI genel kabulü anlamına gelmez.

## 5. Kapsam dışı ve bloklanan vakalar

Bu kampanyadaki 30 örneklenmiş ızgara vakasında Do/t 8 veya 700, L/Do 0.25 veya 50 gibi chart aralığı sınırları bulunur. Bunlar dış basınç aritmetiği için örnek girdi niteliğindedir; A/B katsayıları kampanya girdisi olarak seçilmiştir, yayımlanmış grafik değerleri değildir. `UG-33` başlık satırları API’de `BLOCKED CODE DATA` döndü; baş Pa kıyası sonuç tablosuna giremedi. Harness satır filtrelemesi gövde UG-28 sonuçlarıyla sınırlıdır.

## 6. Temiz oda beyanı

Oracle yalnız bu ailede yazılan UG-28(c)(1) aritmetiğine dayanır. Temiz oda kuralına uyuldu; yasaklı implementasyon paketleri açılmadı/okunmadı. Suite sonuçları yalnız API TestClient çıktısından alındı. K2-16’daki A/B ve yayınlanmış EMAWP değerleri kaynakta yayımlanan sayılardır; diğer örnek B değerleri test girdileridir, kaynak katsayısı oldukları iddia edilmez.
