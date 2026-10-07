# F02 — 2:1 eliptik bombe UG-32(d)

## 1. Özet

30 varyant ve K1-19 yayınlanmış vakası API üzerinden koşturuldu; her vaka için gerekli basınç kalınlığı ve MAWP kaydı üretildi (toplam 62 kıyas). Etiket dağılımı: **DOĞRULANDI 58 · FORMÜLASYON_FARKI 0 · SAPMA 2 · TEK_KAYNAK 0 · KAYNAK_BEKLİYOR 0 · KAPSAM_DIŞI 2**. Geçersiz MISSING-MATERIAL vakası hesap sonucu üretmedi ve kapsam dışı kaldı. Kıyaslanan kalınlık, UG-32(d) basınç kalınlığıdır; korozyon payı/API nominal paylaştırma adımı ayrıca ayrıştırılmıştır.

## 2. Oracle formülleri

- UG-32(d), 2:1 eliptik başlık ve K=1: `t = P·D / (2·S·E − 0.2·P)`; uygulamada çap mm, P ve S MPa olduğundan sonuç mm'dir. `oracle.py` ayrıca nominal kalınlık kıyası için CA'yı ekleme seçeneği sunar.
- UG-32(d) ters form: `MAWP = 2·S·E·t_net / (D + 0.2·t_net)`; `t_net`, nominalden tolerans, şekillendirme incelmesi ve CA çıkarıldıktan sonraki kalınlıktır.
- Düz flanş eki için bağımsız UG-27(c)(1) referans fonksiyonu: `t = P·R / (S·E − 0.6·P)`. Bu kampanyada bombe sonuçlarının yerine kullanılmaz.

## 3. SAPMA tablosu

| case_id | girdiler | suite | oracle | fark | yön | olası neden |
|---|---|---:|---:|---:|---|---|
| CA3 / gerekli kalınlık | P=.8 MPa, D=1000 mm, CA=3 mm, E=1 | 2.9410 mm | 2.9002 mm | +1.41% | Suite daha kalın, emniyetli | Tahmin: suite CA'yı başlık çapına/kalınlığa farklı yansıtıyor; API ara değerinde bu katkı ayrıştırılmalı. |
| SMALL_HIGH / gerekli kalınlık | P=6 MPa, D=300 mm, CA=1 mm, tolerans=3%, incelme=2 mm, E=.85 | 7.8327 mm | 7.7121 mm | +1.56% | Suite daha kalın, emniyetli | Tahmin: API nominal/tolerans dönüşümü ile saf basınç kalınlığı aynı büyüklük değil; girdiler ve ara değer semantiği yeniden incelenmeli. |

## 4. Yayınlanmış vakalar

| Vaka | Kaynak ve girdi | Yayın sonucu | Suite / oracle | Etiket |
|---|---|---|---|---|
| K1-19 | PVE-3247, s.3; P=201.4 psi, Do=18 in, t_f=.188 in, CA=.010 in, S=20 ksi, E=.85 | t_req=.115 in (CA dahil); Pmax=341.3 psi | Basınç kalınlığı 2.6637 / 2.6567 mm, +.265%; MAWP 2.3585 / 2.3612 MPa | DOĞRULANDI (tek yayın vakası; formülün geniş teyidi değildir) |

Kaynak notu: `sources-K1.md`, K1-19 Pmax değerinin kendi girdileriyle yaklaşık 342.3 psi verdiğini bildiriyor; bu kaynak içi uyuşmazlık nedeniyle yayın MAWP sayısı bağımsız referans olarak seçilmedi. Kalınlık kıyasında yayınlanan .115 in CA'yı içerdiğinden suite'in basınç kalınlığı, yayınlanan CA hariç kalınlığa (.105 in) çevrilerek karşılaştırıldı.

## 5. Kapsam dışı ve bloklanan vakalar

`INVALID-MATERIAL`: head malzeme kimliği MISSING olarak değiştirildi. API bu başlık için karşılaştırılabilir UG-32(d) kalınlık ve MAWP satırı döndürmedi; her iki ölçüm `KAPSAM_DIŞI` olarak kaydedildi. Geçersiz/eksik veri için sayı uydurulmadı. Başka başlık vakası bloklanmadı; ayrı MDMT kontrollerindeki bloklar bu ailenin hedef ölçümü değildir.

## 6. Temiz oda beyanı

Oracle, UG-32(d), UG-27(c)(1) ve ters MAWP denklemlerinden bağımsız yazıldı. Yasaklı implementasyon paketleri açılmadı/okunmadı; suite sonuçları yalnızca `run_case` API çıktısından alındı. Domain modelleri ve izin verilen kampanya harness'i incelendi.
