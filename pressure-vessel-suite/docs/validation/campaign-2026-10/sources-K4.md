# K4 — Kaynak avı: EN 13445-3 ve ASME UCS-66 MDMT doğrulama vakaları

Tarih: 2026-10-07. Kural K6: metin/tablo kopyalanmadı; yalnızca atıf, URL, girdi sayıları + birim, yayınlanmış sonuç sayıları. UCS-66 eğrisi gömülmedi; vakalarda "kaynağın okuduğu MDMT" yazılır.

Özet: 19 vaka (K4-01..K4-19), 8 yayıncı (CERN, Ray Delaforce/Static Equipment Design, IOP Publishing, Pressure Vessel Engineering Ltd, Key Design Engineering, V. Rana/LinkedIn, EPCLand, amarineblog). Güven yüksek/orta olanlar PDF'i yerelde okunarak doğrulandı (pdftotext); "düşük" olanlar yalnızca web özetleyicisinden geldi (sayfa ham metni görülmedi).

Önemli boşluklar (ayrıca bkz. "Erişilemeyen kaynaklar"): EN 13445-3 Bölüm 8 (dış basınç) için sayısal çözümlü örnek BULUNAMADI; EN 13445-5 10.2.3.3 hidrostatik test basıncı için doğrulanmış sayısal örnek BULUNAMADI (yalnızca bir Bentley KB makalesine işaret eden doğrulanmamış arama özeti var); eliptik bomba için EN 13445 sonucu yalnızca 1 vaka (K4-05, dolaylı).

---

## A. EN 13445-3

