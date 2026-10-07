# K1 — Kaynak avı: ASME VIII-1 yayınlanmış çözümlü örnekler

Tarih: 2026-10-07 · Politika: K6 (metin/tablo kopyalanmadı; yalnız atıf + sayılar + formülasyon notu).
Önceden kullanılanlar (yeniden sayılmadı): PVE-FT (Firetube, PV Elite 2017), PVE-S13 (APV 10.1.5),
PVE-FD (F&D Heads 2.02 tablosu), PVE-CMP (web sayfası: Hemi/SE/F&D/Flat karşılaştırması).

Güven: **yüksek** = sayıları birincil PDF'ten kendim okudum (ve çoğunu elle yeniden hesapladım);
**orta** = birincil okundu ama girdi çıkarımı/kaynak-içi tutarsızlık/zayıf yayıncı var (nedeni vakada yazılı).

## Özet

| Yayıncı | Doküman | Vaka |
|---|---|---|
| Codeware Inc. (COMPRESS) | 3 demo rapor (2004-A06 ve 2021 baskı) | K1-01 … K1-08 |
| Pressure Vessel Engineering Ltd. (PVEng) — 5 ayrı doküman, 4 ayrı yazılım | Four Heads (COMPRESS 2015), Generic Vessel 6847 (COMPRESS 2013), Propane/Butane Sphere 4225 (PVE sayfaları), PVE-3247 eğitim sayfaları, Sample 5 (APV), DesignCalcs Audit | K1-09 … K1-22 |
| ABCM — COBEM 2009 (Bassani, Amorim, Iturrioz) | Konferans bildirisi COB09-3091 | K1-23 |
| CheCalc (checalc.com) | Çevrimiçi rehber | K1-24 |
| IOP Conf. Ser. (Christ University, Niranjana vd.) | MSE 376 (2018) 012135 | K1-25 |

Toplam 25 vaka, 5 yayıncı. Bağımsızlık notu: Four Heads (K1-09…11), PVE-CMP ile **aynı kap**
(ID 47 in, 420 psi) — yeni olan yalnız silindir, F&D MAWP ve UG-34 düz kapak; SE/Hemi değerleri
V-10/V-13'te zaten kullanılmıştı.

---

# A. Codeware (COMPRESS demo raporları)

