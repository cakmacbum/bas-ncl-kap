# F06 — Konik gövde UG-32(g) ve Appendix 1-5

## 1. Özet

48 kayıt: 20 DOĞRULANDI, 12 FORMÜLASYON_FARKI, 0 SAPMA, 0 TEK_KAYNAK, 0 KAYNAK_BEKLİYOR, 16 KAPSAM_DIŞI. 16 geometri/basınç girdisi için kalınlık ve MAWP satırları katalogdaki `thickness` / `mawp` türleriyle, gerçek `t_nominal_required` ve `MAWP` ara değerlerinden okundu. 32 sayısal kıyas yapıldı (16 thickness + 16 mawp; kabul eşiği ≥20). Her varyant için ayrıca junction satırı aranır; katalog bunun sayısal yeterlilik değil girdi/topoloji incelemesi olduğunu söyler. K2-05 yayınlanmış koni girdisi dahil edilmiştir.

## 2. Oracle formülleri

- ASME VIII-1 UG-32(g), bağımsız oracle: `t = P D / [2 cos(α) (S E − 0.6 P)]`; basınç MPa, çap/kalınlık mm, gerilme MPa.
- Basınç ters çözümü: `P = 2 S E t cos(α) / [D + 0.6 t cos(α)]`. MAWP kıyasına nominal et kalınlığından korozyon payı çıkarılarak girildi.
- Kalınlık nominal tolerans kıyasında %12,5 tolerans için gereken nominal kalınlık `t/0.875` kullanıldı.
- Appendix 1-5 için sayısal alan oracle kurulmadı: kaynak kataloğu ve K2, yayımlanmış sayısal alan örneği olmadığını, API junction kontrolünün de yeterlilik hesabı olmadığını gösteriyor.

## 3. SAPMA tablosu

| case_id | girdiler | suite | oracle | fark % | yön | olası neden |
|---|---|---:|---:|---:|---|---|
| Yok | 0 SAPMA | — | — | — | — | Sayısal kıyaslanan hiçbir satır tolerans dışı SAPMA üretmedi. |

`results.json` her vaka için farkı ve yönü saklar. Yön tanımı: düşük MAWP veya yüksek gerekli kalınlık suite bakımından emniyetsiz; tersi emniyetli. FORMÜLASYON_FARKI etiketleri K2-05 OD tabanlı App. 1-4(e) yayını ile ID tabanlı UG-32(g) bağıntısı arasındaki bilinen formül farkıdır.

## 4. Yayınlanmış vakalar

| case_id | Kaynak | Yayınlanmış değer | Sonuç |
|---|---|---|---|
| GRID-16 (K2-05) | PVE, *PVE Sample 5*, s.7; K2-05 | α=25,3°, ODL=12,750 in, yerel OD=10,39 in, P=200,953 psi, E=0,70; büyük uç treq=0,108 in, yerel treq=0,088 in, Pmax=351 psi | Yayın dış çaplı App. 1-4(e) formülüdür; bu vaka iç çaplı bağımsız UG-32(g) oracle ile koştu ve farklı formülasyon olarak işaretlendi. E=0,70 ve yayımlanmış çaplar korundu. |
| K2-18 (bağlam) | PVE, *External Pressure Calculations*, s.35–37 | Bednar süreksizlik gerilmeleri | App. 1-5 takviye alanı kıyası olarak kullanılmadı. |

## 5. Kapsam dışı ve bloklanan vakalar

16 junction vakası `KAPSAM_DIŞI`: katalog `junction_check` için sonuçların topoloji/girdi incelemesi olduğunu, sayısal yeterlilik üretmediğini belirtir. API sonucu girdileri/bağlantıyı REVIEW REQUIRED veya BLOCKED MISSING INPUT olarak raporlayabilir; bu App. 1-5 alanı için sayısal kıyas değildir. K2 kaynak kataloğunda yayınlanmış App. 1-5 iç basınç alan sonucu yok; K2-18 farklı Bednar gerilme yaklaşımıdır. Varyant örnekleri `examples.py` içindeki junction projesini taban alıp her koşulda bileşen sırasını, weld id/verimini ve koni bağlantısını tanımlayacak şekilde oluşturuldu.

## 6. Temiz oda beyanı

Oracle UG-32(g) formüllerinden bağımsız yazıldı. Yasaklı `packages/code-*`, `nozzles`, `supports`, `external-pressure`, `mdmt`, `flanges` ve `calc-core` hesap implementasyonları okunmadı. Suite değerleri yalnızca `harness.run_case` public API çıktısından, katalogdaki doğru `calculation_type` ve `intermediate_values` adlarıyla alındı. Katalog, örnekler ve K2 yayınlanmış vaka notları kullanıldı.