### K4-01 — EN 13445-3 silindirik gövde — 7.4.2 (Denk. 7.4-1, 7.4-2, 7.4-3)
Kaynak: CERN, J. Jovanovic & E. Vik, "NF EN 13445-3 Worksheet template" (Mathcad, doldurulmuş çıktı) · URL: https://indico.cern.ch/event/633791/contributions/2564216/subcontributions/241095/attachments/1548557/2432091/Filled.pdf · Sayfa: ~2 (bölüm "7.4.2 Cylindrical shells") · Standart: EN 13445-3 (NF EN 13445-3, baskı çıktıda belirtilmemiş; ek-bağımsız 7.4 formülleri) · Güven: Orta (P ve z çıktıda boş; sonuçlardan geri türetildi, tutarlılık kontrolü yapıldı)
Girdiler: Di = 25 mm; De = 28.64 mm; f = 154 MPa (6.6'ya göre, çıktıda girilmiş); z = 1.0 ve P = 4 MPa (çıktıda görünmüyor; e=0.329 ve Pmax=20.901 sonuçlarıyla ve aynı sayfadaki 7.4.3/7.5.3 sonuçlarıyla birbirine tutarlı geri-hesap). ea = (De-Di)/2 = 1.82 mm, Dm = 26.82 mm (çıktıda).
Yayınlanmış sonuçlar: e (Di bazlı, 7.4-1) = 0.329 mm; e (De bazlı, 7.4-2) = 0.367 mm; Pmax = 2·f·z·ea/Dm = 20.901 MPa (7.4-3); koşul e/De ≤ 0.16 "OK".
Formülasyon notu: Di-bazlı e = P·Di/(2fz−P), De-bazlı e = P·De/(2fz+P); Pmax Dm-bazlı. Mutlak değerler mm cinsinden çok küçük çap (25 mm) — birim/rölatif tolerans testi için uygun; gerçek tank ölçeği değil. P ve z geri türetildi, kaynakta açık değil.

### K4-02 — EN 13445-3 torispherik bombe — 7.5.3 (Denk. 7.5-1, 7.5-3; es ve eb)
Kaynak: CERN, aynı çalışma sayfası (J. Jovanovic & E. Vik) · URL: https://indico.cern.ch/event/633791/contributions/2564216/subcontributions/241095/attachments/1548557/2432091/Filled.pdf · Sayfa: ~3 ("7.5.3 Torispherical ends") · Standart: EN 13445-3 · Güven: Orta (P=4 MPa, f=154, z=1 geri türetildi; es ve eb sayıları bu girdilerle yeniden üretildi)
Girdiler: R = 600 mm (iç küre yarıçapı); r = 40 mm (iç diz yarıçapı); Di = 430 mm; ea = 2 mm; fb = 133 MPa (Rp0.2/1.5, 133.333'ten yuvarlanmış); f = 154 MPa; z = 1.0; P = 4 MPa (geri türetilmiş). Not: Di = 430 < R geometrik olarak olağandışı (kaynak örnek değerleri), r/Di = 0.093 çıktıda yazılı.
Yayınlanmış sonuçlar: es = 7.843 mm (7.5-1); eb = 8.286 mm (7.5-3); ey ve nihai e = max(es,ey,eb) çıktıda BOŞ ("?"), alfa/beta grafik değerleri girilmemiş; ea/R = 0.003; hi = 68.046 mm (7.5 Not 3); Di/R·P/f koşul terimi = 0.023, 0.75+0.2·Di/R... koşulları çıktıda gösteriliyor.
Formülasyon notu: es = P·R/(2fz−0.5P) (yeniden doğrulandı: 2400/306 = 7.843). eb denklemi (0.75R+0.2Di)·[P/(111·fb)·(Di/r)^0.825]^(1/1.5) biçimindedir ve yeniden hesapla 8.29 verir. Bu vakada beta-faktörü (7.5.3.3) ve ey sayısal olarak yayınlanmamış; yalnızca es ve eb karşılaştırılabilir. İstenen "β faktörü" için bu vaka KISMEN yeterli.

### K4-03 — EN 13445-3 küresel gövde (yardımcı doğrulama) — 7.4.3
Kaynak: CERN, aynı sayfa · URL: aynı · Sayfa: ~3 · Standart: EN 13445-3 · Güven: Orta (P, f, z geri türetilmiş, K4-01 ile aynı küresel girdiler)
Girdiler: Di = 45 mm; De = 45.89 mm; f = 154 MPa; z = 1; P = 4 MPa (geri türetilmiş).
Yayınlanmış sonuçlar: e (7.4-4) = 0.294 mm; e (7.4-5) = 0.296 mm; Pmax (7.4-6) = 6.032 MPa; ea = 0.445 mm; Dm = 45.445 mm.
Formülasyon notu: e = P·Di/(4fz−P). Kapsam dışı (konu listesinde yok) fakat aynı kaynakta ücretsiz kontrol noktası olarak not edildi.

### K4-04 — EN 13445 / ASME / PD 5500 silindirik gövde karşılaştırması — 7.4.2
Kaynak: Ray Delaforce, "Comparison of Various Pressure Vessel Codes", 24 slayt, 24.03.2011 (Static Equipment Design, SlideShare/Scribd) · URL: https://www.slideshare.net/slideshow/comparison-of-various-pressure-vessel-codes/86271930 · Sayfa: Slayt 7 · Standart: ASME VIII-1 (2010 öncesi), ASME VIII-2, EN 13445-3, PD 5500 (baskılar sunumda belirtilmemiş) · Güven: Orta (rakamlar web özetleyicisinden; bir tutarsızlık kontrolü aşağıda)
Girdiler: P = 300 psi (≈2.07 MPa); D = 60 in (1524 mm); malzeme UTS 70000 psi, akma 38000 psi; hesap için sunumda E ihmal (z=1).
Yayınlanmış sonuçlar: ASME VIII-1 t = 0.454 in (11.534 mm); ASME VIII-2 t = 0.453 in; EN 13445 t = 0.453 in (11.516 mm); PD 5500 t = 0.453 in. Slayt 6'da izin verilen gerilmeler: ASME-1 20000 psi; ASME-2/EN/PD5500 25300 psi.
Formülasyon notu: 0.453 in sonucu, 7.4.2 formülüyle f = 20000 psi (25300 değil) kullanılırsa yeniden üretilir (300·60/(2·20000−300) = 0.4533). f = 25300 psi olsaydı ≈0.358 in çıkardı; yani slayt 7'de karşılaştırma kolaylığı için aynı gerilme (20000 psi) kullanılmış olması muhtemel. Bu nedenle bu vakayı yalnızca "f = 20000 psi verilirse e = 0.4533 in" kontrolü olarak kullan; f seçimi (6.6) kaynak hatasına açık.

### K4-05 — EN 13445-3 yarı-eliptik bombe (2:1) ve ASME VIII-1/2, PD 5500 karşılaştırması — 7.5.x (eliptik bomba, torispherik eşdeğer yöntemi)
Kaynak: Ray Delaforce, aynı sunum (SlideShare/Scribd) · URL: https://www.slideshare.net/slideshow/comparison-of-various-pressure-vessel-codes/86271930 · Sayfa: Slayt 10-19 · Standart: ASME VIII-1/-2, EN 13445-3, PD 5500 · Güven: Orta-düşük (yalnızca web özetleyicisi; EN formül adımları görülmedi, sadece nihai sayı)
Girdiler: P = 300 psi; D = 60 in; D/2h = 2 (h = 15 in); f = 25300 psi (Div2/EN/PD5500), S = 20000 psi (Div1); E ihmal.
Yayınlanmış sonuçlar: ASME VIII-1 t = 0.451 in (11.447 mm; UG-32/1-4(c) ile P·D/(2SE−0.2P) = 0.4507 doğrulandı); ASME VIII-2 t = 0.3219 in (8.177 mm, iteratif); EN 13445 t = 0.3886 in (9.862 mm); PD 5500 t = 0.3792 in (9.632 mm; h/D = 0.25, P/f = 0.119).
Formülasyon notu: EN 13445 hesabı kaynakta iteratif/eşdeğer torispherik yoluyla; hangi iç/dış çap veya toleransın kullanıldığı özetten görülmüyor. Eliptik bombeyi 7.5.3'teki eşdeğer torispherik (R, r) ile doğrulamak için bu vaka tek başına yetmez; sonuç kaynak-yanlı (0.3886 in) olarak okunur, güven sınırlı.

### K4-06 — EN 13445-3 silindirik gövde, yüksek basınç (8.25 MPa) — 7.4.2
Kaynak: K. M. B. Karthikeyan, T. Balasubramanian, A. R. Bruce, P. Premkumar, "Pressure Vessel Design by Design by Analysis Route", IOP Conf. Ser.: Mater. Sci. Eng. 923 (2020) 012020, doi:10.1088/1757-899X/923/1/012020 (CC BY 3.0) · URL: https://iopscience.iop.org/article/10.1088/1757-899X/923/1/012020/pdf · Sayfa: s. 3, Tablo 1, 3, 4 · Standart: prEN 13445-3 (yayın 2020; sürüm belirtilmemiş) ve ASME VIII (karşılaştırma) · Güven: Orta (PDF yerelde okundu; ancak makale kalite olarak zayıf: izin verilen gerilme hesabı "min(386.67; 299)" biçiminde, formül görselleri metne çıkmadı)
Girdiler: P = 8.25 MPa; Di = 2900 mm (R = 1450 mm); T = 120 °C; z (E) = 1.0; f = 299 MPa (P500-QT, Rm = 640, Rp0.2 = 580 MPa); f = 250 MPa (P355, Rm = 600, Rp0.2 = 380 MPa); korozyon payı 4 mm (gövde), 2 mm (kafa).
Yayınlanmış sonuçlar: hesaplanan kalınlık 40 mm (P500-QT) ve 48 mm (P355); ticari kalınlık seçimi 50 mm (4 mm korozyon payı dahil kullanıldığı belirtilmiş). Yeniden hesap: P·Di/(2fz−P) = 40.6 mm (f=299) ve 48.7 mm (f=250); makale aşağı yuvarlamış (40, 48).
Formülasyon notu: Kaynak sayıları tam sayı yuvarlanmış; test toleransı en az ±1 mm tanımla. Hesaplanan kalınlığa korozyon payı eklenmesi açıkça gösterilmemiş.

### K4-07 — EN 13445-3 izin verilen maksimum basınç (Pmax) — 7.4 / 7.6.6.3 atfı
Kaynak: Karthikeyan ve ark., IOP Conf. Ser. 923 012020 (aynı makale) · URL: https://iopscience.iop.org/article/10.1088/1757-899X/923/1/012020/pdf · Sayfa: s. 4, Tablo 7 · Standart: prEN 13445-3 · Güven: Orta
Girdiler: Dm = 3000 mm; ea = 50 mm; z = 1.0; f = 299 MPa (P500-QT) ve 250 MPa (P355).
Yayınlanmış sonuçlar: Pmax = 9.96 MPa (P500-QT) ve 8.33 MPa (P355).
Formülasyon notu: Pmax = 2·f·z·ea/Dm yeniden üretildi (9.967 ve 8.333 MPa); bu, K4-01 7.4-3 ile aynı bağıntı. Makale denklemi "7.6.6.3" olarak atıf yapıyor; asıl madde 7.4.2 (Denk. 7.4-3) olmalı.

### K4-08 — EN 13445-3 torispherik bombe, yüksek basınç — 7.5.3
Kaynak: Karthikeyan ve ark., IOP Conf. Ser. 923 012020 · URL: https://iopscience.iop.org/article/10.1088/1757-899X/923/1/012020/pdf · Sayfa: s. 3-4, Tablo 5-6 · Standart: ASME/prEN 13445-3 karışık atıf ([3],[5]) · Güven: Düşük (kafa geometrisi R, r verilmemiş; denklemler görsel olarak çıkmadı; hangi standardın formülü olduğu belirsiz)
Girdiler: P = 8.25 MPa; R1 = 1450 mm; f = 299 / 250 MPa; z = 1.0; gövde kalınlığı 50 mm; korozyon payı 2 mm.
Yayınlanmış sonuçlar: hesaplanan kalınlık 20 mm (P500-QT) ve 23 mm (P355); ticari 25 mm.
Formülasyon notu: Doğrulama için kullanılmamalı; yalnızca "yaklaşık mertebe" olarak kaydedildi. 7.5.3 es/ey/eb ayrımı veya β faktörü kaynakta yok.

---

## B. ASME UCS-66 / UCS-66.1 MDMT

Genel not: Aşağıdaki "kaynağın okuduğu MDMT" değerleri yazılım çıktılarından (PV Elite, COMPRESS) alınmış, UCS-66 eğrisi gömülmemiştir. Oran tanımı: stress ratio = tr·E* / (tg_sr − c); "Temp. Reduction" Fig. UCS-66.1 okumasıdır (yazılım çıktıda 140 °F'te sınırlıyor görünüyor). Birimler °F ve inç (kaynak aslı).

### K4-09 — Eliptik bombe SA-516 70, Curve B — UCS-66 / UCS-66.1 (yöneten kalınlık, oran, azaltım) + ASME UG-99 hidrotest
Kaynak: Pressure Vessel Engineering Ltd. (PVEng), "Design Calculation, ASME Code Version 2015", PV Elite 2017 çıktısı, Firetube örneği, 21.07.2017 · URL: https://pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf · Sayfa: PDF sayfa 4-5 (Shell Analysis: Head, Item 1) · Standart: ASME VIII-1 2015 · Güven: Yüksek (PDF yerelde okundu)
Girdiler: 2:1 eliptik bombe (AR = 2.0), Do = 72.0 in; Tmin = Tnom = 0.390 in; CA = 0; P = 125 psig @ 500 °F; S = 20000 psi; Sy = 31000 psi; E = 1.0; SA-516 70 (normalize değil), Curve B; düz boyun 2.0 in; girilmiş MDMT = −20 °F.
Yayınlanmış sonuçlar: tr = 0.2237 in (Appendix 1-4(c)); MAWP = MAPNC = 218.80 psig; tg = tg_sr = 0.390 in; stres oranı = 0.574; Fig. UCS-66.1 azaltımı = 45 °F; Fig. UCS-66 (azaltımsız) kaynağın okuduğu MDMT = −20 °F; UCS-66.1 ile gereken kalınlıkta MDMT = −55 °F; UG-20(f) muafiyeti −20 °F. Hidrotest: 284.44 psig (UG-99(b) ve (c)), pnömatik 240.68 psig (UG-100).
Formülasyon notu: Oran = tr/tg_sr (E*=1, c=0). Azaltım −20 − 45 = −65 olurdu; yazılım −55 °F raporluyor (başka bir sınır/yuvarlama ya da eğri okuması) — bu fark, PV Elite'in UCS-66.1 eğrisini ve alt sınırları uyguladığını gösterir. Uyumsuzluk 10 °F'dir; test toleransına dahil edilmeli. (Aynı sayfada "Min. Metal Temp. at Req'd thk." = −55 °F, azaltım 45 °F ve base −20 °F: −20−45 = −65 ≠ −55; bu tutarsızlık kaynakta açıklanmamış.)

### K4-10 — Yöneten kalınlık ≠ oran kalınlığı (kapak) — UCS-66 tg ve tg_sr ayrımı
Kaynak: PVEng, aynı çıktı (Firetube örneği), "Shell Analysis: Cover, Item 2" · URL: https://pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf · Sayfa: PDF sayfa ~27-28 · Standart: ASME VIII-1 2015 · Güven: Yüksek
Girdiler: SA-516 70 (normalize değil), Curve B; P = 125 psig @ 500 °F; E = 1.0; c = 0; tg = 0.297 in; tg_sr = 1.188 in; tr = 1.137 in.
Yayınlanmış sonuçlar: stres oranı = 0.957; Fig. UCS-66.1 azaltımı = 4 °F; Fig. UCS-66 kaynağın okuduğu MDMT = −20 °F (tg = 0.297 in); UCS-66.1 ile MDMT = −24 °F.
Formülasyon notu: İki ayrı kalınlık var: tg (UCS-66 eğrisinde okunan yöneten kalınlık) ve tg_sr (oran paydası). Bu vaka, "oran paydasında yönetici kalınlık" ile "eğri girişi" kalınlığının farklı olabileceğini sayısal olarak gösterir.

### K4-11 — İnce cidarlı boru (firetube) SA-106 B, Curve B — azaltım üst sınırı
Kaynak: PVEng, aynı çıktı, "Shell Analysis: Firetube, Item 3" · URL: https://pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf · Sayfa: PDF sayfa ~25 · Standart: ASME VIII-1 2015 · Güven: Yüksek (oran/azaltım/MDMT netçe okundu; basınç alanı sayfa yerleşiminde karışık)
Girdiler: SA-106 B boru, Do = 14.0 in; Tnom = 0.375 in, Tmin = 0.3281 in; S = 17100 psi; E = 1.0; c = 0; tg = tg_sr = 0.328 in; tr = 0.063 in (UG-16(b) minimumu 0.0625 in).
Yayınlanmış sonuçlar: stres oranı = 0.190; azaltım = 140 °F; Fig. UCS-66 kaynağın okuduğu MDMT = −20 °F; UCS-66.1 ile −155 °F; UG-20(f) −20 °F. MAWP = 816.88 psig.
Formülasyon notu: Oran ≤ 0.35 bölgesinde azaltım 140 °F ile sınırlanıyor (kaynak çıktısı: ≤0.35 muafiyet-bölgesi aynı mantık). tr burada UG-16(b) alt sınırından geliyor, basınç hesabından değil.

### K4-12 — Flanş, SA-516 70, Curve B — yüksek oran
Kaynak: PVEng, aynı çıktı (Firetube örneği) · URL: https://pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf · Sayfa: PDF sayfa ~35 (flanş MDMT sonuçları) · Standart: ASME VIII-1 2015 · Güven: Orta-yüksek (flanş geometrisi bu satırlarda yok)
Girdiler: SA-516 70, Curve B; stres oranı çıktıda doğrudan 0.911.
Yayınlanmış sonuçlar: azaltım = 9 °F; Fig. UCS-66 kaynağın okuduğu MDMT = −20 °F; UCS-66.1 ile −29 °F; UG-20(f) −20 °F.
Formülasyon notu: Tek başına oran ve azaltım, eğri-okuma testi için kullanılabilir (0.911 → 9 °F). tg ve tr çıktıda yok.

### K4-13 — Nozul boyun-flanş kaynağı, Curve B, ince cidar (0.5 in) — UCS-66 base temp
Kaynak: PVEng, aynı çıktı, Nozzle Analysis: Neck · URL: https://pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf · Sayfa: PDF sayfa 6-7 · Standart: ASME VIII-1 2015 · Güven: Yüksek
Girdiler: Curve B; tg = tg_sr = 0.500 in; tr = 0.100 in; c = 0; E* = 1.0.
Yayınlanmış sonuçlar: oran = 0.201; azaltım = 140 °F; Fig. UCS-66 kaynağın okuduğu MDMT = −6 °F (tg = 0.5 in); UCS-66.1 ile −146 °F; UG-20(f) −20 °F.
Formülasyon notu: "Kaynağın okuduğu MDMT = −6 °F" tg = 0.500 in için Curve B okumasıdır (başka vakalarda tg = 0.39 in için −20 °F ve tg = 0.625 in için +6 °F — bkz. K4-16). Bu üç nokta, eğri okuma yönü ve monotonluğu için kontrol noktasıdır.

### K4-14 — Silindirik gövde 0.750 in, SA-516 70 Curve B, korozyon payıyla — yöneten kalınlık ve oran
Kaynak: PVEng, "Heat Exchanger Sample" (PVE-4293, PV Elite 2012, yazar J. Luszczki CET, gözden geçiren L. Brundrett P.Eng., 20.09.2012; ASME VIII-1 2010/2011 add.) · URL: https://www.pveng.com/wp-content/uploads/2016/06/HeatExchanger_Calcs.pdf · Sayfa: PDF sayfa 24 ("Cylindrical Shell from 60 To 70", Step 5) · Standart: ASME VIII-1 2010, Addenda 2011 · Güven: Yüksek (PDF yerelde okundu)
Girdiler: SA-516 70, Curve B @ 650 °F; tg = 0.750 in; tr = 0.647 in; c = 0.0625 in; E* = 1.0; tasarım MDMT −20 °F.
Yayınlanmış sonuçlar: oran = 0.941 (= 0.647/(0.750−0.0625)); azaltım = 6 °F; Fig. UCS-66 kaynağın okuduğu MDMT = +16 °F; UCS-66.1 ile gereken kalınlıkta +10 °F; UG-20(f) −20 °F.
Formülasyon notu: Oran paydasında (tg − c) kullanılıyor; azaltım küçük (6 °F). Sonuç tasarım MDMT'sini (−20 °F) karşılamıyor (10 °F > −20 °F), ancak aynı çıktıda "UG-20(f)" satırı −20 °F — kaynak bu bileşen için muafiyet satırını ayrı raporluyor; çıktı nihai karar için tek başına yeterli değil.

### K4-15 — Nozul boyun-flanş kaynağı 0.756 in, yüksek azaltım ve alt sınır
Kaynak: PVEng, Heat Exchanger Sample (PVE-4293) · URL: https://www.pveng.com/wp-content/uploads/2016/06/HeatExchanger_Calcs.pdf · Sayfa: PDF sayfa ~55 (Nozzle junction MDMT) · Standart: ASME VIII-1 2010 add.2011 · Güven: Orta-yüksek
Girdiler: Curve B; tg = 0.756 in; tr = 0.263 in; c = 0.0625 in; E* = 1.0.
Yayınlanmış sonuçlar: oran = 0.379; azaltım = 118 °F; Fig. UCS-66 kaynağın okuduğu MDMT = +17 °F; UCS-66.1 ile −55 °F; UG-20(f) −20 °F.
Formülasyon notu: 17 − 118 = −101 °F iken kaynak −55 °F raporluyor: −55 °F ayrı bir alt sınır (örn. flanş/UCS-66(b)(1)(b)) gibi görünüyor, ama çıktıda gerekçe satırı alıntılanmadı. Bu vakada "−55 °F tabanı" kaynak-gözlemi olarak not edilir.

### K4-16 — Nozul-takviye (pad) yöneten kalınlık 0.625 in, oran 0.910
Kaynak: PVEng, Heat Exchanger Sample (PVE-4293), "Nozzle Calcs: S2, Nozl: 7" · URL: https://www.pveng.com/wp-content/uploads/2016/06/HeatExchanger_Calcs.pdf · Sayfa: PDF sayfa 61 · Standart: ASME VIII-1 2010 add.2011 · Güven: Yüksek
Girdiler: tg = 0.625 in; c = 0.0625 in; E* = 1.0; oran 0.910 (pad gerilmesi kabuk gerilmesine eşit alınmış, Div. 1 L-9.3 konservatif); Curve B.
Yayınlanmış sonuçlar: azaltım = 9 °F; Fig. UCS-66 kaynağın okuduğu MDMT = +6 °F; UCS-66.1 ile −3 °F; UG-20(f) −20 °F.
Formülasyon notu: K4-13 (0.5 in → −6 °F) ve K4-14 (0.75 in → +16 °F) ile birlikte Curve B için yönetici kalınlığa karşı üç nokta verir (0.5, 0.625, 0.75 in).

### K4-17 — Eliptik bombe diz bölgesi ve düz boyun, ince cidar, korozyon payı 0.0625 in
Kaynak: PVEng, Heat Exchanger Sample (PVE-4293), baş "Knuckle Portion" ve "Head Straight Flange" · URL: https://www.pveng.com/wp-content/uploads/2016/06/HeatExchanger_Calcs.pdf · Sayfa: PDF sayfa ~20 · Standart: ASME VIII-1 2010 add.2011 · Güven: Yüksek
Girdiler: SA-516 70 Curve B @ 650 °F; diz: tg = 0.168 in, tr = 0.074 in, c = 0.0625 in; düz boyun: tg = 0.188 in, tr = 0.075 in, c = 0.0625 in; E* = 1.0; tasarım MDMT −20 °F.
Yayınlanmış sonuçlar: diz: oran 0.699, azaltım 30 °F, UCS-66 kaynağın okuduğu −20 °F, UCS-66.1 ile −50 °F. Düz boyun: oran 0.597, azaltım 41 °F, UCS-66 −20 °F, UCS-66.1 ile −55 °F.
Formülasyon notu: Her iki satırda −20 − azaltım ile bulunan değerler (−50, −61) yerine düz boyunda −55 °F raporlanıyor; yine −55 °F tabanı görülüyor (bkz. K4-15). Küçük oranda (0.597 ve 0.699) çok net azaltım değerleri: 41 ve 30 °F.

### K4-18 — COMPRESS: nozul, SA-240 304 gövde/flanş, Curve B, azaltım 116.1 °F
Kaynak: Key Design Engineering (Waterloo, ON), "Sample Filter, KEY-026, COMPRESS Pressure Vessel Design Calculations per ASME VIII-1" · URL: https://keydesigneng.com/wp-content/uploads/2018/10/KEY026FilterVesselCalculationsperASMEVIII1.pdf · Sayfa: PDF sayfa 5/39 (MDMT özeti) ve ~28 (nozul) · Standart: ASME VIII-1 (baskı PDF'te yazılı, sürüm özeti okunmadı) · Güven: Orta-yüksek (PDF yerelde okundu; oranın hangi bileşene ait olduğu özet notundan, girdi tablosu görülmedi)
Girdiler: UCS-66 governing thickness = 0.1875 in; nozul boyun için Curve B muafiyet sıcaklığı; hesap basıncı 409.67 psi @ 250 °F (nozul bölümü); flanş sınıfı 150 6" WN A105.
Yayınlanmış sonuçlar: Fig. UCS-66 Curve B kaynağın okuduğu MDMT = −20 °F; Fig. UCS-66.1 azaltımı = 116.1 °F; coincident ratio = 0.38091; nominal nozul MDMT −55 °F (flanş yöneten, UCS-66(b)(1)(b) ve UHA-51 −320 °F); nihai MDMT UCS-66(b)(2) ile yöneten.
Formülasyon notu: COMPRESS azaltımı ondalıklı (116.1 °F) rapor ediyor, PV Elite tamsayı. Aynı ratio 0.38 değeri K4-15'te 118 °F verdi (PV Elite 0.379); iki yazılım arasında ~2 °F fark.

### K4-19 — Örnek soru/cevap derlemeleri (Curve D, normalize SA-516 70) — düşük güvenli
Kaynak 1: V. Rana, "ASME VIII MDMT and Impact Test Exemption", LinkedIn Pulse, 08.10.2022 · URL: https://www.linkedin.com/pulse/asme-viii-mdmt-impact-test-exemption-vikas-rana
Kaynak 2: amarineblog, "API 510 Questions and Answers (ASME VIII – Impact test)", 11.11.2020 · URL: https://amarineblog.com/2020/11/11/api-510-questions-and-answers-asme-viii-impact-test/
Kaynak 3: A. Singla, EPCLand, "Minimum Design Metal Temperature (MDMT) and Impact Testing Guide" · URL: https://epcland.com/minimum-design-metal-temperature-guide/
Sayfa: n/a (web) · Standart: ASME VIII-1 UCS-66, UCS-66.1, UCS-68(c); baskı belirtilmemiş · Güven: Düşük (üçü de yalnızca web özetleyicisinden; ham metin görülmedi; kaynak 2 içinde tutarsız ifadeler)
Girdiler/sonuçlar (yayınlandığı gibi, doğrulanmadı):
- Rana Örnek 3: normalize SA-516 70, Curve D, t = 1.125 in, tr = 0.95 in, E = 1.0, C = 0.125 in; oran 0.95; kaynak "sıcaklık bonusu = 8 °F"; MDMT −27 °F; hesap sonucu "muaf". (Oran = 0.95/(1.125−0.125) = 0.95 ile tutarlı.) Örnek 2: t = 1.125 in, MDMT −20 °F, tabloda izin verilen asgari sıcaklık −26 °F, "muaf". Örnek 4: UCS-68(c) PWHT bonusu 30 °F, MDMT −45 °F, nihai izin verilen −66 °F.
- amarineblog Q2: normalize SA-516 70, t = 2 in, oran 0.85, MDMT −25 °F; UCS-66 muafiyet sıcaklığı −4 °F; ek azaltım −15 °F; toplam −19 °F; "UCS-68(c) ile daha ileri kontrol gerekir". Q5: Curve B, t = 0.622 in, oran 0.64, MDMT −15 °F.
- EPCLand: SA-516 70 Curve D, yöneten kalınlık 38 mm (1.5 in), taban −32 °C, oran 0.65, azaltım 20 °C, nihai −52 °C.
Formülasyon notu: Bu sayılar eğri okumasına bağlı olduğundan K6 gereği sadece yayınlanmış değer olarak saklanır. Rana'daki 8 °F bonus ve EPCLand'daki 20 °C azaltımı, Fig. UCS-66.1 tablosuyla bağımsız doğrulanmadı; birim testi için değil, "dikkatle kullan" listesi. amarineblog Q2'de −4 °F + −15 °F = −19 °F aritmetiği tutarlı.

---

## Erişilemeyen / yetersiz çıkan kaynaklar (sayı UYDURULMADI)

- EN 13445-3 tam metni ve çözümlü örnekleri: DIN/Beuth/BSI/iteh/normoff katalog sayfaları yalnızca içindekiler; örnek yok.
- Dr. Ir. föyleri, üniversite ders notları (EN 13445-3 7.4.2/7.5.3/Bölüm 8): arama sonuç vermedi; bulunamadı.
- EN 13445 Bölüm 8 (dış basınç) sayısal örnek: YOK. UNM "EN 13445 Background to the rules in Part 3" (https://unm.fr/wp-content/uploads/2022/10/EN13445_background_part3.pdf, ed. G. Baylac & D. Koplewicz, Issue 2, 20.08.2004) yerelde okundu; Bölüm 8 ve 7C (dished ends) için teori ve karşılaştırma var, tek tek sayısal örneği yok. Örnekler yalnızca 16D-1 (nozul) ve 16D-2 (semer), tubesheet (13D) için; konu dışı.
- EN 13445-5 10.2.3.3 hidrostatik test: UNM CLAP 57 fişi (https://unm.fr/wp-content/uploads/2022/10/clap57e.pdf) sayısal örneği kaldırmış; MHD 2014-05-22 (https://unm.fr/wp-content/uploads/2022/10/EN13445MHD_questions_2020.pdf) yalnızca açıklama. Bentley KB (Pt = 1.3568 MPa örneği, arama özetinde geçti) — sayfa içeriği alınamadı, doğrulanamadı; kullanma.
- Eng-Tips başlıkları (UCS-66.1 coincident ratio 0.4965 / 32 °C / 35 mm gibi özetlerde geçenler; qid 485876 ve 324052): 403, ham metin yok; sayı doğrulanamadı.
- industrialmonitordirect.com UCS-66(b) sayfası: 403.
- Scribd belgeleri (EN 13445 Vessel "Try Vessel" 62 s; Astatine tank EN 13445-3:2021, 7.2 barg, 140 °C, 1800 mm × 5300 mm, 30 s; "PR EN 13445-3"; "Design of Unfired Pressure Vessels BS EN 13445-3"; Torispherical head 24 in Di, tmin 0.3 in, tr 0.2945, MAWP 101.92 psig — kod belirtilmemiş): yalnızca başlık meta bilgisi, hesap sayfaları alınamadı.
- Codeware COMPRESS EN 13445 örnek raporu: bulunamadı (Key Design örneği ASME'dir).
- PD 5500 ile kıyas makaleleri: yalnızca Delaforce sunumu bulundu.
- Annals of Faculty Engineering Hunedoara 2014 (Solticzky ve ark., EN 13445 ve ASME VIII yatay tank + semer): konu dışı (semer gerilmesi); sayısal örnek var (pd = 0.52 MPa, De = 2440 mm, e = 8 mm, P295GH) ama 7.4.2/7.5.3 değil. Gerekirse ileride semer kampanyasında kullanılabilir.
- PVEng DesignCalcsAuditSample, Sample3/Sample5 APV: MDMT satırları UG-20(f) muafiyeti veya yüksek hesaplanan azaltımlar (−122 °F, −155 °F) veriyor, ayrıntı girdileri okunmadı; kullanılmadı.
