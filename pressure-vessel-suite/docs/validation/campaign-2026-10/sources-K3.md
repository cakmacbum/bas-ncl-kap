# K3 — Kaynak avı: destekler ve dış yükler (2026-10-07)

Kapsam: Zick eyer (S1–S5/K1–K7), etek + taban halkası + ankraj, bacaklı kap, rüzgâr/deprem, Blodgett çizgi-kaynak.
Kural (K6): metin/tablo kopyalanmadı; yalnız atıf, URL, sayfa, girdi sayısı+birim, yayınlanmış sonuç sayısı. WRC eğri/katsayıları gömülmedi, "kaynağın kullandığı katsayı=..." notu düşüldü.
Güven: Y = yüksek (sayılar PDF'den doğrudan okundu ve iç tutarlılığı elle kontrol edildi), O = orta (sayılar okundu, girdi eksik veya kaynak ikincil), D = düşük (kısmi girdi / yalnız özet).
Toplam 22 vaka, 12 ayrı yayıncı/kaynak: Pressure Vessel Engineering (PV Elite + COMPRESS + elektronik tablo), AISC, ASCE, CRC Press, IJERT, IJIRSET, IJRASET, IAEME, IRJMETS, Kezar Engineering, Union College, Calcs.com.
Önemli not: PVE belgeleri bağımsız elle hesap değil yazılım çıktısıdır (PV Elite 2012, COMPRESS 2013, PVE e-tablosu); "yayınlanmış sonuç" bu yazılımların basılı çıktısıdır. Bağımsız doğrulama gücü AISC DG1 ve CRC/Union vakalarında daha yüksektir.

---

## A. Zick eyer (yatay kap)

### K3-01 — PV Elite 2012 eşanjör, Zick eyer, işletme durumu (sol eyer)
Kaynak: Pressure Vessel Engineering (Waterloo), "H&C Heat Transfer Sample", PVE-4293, PV Elite 2012, 18 Eyl 2012 · URL: https://www.pveng.com/wp-content/uploads/2016/06/HeatExchanger_Calcs.pdf · Sayfa: PDF s.34–37 (rapor "Page 34–37 of 96"); girdi yankısı s.6–7 · Yöntem/kod: ASME VIII-1 2010 + 2011a; eyer "ASME Sec. VIII Div. 2 (4.15) Zick" · Güven: Y (formüllerin ikamesi raporda açık, S1/S3/S5 elle yeniden üretildi)
Girdiler: kabuk Do=18.5 in, nominal t=0.75 in, korozyon payı 0.0625 in (t_cor=0.6875 in, Rm=8.9062 in); SA-516 70, S(işletme)=18 800 psi; teğetten teğete L=7.667 ft (rapordaki "stiffened L"=7.67 ft); eyer-teğet mesafesi a=6.62 in; eyer genişliği b=4.00 in; sarma açısı θ=120°; aşınma plakası 5.0 in genişlik x 0.25 in, 132° (rapor "kabuktan dar, yok sayıldı" diyor); tasarım basıncı P=1400 psig, 650 °F; eyer kuvveti Q=1696.94 lb; ek rüzgâr/deprem 0.
Yayınlanmış sonuçlar: M1=-6.5 ft·lb, M2=2376.7 ft·lb; boy. gerilme kabuk üst orta 8903.77, alt orta 9236.72, eyer üst 9074.51, eyer alt 9067.88 psi (izin 18 800); teğetsel kesme kabuk 277.72 psi (izin 15 040), T=1452.6 lb; eyer boynuzunda çevresel basma 253.77 psi (izin 23 500); σ6 (halka basması) 23.87 psi; B1=7.8602 in; etkin yarı-genişlik x1=x2=1.930 in; serbest ısıl genleşme 0.251 in. Kaynağın kullandığı katsayı (ASME Tablo 4.15.1, θ=120°, k=0.1): K1=0.1066, K2=1.1707, K3=0.8799, K4=0.4011, K5=0.7603, K6=0.0529, K7=0.0325, K8=0.3405, K9=0.2711, K10=0.0581, K1*=0.1923. Eyer yapısı: K8-benzeri yatay itki Fh=345.36 lb (0.2035·Q), taban plakası (Moss) min. 0.164 in.
Formülasyon notu: bu raporda σ3*=P·Rm/(2t) − M1/(K1·π·Rm²·t) ve σ4* ayrı K1* ile; M2'li orta kesit ve M1'li eyer kesiti ayrı. Dikkat: raporda "a ≥ Rm/2" uyarısı var (a=6.62 in, Rm/2=4.45 in) ve teğetsel kesme için K2 kullanılmış (kabuk, halkasız, ASME 4.15.14). Çevresel boynuz gerilmesi σ7 için L≥8Rm biçimi (3·K7·Q/(2t²)) kullanılmış ve basma işaretli. ASME'deki K adlandırması Zick orijinalinden ve COMPRESS adlandırmasından (K3-03) farklı; K-eşlemesi doğrulanmadan sayılar kullanılmamalı.

### K3-02 — Aynı rapor, hidrotest durumu ve sağ eyer (tek kaynak, ek yük durumları)
Kaynak: yukarıdaki PVE-4293 · URL: aynı · Sayfa: PDF s.38–46 ("Horizontal Vessel Analysis (Ope.)" sağ eyer ve "(Test)" sol/sağ) · Yöntem/kod: aynı · Güven: Y (aynı belge, aynı yazılım; ayrı yük durumları)
Girdiler: K3-01 ile aynı geometri; sağ eyer; hidrotest basıncı 1820.32 psig (kabuk merkezinde); hidrotest izin gerilmesi S=20 000 psi (kabuk), teğetsel izin 16 000, boynuz izin 25 000.
Yayınlanmış sonuçlar: işletme/sağ eyer Q=1961.51 lb: üst orta 8877.81, alt orta 9262.67, eyer üst 9075.18, eyer alt 9067.51, kesme 321.02, boynuz 293.34, halka basması 27.60 psi. Hidrotest/sol eyer Q=1800.76 lb: üst orta 10 607.18, alt orta 10 933.28, eyer üst 10 774.69, eyer alt 10 767.76, kesme 271.10, boynuz 232.08, halka 22.75 psi.
Formülasyon notu: iç basınç terimi (1400 psi) gerilmenin %95'ini oluşturuyor; bu vaka eyer momentini değil basınç+moment süperpozisyonunu ve izin gerilmesi tablolarını sınar. Eyer kaynaklı bileşenin kendisi (M/(K·π·R²·t)) mutlak değerce küçüktür (~2 ila ~200 psi), bu yüzden S1 türü bileşenlerin tek başına doğrulanması zayıf; boynuz ve kesme için duyarlı.

### K3-03 — COMPRESS 2013 "Generic Vessel", Zick eyer + deprem (NBC 2005) + ankraj
Kaynak: Pressure Vessel Engineering (T. Briant, B. Twolan, B. Munn), "Generic Vessel", PVE-6847, COMPRESS 2013 Build 7320, 18 Haz 2013 · URL: https://www.pveng.com/wp-content/uploads/2016/06/PVEclc-6847-0.1_Generic_Vessel.pdf · Sayfa: PDF s.~45–54 ("Saddle" bölümü 1/6–6/6, Support Skirt s.50–51) · Yöntem/kod: ASME VIII-1 2010 A11; not (1): "Zick" yöntemi; NBC Canada 2005 deprem/rüzgâr · Güven: Y (S1, S3, S4, S5 elle yeniden üretildi)
Girdiler: dış yarıçap R=18 in (hesapta 17.8125 in), kabuk t=0.375 in, baş t_h=0.2813 in; L=100 in; eyer ayrımı Ls=82.75 in; sol/sağ teğet mesafesi A=8.625 in; eyer yüksekliği Hs=30 in; θ=120°; eyer genişliği b=4 in; taban plakası 31.18x4x0.375 in; 4 rib; ts=0.375 in web; 2 ankraj/eyer, 0.625 in seri 8, kayma izni 15 000 psi; sürtünme μ=0.45; eyer başına ağırlık 2680 lb (işletme), eyer çifti ağırlığı 156 lb; P=288.27 psi; deprem Sa(0.2)=2.3, IE=1, Fa=1; Vp=3698.4 lbf; rüzgâr basıncı 21.93 psf.
Yayınlanmış sonuçlar: Qt=3558.79 lbf (enine deprem reaksiyonu), Ql=1340.81 lbf; Q=W+Qt=6238.79 lbf. S1 (eyerler arası, deprem/işl.)=246 psi (+Sp=6774 → 7020 çekme; izin 25 680); S2 (eyerde)=4 psi (+Sp → 6778); S3 kabuk 822 psi, S3 baş 1096 psi (izin 17 120), ek baş gerilmesi 500 psi (toplam 18 689, izin 26 750); S4 boynuz=-1768 psi (izin 32 100); S5 halka basması=2857 psi (izin 18 000); S6 eyer yarılma=564 psi (izin 11 067). Ankraj kayma 9154 psi (bir uç oluklu). Taban plakası 0.2474 in. Kaynağın kullandığı katsayı: K1=0.5892 (S1), K2.3=0.8799, K2.4=0.4011, K3=0.0132 (boynuz), K5=0.7603 (halka), K8=0.2035 (yarılma), K1'=1 (S2).
Formülasyon notu: bu raporda S1 = 3·K1·Q·(L/12)/(π·R²·t), S4 = -Q/(4t(b+1.56√(Ro·t))) − 12·K3·Q·R/(L·t²) (L<8R biçimi), S5 = K5·Q/(t(ts+1.56√(Ro·tc))), S2 = Mq·K1'/(π·R²·t) (K1'=1 girilmiş). COMPRESS "K1/K2.3/K3/K5/K8" adları K3-01'deki ASME adlarıyla (K1=0.1066, K3=0.8799, K5=0.7603, K7=0.0325, K8=0.3405) ve Zick orijinal adlarıyla bire bir değil: K5=0.7603 her iki raporda ortak (halka basması), K3(COMPRESS)=0.0132 ile K7(PV Elite)=0.0325 farklı büyüklükler (farklı yük kolu/biçim). Bu vaka, bağlam notundaki "Moss/Megyesy adı ile Zick adı eşlemesi" boşluğunun somut örneğidir.

