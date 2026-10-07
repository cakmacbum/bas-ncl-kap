# F06 — Konik gövde UG-32(g) ve Appendix 1-5

## 1. Özet

48 kayıt: 12 DOĞRULANDI, 20 FORMÜLASYON_FARKI, 16 KAPSAM_DIŞI; SAPMA, TEK_KAYNAK ve KAYNAK_BEKLİYOR yok. 16 geometri/basınç varyantında koni kalınlığı ve MAWP; bağlantı takviyesi ayrıca kaydedildi. Suite'in bileşen durumları REVIEW REQUIRED sayı ürettiğinden sayısal kıyaslandı. Junction kontrolü BLOCKED MISSING INPUT döndürdü.

## 2. Oracle formülleri

- ASME VIII-1 UG-32(g): `t = P D / [2 cos(α) (S E − 0.6 P)]` (D iç çap). Uygulanan basınç MPa, D ve t mm, S MPa.
- Aynı bağıntının basınç için çözümü: `P = 2 S E t cos(α) / [D + 0.6 t cos(α)]`.
- Malzeme negatif toleransı girilmediğinde suite nominal kalınlığı `t/0.875` ile bildiriyor; kalınlık kıyas oracle'ı buna göre normalize edildi.
- Appendix 1-5 takviye alanı için Q/Δ ve etkin alan girdilerini sağlayan yayınlanmış nümerik vaka bulunmadığından bağımsız alan oracle'ı kurulmadı.

## 3. SAPMA tablosu

| case_id | girdiler | suite | oracle | fark % | yön | olası neden |
|---|---|---:|---:|---:|---|---|
| GRID-02, GRID-05, GRID-08, GRID-11, GRID-14, GRID-17, GRID-20, GRID-23, GRID-26, GRID-29 (kalınlık) | α 5–60°, D_L/D_S 0.50–0.85, P 0.5–2 MPa, CA 0–2 mm | results.json | results.json | ~14.3 | emniyetli | Kalınlık kıyası nominal toleranslı suite sonucu ile teorik gerekli t arasında formülasyon farkıdır; tolerans dönüşümünün etkisi. |
| GRID-02-MAWP, GRID-05-MAWP, GRID-08-MAWP, GRID-11-MAWP, GRID-14-MAWP, GRID-17-MAWP, GRID-20-MAWP, GRID-23-MAWP, GRID-26-MAWP, GRID-29-MAWP | aynı açı/çap ızgarası; t_nom=12.7 mm | results.json | results.json | sonuç başına JSON'da | emniyetsiz | Suite basınç ters çözümünde nominal/etkin et kalınlığı ile oracle girdisinin tanım farkı olasıdır (tahmin). |

Fark ve işaret değerleri her vaka için `results.json` içinde; yön, daha düşük izin verilebilir basınç veya daha yüksek gerekli kalınlığın emniyetli olduğu konvansiyonuyla verilmiştir. Kalan DOĞRULANDI kayıtları bu notta listelenen açı/çap noktaları dışındaki karşılaştırmalardır; tüm kesin değerler JSON'dadır.

## 4. Yayınlanmış vakalar

| case_id | Kaynak | Yayınlanmış değer | Sonuç |
|---|---|---|---|
| GRID-31 (K2-05) | PVE, *PVE Sample 5*, s.7; K2-05 | 25.3°, OD büyük uç 12.750 in, yerel OD 10.39 in, P 200.953 psi, E=0.70; t_req 0.108 in (büyük uç), 0.088 in (yerel); Pmax 351 psi | Bu varyant iç çap UG-32(g) / E=1 koşulunda tekrar hesaplanır; yayımlanmış 1-4(e) OD biçimi ile doğrudan eşdeğer sayılmadı (FORMÜLASYON_FARKI). |
| K2-18 (bilgi) | PVE, *External Pressure Calculations*, s.35–37 | Bednar süreksizlik gerilmeleri; Q/Δ takviye alanı değil | App. 1-5 kıyası olarak kullanılmadı. |

## 5. Kapsam dışı ve bloklanan vakalar

Her GRID-xx-APP15 kaydı, bağlantı verisinde gereken App. 1-5 girdileri bulunmadığı için API'nin BLOCKED MISSING INPUT durumunu korur ve KAPSAM_DIŞI sayılır. K2-18 bir gerilme yaklaşımıdır, alan takviyesi değildir. Yayınlanmış App. 1-5 nümerik örneği olmadığı için bu başlıkta sonuç uydurulmamıştır. Açı 5°–60° aralığı ve 30° sınırı kapsandı; geçersiz alfa test girdisi modele giremediğinden ayrıca koşturulmadı.

## 6. Temiz oda beyanı

Oracle, paketin dışındaki hesap implementasyonları okunmadan UG-32(g) eşitliğinden bağımsız olarak yazıldı. Suite değerleri yalnızca harness'in public API çıktısından alındı. Yasaklı hesap paketleri açılmadı; C-1/C-2 harness sözleşmesi kullanıldı.
