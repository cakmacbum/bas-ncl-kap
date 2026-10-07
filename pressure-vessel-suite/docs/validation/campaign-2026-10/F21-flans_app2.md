# F21 — Flanş Appendix 2 kıyas kampanyası

## Sonuç

Katalogdaki `example_flange_stress()` taban alınarak 30 API vakası koşturuldu. Her vakada `calculation_type=flange_stress` satırı bulundu ve katalogda belirtilen `intermediate_values` içinden `W` (N) ile `M` (N·mm) çekildi. Oracle bu iki tanımı doğrudan açıkça verilen cıvata yükü ve moment girdileriyle karşılaştırır; gasket etkili çapı veya basınç itki alanı varsaymaz.

| Etiket | Satır |
|---|---:|
| DOĞRULANDI | 60 |
| FORMÜLASYON_FARKI | 0 |
| SAPMA | 0 |
| TEK_KAYNAK | 0 |
| KAYNAK_BEKLİYOR | 16 |
| KAPSAM_DIŞI | 0 |

60 sayısal kıyas 30 vakanın `W` ve `M` ara değerleridir. Bunlar verilen yük girdilerinin API ara değerlerinde korunmasını doğrular; App. 2 conta yükü ve flanş gerilmelerinin bağımsız formül doğrulaması değildir. `K2-12` ve `K2-13` kaynak değerleri `sources-K2.md` ile izlenebilir, ancak katalog/model girdileri yayınlanmış conta geometrisini bütünüyle taşımadığından 16 satır (8 metrik × 2 vaka) KAYNAK_BEKLİYOR olarak tutuldu.

## SAPMA tablosu

| Vaka / metrik | Suite | Oracle | Fark | Yön (emniyetsiz / emniyetli) |
|---|---:|---:|---:|---|
| SAPMA yok | — | — | — | Uygulanamaz |

DOĞRULANDI olan `W` ve `M` girdileri eşit olduğundan farkın emniyet yönü yoktur. SAPMA olarak sınıflanan gerilme/kapasite sonucu bulunmadı.

## Temiz oda ve sınırlamalar

Oracle yalnızca Appendix 2 ara değer adlarının katalog tanımını ve açık girdileri kullanır: `W = bolt_load_W_N`, `M = moment_M_Nmm`. Yasaklı hesap implementasyonları bu çalışma sırasında okunmadı; formüller API sonucuna göre ayarlanmadı. Bu kampanya, Appendix 2-5/2-6 gasket yüklerini, montaj/işletme moment bileşimini veya `S_H`, `S_R`, `S_T` gerilmelerini kıyaslamaz. Yayınlanmış K2 vakalarını gerçek API vakası olarak kurmak için kaynak geometrisi ve alanlarının makinece okunabilir proje eşlemesi eksiktir.