Kaynak dosyaları (hepsi Codeware'in kendi sitesinde, "prospects" demo raporu):
- **CW-1** `https://www.codeware.com/prospects/total-metalworks/COMPRESS-Report-Demo-Vessel.pdf` — COMPRESS 2023 Build 8310, ASME VIII-1 **2021 Ed.**, "Demo Vessel", sayfa "x/74".
- **CW-2** `https://www.codeware.com/prospects/bgr-tech/COMPRESS-PV-Report.pdf` — COMPRESS 2023 Build 8300, ASME VIII-1 **2004 Ed., A06 Add.**, rapor tarihi 30 May 2023, sayfa "x/182" (indirilen PDF 53 sayfa; sayfa numaraları raporun basılı alt bilgisinden).
- **CW-3** `https://www.codeware.com/prospects/progressive-recovery/Demo-Vessel-Report.pdf` — COMPRESS 2022 Build 8200, ASME VIII-1 **2021 Ed.**, 5 Ocak 2022, sayfa "x/56".

### K1-01 — Silindirik gövde + statik kafa — UG-27(c)(1)
Kaynak: Codeware, COMPRESS Demo Vessel raporu (CW-3), 2022 · URL: https://www.codeware.com/prospects/progressive-recovery/Demo-Vessel-Report.pdf · Sayfa: 18-19/56 (Cylinder #2) · Kod: VIII-1 2021 Ed. · Güven: yüksek
Girdiler: P=100 psi @ 250 °F; Ps (işletme statik kafa)=0.87 psi (Hs=24 in, SG=1); ID=24 in → R=12 in (iç); S=20 000 psi (hot) / 20 000 (70 °F); E=1.00; CA=0; t_nom=0.1875 in
Yayınlanmış sonuçlar: t_req=0.0608 in (hesapta P_etkin=100.87 psi); MAWP(hot)=308.73 psi; MAP(70 °F, Ps yok)=309.6 psi
Formülasyon notu: Statik kafa **P'ye eklenerek** kalınlığa girer (100+0.87), **MAWP'den çıkarılır** (SEt/(R+0.6t) − Ps). R iç yarıçap, korozyon 0. MAP (soğuk) formülde Ps düşülmez. Yeniden hesap: 0.06071 / 308.73 ✓.

### K1-02 — 2:1 elipsoidal bombe — UG-32(d)(1) (iç çap formu)
Kaynak: Codeware, COMPRESS Demo Vessel raporu (CW-1), 2023 · URL: https://www.codeware.com/prospects/total-metalworks/COMPRESS-Report-Demo-Vessel.pdf · Sayfa: 22-23/74 (Ellipsoidal Head #1) · Kod: VIII-1 2021 Ed. · Güven: yüksek
Girdiler: P=100 psi @ 650 °F; D=36 in (iç); S=18 800 psi (hot) / 20 000 (70 °F); E=1.00; CA=0; t_min(şekillendirme sonrası)=0.1007 in; Ps(işletme)=1.6 psi test için; bombe oranı D/2h=2
Yayınlanmış sonuçlar: t_req=0.0958 in; MAWP(hot)=105.12 psi; MAP(70 °F)=111.83 psi (statik kafa test durumu için ayrı, MAWP'ye karışmıyor: "−Ps=0")
Formülasyon notu: t=PD/(2SE−0.2P); P=2SEt/(D+0.2t) − Ps. D iç çap, korozyon sıfır (CA'lı vaka değil). Yeniden hesap: 0.09580 / 105.12 / 111.83 ✓. **Dikkat:** bu bombede 'governing' dış basınçtır (t_e=0.1007), t_req iç basınç içindir.

### K1-03 — 2:1 elipsoidal bombe, kalın cidar — UG-32(d)(1)
Kaynak: Codeware, COMPRESS PV Report (CW-2), 2023 · URL: https://www.codeware.com/prospects/bgr-tech/COMPRESS-PV-Report.pdf · Sayfa: 26-27/182 (Ellipsoidal Head #2) · Kod: VIII-1 2004 Ed., A06 Add. · Güven: yüksek
Girdiler: P=250 psi @ 600 °F; D=168 in (iç); S=19 400 psi (hot) / 20 000 (70 °F); E=1.00; CA=0; t_min=1.3 in; Ps(işletme)=0 hesapta
Yayınlanmış sonuçlar: t_req=1.0839 in; MAWP(hot)=299.77 psi; MAP(70 °F)=309.05 psi
Formülasyon notu: Aynı UG-32(d)(1) iç çap formu; 2004 baskısında da numara aynı (c)(1) değil (d)(1). t/D=0.0077, ince kabuk aralığı. Yeniden hesap: 1.08387 / 299.77 / 309.05 ✓.

### K1-04 — Silindir (düz yaka), kalın cidar — UG-27(c)(1)
Kaynak: Codeware, COMPRESS PV Report (CW-2), 2023 · URL: https://www.codeware.com/prospects/bgr-tech/COMPRESS-PV-Report.pdf · Sayfa: 29/182 ("Straight Flange on Ellipsoidal Head #2", silindir olarak hesaplanmış) · Kod: VIII-1 2004 Ed., A06 Add. · Güven: yüksek
Girdiler: P=250 psi @ 600 °F; ID=168 in → R=84 in (iç); S=19 400 psi; E=1.00; CA=0; t_nom=1.375 in; Ps(işletme)=0
Yayınlanmış sonuçlar: t_req=1.091 in; MAWP(hot)=314.47 psi; MAP(70 °F, S=20 000)=324.2 psi
Formülasyon notu: R iç, korozyon yok. t/R=0.0164 ve P<0.385SE → ince cidar formülü geçerli. Yeniden hesap: 1.0909 / 314.46 / 324.20 ✓.

### K1-05 — Kaynaklı düz kapak — UG-34(c)(2), Fig. UG-34 sketch (i)
Kaynak: Codeware, COMPRESS Demo Vessel (CW-3), 2022 · URL: https://www.codeware.com/prospects/progressive-recovery/Demo-Vessel-Report.pdf · Sayfa: 16-17/56 (Welded Cover #1) · Kod: VIII-1 2021 Ed. · Güven: yüksek
Girdiler: P=100 psi @ 250 °F; d=24 in (iç çap); S=20 000 psi; E=1.00; CA=0; t_nom=0.875 in; C=max(0.33·tr/ts, 0.2)=**0.2** (ts=0.1875 in gövde, tr=0.0602…0.0801 in); Fig. UW-13.2 (a); Ps=0 (MAWP formülünde)
Yayınlanmış sonuçlar: t_req=0.7589 in; MAWP=132.92 psi; (dış basınç 15 psi için t_e=0.3776 in, C=0.33 → MAEP=80.56 psi)
Formülasyon notu: t=d√(CP/SE); MAWP=(SE/C)(t/d)². C, 2021 baskısında **alt sınırı 0.2'ye kenetlenmiş** (0.33·tr/ts<0.2 olduğu için). Yeniden hesap: 0.75895 / 132.92 ✓. **Bu vaka bombe değil kapak olduğu için chamber MAWP'yi (132.92) belirliyor** — K1-06 testinin tabanı.

### K1-06 — UG-99(b) hidrostatik test + statik kafa (MAWP tabanı; kapak sınırlayıcı)
Kaynak: Codeware, COMPRESS Demo Vessel (CW-3), 2022 · URL: aynı (CW-3) · Sayfa: 13/56 · Kod: VIII-1 2021 Ed. · Güven: yüksek
Girdiler: Chamber MAWP=132.92 psi (K1-05 kapağı); LSR (Sa/S en düşük oran)=1; yatay test; Hs (test)=30.1875 in, SG=1; tüm bileşenlerde S oranı 1.0
Yayınlanmış sonuçlar: Gauge basıncı (üstte, 70 °F)=1.3×132.92×1=**172.8 psi**; yerel test basıncı (cylinder #2)=173.887 psi (statik kafa 1.09 psi)
Formülasyon notu: Taban **MAWP** (tasarım basıncı 100 değil). Gauge 'en üstte', yerel basınç = gauge + statik kafa. Yeniden hesap: 1.3×132.92=172.80 ✓; 172.80+1.09=173.89 ✓. V-07 düzeltmesinin ikinci bağımsız teyidi.

### K1-07 — UG-99(b) hidrostatik test + S oranı ≠ 1 (bileşen) ama LSR=1 (nozul sınırlıyor)
Kaynak: Codeware, COMPRESS Demo Vessel (CW-1), 2023 · URL: https://www.codeware.com/prospects/total-metalworks/COMPRESS-Report-Demo-Vessel.pdf · Sayfa: 17/74 · Kod: VIII-1 2021 Ed. · Güven: yüksek
Girdiler: Chamber MAWP=78.93 psi; gövde/bombe S_test/S_tasarım=20 000/18 800=1.0638; nozul #4 oranı=1.0 (en düşük); Hs(test)=1.595 psi
Yayınlanmış sonuçlar: Gauge=1.3×78.93×1=**102.61 psi**; yerel test basıncı (bombe/gövde)=104.205 psi
Formülasyon notu: UG-99(b) "lowest ratio" kuralı **tüm bileşenler üzerinden** minimumu alır: bombenin oranı 1.0638 olsa da nozul 1.0 olduğu için 1.0 kullanılmış. Yeniden hesap: 1.3×78.93=102.609 ✓. İyi bir sınama: suite oranı bileşen bazında değil sistem min'i olarak almalı.

### K1-08 — UG-99(b) hidrostatik test, MAWP başka bileşenden (zincir kontrolü)
Kaynak: Codeware, COMPRESS PV Report (CW-2), 2023 · URL: https://www.codeware.com/prospects/bgr-tech/COMPRESS-PV-Report.pdf · Sayfa: 17/182 · Kod: VIII-1 2004 Ed., A06 Add. · Güven: yüksek
Girdiler: Chamber MAWP=255.74 psi (sınırlayıcı: nozul); gövde S oranı 1.0309 (20 000/19 400); chamber LSR=1; yatay test; Hs(test)=207 in SG=1 (7.47 psi bombe #2)
Yayınlanmış sonuçlar: Gauge=1.3×255.74×1=**332.46 psi**; yerel test basıncı=339.93 psi (bombe #2/gövde), 343.504 psi (bombe #3, en alt)
Formülasyon notu: MAWP gövde/bombe MAWP'sinden (299.77/314.47) **küçük** (255.74) olduğu için test onu kullanıyor — yani "tasarım basıncının üstü ama bileşen MAWP'sinin altı" durumu. Yeniden hesap: 332.462 ✓.

---

# B. Pressure Vessel Engineering Ltd. (ek dokümanlar)

PVEng daha önce PVE-FT/S13/FD/CMP olarak kullanıldı; aşağıdaki dokümanlar **farklı kap ve farklı yazılım/sürüm**, yani yeni.

### K1-09 — Silindir — UG-27(c)(1) (R=23.5, ID=47 in)
Kaynak: Pressure Vessel Engineering Ltd., "Comparison of Four Head Types" (Four Heads, PVE-3101, COMPRESS), 24 Ağu 2016 · URL: https://www.pveng.com/wp-content/uploads/2016/08/Four_Heads_Compress_Calculation_Set.pdf · Sayfa: 5-6 (Cylinder) · Kod: VIII-1 2015 Ed. · Güven: yüksek
Girdiler: P=420 psi @ 100 °F; ID=47 in → R=23.5 in; S=20 000 psi; E=1.00; CA=0; t_nom=0.5 in; Ps(test)=1.7 psi (MAWP'den çıkarılan işletme statik kafa=0)
Yayınlanmış sonuçlar: t_req=0.4998 in; MAWP=420.17 psi; MAP=420.17 psi
Formülasyon notu: Standart iç yarıçap formu, korozyon 0. Aynı kap V-10/V-13 ile **aynı** (bağımsız değil); yalnız silindir yeni. Yeniden hesap: 0.49980 / 420.17 ✓.

### K1-10 — F&D (torisferik) bombe MAWP — App. 1-4(d), r/L=6.1 %
Kaynak: aynı (Four Heads), s. 9-10 (F&D Head) · Kod: VIII-1 2015 Ed. · Güven: yüksek
Girdiler: P=420 psi @ 100 °F; D=47 in (iç); crown **L=48 in**; knuckle **r=2.9273 in** (r/L=0.0610); S=20 000; E=1.00; CA=0; t_min=0.8901 in; Lsf=1.5
Yayınlanmış sonuçlar: M=1.7623; t_req=0.8901 in; MAWP=MAP=420.01 psi
Formülasyon notu: M=¼[3+√(L/r)]; t=PLM/(2SE−0.2P); P=2SEt/(LM+0.2t). L=48 = dış çap (ID 47 + 2×0.5) — V-14'ün "L=Do" bulgusuyla uyumlu. r>0.06L olduğu için UG-32(e) asgarisi sağlanıyor. t_min 0.8901'in **tam** bu P için seçilmiş bir "boyutlandırma geri çıkarımı" olduğu görülüyor (MAWP≈420.01). Yeniden hesap: M=1.76234, t=0.89009, P=420.005 ✓.

### K1-11 — Kaynaklı düz kapak — UG-34(c)(2), Fig. UG-34 sketch (f)/(b-2)
Kaynak: aynı (Four Heads), s. 11-12 (Welded Flat Head) · Kod: VIII-1 2015 Ed. · Güven: yüksek
Girdiler: P=420 psi @ 100 °F; d=47 in; S=20 000; E=1.00; CA=0; t_nom=3.912 in; C=0.33·tr/ts=0.33×0.4998/0.5=**0.3299**; iç/dış köşe kaynağı bacağı 0.5/0.5 in; kapak çukuru (inset) 0.5 in
Yayınlanmış sonuçlar: t_req=3.912 in; MAWP=MAP=420 psi
Formülasyon notu: t=d√(CP/SE), MAWP=(SE/C)(t/d)²; C burada gövde incelik oranından (0.33 tr/ts) çıkıyor ve **0.2'ye kenetleme yok** (2015 baskısında sketch (f) için bu form). Yeniden hesap: 3.91200 / 420.00 ✓. V-17/UG-34(c)(3) ile ilgili: bu vaka Z faktörü gerektirmiyor.

### K1-12 — Küre segmenti (UG-27(d)/UG-32(f)) + yükseklik başına statik kafa (üst kep)
Kaynak: Pressure Vessel Engineering Ltd., "Propane/Butane Sphere", PVEcalc-4225-0-1 Rev 0, 6 Ağu 2010 · URL: https://www.pveng.com/wp-content/uploads/2016/06/PVEcalcs-4225-Rev-0.pdf · Sayfa: 4 (Top Cap), 3 (malzeme/test) · Kod: VIII-1 2007 Ed., Add. 2009 · Güven: yüksek
Girdiler: Pt (tepe)=157 psig; sg=0.58; Di=720 in; **L = Di/2 + CA = 360.03 in**; CA=0.03 in; S=21 400 psi (SA-299, 150 °F); E=1.00; t_nom (şekillendirme sonrası)=1.48 in; segment altındaki yükseklik h=7.867 in (0°–12°); P(segment dibi)=Pt+0.4331·sg·h/12 = 157.165 psi
Yayınlanmış sonuçlar: t_req(CA dahil)=1.353 in; P_max=172.2 psi
Formülasyon notu: t=PL/(2SE−0.2P)+CA, P_max=2SE(t−CA)/(L+0.2(t−CA)); **L korozyonlu iç yarıçap** (R+CA, V-16 ile uyumlu); statik kafa **segmentin altındaki** sıvı yüksekliğinden (0.4331·sg·h/12, h inç). Yeniden hesap: 1.3530 / 172.24 (yayın 172.2) ✓.

### K1-13 — Küre segmenti, ekvator plakası (statik kafa en büyük)
Kaynak: aynı (PVE 4225), s. 8 (Zone Z4) · Kod: VIII-1 2007 Ed., Add. 2009 · Güven: yüksek
Girdiler: Aynı Pt, sg, Di, CA, S, E; t_nom=1.46 in; segment 87°–132°; h=600.887 in; P(dip)=157+0.4331×0.58×600.887/12=169.578 psi
Yayınlanmış sonuçlar: t_req=1.458 in; P_max=169.9 psi (t=1.46 ≥ 1.458 → Acceptable)
Formülasyon notu: Statik kafa tepe basıncından +12.6 psi; segment kalınlıkları (1.37–1.48) bu yüzden basamaklı. Yeniden hesap: 1.4576 / 169.86 ✓. Aynı doküman Z1 (P=158.517; t_req 1.364; P_max 159.2) ve Z2 (P=160.998; 1.385; 162.7) için de veriyor.

### K1-14 — UG-99(b) hidrostatik: MAWP=tasarım, S oranı 1, yuvarlama yukarı
Kaynak: aynı (PVE 4225), s. 3 (Material Properties) · Kod: VIII-1 2007 Ed., Add. 2009 · Güven: yüksek
Girdiler: P (tepe, nameplate)=157 psig; MR (min Sa/S)=1.000 (malzemelerin hepsi 1.0: 21 400/21 400…); gauge tepede ölçülür
Yayınlanmış sonuçlar: Test=P×1.3×MR=204.1 → yayınlanan **205 psig** ("rounded up", tam sayıya yukarı)
Formülasyon notu: Taban nameplate MAWP=157 psig (kapak başlığında MAWP: 157 psi); formül P×1.3×MR. Yukarı yuvarlama bir **kural değil, yazılım seçimi** — karşılaştırmada ±1 psi tolerans gerektirir.

### K1-15 — 2:1 elipsoidal bombe MAWP — App. 1-4(c), dış çap formu, E=0.85
Kaynak: Pressure Vessel Engineering Ltd., "Generic Vessel" PVE-6847 (COMPRESS 2013 Build 7320), 18 Haz 2013 · URL: https://www.pveng.com/wp-content/uploads/2016/06/PVEclc-6847-0.1_Generic_Vessel.pdf · Sayfa: 11-12/54 (Ellipsoidal Head, Top) · Kod: VIII-1 2010 Ed., A11 Add. · Güven: yüksek
Girdiler: P=200 psi @ 250 °F; **Do=36 in (dış)**; K=1; S=21 400 psi (SA-414 G); E=0.85; CA=0; t_min=0.2813 in; Ps=0.32 psi (işletme); P_etkin (kalınlık için)=200.32 psi
Yayınlanmış sonuçlar: t_req=0.1963 in; MAWP=288 psi (Ps çıkarılmış)
Formülasyon notu: t=PDoK/(2SE+2P(K−0.1)); MAWP=2SEt/(KDo−2t(K−0.1))−Ps. V-04/V-05 ile aynı dış-çap alternatifi; bu kez **bağımsız bir COMPRESS çıktısı**. Suite UG-32(d) iç-çap formunu kullandığından yine FORMÜLASYON_FARKI beklenir (~%0.4-0.9). Yeniden hesap: 0.19628 / 288.00 ✓.

### K1-16 — Silindir, E=0.70 + statik kafa — App. 1-1(a)(1) (dış yarıçap)
Kaynak: aynı (PVE-6847), s. 15-16/54 (Shell) · Kod: VIII-1 2010 Ed., A11 Add. · Güven: yüksek
Girdiler: P=200 psi @ 250 °F; Ps=3.86 psi (Hs=106.86 in, SG=1) → P_etkin=203.86; **Ro=18 in (OD 36)**; S=21 400; E=0.70 (RT yok); CA=0; t_nom=0.375 in
Yayınlanmış sonuçlar: t_req=0.2437 in; MAWP=310.85 psi (−Ps dahil)
Formülasyon notu: t=PRo/(SE+0.4P); MAWP=SEt/(Ro−0.4t)−Ps (dış yarıçap formu, V-06 ile aynı FORMÜLASYON_FARKI sınıfı: suite UG-27(c)(1) iç-yarıçap formunu kullanırsa küçük fark beklenir). E=0.70 (V-02/03'te E=0.85 idi) → düşük-E vakası. Yeniden hesap: 0.24363 (yayın 0.2437) / 310.85 ✓.

### K1-17 — UG-99(b) hidrostatik + MAWP=200 (nozul sınırı) + yerel statik kafa
Kaynak: aynı (PVE-6847), s. 10/54 (Hydrostatic Test) · Kod: VIII-1 2010 Ed., A11 Add. · Güven: yüksek
Girdiler: Chamber MAWP=200 psi (sınırlayıcı nozul; bombe/gövde MAWP 284-318 psi); LSR=1; yatay test; Hs≈35.9 in
Yayınlanmış sonuçlar: Gauge=**260 psi**; yerel test basıncı: bombe 261.299, gövde 261.295, NPS 6" nozul 261.417 (statik kafa 1.30…1.42 psi)
Formülasyon notu: 1.3×200=260 ✓. K1-08 ile aynı yapı (nozul sınırlıyor). Test gerilmesi sınırı: 90 % akma.

### K1-18 — Silindir, iç korozyonlu, farklı E'ler — UG-27(c)(1,2)
Kaynak: Pressure Vessel Engineering Ltd., "Sample Vessel Calculations" PVE-3247 Rev 0 ("ASME9_FEA_Report"), 17 Şub 2009, B. Vanderloo · URL: https://www.fabricadoprojeto.com.br/wp-content/uploads/2014/02/ASME9_FEA_Report.pdf (PVEng eğitim sayfaları; barındıran site Brezilyalı fabricadoprojeto.com.br) · Sayfa: 2/8 · Kod: baskı belirtilmemiş ("educational") · Güven: orta (barındıran site resmi PVEng değil; baskı yok)
Girdiler: P=201.4 psi; Do=18 in; t_nom=0.250 in; **CA=0.010 in**; S=20 000 psi; **E_boyuna-kaynak=0.70**, **E_çevresel-kaynak=0.85**; nt=t−CA=0.240 in → **Ri=Do/2−nt=8.760 in**
Yayınlanmış sonuçlar: ta=0.127 in (çevresel gerilme); tb=0.052 in (boyuna); T_req=max(ta,tb)+CA=0.137 in; P_max=377.4 psi (çevresel taraf 377, boyuna taraf 942)
Formülasyon notu: **Korozyon, iç yarıçapı BÜYÜTÜYOR** (Ri = Do/2 − (t−CA), yani R_yeni+CA) — V-16'nın yönünü bağımsız doğrular. ta=PRi/(S·El−0.6P), tb=PRi/(2·S·Ec+0.4P). Korozyon P_max'ta kalınlıktan düşülüyor (nt=t−CA), T_req'e ise eklenmiyor da hesap içinde zaten Ri'ye yansımış; T_req=max(ta,tb)+CA. Yeniden hesap: 0.12712 / 0.05177 / 377.36 / 941.8 ✓.

### K1-19 — 2:1 elipsoidal bombe, CA'lı iç-çap formu — App. 1-4(c), UG-37(a)(1)
Kaynak: aynı (PVE-3247), s. 3/8 · Güven: **orta** (kaynak içi tutarsızlık, aşağıda)
Girdiler: P=201.4 psi; Do=18 in; t_nom (şekillendirme sonrası)=0.188 in; CA=0.010 in; S=20 000; E=0.85; nt=tf−CA=0.178 in; **D=Do−2·nt=17.645 in**; K=1
Yayınlanmış sonuçlar: T_req=0.115 in (+CA dahil); P_max=341.3 psi
Formülasyon notu: Sayfa dış ölçüyle başlayıp **korozyonlu iç çapa** çevirip iç-çap formunu (t=PD/(2SE−0.2P)+CA) uyguluyor: yani suite'in UG-32(d) yoluna doğrudan benzer. **Tutarsızlık:** yayınlanan P_max=341.3, kendi girdileriyle 342.3 psi çıkıyor (−%0.3); T_req yeniden hesap 0.11464 ✓. P_max için ±%0.3 tolerans veya hiç kullanma.

### K1-20 — F&D (torisferik) bombe — App. 1-4(a)/(d), CA'lı
Kaynak: aynı (PVE-3247), s. 4/8 · Güven: orta (baskı yok; barındıran site)
Girdiler: P=201.4 psi; Do=18 in; **crown L=18 in** (=Do); **knuckle IKR=1.08 in** (=0.06 L); t_f=0.218 in; CA=0.010 in; S=20 000; E=0.85; nt=0.208 in
Yayınlanmış sonuçlar: M=1.771; T_req=0.199 in (CA dahil); P_max=221.6 psi
Formülasyon notu: M=¼(3+√(L/r)); t=PLM/(2SE−0.2P)+CA; P_max=2SEnt/(LM+0.2nt). **Crown yarıçapı L=18 = dış çap Do** (V-14/UG-32(e) ile uyumlu) ve CA, yarıçaplara uygulanmamış (L=Do sabit). Yeniden hesap: M=1.77062, T_req=0.19901, P_max=221.60 ✓.

### K1-21 — Paslanmaz silindir E=0.70 + UG-99(b) MR kısıtı — UG-27(c)(1,2)
Kaynak: Pressure Vessel Engineering Ltd., "Sample 5 — Vessel with Large Opening", PVE-Sample 5, 20 Kas 2008 · URL: https://www.pveng.com/wp-content/uploads/2016/06/Sample5_Spreadsheet.pdf · Sayfa: 3-5/25 · Kod: VIII-1 2007 Ed. · Güven: yüksek
Girdiler: P_etkin=200.95 psi (200 + statik 0.95: 0.4331×2.2 ft); Do=12.75 in; t_nom=0.188 in; CA=0; undertolerance=0; **Ri=6.187 in**; S=18 600 psi (SA-240 304, 350 °F); El=0.70; Ec=0.70; UG-16(b) min=0.063 in
Yayınlanmış sonuçlar: ta=0.096 in; tb=0.048 in; tmin=max(ta,tb,0.063)=0.096 in. Test: P×1.3×MR=200×1.3×1=**260 psig** (MR=1.000; malzeme oranları 1.075 / 1.149 ama cıvata SA-193 B7 oranı 1.000 → min)
Formülasyon notu: Yalnız 3 hane yayınlanmış (0.096 / 0.048) — yeniden hesap 0.09638 / 0.04760 ✓. Test taban P=200 (nameplate MAWP). **MR=1.000** oranı cıvatadan geliyor; yani "lowest ratio" kuralı sistemde cıvata dahil min alıyor (K1-07 ile aynı mantık).

### K1-22 — Boru-tabanlı silindir + 2:1 elipsoidal, 12.5 % boru eksik-tolerans + UG-99(b) (tasarım basıncı tabanı)
Kaynak: Pressure Vessel Engineering Ltd., "Design Calcs Sample" (DesignCalcs 2012.4, Computer Engineering Inc.), 21 Mar 2012 · URL: https://www.pveng.com/wp-content/uploads/2016/06/DesignCalcsAuditSample.pdf · Sayfa: 1/21 (Shell), 2/21 (Head), 21/21 (hidro) · Kod: VIII-1 2007 Ed., 2008 Add. · Güven: orta (boru + 12½ % toleransı karıştırıyor; karşılaştırma için dönüştürme gerekir)
Girdiler: P=200 psi + statik 0.50 → P_etkin=200.50; 12 in STD boru Do=12.75 in, t_nom=0.375 in; S=17 100 psi (SA-106 B); E_boyuna-kaynak=0.85, E_çevresel=0.70; CA=0; elipsoidal bombe Do=12.75 in, K=1, E=0.85, t_min(şek. sonrası)=0.3281 in
Yayınlanmış sonuçlar: UG-27(c)(2) t=0.0501 in; App. 1-1(a)(1) t=0.0875 in; bombe App. 1-4(c) t=0.0869 in (her biri ayrıca **+0.0469 in = %12.5 boru eksik-toleransı** eklenerek min 0.1094 / 0.1344 / 0.1338 in); UG-99(b): 1.3×17 100/17 100×200.00=**260.00 psi**
Formülasyon notu: **Test tabanı burada MAWP değil TASARIM basıncı (200)**: DesignCalcs "MAWP hesaplanmadıysa tasarım basıncı" endnote'unu kullanıyor — suite'in V-07 öncesi davranışıyla aynı (ve MAWP ≥ P olduğunda emniyetsiz). Yani **iki yayınlanmış yazılım iki farklı taban kullanıyor**; suite MAWP hesapladığı için K1-06/08/17 örnekleriyle (MAWP tabanı) sınanmalı. Yeniden hesap: 0.05008 / 0.08744 / 0.08686 ✓.

---

# C. ABCM — COBEM 2009 (üniversite/konferans)

### K1-23 — Silindir + elipsoidal bombe MAWP, SI, eski 1.5× hidro katsayısı
Kaynak: P. V. Bassani, H. J. Amorim, I. Iturrioz, "Pressure Vessel Failure Analysis", Proc. COBEM 2009 (20th Int. Congress of Mechanical Engineering, Gramado RS), paper COB09-3091 · URL: https://www.abcm.org.br/anais/cobem/2009/pdf/COB09-3091.pdf · Sayfa: Bölüm 2, 3.2, 3.3, 4.1 (~s. 1-6) · Kod: ASME VIII-1 (baskı belirtilmemiş; "2004'e kadar 1.5×" ifadesi var) · Güven: orta (E ve D bildiride yazılı değil, sonuçlardan çıkarıldı)
Girdiler: Ri=220 mm; t_nom=3 mm (UT 2.9-3.1); S=108 MPa (SA-414 C, STS/3.5); E=**1.0 (çıkarım)**; elipsoidal bombe D=**440 mm (çıkarım)**, K=1 (2:1); MAWP etiket=1.27 MPa; CA belirtilmemiş (0 varsayıldı)
Yayınlanmış sonuçlar: MAWP_silindir=1.46 MPa; MAWP_bombe=1.47 MPa (silindir sınırlayıcı); etiket MAWP 1.27 MPa için hidro=**1.91 MPa (=1.5×1.27)**
Formülasyon notu: P=SEt/(Ri+0.6t); P=2SEt/(KD+0.2t), K=(1/6)[2+(D/2h)²]. Yeniden hesap (E=1, D=440): 1.4608 / 1.4707 / 1.905 ✓ — yani çıkarımlarım sonuçları tam üretiyor. **Hidro katsayısı 1.5 (2004 öncesi baskı mantığı)** → güncel UG-99(b) 1.3 ile **kullanma**; yalnız silindir/bombe MAWP'si için uygun. Birimler SI → birim dönüşümü hatasızlığını da sınar.

---

# D. Zayıf yayıncılar (düşük ağırlık, yine de listelendi)

### K1-24 — Silindir, 2:1 bombe kalınlık/MAWP, UG-99 oran hesabı (özet örnekler)
Kaynak: CheCalc (checalc.com), "ASME BPVC VIII-1 vessel guide" (çevrimiçi rehber, güncelleme 13 May 2026; yazar/baskı belirtilmemiş) · URL: https://checalc.com/vessel_guide.html · Sayfa: n/a (web) · Kod: baskı belirtilmemiş · Güven: **orta-düşük** (hesap makinesi sitesi; doğrulanmış yazılım çıktısı değil — ama dört sayıyı elle yeniden hesapladım ve tutuyor)
Girdiler/sonuçlar:
- Ö1 silindir: P=250 psig; R=36 in (iç); S=20 000 psi; E=1.0; CA=0.125 in → t=0.453 in; toplam 0.578 in; seçilen 0.625 in. Yeniden: 0.45340 ✓
- Ö1b 2:1 elipsoidal: P=250 psig; D=72 in (iç); S=20 000; E=1.0; CA=0.125 → t=0.450 in (yayın; yeniden hesap 0.4506 → 0.451, yayın kesmiş); toplam 0.575 in
- Ö2 elipsoidal MAWP: t_nom=0.625 in; CA=0.125; D=72 in; S=20 000; E=0.85 → t_corr=0.50 in; MAWP=235.8 psig. Yeniden: 235.78 ✓
- Ö3 hidro: MAWP=235.8 psig; Sa=20 000 / S_hot=17 500 → oran 1.143 → test=**350.5 psig**. Yeniden: 1.3×235.8×1.1429=350.3 (yayın 350.5: yuvarlama farkı ~%0.06)
Formülasyon notu: **CA'lı kalınlıkta R ham iç yarıçap alınmış; korozyonlu iç ölçü (R+CA) KULLANILMAMIŞ** (0.453 = P·36/(SE−0.6P); korozyonlu R=36.125 ile 0.4547 olurdu). Bu, V-16'nın tersi yöndeki bir kaynak — **suite'in R+C kuralının doğruluğunu sınamak için kullanma**, yalnız E/oran/hidro aritmetiği için. Güven yüksek DEĞİL: kaynak hesap kuralını yanlış uygulamış olabilir.

### K1-25 — Silindir + 2:1 elipsoidal bombe, SI, E=1, CA=1.5 mm
Kaynak: S. J. Niranjana, S. V. Patel, A. K. Dubey (Christ University, Bengaluru), "Design and Analysis of Vertical Pressure Vessel using ASME Code and FEA Technique", IOP Conf. Ser.: Mater. Sci. Eng. 376 (2018) 012135, açık erişim (CC BY 3.0) · URL: https://iopscience.iop.org/article/10.1088/1757-899X/376/1/012135 · Sayfa: 2-4 · Kod: baskı belirtilmemiş (özet "Div. 2" diyor, gövde formülleri Div. 1 UG-27) · Güven: **orta-düşük** (S=138 MPa 250 °C'de SA-516-70 için şüpheli; baş formülü yazım hatalı)
Girdiler: P=3.6 MPa @ 250 °C; Di=1300 mm (R=650 mm); S=138 MPa; E=1.0; CA=1.5 mm; 2:1 bombe, t_nom=20 mm
Yayınlanmış sonuçlar: gövde ts=17.226 mm (+C=18.72 mm); bombe 17.00 mm (+1.5=18.5 mm); MAWP gövde 3.61 MPa, bombe 3.605 MPa (Do=1332 mm, t=17.22/17.0 mm)
Formülasyon notu: Gövde t=PR/(SE−0.6P) iç yarıçap, CA sona **eklenmiş** (R korozyonsuz). MAWP'de t=hesaplanmış (CA'sız) değerler kullanılmış → "t_req tersi" doğrulaması. Yeniden hesap: 17.226 ✓; bombe 17.00 ✓. Metinde bombe formülü "UG-27(c)(3)" diye anılıyor (yanlış atıf; UG-32(d)). Düşük güvenle yalnız aritmetik teyit.

---

# Erişilemedi / kullanılamadı (uydurma sayı YOK)

| Kaynak | Durum |
|---|---|
| ASME PTB-4 (VIII-1 örnek problem kılavuzu, 2013/2021) | Ücretli. Yalnız içindekiler (PTB-4-2021 TOC) görüldü; sayı yok. |
| Megyesy, *Pressure Vessel Handbook* | Basılı kitap; çevrimiçi sayısal örnek bulunamadı. |
| Moss, *Pressure Vessel Design Manual* | Basılı kitap; çevrimiçi örnek bulunamadı. |
| Hexagon (PV Elite/CodeCalc) yardım "Example Shell Analysis" (docs.hexagonppm.com …/CodeCalc-Help/25/303400, 303883, 336981; PV-Elite-Quick-Start/25/448047) | Arama sonucunda göründü; getirme sırasında 404. Sayı okunamadı. |
| textoscientificos.com/biodisel/archivos/36-1002-EQ-MC-003.pdf, 38-1002-EQ-MC-006.pdf (COMPRESS çıktıları) | URL artık 404/HTML; okunamadı. |
| LBL NEXT (www-eng.lbl.gov/~shuman/NEXT/… torisferik baş hesapları) | Hepsi 404. |
| Fermilab indico (Pressure_vessel_design_optimization.pdf; StressAnalysis_v1.4.pdf) | 403 / erişim engelli. |
| Scribd belgeleri ("Shell", "Calc Diesel Fuel Rev", "Compress Calculation", "Sample4-Spreadsheet/APV", "Sample5-APV") | Giriş duvarı; içerik alınamadı. (Sample5-APV'nin PVEng orijinali ayrıca alındı: K1-21 Sample 5 Spreadsheet.) |
| Eng-Tips, CR4, industrialmonitordirect.com bilgi tabanı (UG-34 örnekleri) | 403; ayrıca forum/ikincil içerik. |
| arXiv 2511.09689 (SpinQuest He-4 soğutucu, UG-27 MAWP tabloları) | Okundu ama tablo sütunları metin çıkarımında bozuk ve ana örnek (R=1.87 in, t=0.013 in, S=12.0 ksi → 97.7 psia) **yeniden hesapla tutmuyor (≈83 psia)**; kullanılmadı. |
| UIS (Santander) 2020 tez, COMPRESS karşılaştırma tabloları | Okundu; kritik girdiler (çap, S, E) çıkarılabilir değil; kullanılmadı. |
| amarineblog.com API 510 Soru-Cevap (UG-27/32/99/100) | Okundu; bazı cevaplar yeniden hesapla tutmuyor (örn. t=0.353 in, Ri=12 in, E=0.85, S=13 800 → ≈339.1, yayın 338.46); metin soru-cevap, yazılı kod baskısı yok; kullanılmadı. |
| uomus.edu.iq ders notu (Ex. 13.1) | Sinnott/BS tarzı formüller, ASME değil; kullanılmadı. |
| cis-inspector.com hesaplayıcıları | Etkileşimli, sabit yayınlanmış sayı yok (önceden de elenmişti). |
| ASME PVP 2017 "Ellipsoidal Head Rules: Div.1 vs Div.2" | Ücretli. |

## Kapsam boşlukları (açıkça)

- **UG-100 pnömatik (1.1×)**: bu turda **yeni** yayınlanmış sayısal pnömatik vaka bulunamadı (yalnız V-07'deki PVE-FT 240.68 psig var). Codeware ve PVEng raporlarında pnömatik test hesabı yok. İkinci kaynak hâlâ eksik.
- **UG-32(f) yarım küre** (bağımsız): yalnız K1-12/13 (küre segmenti, PVEng); standart yarım küre bombe için PVE-CMP (V-10) dışında yeni kaynak yok. K1-12/13 aynı denklemi kullandığı için pratikte örtüşür (R+CA, E=1).
- **UG-34(c)(3) Z-faktörlü** ve **kalın cidar (t>R/2)** için hâlâ kaynak yok (önceki listeyle aynı).

## Yöntem notu

Tüm "yüksek" vakalarda yayınlanmış sonuçları kendi girdileriyle elle yeniden hesapladım (yukarıda ✓ işaretli). Yeniden hesabın yayınla tutmadığı yerler vakada açıkça yazılı (K1-19 P_max; K1-24 hidro yuvarlama). Hiçbir kaynaktan metin/tablo kopyalanmadı; yalnız atıf, girdi/sonuç sayıları ve kısa formülasyon notları.
