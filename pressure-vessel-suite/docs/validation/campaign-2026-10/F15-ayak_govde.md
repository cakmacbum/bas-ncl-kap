# F15 — Gövdeye bağlı ayaklar

## Özet

30 proje varyantı çalıştırıldı. 28 çalışan geometri varyantında üç nicelik ayrı ayrı kıyaslandı: 84 `DOĞRULANDI`. İki yayın vakası `KAPSAM_DIŞI`; sayısal kıyas toplamı 84 olup hedef 20'yi aşar. API'deki hedef satır katalog sözleşmesine uygun olarak `component_id=LEGS`, `calculation_type=leg_stress` seçildi. Destek satırı `REVIEW REQUIRED` olsa da ara değerleri niceliksel olarak kıyaslandı.

## Oracle

Boru ayağı için iç çap `Di = D − 2t`, kesit alanı `A = π(D² − Di²)/4`; eşit dağılımlı eksenel tepki `N = W_total/n`, taban eksenel gerilmesi `σ = N/A` olarak bağımsız hesaplandı. Suite'in `W_total` ara değeri yük girdisi, `n`, `D`, `t` ise varyant girdisi olarak kullanıldı. Böylece suite yük toplamını tekrar hesaplama iddiası olmadan tepkime, alan ve gerilme denetlendi. Moment/eksantrisite ve burkulma bu API vaka kümesinde kıyaslanmadı.

## Etiketler ve sapmalar

| Etiket | Adet |
|---|---:|
| DOĞRULANDI | 84 |
| FORMÜLASYON_FARKI | 0 |
| SAPMA | 0 |
| TEK_KAYNAK | 0 |
| KAYNAK_BEKLİYOR | 0 |
| KAPSAM_DIŞI | 2 |

SAPMA yok; bu nedenle sapma yönü (emniyetsiz/emniyetli) oluşmadı. Karşılaştırılan tüm eşit dağılım tepkileri, annulus alanları ve gerilmeler tolerans içinde uyuştu.

## Yayınlanmış vakalar

| Vaka | Kaynakta raporlanan kıstas | Sonuç |
|---|---|---|
| K3-13-PVE-Sample8 | PVE Sample 8, 4 ayak, toplam 12,300 lb ve moment paylaşımı içeren f2 | API `leg_stress` satırında gereken ara değerlerin tamamı alınamadı; kıyas dışı. Kaynak f2 moment bileşenini içerdiğinden yalnız W/n ile aynı ölçüt değildir. |
| K3-14-IJERT-2013 | IJERT 2013, 3 ayak, Sma=3.58 MPa ve KL/r=23.68 | API `leg_stress` satırında gereken ara değerlerin tamamı alınamadı; kıyas dışı. Kaynak künyesi `sources-K3.md` içindedir. |

## Kapsam dışı

Yukarıdaki K3-13 ve K3-14 API örnek projeleri yürütüldü ancak beklenen `W_total`, `N_max`, `A_leg`, `P_base` değerlerinin tümü gelmedi; bu sebeple sayısal kayıt uydurulmadı ve `KAPSAM_DIŞI` bırakıldı. 28 diğer varyantta her üç değer de mevcut olduğundan 84 bağımsız sonuç satırı üretildi.

## Temiz oda beyanı

Oracle, annulus geometrisi ve eşit yük dağılımı bağıntılarından sıfırdan yazıldı. Yasaklı implementasyon paketleri okunmadı. Suite değerleri yalnızca kampanya harness'inin public API çıktısından, katalogdaki `leg_stress` satırı ve ara değer adları kullanılarak alındı. Kataloğa ve örnek projelere başvuruldu.
