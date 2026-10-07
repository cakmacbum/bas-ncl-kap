# F07b — Global MAWP ve statik sıvı kafası

## 1. Özet

30 vaka API üzerinden koşturuldu. Etiket dağılımı: DOĞRULANDI 28, FORMÜLASYON_FARKI 0, SAPMA 0, TEK_KAYNAK 1, KAYNAK_BEKLİYOR 0, KAPSAM_DIŞI 1. Sayısal kıyasların tümü `calculation_type=mawp` sonuçlarından, `final_result` ve `intermediate_values` alanlarıyla yapıldı; suite global MAWP çıktısı da fixture karşılaştırması için saklandı. Yoğunluk girdisi ve yönelim değişiklikleri bu API sözleşmesinde statik kafa yüksekliği oluşturmadığından yalnızca komponent MAWP doğrulamasına katkı verir.

## 2. Oracle

- UG-27(c)(1): `P = S·E·t / (R + 0.6t)`; `R = ID/2 + CA`, `t = t_nom·(1 − mill_tolerance/100) − forming_thinning − CA`.
- UG-32(d): `P = 2·S·E·t / (D + 0.2t)`; `D = ID + 2·CA`, aynı etkin et; kaynak verisindeki `E`, bağlı weld `joint_efficiency` değeridir.
- Global bileşen kapasitesi, bileşen MAWP'lerinin minimumudur. UG-98/UG-22 statik kafa için `ΔP = ρgh`; global kapasiteden düşüm ancak ilgili sıvı yüksekliği ve datum tanımlıysa yapılabilir. Katalog ve çalışan örnekler böyle bir yükseklik alanı sağlamıyor.
- PUB-CW-K1-01: yayımlanmış silindir MAWP 308.73 psi = 2.128 MPa; bu kaynak vakasının girdisi örnek fixture'dan türetildiğinden yalnız tek kaynak kontrolü sayıldı.

## 3. SAPMA tablosu

SAPMA bulunmadı; bu nedenle yön sınıflandırılacak fark yok. Yön kuralı: suite sonucu oracle'dan düşükse emniyetli, yüksekse emniyetsiz. Ham değerler, yüzde fark ve komponent yöneticisi `tools/campaign/families/f07_mawp_statik_kafa/results.json` içindedir.

## 4. Yayınlanmış vaka

| Vaka | Kaynak ve yayımlanmış sonuç | Suite | Fark | Etiket |
|---|---|---:|---:|---|
| PUB-CW-K1-01 | Codeware COMPRESS Demo Vessel (2022), K1-01, 308.73 psi = 2.128 MPa; `sources-K1.md` | 2.1346 MPa | +0.31% | TEK_KAYNAK |

Yayımlanmış silindir ölçüleri (ID 24 in, nominal et 0.1875 in) ve gerilme K1-01'den taşındı; suite fixture'ının alaşım/etkin et ayrıntıları tam eşleşmediğinden bu vaka doğrulanmış etiketi almadı.

## 5. Kapsam dışı ve sınırlamalar

| Vaka | Sonuç | Neden |
|---|---|---|
| INVALID-NO-MATERIAL | KAPSAM_DIŞI | Malzeme kaldırılınca API `NOT CALCULATED` döndürdü; sayısal referans üretilemez. |

28 vaka sayısal olarak kıyaslandı ve hedef ≥20 karşılandı. Statik kafa varyant ekseni tam doğrulanamadı: katalogdaki `mawp` tetikleyicisi geometri, et, malzeme, gerilme, verim ve korozyon payını listeliyor; sıvı yüksekliği/datum alanı yok. Bu yüzden yoğunluk değişimleri bağımsız hidrostatik sınama gibi yorumlanmamalıdır.

## 6. Temiz oda beyanı

Oracle UG-27(c)(1), UG-32(d) ve `ρgh` denklemlerinden bağımsız yazıldı. `packages/code-*`, `nozzles`, `supports`, `external-pressure`, `mdmt`, `flanges` ve `calc-core` implementasyonları okunmadı. Suite sonuçları yalnız katalog sözleşmesindeki `mawp` satırlarının `intermediate_values`/`final_result` alanları ve API payload'ından alındı. Yalnız izinli aile dizini ile bu rapor güncellendi.