### K3-04 — IJIRSET 2013, büyük yatay kap, stiffener halkalı Zick sonuçları (kısmi)
Kaynak: Adithya M., M. M. M. Patnaik, "Finite Element Analysis of Horizontal Reactor Pressure Vessel Supported on Saddles," IJIRSET Vol.2 Issue 7, Temmuz 2013 · URL: https://www.ijirset.com/upload/july/55A_Finite.pdf · Sayfa: s.3213–3215 (Tablo 1, 3, 4) · Yöntem/kod: Zick 1951 (kaynak [15]) + ANSYS · Güven: D (eyer yükü/ağırlık ve malzeme yoğunluğu verilmemiş; sonuçlar yeniden üretilemez)
Girdiler: L=13 107 mm, D=4267 mm (iç), t=23 ve 18 mm (iki konfigürasyon, hangisinin tabloya karşılık geldiği belirsiz), baş t=18 mm, A=1778 mm ve 275 mm (iki konfigürasyon), eyer genişliği 533.375 mm, θ=150°; SA-516 70; halkalar eyere bitişik.
Yayınlanmış sonuçlar (halkalar eyere bitişik, A=1778 mm): işletme S1 eyerde 16.248 MPa, orta açıklıkta 16.864 MPa; S2 kabukta 1.738 ve 0.694 MPa; S4=-1.957 MPa; S5=-5.267 MPa; halka dışı S6=-4.332 MPa. Hidrotest: S1 16.276 / 17.12 MPa; S2 2.38 / 0.95 MPa; S4=-2.679; S5=-7.213; S6=-5.932 MPa. İzinler: 128, 102.4, 161.89 MPa (işletme).
Formülasyon notu: S1…S6 adlandırması Moss/Megyesy tarzı, Zick orijinal etiketleri değil. Çalışma aynı zamanda ANSYS gerilim şiddetleri (örn. 298.278 MPa) verir fakat bunlar kuvvet–yer değiştirme farklı tanımlıdır; doğrudan Zick doğrulaması için kullanılmamalı. Q yok → yalnız sıralama/mertebe kontrolü.

### K3-05 — IJRASET 2025, küçük yatay kap, Zick kuramı / deney / FEA karşılaştırması (kısmi)
Kaynak: R. P. Jadhav, Y. G. Kamble, N. M. Mahajan, V. P. Rathod, "Comparative Analysis of Circumferential Stress in Horizontal Pressure Vessels Using Finite Element Analysis," IJRASET 2025, DOI 10.22214/ijraset.2025.66563 · URL: https://www.ijraset.com/research-paper/comparative-analysis-of-circumferential-stress-in-horizontal-pressure-vessels · Sayfa: Tablo 1 ve Tablo 2 (sayfa numarası HTML'de yok) · Yöntem/kod: Zick + ANSYS + gerinim ölçer deneyi · Güven: D (eyer yükü Q, D ve A sütun tanımları tam değil; deney-Zick karşılaştırmasında "Theory" sütunu basınçtan bağımsız)
Girdiler: dış yarıçap R=152.5 mm, t_s=3 mm, teğetten teğete 900 mm, eyer genişliği b=101.60 mm, θ=125°, SA-515 70; P=0.2/0.4/0.6/0.7 MPa; "D"=305 mm, A=180/225/247.5/292.5 mm (A: teğet–eyer mesafesi).
Yayınlanmış sonuçlar: Deneysel çevresel (hoop) gerilme P=0.7 MPa: A=180 → 30.38; 225 → 31.64; 247.5 → 35.35; 292.5 → 38.08 MPa. FEA: 40.34; 48.06; 47.63; 50.45 MPa. "Theory (Zick)": A=180 → 9.46; 225 → 16.7; 247.5 → 20.9; 292.5 → 30.54 MPa (basınçtan bağımsız, tüm P için aynı). P=0.2 MPa deney: 8.33; 9.52; 10.29; 12.04 MPa.
Formülasyon notu: Zick "Theory" sütununun hangi S bileşeni olduğu (S4/S5/boynuz) yazılmamış; ortalama gerinimden hoop gerilmesi "2×boy. gerilme" olarak çıkarılmış (Long.Stress sütunu = hoop/2). Bu sayıları regresyon eşiği olarak değil, Zick'in boynuz gerilmesini az tahmin ettiğine dair mertebe kanıtı olarak kullanın.

