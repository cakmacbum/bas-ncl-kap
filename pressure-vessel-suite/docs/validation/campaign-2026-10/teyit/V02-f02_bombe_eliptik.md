# V02 doğrulama — F02 2:1 eliptik bombe

## Bağımsız yöntem

ASME VIII-1 UG-32(d), 2:1 geometri için K=1: `t = P·D/(2SE−0.2P)`. D, korozyon sonundaki iç çap; CA metal kaybı net et kalınlığından ayrıca düşülür. Temsilci girdilerinde S=138 MPa; D_i yeni durum çapı, D=D_i+2CA ve R=D/2. İstenen sonuç basınç için gereken et kalınlığıdır; nominal levha kalınlığı ayrı tasarım payları içerir.

| Grup | Vaka sayısı | Hüküm | Yön | Fark |
|---|---:|---|---|---:|
| Korozyon payı çapı büyütüyor, suite gerekli et kalınlığında kullanıyor; referans yeni durum çapında kalıyor | 2 | ORACLE_HATASI | suite daha kalın (emniyetli) | +1.4072%, +1.5645% |

SAPMA sayımı sonuç satırları değil iki vaka (CA3, SMALL_HIGH) üzerindendir. Her ikisi aynı bağımsız formül/çap semantiği farkıdır.

## Temsilci el hesapları

**CA3:** P=0.8 MPa, D_i=1000 mm, CA=3 mm, mill tol=0%, şekillendirme incelmesi=0, E=1. R_yeni=500 mm; R_korozyonlu=503 mm; D=1006 mm. Payda `2SE−0.2P = 276−0.16 = 275.84 MPa`. `t_req=0.8·1006/275.84=2.917627 mm`. Referansın D_i=1000 kullanımı `800/275.84=2.900232 mm`; fark `(2.917627/2.900232−1)·100=+0.5998%` ham formül çap farkı. Suite raporundaki 2.941045 mm (+1.4072%) ek nominal tasarım dönüşümü/paylarının da dahil olduğunu gösteriyor; suite çıktısı doğrudan saf UG-32(d) basınç kalınlığı değil. CA çıkarılmış net kalınlık: suite `2.941045−3` negatif olacağından bu sayı nominal kalınlık olamaz; harness `t_required` alanını farklı adlandırmış olabilir. Kampanya girdisi/çıktı eşlemesini bu yüzden kesin olarak doğrulamak mümkün değil.

**SMALL_HIGH:** P=6 MPa, D_i=300 mm, CA=1 mm, mill tol=3%, şekillendirme incelmesi=2 mm, E=0.85. R_yeni=150 mm, R_korozyonlu=151 mm, D=302 mm. Payda `2·138·0.85−0.2·6=234.6−1.2=233.4 MPa`. UG-32(d) basınç kalınlığı `t_req=6·302/233.4=7.763496 mm`; yeni çap kullanılsaydı `1800/233.4=7.712082 mm` (oracle değeri). Çapın tek başına etkisi +0.667%; kampanya suite 7.832735 mm (+1.5645%) raporlamış. Mill tol 3% ve incelme 2 mm nominal seçim aşamasındadır; doğrudan basınç kalınlığına karıştırılmamalıdır. CA net metal ölçümünde ayrıca düşülür. Raporlanan suite ve oracle farkı çap düzeltmesinden büyüktür; girdi/çıktı semantiği ek farkı açıklamıyor.

## Kod ve hüküm kanıtı

Suite `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py:486-492` bölümünde `D=head.inside_diameter+2*C` kuruyor; `:510-518` UG-32(d) hesabına bu D’yi aktarıyor. Saf formül `packages/code-asme-viii-1/src/code_asme_viii_1/formulas.py:112-151` içinde `P·D/(2SE−0.2P)`. Oracle `tools/campaign/families/f02_bombe_eliptik/oracle.py` içindeki `required_thickness` D girdisini olduğu gibi kullanıyor; `run.py` bu fonksiyona `inp["inside_diameter"]` gönderiyor. Dolayısıyla oracle, korozyon sonrası geometriyi modellemiyor. Hüküm: **ORACLE_HATASI**, bu iki vakada suite’in daha yüksek kalınlığı emniyetli yöndedir; SUITE_HATASI yok.

MAWP için ters formülde kullanılan t_net ile çapın aynı korozyon sonu geometrisi olmalıdır. Raporlanan iki SAPMA yalnız gerekli kalınlık ölçümünde olduğundan bu gruba MAWP hükmü eklenmedi. Sayısal çap farkı tek başına rapor farkını bütünüyle açıklamadığı için sonuç alanının nominal/basınç kalınlığı semantiği açık risk olarak kalır.

HÜKÜM: suite_hatası=0 (emniyetsiz=0) · oracle_hatası=1 · formülasyon=0