### K3-06 — IAEME 2013, Megyesy yöntemiyle eyer, girdi seti (sonuç tablosu görsel)
Kaynak: P. J. Pudke, S. B. Rane, Y. T. Naik, "Design and Analysis of Saddle Support: A Case Study in Vessel Design and Consulting Industry," IJMET Vol.4 Issue 5, Eyl–Eki 2013, s.139–149 · URL: https://iaeme.com/MasterAdmin/Journal_uploads/IJMET/VOLUME_4_ISSUE_5/IJMET_04_05_016.pdf · Sayfa: s.142 (Tablo 1), s.146 (Tablo 2 görsel) · Yöntem/kod: Megyesy "Pressure Vessel Handbook" + ANSYS APDL · Güven: D (Tablo 2 sonuçları görüntü; Tablo 1 metin sırası karışık, eşleme tahmini)
Girdiler (Tablo 1, sütun eşlemesi muhtemel): kabuk t=25 mm; kabuk yarıçapı 2900 mm; kabuk uzunluğu 37 350 mm; aşınma plakası genişliği 850 mm; taban plakası boyu 4000 mm; baş t=25 mm; aşınma plakası t=25 mm; sarma açısı 160°; gusset t=25 mm; SA 283 C eyer, SA 516 70 kabuk (S=133.6 N/mm²), eyer S=105.2 N/mm²; bir eyerdeki yük 6 012 549 N; tasarım sıcaklığı 315 °C; P=3.5 kg/cm².
Yayınlanmış sonuçlar: metinde sayısal Megyesy sonucu yok (Tablo 2 görsel). Metin: gusset kalınlığı 18 mm (6/10 gusset) FEA'da birincil gerilme sınırının altında.
Formülasyon notu: Megyesy sonuçları "gusset plakasının ortalama gerilmesi (N/mm²)" olarak anılıyor; yani Zick kabuk gerilmeleri değil eyer yapısı kontrolü. Zick doğrulamasına uygun değil; yalnız eyer yapısı kontrolü için girdi seti (PDF'den Tablo 2 elle okunursa tamamlanır).

### K3-07 — Kezar Engineering, eyer reaksiyonu + ısıl hareket tarama örneği
Kaynak: Kezar Engineering, "Pressure Vessel Saddle Calculation: Zick Method," Bölüm 10 "screening example" · URL: https://kezareng.com/articles/saddle-support-design-pressure-vessel · Sayfa: Bölüm 10 · Yöntem/kod: yazar kendi "tarama hesabı", ASME VIII-1 / Zick'e atıf · Güven: O (aritmetik elle doğrulandı; Zick gerilmeleri yok)
Girdiler: dış çap 2400 mm; teğetten teğete 9000 mm; eyer aralığı 7200 mm; eyer merkezi teğetten 900 mm; sarma açısı 120°; işletme ağırlığı 92 t; saha hidrotest ağırlığı 132 t; ΔT=80 °C; α=12e-6 /°C.
Yayınlanmış sonuçlar: işletme reaksiyonu eyer başına 451 kN; hidrotest 647 kN; ısıl hareket 6.9 mm. (Elle: 92·9.81/2=451.3; 132·9.81/2=647.5; 12e-6·80·7200=6.91 mm.)
Formülasyon notu: yalnız statik reaksiyon ve serbest genleşme; Zick gerilmeleri, K katsayıları ve izin oranları yok. Eyer reaksiyonu/ısıl hareket birim testi için uygun; S1–S5 doğrulamasında kullanılmaz.

---

## B. Etek (skirt), taban halkası, ankraj

### K3-08 — CRC Press (2005), etek + ankraj bolt örneği (kitap bölümü 10)
Kaynak: CRC Press, "Chapter ten: Design of vessel supports" (c) 2005 CRC Press; dosyada kitap/yazar adı yok, bölüm kaynakçası Widera–Sang–Natarajan 1988 ve Zick'e atıf yapıyor · URL: https://files.engineering.com/download.aspx?folder=4910f459-dcc5-40f9-93b9-143dbd09ceff&file=Chap10-Support_Design.pdf · Sayfa: 10.3.1–10.3.2, denklem (10.2)–(10.6) · Yöntem/kod: elle formül (σ=W/(πDt)+4M/(πD²t)), Norton Machine Design bolt dayanımı · Güven: O (girdiler ve σ doğrulandı; cıvata yükü yayınlanmış sayısı iç tutarsız)
Girdiler: dikey yük W=720 kN; devirme momenti M=2050 kN·m; cıvata dairesi çapı 4.5 m; etek kalınlığı t=10 mm; etek ortalama çapı Dm=4.25 m (D=4250 mm); N=12 cıvata; sınıf 4.6 (ispat gerilmesi 225 MPa).
Yayınlanmış sonuçlar: etek basma gerilmesi σ=19.84 MPa (elle: 5.39+14.45=19.84, doğru); cıvata başına yük P=166.8 kN; gerekli alan 741 mm²; M36 (gerilme alanı 816.72 mm²) x12 seçilmiş.
Formülasyon notu: DİKKAT, P=166.8 kN ifadesi (10.4)'ten üretilemiyor: W/N=60 kN ve 4M/(N·D)=160.8 kN (D=4250) ya da 151.9 kN (BCD=4500); toplam 220.8 ya da 211.9 kN, çıkarma ile 100.8 ya da 91.9 kN. Yayınlanmış 166.8 kN, yazım/hesap kayması olabilir. Bu sayıyı ancak gerekçe (hangi D, hangi W işareti) yeniden kurulursa regresyon eşiği yapın; σ=19.84 MPa güvenle kullanılabilir. Kitap formülü bolt'ı doğrusal alan (4M/(N·D)) ile yükler; Moss/ASCE eşdeğer alan yöntemi değildir.

### K3-09 — COMPRESS 2013 "Generic Vessel", etek (NBC 2005 deprem/rüzgâr)
Kaynak: PVE-6847 (K3-03 ile aynı rapor) · URL: https://www.pveng.com/wp-content/uploads/2016/06/PVEclc-6847-0.1_Generic_Vessel.pdf · Sayfa: PDF s.43–52 (Wind/Seismic Code, Support Skirt "50/54–52/54") · Yöntem/kod: ASME VIII-1 2010; NBC Canada 2005 (4.1.8.11) · Güven: Y (etek kalınlığı formülü elle yeniden üretildi)
Girdiler: etek SA-36, iç çap 36 in (üst/alt), uzunluk 24 in, nominal t=0.1875 in, korozyon 0; etek-baş birleşim verimi üstte 0.55, altta 0.8; Sc=13 226 psi, St=16 600 psi (250 °F); işletme ağırlığı W=5568.07 lb (üstte Wt=5423.29 lb); deprem momenti tabanda M=62 408.7 lbf·ft, üstte Mt=45 370.1 lbf·ft (V=8538.28 lb; Sa(0.2)=2.3; T=0.030 s); rüzgâr tabanda 3821 lbf·ft (Q=685 lbf).
Yayınlanmış sonuçlar: gerekli kalınlık: tabanda çekme t=0.0511 in, üstte çekme 0.0528 in, tabanda basma 0.0588 in, üstte basma 0.0436 in; en kritik 0.0588 in (basma, taban, depremli işletme); hesaplanan gerilme: deprem işletme (-) taban 4144.66 psi, (+) üst 4670.52 psi; rüzgâr işletme (-) taban 499 psi. Yeterlilik: 0.1875 in uygun.
Formülasyon notu: t = W/(π·D·Sc·Ec) + 48·M/(π·D²·Sc·Ec), D=36.1875 in (ortalama), 48 = 4·12 (M ft·lb → in·lb). Ankraj/taban halkası bu raporda yok. Kaynak verimi (0.55/0.8) çekme tarafında kullanılmış, basma tarafında E=1: bağlam notundaki "E=0.6" tartışması için ikinci bir yazılım örneği (üst birleşim 0.55).

### K3-10 — IJERT 2016, UBC-1997 deprem yüklü etek (dökme çelik etek)
Kaynak: Mitesh J. Mungla, "Design and Analysis of Pressure Vessel Skirt Considering Seismic Load as per Uniform Building Code," IJERT NCIMACEMT-2016, Vol.4 Issue 10, DOI 10.17577/IJERTCONV4IS10007 · URL: https://www.ijert.org/research/design-and-analysis-of-pressure-vessel-skirt-considering-seismic-load-as-per-uniform-building-code-IJERTCONV4IS10007.pdf · Sayfa: s.2–4 · Yöntem/kod: UBC-1997 (Cv=0.64 Nv; R=2.9) + birleşik yük (basınç + ağırlık + deprem momenti) · Güven: O (PDF'den okundu, iç aritmetik kontrol edildi; metin ile Tablo 4 arasında 6646/6643 psi küçük fark; Vseismic sınır dışı tutarsızlığı yazarlarca ele alınmamış)
Girdiler: UBC-1997, bölge katsayısı 0.4, Nv=1.2, Na=1.0, I=1.25, Ip=1.50, Cv=0.768, R=2.9; kap toplam ölü ağırlığı 1 073 680 lb; "C.S." etek: yükseklik 240 in, iç çap 169.84 in + 2·1.496 in, t=1.496 in, Dm=171.336 in; etek ağırlığı 88 000 lb; P=0; izin gerilmeleri: çekme 14 337.4 psi, basma 12 387.9 psi.
Yayınlanmış sonuçlar: Vseismic(css)=1 073 791.853 lb; Vmax=509 072.4 lb; Vmin=177 694.04 lb; (Vmax kullanılarak) etek kesme kuvveti 6651.52 lb; kümülatif kesme 6651.52+385 255.8 lb; moment 66 515.2 lb·ft (kümülatif 19 408 530.2 lb·ft); birleşik gerilme çekme 6646.44 psi (0.464 oran), basma -6865.12 psi (0.554 oran).
Formülasyon notu: σ = P·D/(4t) ± 4M/(π·Dm²·t) − W/(π·Dm·t); elle: 4·19 408 530·12/(π·171.336²·1.496)=6752 psi, W terimi 109.3 psi. Yani yayınlanan formül, Moss'un eşdeğer-A/Z "ince kabuk" biçimiyle aynı; etek-birleşim verimi E uygulanmamış (oran doğrudan izin gerilmesiyle). Kaynak tasarım yöntemi bilgi için: UBC-1997 bugün yürürlükte değil; yalnız kapalı-form tutarlılık testi.

### K3-11 — Kezar Engineering, etek tarama örneği (A, Z, hat kuvveti)
Kaynak: Kezar Engineering, "Vertical Pressure Vessel Skirt Support Design" tarama örneği · URL: https://kezareng.com/articles/vertical-pressure-vessel-skirt-support-design · Sayfa: "Worked Screening Example" bölümü · Yöntem/kod: elle formül (A_s=π·Dm·t_eff, Z_s=π/4·Dm²·t_eff); ASME VIII-1/ASCE 7-22 atıfları · Güven: O (aritmetik elle doğrulandı; tek yazarlı pazarlama makalesi)
Girdiler: Dm=3.00 m; nominal t=16 mm; etkin t=14 mm; eksenel basma 1.80 MN; eğilme momenti 2.10 MN·m.
Yayınlanmış sonuçlar: A_s=0.13195 m²; Z_s=0.09896 m³; P/A_s=13.64 MPa; M/Z_s=21.22 MPa; σ_z,max=34.86 MPa (basma); σ_z,min=-7.58 MPa (çekme); maks duvar hat kuvveti q_s,max=488.08 kN/m; q_s,min=-106.10 kN/m.
Formülasyon notu: en yalın A/Z yöntemi; kaynak verimi, burkulma izni, taban halkası ve ankraj yok. Hat kuvveti (kN/m) = σ·t_eff. Yalnız çekirdek A/Z/hat-kuvveti aritmetiği için uygun.

### K3-12 — IRJMETS 2024, PV Elite, 2200 mm iç çaplı dikey kap, "skirt/leg" taban halkası (kısmi)
Kaynak: S. Gawande ve ark., "Design of Vertical Pressure Vessel Using PV Elite Software," IRJMETS Vol.6 Issue 4, Nisan 2024, DOI 10.56726/IRJMETS53653 · URL: https://www.irjmets.com/uploadedfiles/paper/issue_4_april_2024/53653/final/fin_irjmets1713767182.pdf · Sayfa: s.7066–7076 (etek/bacak çıktıları s.7075) · Yöntem/kod: ASME VIII-1; PV Elite taban halkası (Moss, "continuous top ring"), AISC E2-1 · Güven: D (etek/bacak geometrisi ve ankraj girdileri şekillerde, metne alınmamış; kabuk/baş sonuçları açık)
Girdiler: iç çap 2200 mm, T–T 4000 mm, 2:1 elips baş, P=10 barg, 150/-20 °C, SA-516 70N, S=137.9 MPa, E=0.85, korozyon 3 mm, yalıtım 100 mm; rüzgâr IS 875, deprem IS 1893; destek "4 adet", başlıkta "skirt", çıktıda "Kl/r, gusset" yani bacak/ayak tarzı.
Yayınlanmış sonuçlar: gerekli kabuk t=9.8226+3.0 mm; Kl/r=60.6208; Cc=130.1324; izin burkulma (E2-1)=113.76 N/mm²; gerçek 23.57 N/mm²; gusset gerekli t=5.9221 mm (girilen 10 mm); taban halkası gerekli (basit)=13.9919 mm (girilen 25 mm); üst halka sabit kiriş=14.6098 mm; Moss sürekli üst halka=20.6702 mm (girilen 25 mm).
Formülasyon notu: aynı çıktıda hem "skirt" hem "gusset/bacak" terimleri; "Moss sürekli üst halka" kalınlığı 20.6702 mm, "fixed beam" 14.6098 mm'den büyük. Girdiler (cıvata sayısı, daire çapı, rüzgâr/deprem momenti) şekillerde → yeniden üretim için PDF şekilleri elle okunmalı.

---

## C. Bacaklı (leg) kap

### K3-13 — PVE-Sample 8, açı-profil bacaklı dikey kap (NBC-95 deprem, AISC, bacak-gövde kaynağı, WRC 107)
Kaynak: Pressure Vessel Engineering Ltd. (C. Liu, L. Brundrett), "Sample Vessel 8 / PVE-Sample 8, Pressure Vessel Calculations," 27 Nis 2007, e-tablo çıktısı · URL: https://www.pveng.com/wp-content/uploads/2016/06/Sample8_Spreadsheet.pdf · Sayfa: s.22–25 ("Seismic – Vessel on Beams") · Yöntem/kod: ASME VIII-1 2004, NBC-95 deprem, AISC bacak kontrolü (Fa, Fe, birleşik gerilme), bacak-gövde kaynağı, WRC 107 · Güven: Y (f1, f2, Mb, bacak gerilmeleri ve birleşik oran elle yeniden üretildi)
Girdiler: Do=42 in, kabuk t=0.75 in, H=130 in, ağırlık merkezi L=80 in, W=12 300 lb, P=353.9 psi; 4 bacak, açı 4"x5/8", Ix=Iy=6.66 in⁴, A=4.61 in², r=1.2 in, serbest boy ls=26.5 in, bacak aralığı çapı ds=44.5 in, K1=0.8, Sb=17 100 psi, Sa=16 200 psi; kaynak boyu lw=13.5 in, ws=0.25 in, ayak kaynağı 16 in; deprem: I=1, v=0.4, Za=6, Zv=5, F=1.3, S=4.2, R=4, U=0.6; WRC 107 geometrisi 2C1=5.657 in, 2C2=13.5 in.
Yayınlanmış sonuçlar: statik sehim y=0.024 in; T=0.049 s; Ve=26 863 lb; V=4029 lb; Mb=322 358 lb·in; Mt=215 577 lb·in; f1 (maks. eksantrik)=8208 lb; f2 (eksenel)=10 319 lb; f3x=f3y=1007 lb; e=1.25 in; Mx=My=36 955 lb·in; Sbmax=21 375 psi; fx=fy=11 098 psi; K1·ls/r=17.667; Fa max=25 675 psi; fa=2238 psi; Fe=494 954 psi; Fc1=Fc2=0.53. Bacak-gövde kaynağı: Iwx=102.5, Iwz=30.5, Iwy=133.0; Mx=37 339; Sx=2433, Sy=1791, Sz=93, Sg=456 psi; Slim=7938 psi (=0.49·min(Sb,Sa)); toplam oran 0.601; ayak plakası toplam 0.129. WRC 107: SL=4707 psi, Sc=9768 psi (basınç), β1=0.137, β2=0.327, γ=27.5. Kaynağın kullandığı WRC katsayıları (eğri okuması, gömmeyin): 3C=3.74796, 4C=1.88561, 1C=0.08088, 2C=0.04871 (basınç Nx/Mx), 3A=1.05302, 4A=1.71344, 1A=0.08268, 2A=0.03430, 3B=2.75635, 4B=1.12882, 1B=0.01754, 2B=0.03569.
Formülasyon notu: "Hat kaynak" yaklaşımı Blodgett'tan farklı: Iw = (ws·lw³/12)·2 ile kaynak, bacak boyu ws=0.25 in şeridi olarak alan atalet momenti (birim-boğaz çizgisi değil) ve Slim=0.49·min(Sb,Sa) ortak izin; yani vakanın kaynak kısmı Blodgett Sw doğrulamasına değil, ancak "alan yaklaşımı" regresyonuna uygun. Bacak aksiyal: f2=W/n+4Mb/(n·ds); eksantriklik e=(ds-Do)/2; birleşik gerilim = fa/Fa + 0.85·fx/((1-fa/Fe)·Sbmax). Tabana ankraj/taban plakası bölümü bu örnekte yok.

### K3-14 — IJERT 2013, PV Elite borulu bacak + taban plakası + cıvata (3 bacak)
Kaynak: Binesh P. Vyas, R. M. Tayade, Ankit D. Kumbhani, "Design of Vertical Pressure Vessel Using PVElite Software," IJERT Vol.2 Issue 3, Mart 2013 (VJTI) · URL: https://www.ijert.org/research/design-of-vertical-pressure-vessel-using-pvelite-software-IJERTV2IS3311.pdf · Sayfa: s.4–5 (bacak ve taban plakası çıktıları) · Yöntem/kod: ASME VIII-1; AISC E2-1; taban plakası Moss; cıvata Bednar; IS-1893 Bölge III · Güven: O (PDF'den okundu, KL/r ve gerilme kontrol edildi; kabuk geometrisi kısmi)
Girdiler: 3 boru bacak, OD 88.9 mm, ID 77.927 mm, boy 700 mm (bacak boyu), A=14.377 cm², I=125.583 cm⁴, r=29.555 mm, k=1.0, Fy=248 N/mm²; yük W=1574.2 kgf (üst), devirme momenti 0, kesme 0; taban plakası 150x150 mm, girilen t=14 mm, cıvata dairesi/OD 1006 mm?, tasarım P (iç basınç) 35.535 psig, 316L kabuk, ρ=1.0.
Yayınlanmış sonuçlar: KL/r=23.68, Cc=127.18; izin basma Sa=140.53 N/mm²; gerçek Sma=3.58 N/mm²; izin eğilme 148.93 N/mm²; birleşik oran 0.0255; bearing FC=228.69 kPa (P=524.72 kgf, AA=225 cm²); m=43.57 mm; gerekli plaka t=2.51 mm (girilen 14 mm); gerekli cıvata alanı -0.3970 cm² (çekme yok); cıvata kök alanı 1.44 cm².
Formülasyon notu: bu vaka devirme/kesme sıfır; yalnız ağırlık yükü. Taban plakası formülü t=√(3·FC·m²/(1.5·SBA)); burkulma izni AISC E2-1 (ASD) biçiminde. Rüzgâr/deprem yüklü sürüm ve eğilme kontrolü sınanmaz; yalnız eksenel+plaka+cıvata zinciri.

---

## D. Taban plakası, ankraj, beton (AISC Design Guide 1)

Ortak kaynak: J. M. Fisher, L. A. Kloiber, "Base Plate and Anchor Rod Design," AISC Steel Design Guide 1, 2. baskı, 2006 (AISC 2005 Spec., ACI 318-08 D eki). URL (Hilti barındırması, resmi AISC nüshasıyla aynı baskı): https://files-ask.hilti.com/original/gd/gd8nj58a0r.pdf · Bölüm 4 "Design Examples". Birimler ABD (kips, in, ksi). Bina kolonu için yazılmıştır; kap taban plakası/ankraj hesabına yalnız plaka eğilmesi, beton ezilmesi ve ankraj çekmesi bakımından aktarılır. Güven: Y (PDF metninden okundu; "Use" satırlarındaki kesirli kalınlıklar OCR'da harf olarak geldi, aşağıda "?" ile işaretlendi).

### K3-15 — DG1 Örnek 4.1: merkezi eksenel basma (W12x96)
Kaynak: AISC DG1 2. bas. · URL: yukarıda · Sayfa: Bölüm 4.1, s.30–32 · Yöntem/kod: AISC 2005 (LRFD/ASD), ACI 318-08 · Güven: Y
Girdiler: Pu=700 kips (LRFD), Pa=430 kips (ASD); kolon W12x96 (d=12.7 in, bf=12.2 in); fc'=3 ksi; plaka Fy=36 ksi; direk/ayaklık 24x24 in; φc=0.65, Ωc=2.50.
Yayınlanmış sonuçlar: A1(req)=422 in²; seçilen plaka N=22 in, B=20 in (A1=440 in²); betonun taşıma kapasitesi 729 kips (LRFD) / 449 kips (ASD); m=4.97 in, n=5.12 in, n'=3.11 in, l=5.12 in; X=0.960 → λ=1.63→1; t_min=1.60 in (LRFD) / 1.54 in (ASD); kullanılan 1⅝? in (OCR "1w"); ankraj çubuğu çekmesi yok.
Formülasyon notu: Thornton/Murray tipi m,n,n' yaklaşımı, φ ve Ω farklı; confinement yok (Örnek 4.2 aynı yükle A2 kullanır: A1(req)=211 in², N=16, B=14 in).

### K3-16 — DG1 Örnek 4.6: küçük moment taban plakası
Kaynak: AISC DG1 2. bas. · Sayfa: Bölüm 4.6, s.37–39 · Güven: Y
Girdiler: PD=100, PL=160 kips; MD=250, ML=400 kip·in; W12x96; fc'=4 ksi; Fy=36 ksi; N=B=19 in; A2/A1=1.
Yayınlanmış sonuçlar: Pu=376 kips, Mu=940 kip·in; e=2.50 in (LRFD ve ASD); fp(max)=2.21 ksi (LRFD) / 1.36 ksi (ASD); qmax=42.0 / 25.8 kips/in; ecrit=5.02 / 4.46 in (e<ecrit, küçük moment); Y=N-2e=14.0 in; fp=1.41 / 0.977 ksi; q=26.9 / 18.6 kips/in; t_req=1.36 in (LRFD) / 1.39 in (ASD), n kontrolü yönetiyor; kitapta seçilen "12?" in x19 in x 1 ft-7 in (1½ in, OCR).
Formülasyon notu: ASD fp(max) için Ωc=2.50; basma dikdörtgen gerilme bloğu e<ecrit.

### K3-17 — DG1 Örnek 4.7: büyük moment taban plakası (çekme ankrajlı)
Kaynak: AISC DG1 2. bas. · Sayfa: Bölüm 4.7, s.39–41 · Güven: Y
Girdiler: PD=100, PL=160 kips; MD=1000, ML=1500 kip·in; W12x96; fc'=4 ksi; Fy=36 ksi; ankraj kenar mesafesi 1.5 in; ilk deneme 19x19 in, ikinci deneme 22x22 in.
Yayınlanmış sonuçlar: Pu=376, Mu=3600 kip·in (LRFD); Pa=260, Ma=2500 kip·in (ASD); e=9.57 / 9.62 in; ilk deneme: ecrit=5.02 / 4.46 in, Denklem 3.4.4 sağlanmıyor (315>306, 355>306 in²); ikinci (22x22): qmax=48.6 / 29.9 kips/in; ecrit=7.13 / 6.65 in; f=9.5 in; Y=9.30 / 11.2 in; ankraj çekmesi Tu=76.0 kips, Ta=74.9 kips; t_req (basma ara yüzü, yönetici)=2.26 in (LRFD) / 2.18 in (ASD); çekme ara yüzü 1.24 / 1.51 in; 1/2? in çaplı F1554 Gr.36 çubuk 57.7 kips tasarım dayanımı (2 çubuk/yüz, çubuk başına 38.0 kips).
Formülasyon notu: Y, Tu = qmax·Y − Pu; Denklem 3.4.4 varlık koşulu; çekme ara yüzünde x=3.60 in kolu. Bu vaka kap ankrajı için "büyük devirme" kontrol zincirini en iyi sınayan örnek.

### K3-18 — DG1 Örnek 4.5: çekme ankrajı, beton kopma konisi ve pier donatısı
Kaynak: AISC DG1 2. bas. · Sayfa: Bölüm 4.5, s.34–37 · Güven: Y (kısmi: OCR'da bazı kesirler harf)
Girdiler: W10x45 kolon; PDL=22 kips, PUPLIFT=56 kips (rüzgâr, nominal); fc'=4000 psi; donatı fy=60 ksi; 4 çubuk, 4 in kare desen; çubuk 7/8? in (OCR "d-in."), Fu=58 ksi, Ab=0.601 in²; büyük serbest temel (a) ve 20x20 in pier (b).
Yayınlanmış sonuçlar: net çekme 69.8 kips (LRFD), çubuk başına 17.5 kips (LRFD) / 10.7 kips (ASD); Rn=26.1 kips, tasarım 19.6 / izin 13.1 kips/çubuk; plaka t=1.04 in (LRFD) / 0.996 in (ASD) (1¼? / 1 in); kanca yatak dayanımı 8.10 kips < 17.5 → olmaz; hef=13 in için Ncbg=77.5 kips > 69.8 (AN=1850 in², ANo=1520 in²); pier içinde (b) Ncbg=25.6 kips < 69.8 → donatıya aktar: As=1.29 in², 4-#10; ld=44.1 in; le=14.6 in; hef=22 in. Kaynak (kolon-plaka): 3/16? in köşe kaynak her iki yüzde; ağ gerilmesi 27.4 ksi (LRFD).
Formülasyon notu: ACI 318-08 Ek D beton kopma dayanımı Ncbg (hef<11 in için 24λ√f'c hef^1.5 biçimi, hef=13 in için 16λ√f'c hef^5/3 biçimi), çubuk Rn=0.75·Fu·Ab. Güncel ACI 318-19 Bölüm 17 ile katsayılar farklı olabilir; bu vaka eski baskı rejimidir.

---

## E. Rüzgâr, deprem, çubuk burkulması, çizgi-kaynak

### K3-19 — ASCE, "Wind Loads for Petrochemical and Other Industrial Facilities" §6.4: 150 ft dikey kap rüzgâr yükü
Kaynak: ASCE Petrochemical Committee, Task Committee on Wind-Induced Forces, ASCE Press 2011; PDF nüshası üçüncü taraf barındırmada, resmi ASCE nüshası değil · URL: http://m.16streets.com/39-B/PDF%20files/WIND%20LOADS%20FOR%20PETROCHEMICAL%20AND%20OTHER%20INDUSTRIAL%20FACILITIES.pdf · Sayfa: kitap s.140–149 (§6.4, Şekil 6.4.1, Tablo 6.4.1–6.4.3, Gf hesabı) · Yöntem/kod: ASCE 7-05 (Şekil 6-21, §6.5.8) · Güven: Y (tablolar metinde açık; telif nedeniyle yalnız toplamlar aktarıldı)
Girdiler: D=10 ft, h=150 ft (etkin yükseklik 160 ft); V=120 mph (qz'de V²=120²), I=1.15 (Kategori III), Kd=0.95, Kzt=1.0, Maruziyet C, G=0.85; basit yöntem pürüzlü: Cf=0.84, etkin D=15 ft; ayrıntılı: Cf=0.64, etkin D=11.5 ft; boş ağırlık 280 kip (+%10), işletme 500 kip (+%10); t=1.0 in; sönüm 0.01; b=0.65, c=0.20; platform çerçevesi/korkuluk Cf=2.0; 18 in boru Cf=0.7.
Yayınlanmış sonuçlar: basit yöntem taban kesmesi 82 496 lb (367 kN) (z=0–15: Kz=0.85, qz=34.2 psf, 5495 lb … 140–160: Kz=1.39, 56.0 psf, 11 995 lb); ayrıntılı kap+çeşitli 44 690 lb (199 kN); büyük boru 6716 lb (29.9 kN); platformlar 7468 lb (33.22 kN); toplam ayrıntılı 58 868 lb (261 kN). Esnek (Gf=1.099): basit 106 659 lb (475 kN); ayrıntılı 76 114 lb (339 kN). Periyot: boş T=0.869 s (rijit), işletme T=1.138 s (esnek, h1=0.879 Hz); gR=4.159; N1=4.02; Rn=0.058; Rh=0.196; RB=0.825; RL=0.564; Vz=133.49.
Formülasyon notu: F = qz·G·Cf·Ae, qz = 0.00256·Kz·Kzt·Kd·V²·I; kaynak devirme momentini ayrıca yazmıyor (kesme tablolarından z ile çarparak türetilebilir, yayınlanmış değil). Bu, ASCE 7-05 (G=0.85) çerçevesidir; güncel ASCE 7-16/22'deki Kd/qz ve Cf kuralları farklıdır, kod baskısı belirtilmelidir.

### K3-20 — AISC Companion Examples (v15.1): W14x132 pimli kolon, KL/r burkulma (E.1A)
Kaynak: AISC, "Companion to the Steel Construction Manual, Version 15.1" (2019), Örnek E.1A; sayısal okuma Calcs.com doğrulama sayfasından · URL: https://support.clearcalcs.com/article/164-steel-column-validation-examples (yönlendirme: https://calcs.com/support/steel-column-validation-examples) · Sayfa: Örnek 1 (E.1A) · Yöntem/kod: AISC 360-16 Bölüm E (LRFD) · Güven: O (asıl AISC örneği doğrudan okunmadı; sayılar ikincil sayfadan)
Girdiler: W14x132 (Fy=50 ksi) ve W14x120 (Fy=65 ksi); L=30 ft; pimli uç; D=140 kips, L=420 kips.
Yayınlanmış sonuçlar: faktörlü yük 840 kips; mevcut dayanım φPn=893 kips (Gr.50), 856 kips (Gr.65).
Formülasyon notu: bacak/ayak burkulma doğrulaması için bir kontrol; kap bacağı genellikle K=1.0 olmayabilir. Hesap Calcs.com tarafından birebir üretilmiş (893/856).

### K3-21 — AISC Companion Examples: HSS 12x8x3/16, narin elemanlı kolon (E.10)
Kaynak: AISC Companion v15.1, Örnek E.10 (okuma Calcs.com) · URL: aynı (Örnek 3) · Güven: O
Girdiler: HSS 12x8x3/16, L=24 ft, Fy=50 ksi (ASD).
Yayınlanmış sonuçlar: kritik burkulma gerilmesi Fcr=29.1 ksi; etkin alan 5.77 in² (Calcs.com 5.7 in², nominal et kalınlığı kullandığı için); mevcut basma dayanımı Pn/Ω=101 kip (Calcs.com 99.4 kip).
Formülasyon notu: borulu/kutu bacak için narinlik azaltma kontrolü; Calcs.com ve AISC arasındaki %1.6 fark, yazılımın nominal kalınlık seçiminden gelir (kaynakta açık).

### K3-22 — Union College MER419, Shigley 10. bas. Tablo 9-2: kapalı dikdörtgen kaynak grubu (çizgi kaynak)
Kaynak: R. B. (ders notu "RBB"), Union College MER419 Machine Design, L15 "Welding Bending Fatigue Strength"; Shigley's Mechanical Engineering Design 10. bas. Tablo 9-2/9-3/9-4 · URL: https://rbb.union.edu/courses/MER419/content/data/Lectures/MER419%20L15%20Welding%20Bending-Fatigue-Strength.pdf · Sayfa: slayt 12–18 · Yöntem/kod: kaynak = çizgi (birim ikinci alan momenti Iu, birim boğaz t=0.707h); AISC izinleri (0.30·Sut) · Güven: O (aritmetik elle doğrulandı; problem şekli metinde yok, geometri b,d sayılarından çıkarıldı)
Girdiler: kapalı dikdörtgen kaynak grubu b=70 mm, d=120 mm (toplam çizgi uzunluğu 2(b+d)=380 mm); V=10 000 N; kol l=160 mm (M=1600 N·m); c=60 mm; E60 elektrot (Sut=427 MPa; Sy=345 MPa); güvenlik katsayısı 3.
Yayınlanmış sonuçlar: Iu=d²(3b+d)/6=0.792e-3 m³; birincil kesme V/(2(b+d))=26.3 kN/m (≙26.3e3 N/m / t); ikincil kesme M·c/Iu=121.2 kN/m; bileşke 124.0 kN/m; gerekli boğaz t=0.968 mm (izin 0.30·427=128.1 MPa); güvenlik katsayısı 3 ile (0.577·345/3) t=1.869 mm, bacak h=2.64 mm (pratikte ≥3 mm).
Formülasyon notu: Blodgett eşdeğeri: Sw = Iu/c = bd + d²/3 = 13 200 mm² (kapalı dikdörtgen) ve Lw=2(b+d)=380 mm; M/Sw=1.6e6 N·mm/13 200 mm²=121.2 N/mm, V/Lw=26.3 N/mm; bileşke √(26.3²+121.2²)=124.0 N/mm. Yani bu vaka, bağlam notundaki "Sw=bd+d²/3" kimliğini bağımsız yayından doğruluyor (Sw değeri burada türetilmiştir, kaynak Iu'yu verir). Bileşkede birincil ve ikincil kesme dik toplanmış.

---

## Erişilemeyen / kullanılamayan kaynaklar (uydurma sayı yazılmadı)

- Scribd belgeleri (HTML sayfası gövdeyi vermiyor): Skirt-Support-Design (343854205), Leg-Calculation (212549310), Saddle-Calc (357093225), Zick Analysis for Saddle Support (908580609/355101316/908580597), ASME-Code-Calculation (662290269), Skirt & Anchor Bolt Brownell&Young (508007854), Support Leg Design (322680314), Leg-Support-Design (381516446), Blodgett Welds LRFD ASD (357409262), Design of Welded Structures (54993739). Arama özetleri sayı veriyordu (örn. "323 170 lb-ft rüzgâr momenti, 16 mm etek, M40 x12 bolt, 45.1 mm halka") ama belge gövdesi okunamadı; yazılmadı.
- GlobalSpec "Pressure Vessel Design: The Direct Route", Ek E.8 (skirt'li reaktör kolonu, işletme ağırlığı 3.6 MN, rüzgâr momenti 0.6096 MN·m): sayfa 403 verdi; yalnız arama özetinden bilinen birkaç girdi var, sonuçlar yok. DIN EN 13445-3/A2 (din.de) yalnız içindekiler sayfasını verdi.
- Eng-Tips / CR4 (403): eyer ve Blodgett tartışmaları, aranan örnekler okunamadı.
- Megyesy "Pressure Vessel Handbook", Moss "Pressure Vessel Design Manual", Bednar: yalnız ticari/ödünç (archive.org kayıtları ödünç); çalışılmış örnek sayıları ücretsiz erişimde yok. IAEME 2013'teki Megyesy kullanımı (K3-06) sonuç görüntüsü.
- Codeware: https://www.codeware.com/support/papers/zick.pdf Zick 1951/1971 nüshasını veriyor (sayısal çalışılmış örnek yok; bağlam notuyla aynı içerik, 298 008 bayt). Codeware'ın resmi örnek raporu bulunamadı; K3-03 Pressure Vessel Engineering'in COMPRESS çıktısıdır.
- Zick 1951 makalesi: ölçülen 30 000 galon propan tankı yalnız Şekil 1'de (düzenek); çalışılmış sayısal örnek yok (doğrulandı).
- Duan & Hu 2016 (SAGE), Khan 2010 (ScienceDirect), SAE 900892: özet/ücretli; sayı alınamadı. Tooth ve ark. (Strathclyde, strathprints005901): plastik çökme yükü çalışması (t=1.57 mm, σy=222.2 N/mm², çökme 23–56 kN düzeyi), Zick gerilmesi örneği değil; düz-metin okundu fakat ilgisi dolaylı, vaka yapılmadı.
- Blodgett "Design of Weldments" çözüm kitabı (slideshare 15868710): OCR metni bozuk (Signal Tower, 750-ton press vb. problemler var); sayılar güvenilir ayıklanamadı. Blodgett & Miller, "Welded Connections" (CRC 1999, Bölüm 22, http://freeit.free.fr/Structure%20Engineering%20HandBook/22.pdf): Tablo 22.3 ve Şekil 22.11 örneği görüntü; metinde yalnız yöntem var.
- NPTEL 103103027 (Modül 6, Ders 5): 2.5 m çap/60 m yükseklik etek+kabuk örneği (W≈602 kN) var ama basınç birimi çelişkili ("0.9 MN/mm²" vs "1.0 N/mm²"), etek/halka/ankraj sonuçları sayfalarda bölünmüş; vaka çıkarılmadı.
- STAAD Foundation (Bentley) rüzgâr yardım sayfaları: formül/girdi açıklaması var, sayısal çalışılmış örnek yok.
- AIJR/CEST-2018 (Yahya ve ark., DOI 10.21467/proceedings.4.33): küre başlı kapta 4 bacak, yerel K1…K8 katsayı tablosu (kaynakta eğrilerden okunmuş, K1=0.055, K2=0.02, K3=0.06 …) ve Q=30 028.1 N; denklemler OCR'da bozuk, sonuç "79" anlamsız; güven çok düşük, vaka yapılmadı.

## Yayıncı/kapsam özeti

| Konu | Vaka | Yayıncı/kaynak |
|---|---|---|
| Zick eyer (S1–S5/K) | K3-01, 02, 03 (tam); 04, 05, 06, 07 (kısmi) | PVE (PV Elite, COMPRESS), IJIRSET, IJRASET, IAEME, Kezar |
| Etek (A/Z, halka, ankraj) | K3-08, 09, 10, 11, 12 | CRC Press, PVE, IJERT, Kezar, IRJMETS |
| Bacak (axial/bükülme/kaynak/plaka) | K3-13, 14 | PVE e-tablo, IJERT |
| Taban plakası, ankraj çekme, beton | K3-15…18 (+13, 14) | AISC DG1 |
| Rüzgâr/deprem | K3-19 (ASCE rüzgâr), K3-03/09 (NBC 2005 deprem+rüzgâr), K3-10 (UBC deprem), K3-13 (NBC-95) | ASCE, PVE, IJERT |
| Çubuk burkulması KL/r | K3-20, 21, 13, 14 | AISC (Calcs.com), PVE, IJERT |
| Blodgett çizgi kaynak | K3-22 (+K3-13 alan yaklaşımı) | Union College / Shigley |

Boşluklar: (1) Megyesy/Moss çalışılmış sayısal örnek yok (ticari), (2) Blodgett kitabının kendi Sw örnekleri okunamadı, (3) deprem için ASCE 7 baskısı ile tam çalışılmış devrilme momenti + etek + ankraj zinciri yok (yalnız NBC/UBC), (4) K1′ (çekme/basma ayrımı) için tek doğrudan işaret COMPRESS S2'deki K1'=1 ve PV Elite'taki K1=0.1066/K1*=0.1923 çifti; Zick orijinal tablosuyla bire bir eşleme tamamlanmadı.
