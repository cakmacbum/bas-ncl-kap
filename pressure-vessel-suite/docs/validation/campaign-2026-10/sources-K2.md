# Kaynak avı K2 — nozul takviyesi, UG-45, Appendix 2 flanş, koni, dış basınç

Tarih: 2026-10-07 · Kapsam: ASME VIII Div.1 · K6 telif kuralı uygulandı (metin/tablo/grafik kopyası yok; yalnız atıf + girdi sayıları + yayınlanmış sonuç sayıları).

## Özet

- 21 vaka (K2-01 … K2-21), 3 yayıncı: **Pressure Vessel Engineering Ltd. (PVE)**, **Paget Equipment Co.**, **IJERT (Vyas–Tayade–Kumbhani, VJTI)**. Dördüncü olarak PVE'nin yayımladığı üçüncü taraf yazılım çıktıları ayrı satırda belirtildi (PV Elite, Advanced Pressure Vessel, PVE Excel tabloları).
- Kapsam: nozul takviyesi (pedsiz/pedli; gövde, koni, 2:1 bombe, torisferik) · UG-45 · App. 2 flanş (gevşek + integral) · koni 1-4(e) · UG-28/UG-33 dış basınç (A ve B kaynağın kullandığı değerler).
- **Doldurulamayan kalemler (dürüst boşluk):** App. 1-5 koni-silindir bağlantısı takviyesi (internal) ve App. 1-8 (dış basınç) için sayısal çıktısı yayınlanmış vaka **bulunamadı**; UG-32(g) iç-çap formu doğrudan yayınlanmış vaka yok (kaynaklar 1-4(e) dış-çap formunu kullanıyor, bkz. K2-05/K2-15). K2-18 yalnız bilgi amaçlı (Bednar, 1-5 değil).
- Okuma yöntemi: PVE/Paget PDF'leri indirilip `pdftotext -layout` ile okundu (satır satır doğrulandı). Sayfa numarası = PDF'in kendi "Page N of M" etiketi. APV (Advanced Pressure Vessel) çıktılarında etiket sayfa **sonundadır**, PVE Excel/PV Elite çıktılarında **başındadır**; bu nedenle aşağıdaki numaralar ilgili bloğu içeren sayfadır.
- Kısaltmalar: PVE-S5 = Sample 5 "Vessel with Large Opening" (2008); PVE-EP = External Pressure Calculations (2010/2011); PVE-S3 = Sample 3 horizontal retention tank (2008); PVE-S13 = Sample 13 tower (2009; önceki turda V-02…V-06'da kullanıldı, burada **yeni** bölümleri: koni + pedli nozul); PVE-HX = Heat Exchanger Sample (2012); PVE-FT = Firetube (2017; önceki turda V-15'te nozul için kullanıldı, burada **yeni** bölümleri: dış basınç + flanş).
- Birim notu: inç/psi/lb orijinal; dönüşüm 1 in = 25,4 mm, 1 psi = 0,006894757 MPa.

---

### K2-01 — Pedsiz nozul, KONİ gövde üzerinde, küçük nozul — UG-37/UG-40 (A, A1, A2, A41), UG-45

Kaynak: Pressure Vessel Engineering Ltd., *PVE Sample 5 — Vessel with Large Opening, Pressure Vessel Calculations* (PVE Excel hesap tabloları, "Nozzle Reinforcement ver 3.90"), 20-Kas-2008 · https://www.pveng.com/wp-content/uploads/2016/06/Sample5_Spreadsheet.pdf · Sayfa: 7 (koni), 11 (Nozul A) · Kod: ASME VIII-1 (baskı PDF'te belirtilmemiş; 2007 dönemi tabloları — baskı yılı doğrulanmadı) · Güven: yüksek
Girdiler: konik gövde SA-240 304, S = 18600 psi, E(boyuna kaynak) = 0,70, t = 0,188 in, CA = 0, ODL = 12,750 in, ODS = 8,030 in, L = 5,000 in, α = 25,3° (0,441 rad); nozul ekseni küçük uçtan 2,5 in → yerel OD = 10,39 in; P = 200,953 psi (201,0); nozul SA-312 TP304 boru, Sn = 18600 psi, OD = 2,375 in, kullanılan açıklık d = 2,333 in (hillside girişi), Nt = 0,154 in, eksik tolerans %12,5 (UT = 0,019), dış çıkıntı L = 3,000 in, içe çıkıntı yok, ped yok, Leg41 = 0,188 in, E1 = 1, F = 1, fr1 = fr2 = 1,000
Yayınlanmış sonuçlar: tr (koni, yerel OD) = 0,088 in (tln); koni büyük uç treq = 0,108 in; Rn = 1,053 in; trn = 0,011 in; **A = 0,206 in²**; **A1 = 0,233 in²**; **A2 = 0,110 in²**; A3 = 0; **A41 = 0,035 in²**; toplam mevcut = 0,378 in² (fazla +0,173); UG-45: UG45a = 0,011, UG45b = 0,088 → **UG45 = 0,088 in** ≤ Nact = 0,135 in (Tstd = 0,154); App. 1-7 gerekmiyor. Koni Pmax = 351,0 psi.
Formülasyon notu: Kaynak A1'de max(d, 2(t+tn)) kullanıyor; A2 = min(5·(tn−trn)·fr2·t ; 5·(tn−trn)·fr2·tn) — yani min(5t, 5tn) biçimi (yanlışlıkla 2,5tn+te ile karıştırma). Koni üzerinde tr, koni formülü (App. 1-4(e), yerel OD ile) sonucundan geliyor ve E=0,70 kullanılmış; suite'in koni-üstü nozul tr'si bu şekilde türetilmiyorsa tr'yi girdi olarak verip yalnız alan dengesi sınanmalı. Eğik/hillside açıklık için F ve düzlem geometrisi kapsam dışı (suite yalnız radyal).

### K2-02 — Pedsiz nozul, SİLİNDİR gövde, ferrule — UG-37/UG-40, UG-45

Kaynak: PVE, *PVE Sample 5* (aynı belge) · URL yukarıdaki · Sayfa: 13 (Nozul B) · Kod: bkz. K2-01 · Güven: yüksek
Girdiler: gövde SA-240 304, Sv = 18600 psi, Ds (iç çap) = 12,37 in, Vt = 0,188 in; tr (gövde) = 0,067 in; nozul SA-479 304, Sn = 18600 psi, Do = 2,192 in, Nt = 0,161 in (UT = 0), d = Do − 2tn = 1,870 in, Rn = 0,935 in, dış çıkıntı L = 1,500 in, Leg41 = 0,188 in, P = 200,95 psi, E1 = 1, F = 1, fr1 = fr2 = 1,000, ped yok
Yayınlanmış sonuçlar: trn = 0,010 in; **A = 0,126 in²**; **A1 = 0,226 in²**; **A2 = 0,121 in²**; A41 = 0,035 in²; toplam mevcut = 0,383 in² (fazla +0,257); **UG45 = 0,067 in** ≤ Nact = 0,161 in (Tstd = 0,145); App. 1-7 gerekmiyor.
Formülasyon notu: Nozul B'de "Ds" hücresi 200,95 olarak basılmış (etiket kayması, PDF metin katmanı) — girdi olarak 12,37 in iç çap (Nozul A/C ile aynı gövde) alındı; tr = P·R/(S·E − 0,6P) ile 0,0672 geri doğrulandı. Hesap tr'si E = 1 ile.

### K2-03 — Büyük açıklıklı nozul, sınır yarıçaplı (dLr) — UG-37, App. 1-7 sınırında

Kaynak: PVE, *PVE Sample 5* · Sayfa: 14 (Nozul C) · Güven: orta (A1'in limit-yarıçap girdisi PDF'te açık değil)
Girdiler: gövde aynı (Ds = 12,37 in, Vt = 0,188, tr = 0,067 in); nozul Do = 10,750 in, Nt = 0,365 in (UT %12,5 → Rn = 5,056 in), d = 10,020 in, dış çıkıntı L = 4,000 in, Leg41 = 0,250 in, P = 200,95 psi, fr = 1,000
Yayınlanmış sonuçlar: trn = 0,055 in; **A = 0,674 in²**; **A1 = 0,605 in²** (formül (2·dLr − d)·(E1t − F·tr) biçimli, yani sınır yarıçaplı); **A2 = 0,291 in²**; A41 = 0,063 in²; toplam = 0,959 in² (fazla +0,285); UG45a = 0,055, UG45 = 0,067 in ≤ Nact = 0,319 in.
Formülasyon notu: Açıklık gövde çapının ~%81'i; PVE bu nozulda App. 1-7 kontrolünü ayrıca (sayfa 15) yapıyor. Suite'in büyük-açıklık kontrolü olmadığından (docs: "App 1-7 kapsam dışı") bu vaka ancak A/A1/A2 aritmetiği için kullanılabilir; A1'deki dLr kaynak içi geometriden geliyor, suite'in standart UG-40 sınırından farklı olabilir → sonuç farkı beklenir, hata sayılmamalı.

### K2-04 — App. 2 gevşek (loose) flanş, halka tipi — cıvata yükü, momentler, gerilmeler, esneklik

Kaynak: PVE, *PVE Sample 5* ("Flange ver 4.27", "10-inç custom flange") · Sayfa: 16 (girdiler), 17 (yükler/gerilmeler), 18 (rijitlik) · Kod: ASME VIII-1 App. 2 (Fig. 2-4(3a) seçimi) · Güven: yüksek
Girdiler: A (OD) = 14,750 in; Bn (iç çap) = 10,750 in; t = 1,250 in; nozul tn = 0,365 in; gasket GOD = 12,125, GID = 10,750 in, m = 1,00, y = 200 psi; cıvata dairesi C = 13,000 in, 8 adet 5/8-11 UNC (kök alanı 0,208 in²/adet, Ab = 1,664 in²); P = 201,0 psi, Pe = 0; Sf = 18600 psi (tasarım), Sfa = 20000 psi (montaj), Sb = Sba = 25000 psi, Efo = 26,4E6, Efs = 28,3E6 psi; CA = 0
Yayınlanmış sonuçlar: b0 = 0,344; b = 0,293 in; G = 11,539 in; H = 21003 lb; Hp = 4269 lb; HD = 18239 lb; HT = 2764 lb; **Wm1 = 25272 lb**; **Wm2 = 2125 lb**; Am = 1,011 in²; Ab = 1,664 in²; **W = 33436 lb**; HG = 4269 lb; hD = 1,125; hG = 0,731; hT = 0,928 in; MD = 20519; MT = 2564; MG = 3119 in·lb; **Mo (işletme) = 26202 in·lb**; **Mo2 (montaj) = 24430 in·lb**; K = A/B = 1,372; Y = 6,299; **ST (montaj) = 9161 psi**; **ST (işletme) = 9826 psi**; rijitlik J (montaj) = 0,764, J (işletme) = 0,879 (≤ 1).
Formülasyon notu: PVE H = 0,785·G²·P ve Hp'de π yerine 3,14 kullanıyor (≈ %0,05 fark). Y yayınlanmış bir grafik/tablodan "K" ile okunmuş (6,299) — suite Y'yi kapalı formla (App. 2-7) hesaplarsa 6,3 civarı beklenir, kaynak değerini ara kontrol olarak kullan; grafik yeniden üretilmedi. Rijitlik indeksi bu flanş için formülde ln(K) biçiminde (loose flanş).

### K2-05 — Konik gövde, iç basınç, App. 1-4(e) (≈ UG-32(g)) — kalınlık ve Pmax

Kaynak: PVE, *PVE Sample 5* · Sayfa: 7 · Güven: yüksek
Girdiler: bkz. K2-01 (ODL = 12,750, t = 0,188, α = 25,3°, S = 18600 psi, E = 0,70, P = 200,953 psi)
Yayınlanmış sonuçlar: treq (büyük uç) = **0,108 in**; yerel OD = 10,39 in'de treq = **0,088 in**; Pmax = **351,0 psi**
Formülasyon notu: Formül App. 1-4(e) dış-çap biçiminde t = P·OD/(2cosα(SE + 0,4P)); suite UG-32(g) iç-çap biçimi (SE − 0,6P) kullanıyorsa küçük, sistematik fark beklenir (V-04/V-05/V-06 ile aynı sınıf: FORMÜLASYON_FARKI). Pmax = 2SE·t·cosα/(OD − 0,8t·cosα).

### K2-06 — Dış basınç, silindirik gövde (UG-28(c)) — 48 in, kısa/uzun, A ve B

Kaynak: Pressure Vessel Engineering Ltd., *External Pressure Calculations* (sample calc set PVEcalc-3473-1.0, yazar L. Brundrett, 10-Mayıs-2010, Rev. 17-May-2011) · https://www.pveng.com/wp-content/uploads/2016/06/External-Pressure-Calculations.pdf (ayrıca anlatı: https://www.pveng.com/home/asme-code-design/external-pressure-methods/) · Sayfa: 5 (gövde 1), 10 (vakum halkalı gövde), 33 (72 in gövde) · Kod: ASME VIII-1 Edition 2007, Addenda 2009 · Güven: yüksek
Girdiler (sayfa 5): SA-240 304, 150 °F, Chart HA-1; Do = 48,000 in; t = 0,225 in; CA = 0; Le = 119,259 in (Le/Do = 2,485); Do/t = 213,33; Pa = 15,0 psi (iç P = 30 psi; S = 18350 psi; E = 0,70)
Yayınlanmış sonuçlar: **A = 0,0001743**; kaynağın kullandığı **B = 2410 psi**; **PaMax = 4B/(3·Do/t) = 15** psi (≥ 15 → uygun); gerekli tre = 0,225 in (B' = 2404 ile); iç basınç için tmin = 0,063 in.
Ek vaka (sayfa 10, vakum halkalı kısa gövde): Do = 48,000, t = 0,169 in, Le = 59,629 in (Le/Do = 1,242), Do/t = 284,02, Pa = 15 psi → A = 0,0002332, kaynağın kullandığı B = 3224 psi, PaMax = 15; tre = 0,168 in (B' = 3206).
Ek vaka (sayfa 33): Do = 72,000, t = 0,200 in, Le = 49,500 in (Le/Do = 0,688), Do/t = 360 → A = 0,0002938, kaynağın kullandığı B = 4061 psi, PaMax = 15; tre = 0,200 in (B' = 4054).
Formülasyon notu: UG-28(c)(2) (Do/t ≥ 10). "B = …" değerleri HA-1 malzeme grafiğinden (150 °F) kaynağın okuduğu değerlerdir; grafik yeniden üretilmedi. Suite kendi grafik/ortak interpolasyonuyla farklı B okursa küçük farklar normaldir; A ve PaMax = 4B/(3Do/t) cebri doğrudan kontrol edilir. Yayınlayıcı ikinci bir B' (basınca göre tersten) veriyor — kalınlık sorusunda onu kullanmış.

### K2-07 — Dış basınç, KONİ (UG-33(f)) ve iç basınç App. 1-4(e)

Kaynak: PVE, *External Pressure Calculations* (aynı belge) · Sayfa: 34 (Cone ver 3.00) · Kod: ASME VIII-1 2007 + Add. 2009 · Güven: yüksek
Girdiler: SA-240 304, S = 18350 psi, E = 0,70, Chart HA-1; DL = 72,000 in, DS = 48,000 in, L (koni yüksekliği) = 12,046 in; t = 0,126 in; CA = 0; α = 44,89° (0,783 rad); P (iç) = 30 psi; Pa = 15 psi; T = 300 °F
Yayınlanmış sonuçlar: iç basınç: treq = **0,119 in**, Pmax = **31,9 psi**; dış basınç: DL/t = 571,4; Le/DL = min(50, L/DL) = 0,167; **A = 0,00068**; kaynağın kullandığı **B = 6501 psi**; **PaMax = 4B/(3·DL/t) = 15,2 psi**; gerekli tre = 0,125 in (B' = 6474 psi).
Formülasyon notu: Bu PVE tablosu dış basınç denkleminde DL/t (nominal t, te = t·cosα uygulanmamış) kullanıyor; K2-15'teki APV çıktısı ise te = t·cosα kullanıyor. İki PVE aracı arasındaki bu tanım farkı yayıncının kendi iç tutarsızlığıdır — suite hangi te tanımını seçerse sonuç ~cosα oranında farklı çıkar (α = 44,9° için ~%30); bu yüzden K2-07 yalnız A ve 4B/(3·DL/t) aritmetiği için kullanılmalı, güçlü doğrulama için K2-15 tercih edilmeli.

### K2-08 — Dış basınç, F&D ve 2:1 yarı-eliptik bombe (UG-33(d)/(e))

Kaynak: PVE, *External Pressure Calculations* · Sayfa: 6 (F&D), 7 (SE), 32 (72 in SE) · Kod: ASME VIII-1 2007 + Add. 2009 · Güven: yüksek
Girdiler (sayfa 6, F&D): SA-240 304, Do = 48,000, L (taç yarıçapı) = 48,000 in, r = 0,06L = 2,88 in → M = 1,771; t = 0,142 in (öncesi/sonrası aynı); E = 0,85; S = 18350 psi; P = 30 psi; Pa = 15 psi; 150 °F; Ro = L + tb = 48,142 in
Yayınlanmış sonuçlar: iç basınç Tmin = 0,082 in; dış basınç **A = 0,125/(Ro/t) = 0,0004**; kaynağın kullandığı **B = 5097 psi**; **PaMax = B/(Ro/t) = 15,0 psi**; TMinE = Pa·Ro/B' = **0,142 in** (B' = 5091).
Girdiler (sayfa 7, 2:1 SE): Do = 48,000 in; h = 11,937 in; t = 0,127 in; E = 0,85; Kzero = 0,895 (Ro = 0,895 Do = 42,973 in); K = 1,000, Kone = 0,900 (UG-37 tablosundan interpole)
Yayınlanmış sonuçlar: Tmin (iç) = 0,046 in; A = 0,0004; kaynağın kullandığı B = 5107 psi; PaMax = **15,1 psi**; TMinE = **0,127 in** (B' = 5091).
Ek (sayfa 32, 72 in SE): Do = 72, h = 17,905, t = 0,190 in, Ro = 64,460 in → B = 5094, PaMax = 15,0; TMinE = 0,190 in.
Formülasyon notu: Bombe dış basıncı Ro = Ko·Do ile (0,9·Di benzeri) yapılıyor; V-18 (iç çap hatası) bulgusu ile doğrudan ilişkili: suite'in bombe dış basıncı Ko·Do'dan türetilmeli, iç çaptan değil. A = 0,125/(Ro/t) formülü App. UG-33(a)(1).

### K2-09 — PEDLİ nozul, 2:1 yarı-eliptik BOMBE (SA-516-70 bombe, SA-106-B nozul) — tam A1…A5 + UG-45 + kaynak yolları

Kaynak: Pressure Vessel Engineering Ltd., *Sample 3 — Horizontal Retention Tank, Advanced Pressure Vessel 10.0.2 (Computer Engineering Inc.)*, 27-Eki-2008 · https://www.pveng.com/wp-content/uploads/2016/06/Sample3_APV.pdf · Sayfa: 11 (nozul C bilgi), 12 (trn, UG-45), 13 (alan dökümü) · Kod: ASME VIII-1, 2007 Edition · Güven: yüksek
Girdiler: Nozul C = 6 in Sch 80 boru, SA-106 B, Sn = 17100 psi; bombe SA-516-70 2:1 (Do = 96,000 in, K = 1,0), Sv = 20000 psi, bombe t (yeni) = 0,3125, kullanılan t = 0,2820 in; P = 75 + 3,5 statik = 78,50 psi; E = E1 = 1; F = 1; nozul ID = 5,761 in, tn = 0,432 in; Rn = 2,8805 in; **açıklık d (developed) = 6,800 in**; dLR = 10,000 in; dış çıkıntı 4,0 in, içe 0; Weld41 = 0,3125; Weld42 = 0,250; Weld43 = 0; ped SA-516-70, Sp = 20000 psi, te = 0,3125 in, Dp = 12,000 in; fr1 = fr2 = fr3 = 0,855, fr4 = 1,000
Yayınlanmış sonuçlar: tr (bombe) = 0,1877 in; trn = 0,0133 in; **A = 1,2999 in²**; **A1 = 0,2899 in²**; **A2 = 0,5048 in²** (formül 1; formül 2 = 0,9970); A3 = 0; **A41 = 0,0835 in²**; A42 = A43 = 0; **A5 = (Dp − d − 2tn)·te·fr4 = 0,7300 in²**; toplam mevcut = **1,6082 in²** (> A); UG-45: UG-45(a) = 0,0133 (+CA = 0,0133), (b)(1) = 0,1877, (b)(4) std boru = 0,2450 → seçilen **0,1877 in** ≤ tn·0,875 = 0,3780; kaynak yolu yükü W = 11800 lb, yollar 77500/91500/91500 lb.
Formülasyon notu: Bu nozul teğetsel/eğik yerleşimli ("tangential to the vessel wall"; d = 6,8 ≠ ID) — suite yalnız radyal nozulu destekliyor; yalnız ardışık alan aritmetiğini (A1…A5, fr faktörleri, ped A5) girdi olarak vererek kullanın, açıklık geometri üretimini kontrol etmeyin. Ped OD 12,0 < UG-40 sınırı → kırpma tetiklenmez (sınır aşımı için K2-11'e bakın). Bu vaka pedli nozulu doğrudan sınar (V-15 pedsizdi).

### K2-10 — PEDLİ nozul, 2:1 bombe, kalın cidar — dış basınç dahil (iç ve dış çift kontrol)

Kaynak: PVE, *Sample 13 — Sample Tower*, Job PVE-3602 (APV 10.1.5), 12-Kas-2009 · https://www.pveng.com/wp-content/uploads/2016/06/Sample13_Spreadsheet.pdf · Sayfa: 29 (nozul N1 bilgi), 30 (UG-45), 31 (alan, iç), 32 (alan, dış) · Kod: ASME VIII-1, 2007 Ed. + 2008 Add. · Güven: yüksek
Girdiler: bombe = Head 1, 2:1 SE, SA-516-70, Do = 86,000 in, K1 = 0,9, t(yeni) = 1,250, t (korozyonlu, thin-out) = 0,8750 in, CA = 0,125 in; Sv = 19700 psi, normalize; P = 250 psi (iç statik 34 psi ayrı), 550 °F; nozul N1 = 8 in Sch 80, SA-106 B, Sn = 17100 psi, ID(yeni) = 7,625 → korozyonlu 7,875 in (d), tn = 0,500 → korozyonlu 0,375 in, Rn = 3,9375 in; dış çıkıntı 2,0 in; Weld41 = 0,375, Weld42 = 0,625 (ped-gövde), groove = 1,25; ped SA-516-70, Sp = 19700, te = 0,7500, Dp = 10,000 in; fr1 = fr2 = fr3 = 0,868, fr4 = 1,000; E1 = 1; F = 1; dış tasarım Pa = 15 psi
Yayınlanmış sonuçlar iç basınç: tr = 0,4886 in; trn = 0,0581 in; **A = 3,8961 in²**; **A1 = 3,0047 in²** (formül 1; formül 2 = 0,9278); **A2 = 0,9284 in²** (formül 2); A3 = 0; **A41 = 0,1221 in²**; **A42 = 0,3906 in²**; A43 = 0; **A5 = 1,0313 in²**; toplam = **5,4771 in²** (> A); UG-45: (a) = 0,1831, (b)(1) = 0,6645, (b)(2) = 0,2188, (b)(3) = 0,6645 → UG-45 = **0,4067 in** ≤ 0,4375 (tn·0,875). Dış basınç: tr = 0,2273 in; trn(dış) = 0,0152 in; A(dış) = 0,5·(…) = 0,9062 in²; A1 = 5,0365; A2 = 1,0541; toplam dış = 7,6346 in².
Formülasyon notu: Bu bombe ve malzeme zaten V-05/V-15'in kardeşi — bu yüzden bombe tr'sinde Appendix 1-4(c) dış çap biçimi (K1 = 0,9) kullanılıyor; suite UG-32(d) iç-çap biçimiyle %0,4–0,9 daha ince tr verir (FORMÜLASYON_FARKI sınıfı) ve bu fark A'yı birkaç binde etkiler; tr'yi girdi olarak vererek yalnız alan dengesini sınamak daha temiz. PVE'nin A1'i "iki formülden büyüğü", A2'si "iki formülden küçüğü" olarak alıyor.

### K2-11 — PEDLİ nozul, silindirik gövde — iç ve dış basınç, UG-45 (a/b), App. 2 flanşlı kanal

Kaynak: Paget Equipment Co. (Marshfield, WI), *Example Vessels — Fixed Tube, 5-in Inlet N2* (APV 9.1.1, Computer Engineering Inc.), 27-Şub-2006; üçüncü taraf barındırma (SlideShare, "Engineering example calculation", MOSTAFA DAIF yüklemesi) · https://www.slideshare.net/slideshow/engineering-example-calculation/230327303 · Sayfa: 1 (gövde S1), 2 (nozul bilgi), 3 (trn, UG-45), 4 (alan, iç), 5 (alan, dış) · Kod: ASME VIII-1, 2004 Edition, 2005 Addenda · Güven: orta (birincil üretici belgesi ancak ikinci el barındırma; sayılar PDF metninden okundu, orijinal PDF'e ulaşılamadı)
Girdiler: gövde SA-516-70, Sv = 18800 psi (650 °F), iç çap (yeni) = 42,000 → korozyonlu 42,125 in, t(yeni) = 0,3125 → t (korozyonlu) = 0,2500 in, CA = 0,0625, E = 1; P = 200,0 psi; Pa = 15 psi; nozul 5 in Sch 80 SA-106 B, Sn = 17100 psi, ID(yeni) = 4,813 → korozyonlu d = 4,9380 in, tn(yeni) = 0,375 → korozyonlu 0,3125 in, Rn = 2,4690 in, dış çıkıntı 6,0 in, içe 0; Weld41 = 0,250, Weld42 = 0,1786, groove = 0,3125; ped SA-516-70, Sp = 18800, te = 0,2500, Dp = 8,0000 in; fr1 = fr2 = fr3 = 0,9096, fr4 = 1,0000; E1 = 1; F = 1; UG-40 çap limiti 9,876 in
Yayınlanmış sonuçlar iç basınç: tr = 0,2255 in; trn = 0,0291 in; **A = 1,1263 in²**; **A1 = 0,1196 in²** (formül 1; formül 2 = 0,0262); **A2 = 0,3222 in²** (formül 1; formül 2 = 0,5317); A3 = 0; **A41 = 0,0568 in²**; **A42 = 0,0319 in²**; A43 = 0; **A5 = 0,6093 in²**; toplam = **1,1398 in²** (> A, marjin yalnız +0,0135 → sınır vaka). Dış basınç: tr(dış) = 0,2158 in; trn(dış) = 0,0193 in; A(dış) = 0,5389; A1 = 0,1669; A2 = 0,3334; toplam = 1,1983 in². UG-45: (a) 0,0916; (b)(1) 0,2880; (b)(2) 0,1250; (b)(3) 0,2880; (b)(4) 0,2882 → seçilen **0,2880 in** ≤ tn·0,875 = 0,3281.
Formülasyon notu: İç basınç toplamı gereken alanı yalnız %1,2 aşıyor → suite'in küçük bir sapması (örn. A2 formülü, fr, UT) kararı ters çevirebilir; bu yüzden yüksek değerli bir "kritik karar" vakası. Dış basınç gereken alan 0,5·(iç formül) olarak (UG-37(d)(1)'in 0,5 çarpanı). "A1 formül 2"nin tr'den büyük çıkmasına gerek yok: kaynak "iki formülden büyüğünü" alıyor. Eski baskı (2004/2005): A2 için min(5·t, 2,5tn+te) kuralı; PVE-S5'in min(5t,5tn) ile pedsiz durumda aynı.

### K2-12 — App. 2 integral flanş (Fig. 2-4(5)), halka gasket, tam yük/moment/gerilme dökümü

Kaynak: Paget Equipment Co., *Example Vessels — Fixed Tube, Flange F1 "Pair, Mating to Shell Flange"* (APV 9.1.1), 27-Şub-2006 · aynı SlideShare URL · Sayfa: 22 (girdiler), 23 (yükler, momentler), 24 (şekil sabitleri), 25 (gerilmeler), 26 (rijitlik) · Kod: ASME VIII-1, 2004 Ed. + 2005 Add. App. 2 · Güven: orta (ikinci el barındırma)
Girdiler: P = 200,0 psi, 650 °F; SA-516-70, Sfo = 18800, Sfa = 20000 psi; A = 50,250 in, B = 42,000 in (korozyonlu 42,125), C = 47,000 in; g0 = g1 = 0,1875 in (korozyonlu), hub uzunluğu h = 0; t = 4,2500 in; CA = 0,0625; cıvata SA-193 B7, Sb = Sa = 25000 psi, 24 adet 1-5/8" 6 TPI, kök alanı 1,5150 in²/adet; gasket kontak OD 45,000 in, N = 1,000 in, m = 2,75, y = 3700 psi, kaplama 1a(1)
Yayınlanmış sonuçlar: b0 = 0,5000; b = 0,3536 in; G = 44,2928 in; Wm2 = 182053 lb; H = 308167 lb; Hp = 54124 lb; **Wm1 = 362291 lb**; Am1 = 14,4916; Am2 = 7,2821; **Am = 14,4916 in²**; Ab = 36,3600 in²; **W = 635645 lb**; HD = 278740; HG = 54124; HT = 29427 lb; R = 2,2500; hD = 2,3438; hG = 1,3536; hT = 1,8956 in; MD = 653311; MG = 73262; MT = 55782; **Mo = 782355 in·lb**; **Ma = W·hG = 860409 in·lb**; K = 1,1929; Y = 11,1025; T = 1,8418; U = 12,2005; Z = 5,7280; ho = 2,8104 in; F = 0,9089; V = 0,5501; f = 1,0000; e = 0,3234; d = 2,1913; L = 36,3212; **işletme: SH = 14545, SR = 80, ST = 10958, Sc = 12752 psi**; **montaj: SH = 15996, SR = 88, ST = 12051, Sc = 14024 psi**; rijitlik J (işletme) = 0,80; J (montaj) = 0,88; min. kalınlık = 3,6834 in (t = 4,25 seçilmiş); flanş MAWP = 294,89 psi.
Formülasyon notu: Hub uzunluğu sıfır (h/ho = 0) ve g1 = g0 → "integral" ama hub yok; F, V, f Tablo 2-7.1'den bu uç değerlerle alınmış (F = 0,9089; V = 0,5501; f = 1,0). Suite F/V/f'yi grafik yerine kapalı formla alıyorsa h/ho = 0 uç noktasında farklı çıkabilir (küçük). Montaj hali Ma = W·hG ve Sfa ile sınanıyor. Bu vaka K2-04 (gevşek) ve K2-13 (hublu) ile birlikte App. 2 üç tip.

### K2-13 — App. 2 integral weld-neck flanş (hublu, Fig. 2-4(6)), PV Elite

Kaynak: Pressure Vessel Engineering Ltd., *Heat Exchanger Sample, PVE-4293*, PV Elite 2012 (Intergraph), 20-Eyl-2012 · https://www.pveng.com/wp-content/uploads/2016/06/HeatExchanger_Calcs.pdf · Sayfa: 11 (girdi), 12 (yükler), 13 (momentler), 14 (gerilmeler), 15 (sonuç, rijitlik) · Kod: ASME VIII-1, 2010 Ed. + 2011a Add., App. 2 · Güven: yüksek
Girdiler ("Ch. Flange", kanal flanşı): P = 150 psig, 650 °F; CA = 0,0625 in (kalınlık hesabında kullanılmadı: "No"); B = 18,125 in (korozyonlu Bcor = 18,250), A = 23,500 in, t = 1,7500 in, g0 = 0,1875 → 0,125 in, g1 = 0,5625 → 0,500 in, h = 1,1250 in; SA-105, Sfo = 17800, Sfa = 20000 psi; cıvata SA-193 B7, Sb = Sa = 25000 psi, C = 21,750 in, 16 adet 5/8" UNC; Fod/Fid 19,75/18,125; gasket Go = 19,125, Gi = 18,125 in, m = 2,5, y = 2900 psi, kısım gasketi lp = 18,125, tp = 0,313, mPart = 2,5, yPart = 2900 psi
Yayınlanmış sonuçlar: R = 1,250; N = 0,500; b0 = b = 0,250; G = 18,625 in; H = 40867 lb; Hp = 13098 lb; Hd = 39238 lb; Ht = 1629 lb; **Wm1 = 53966 lb**; **Wm2 = 50647 lb**; **Am = 2,159 in²**; Ab = 3,232 in²; Bsmax = 4,750 in; Bs = 4,243 in; **Bsc = 1,1893**; **W = 67383 lb**; HG = 13098; hg = 1,5625, ht = 1,6562, hd = 1,5000 in; Md = 5833; Mt = 267; Mg = 2028 ft·lb (bolt corr. ile); **Mop = 8129 ft·lb = 97547 in·lb**; **Matm = 10435 ft·lb = 125214 in·lb**; ho = 1,510 in; h/ho = 0,745; g1/g0 = 4,000; K = 0,736; f = 2,930; β = 2,138; L = 3,161; Y = 7,822; Z = 4,039; e/λ = 0,4875 in⁻¹; **SHo = 19821; SHa = 25443 psi; SRo = 1180; SRa = 1515 psi; STo = 8884; STa = 11404 psi; SAo = 14352; SAa = 18423 psi**; bolt stres işletme = 16697, montaj = 15671 psi; min. kalınlık = 1,684 in; flanş MAWP ≈ 186,0 psig; rijitlik Js = 0,724 (Jop = 0,879 bu belgede ayrı sayfa 15).
Formülasyon notu: **PVE bu çıktıda moment çarpanı Bsc'yi (App. 2 eq. 7, cıvata aralığı düzeltmesi) uyguluyor** — Matm/Mop bu çarpanla büyütülmüş. Suite Bsc'yi uygulamıyorsa (yalnız 2-5 / 2-6 ham momentler) momentler ve gerilmeler %19 kadar düşük çıkar → bu bir hata adayıdır (bağlantı: App. 2-3 "bolt spacing" ve Bsmax = 2a + 6t/(m + 0,5)). Faktörler (f, β, L, Y, Z) gerilme formüllerinden geri okunarak doğrulandı; F, V, T, U, d ve γ PDF'te sütun kayması nedeniyle güvenilir eşleşemedi, yazılmadı (kaynak s.14 doğrudan okunmalı).

### K2-14 — Dış basınç, silindirik gövde (kısa kanal ve uzun gövde) — PV Elite/APV karşılaştırması

Kaynak: Paget Equipment Co., *Example Vessels — Fixed Tube, gövde S1 ve kanal gövdesi* (APV 9.1.1), 2006 · SlideShare URL (K2-11) · Sayfa: 1 (gövde), 56 (kanal gövdesi) · Kod: ASME VIII-1, 2004 Ed. + 2005 Add. · Güven: orta
Girdiler (gövde, s.1): SA-516-70, 650 °F, Chart CS-2; iç çap 42,125 in (korozyonlu); t nominal 0,3125 − CA 0,0625 → 0,2500 in; Do = 42,625 in; L = 125,000 in (L/Do = 2,9326, Do/t = 170,50); Pa = 15,0 psi; iç P = 200 psi; S = 18800, E = 1
Yayınlanmış sonuçlar: **A (nominal) = 0,0002268**; kaynağın kullandığı **B = 2849 psi**; **Pa = 4B/(3Do/t) = 22,28 psi**; minimum t (dış) = 0,2783 in → A = 0,0001770, kaynağın kullandığı B = 2224 psi; iç basınç: boyuna t = 0,1743, çevresel t = 0,2880 in (CA dahil).
Girdiler (kanal gövdesi, s.56): SA-516-70, 650 °F; t nominal 0,2500 → 0,1875 in; Do = 42,500 in; L = 30,0000 in (L/Do = 0,7059, Do/t = 226,667); Pa = 15 psi; iç P = 150 psi; S = 20000
Yayınlanmış sonuçlar: **A = 0,0005952**; kaynağın kullandığı **B = 7268 psi**; **Pa = 42,75 psi**; minimum t = 0,1849 in → A = 0,0003112, B = 3910 psi; iç basınç: boyuna 0,1414, çevresel 0,2212 in.
Formülasyon notu: Yüksek sıcaklık (650 °F) CS-2 grafiği — suite'in CS-2 interpolasyonu yayıncınınkinden farklıysa B farkı beklenir, A ve Pa = 4B/(3Do/t) cebri kontrol edilir. Okunan B'ler kaynağın değerleridir, grafik yeniden üretilmedi.

### K2-15 — KONİ: iç basınç 1-4(e) ve dış basınç UG-33(f) — iki koni (α = 8,59° ve 23,03°)

Kaynak: PVE, *Sample 13 — Sample Tower*, PVE-3602 (APV 10.1.5), 12-Kas-2009 · Sample13_Spreadsheet.pdf (K2-10 URL'si) · Sayfa: 23 (R1), 24 (R2) · Kod: ASME VIII-1, 2007 Ed. + 2008 Add. · Güven: yüksek
Girdiler R1: SA-516-70, Sh = 19700 psi, E = 0,85, 550 °F; büyük uç OD = 122,250 in, küçük uç OD = 86,000 in, yükseklik h = 120,000 in, α = 8,59°; t nominal = 1,2500, CA = 0,125 in; P = 250 + 34 statik = 284,00 psi; Pa = 15,0 psi
Yayınlanmış sonuçlar R1: iç basınç t = P·Do/(2cosα(SE + 0,4P)) = **1,0414 in** (+0,1250 CA = **1,1664 in**); dış basınç: nominal te = 1,1124 in; nominal **A = 0,0014486**; kaynağın kullandığı **B = 10066 psi**; **Pa(izinli) = 4B/(3·DL/te) = 122,13 psi**; minimum t(dış) = 0,5053 (te = 0,3760); A = 0,0002814; B = 3657 psi.
Girdiler R2: aynı malzeme; büyük uç OD = 122,250, küçük uç OD = 37,250 in; h = 100,000 in; α = 23,03°; t nominal = 1,1250 in; P = 253,50 psi (statik başlık farklı)
Yayınlanmış sonuçlar R2: iç basınç t = **0,9995 in** (+CA); nominal te = 0,9203 in, **A = 0,0018060**, kaynağın kullandığı **B = 10518 psi**, **Pa(izinli) = 105,57 psi**; minimum t = 0,4624 (te = 0,3105), A = 0,0003408, B = 4431 psi.
Formülasyon notu: Bu vakada UG-33(f) **te = t·cosα** kullanıyor (K2-07'den farklı!) — ve iç basınç yine 1-4(e) dış-çap biçimi. İki koni açı aralığını (8,6° / 23,0°) kapsıyor, ≤ 30° sınırında. Ayrıca gerçek tasarım ile birlikte kullanılan kalın cidar (t/D ≈ 1%). K2-07 ile K2-15 arasındaki te tanımı farkı yazılım/baskı farkıdır; suite hangi tanımı kullanıyorsa gerekçesi kayda geçmeli.

### K2-16 — Dış basınç, borulu hat gövdesi (firetube) — EMAWP ve gerekli kalınlık, çift sonuç

Kaynak: Pressure Vessel Engineering Ltd., *Firetube — ASME VIII-1 Code Calculations*, PV Elite 2017 (Intergraph), 21-Tem-2017 · https://pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf · Sayfa: 24 (girdi), 25 (iç + dış sonuçlar), 26 · Kod: ASME VIII-1, 2015 Edition · Güven: yüksek
Girdiler: SA-106 B sorunsuz boru, S = 17100 psi, E = 1,00; D (OD) = 14,000 in; t minimum = 0,3281 in (nominal 0,3750); CA = 0; L = 120,000 in; iç P = 15 psi; dış Pext = 125 psig, 500 °F; Chart CS-2; Elastik modül 27,0E6 psi
Yayınlanmış sonuçlar: D/T = 42,6667; L/D = 8,5714; **A = 0,0006042**; kaynağın kullandığı **B = 8157,3491 psi**; **EMAWP = 4B/(3·D/T) = 254,92 psig**. Gerekli kalınlık araması: TCA = 0,2566 in → D/T = 54,5671; A = 0,0003790; B = 5115,9312 psi; EMAWP = **125,01 psig** (= istenen 125 psig). Sonsuz uzun halde L/D = 50 → aynı A, B, EMAWP. İç basınç tarafında MAWP = 816,88 psig ve hidro 1061,94 psig (UG-99(b)) bu belgede V-08/V-07'de kullanıldı.
Formülasyon notu: Bu vaka dış basınçta **iki yönlü** sınanır: izinli basınç (PaMax) ve gerekli kalınlık (ters çözüm). Kaynak "Pext = 125 psig" gerçekçi vakum/yüksek dış basınç. L/D = 8,57 ≥ 50 sınırında değil → UG-28(c)(2) L/Do tablosu. Okunan B kaynağın değeridir, grafik kopyalanmadı.

### K2-17 — Torisferik bombe üzerinde PEDLİ manhole (SI birimli, PV Elite 2007)

Kaynak: Binesh P. Vyas, R. M. Tayade, Ankit D. Kumbhani (VJTI, Mumbai), *Design of Vertical Pressure Vessel Using PVElite Software*, International Journal of Engineering Research & Technology (IJERT), Vol. 2 Issue 3, Mart 2013 · https://www.ijert.org/research/design-of-vertical-pressure-vessel-using-pvelite-software-IJERTV2IS3311.pdf · Sayfa: 3–4 (manhole M) · Kod: ASME VIII-1, 2007 Edition, UG-37 – UG-45 (PV Elite çıktısı) · Güven: orta (hakemli dergi makalesi; ancak basılı formül/sayı tutarsızlıkları var: tr formülü K = 1 biçiminde basılı, makalede ise torisferik M = 1,5406 anılıyor; bu yüzden tr yeniden türetilmeden **girdi** olarak kullanılmalı)
Girdiler: dikey kap, DM su, tasarım basıncı 0,245 MPa, 150 °C; torisferik bombe L = Di = 1000, r = 100 mm (M = 1,5406); bombe t = 3,000 mm; manhole M: nozul ID = 428,650 mm, tn = 14,275 mm (OD = 457,2), Rn = 214,325 mm; ped Dp = 600,0 mm, te = 6,000 mm; Wo = 6,000 mm; Wp = 5,000 mm; S(gövde/ped) = 87 N/mm² (basılı), fr = 1,0; UG-40: DL = 857,3008 mm, Tlnp = Tlwp = 7,5000 mm; açı 90°
Yayınlanmış sonuçlar: tr (bombe) = 1,4016 mm; trn = 0,6016 mm; **Ar = 6,008 cm²**; **A1 = 6,852 cm²**; **A2 = 2,051 cm²** (2·min(Tlnp, ho)·(tn − trn)·fr2); A3 = 0; **A4 = 0,407 cm²** (pedli: Wo²·fr3 ... + Wp² = 0,1575 + 0,25); **A5 = (Dp − Nozzle OD)·min(Tp, Tlwp, te)·fr4 = 8,568 cm²**; **Atot = 17,878 cm²**; pedsiz yeterli; UG-45: tra = 0,6016, UG-16(b) = 1,5875, UG-45(b)(1) trb1 = 2,1592, (b)(4) = 8,3344 → **tr45 = 2,1592 mm** ≤ 0,875·tn = 12,4905 mm.
Formülasyon notu: Pedsiz alan (A1 + A2 + A41) zaten Ar'yi aşıyor (6,852 + 2,051 > 6,008) — ped gereksiz; vaka daha çok A5'in UG-40 sınırıyla (min(Dp, DL) ve min(Tp, Tlwp, te)) kırpılması davranışını sınar: Dp = 600 < DL = 857 → kırpma yok. Basılı tr formülü (K = 1, 2SE − 0,2P, S = 87 ve P = 245) birim karışıklığı içeriyor (kPa/MPa/psi); bu yüzden tr'yi sonuç olarak kabul edip yalnız alan aritmetiğini sınayın. Birim: cm² ↔ mm² (1 cm² = 100 mm²).

### K2-18 — Koni–silindir bağlantısı gerilme değerlendirmesi (Bednar yöntemi; App. 1-5(g)/UG-23(e) limitleri) — BİLGİ

Kaynak: PVE, *External Pressure Calculations* (L. Brundrett, 2010/2011) · Sayfa: 35–37 ("Cone Discontinuity ver 4.04", dayanak: H. H. Bednar, *Pressure Vessel Design Handbook*, 2. baskı, s. 231–240 ve ASME VIII-1 App. 1-5(g)) · Güven: orta
Girdiler: büyük silindir ODL = 72,000 in, tLn = 0,200 in; koni α = 45,0°, tCn = 0,126 in, Ec = 0,70; küçük silindir ODS = 48,000 in, tSn = 0,154 in, Es = 0,70; SA-240 304, S = 18350 psi; iç basınç P = 15,0 psi (bağlantı bölgesi "dış basınç" başlıklı sayfada iç P girdisi olarak); CA = 0; W = M = 0
Yayınlanmış sonuçlar (örnekler): nL = 0,630; kL = 1,059; V1L = 0,525; V2L = 0,090; XL = 0,421; YL = 0,443; UL = 1,061; Long1 (A bölgesi) = 16530 psi; Long3 (B) = 41279 psi; Long5 (C) = 32814 psi; MemTan3 = 14147 psi; limitler 3SE ve 1,5SE (örn. 55050, 27525 psi).
Formülasyon notu: **Bu bir App. 1-5 alan-takviye (Q, Δ) hesabı değildir** — süreksizlik gerilmesi (Bednar). Suite'in "Appendix 1-5 koni-silindir takviyesi" maddesi için doğrudan karşılaştırma yapılamaz; yalnız gerilme/limit mantığı için bilgi. Gerçek App. 1-5 vakası için "Boşluklar" bölümüne bak.

### K2-19 — UG-45 nozul boyun kalınlığı — üç yayıncıdan karşılaştırmalı özet

Kaynak: PVE-S5 s.11,13,14 · PVE-S13 s.30 · PVE-S3 s.12 · Paget s.3 · IJERT s.4 (URL'ler yukarıda) · Güven: yüksek (PVE), orta (Paget, IJERT)
Girdiler/sonuçlar (UG-45 bileşenleri, "a = basınçtan", "b = (b)(1)–(b)(4) alt sınırı"):
- PVE-S5 nozul A: UG45a = 0,011; UG45b = 0,088 → **0,088 in**; Nact = 0,135.
- PVE-S5 nozul B: **0,067 in**; nozul C: UG45a = 0,055, UG45b = 0,067 → **0,067 in**; Nact = 0,319.
- PVE-S13 N1 (bombe): (a) = 0,1831; (b)(1) = 0,6645; (b)(2) = 0,2188; (b)(3) = 0,6645; (b)(4) = 0,4067 (std boru) → **0,4067 in** ≤ 0,4375.
- PVE-S3 nozul C: (a) = 0,0133, (b)(1) = 0,1877, (b)(4) = 0,2450 → **0,1877 in**.
- Paget N2: (a) = 0,0916 (CA dahil), (b)(1) = 0,2880, (b)(2) = 0,1250, (b)(3) = 0,2880, (b)(4) = 0,2882 → **0,2880 in** ≤ 0,3281.
- IJERT M (mm): tra = 0,6016, tr16b = 1,5875, trb1 = 2,1592, trb4 = 8,3344 → **2,1592 mm** ≤ 12,4905.
Formülasyon notu: Seçim kuralı = max(UG-45(a), min[(b)(3), (b)(4)]) ve borunun %12,5 eksik toleransı için 0,875·tn karşılaştırması. (b)(4) standart boru kalınlığı tablosu gerektirir — suite'in tablosu yoksa girdi olarak (Tstd = 0,154/0,145/0,365 in vb.) verin.

### K2-20 — Pedsiz-pedli nozul sınır sezgisi: A1 "iki formülden büyüğü"

Kaynak: Paget N2 s.4 + PVE-S13 N1 s.31 + PVE-S3 C s.13 · Güven: orta/yüksek
Girdiler: bkz. K2-09, K2-10, K2-11
Yayınlanmış sonuçlar: Paget: A1 formül 1 = 0,1196, formül 2 = 0,0262 → 0,1196; PVE-S13: formül 1 = 3,0047, formül 2 = 0,9278 → 3,0047; PVE-S3: A1 = 0,2899 (dLR-biçimli). Hepsi formül 1 (d tabanlı) kazanıyor.
Formülasyon notu: Kaynak yazılımlar A1'de iki formülden (d tabanlı ve 2(t+tn) tabanlı) büyüğünü alıyor; bu üç vakada d tabanlı biçim kazanıyor. Suite tek biçim kullanıyorsa bu vakalarda fark çıkmaz; küçük d / kalın t durumunda (2(t+tn) > d) fark çıkabilir — bu kayıt yeni sayı eklemez, yalnız hatırlatmadır. Kod baskısı bağımlılığı doğrulanmadı.

### K2-21 — Nozul çıkıntısı kontrolü: UW-16 kaynak ölçüsü ve UG-41 yol analizi (yan ürün)

Kaynak: PVE-S3 s.13 (kaynak yolları), PVE-S5 s.11 (tc/Leg41 kontrolü) · Güven: yüksek
Girdiler: bkz. K2-09, K2-01
Yayınlanmış sonuçlar: PVE-S5 A: tc41 = min(0,25; 0,7·min(0,75; tn; t)) = 0,108 in; 0,7·Leg41 = 0,132 ≥ tc41 (uygun). PVE-S3 C: nozul duvarı kayma 0,70·Sn = 11970 psi; fileto 0,49·malzeme = 8379/9800 psi; groove çekme 0,74·malzeme = 12654 psi; mukavemet elemanları 50300, 27200, 37100, 46200 lb; yol 1-1 = 77500, 2-2 = 91500, 3-3 = 91500 lb; yük W = 11800 lb.
Formülasyon notu: Suite UG-41 yük/yol analizi sunmuyorsa kapsam dışı; yine de UW-16 minimum fileto ölçüsü (tc = min(0,25 in; 0,7·tmin)) sınanabilir.

---

## Erişilemeyen / kullanılamayan kaynaklar (sayı uydurulmadı)

| Kaynak | Durum |
|---|---|
| ASME PTB-4 (Section VIII Div.1 Example Problem Manual; 2013, 2021) | Ücretli; yalnız içindekiler listesi (asme.org PDF) erişilebildi — **sayısal örnekler okunamadı** |
| Megyesy, *Pressure Vessel Handbook*; Moss, *Pressure Vessel Design Manual* | Çevrimiçi serbest tam metin bulunamadı (yalnız Scribd/üçüncü taraf, erişilemedi) — atlandı |
| Chemical Engineering dergisi, "Nozzle Penetrations in Pressure Vessels: Two Methods for Reinforcement Design" (Stikvoort & Gardaneh, 1 Eki 2025) | Ödeme duvarı |
| LBL/NEXT (www-eng.lbl.gov/~shuman/NEXT/…: Boot_calc.pdf, nozzle_calc_method_bildy.pdf, calcs_pmt_enclosure_ver_B.pdf, Next100_DesignandFabrication_1.pdf) | Arama motoru bağlantı veriyor, sunucu **404** döndürüyor (kaldırılmış) |
| Scribd (Engineering Example Calculation, Compress Calculation, Nozzle Analysis, Backing Ring Calculation, FEM, Assignment 2 Solution vb.) | Yalnız açılış sayfası; içerik okunamadı. Paget belgesinin aynı içeriği SlideShare'den metin olarak okundu (K2-11/12/14) |
| eng-tips.com (qid=249834 vb.) | HTTP 403 |
| Codeware COMPRESS örnek raporu (codeware.com) | Genel örnek rapor bulunamadı. PVE'nin COMPRESS çıktıları (Vertical_Compress.pdf, 22687c-1-R0.pdf "Audit Vessel", COMPRESS 2026 / ASME 2023) açıldı: nozullar muaf (UG-36(c)(3)(a)) veya ped yok/alan dökümü basılmamış → **kullanılabilir sayısal vaka çıkmadı** |
| Hexagon PV Elite yardım sayfaları (docs.hexagonppm.com) | Formül/alan açıklamaları var, sayısal çözümlü örnek yok |
| pveng.com Sample 4 spreadsheet, Sample 5 dışı örnekler, 3602_Calculations_R0.pdf | Sample 4 yalnız Scribd; 3602_Calculations_R0.pdf görüntü tabanlı (metin katmanı yok), okunamadı |

## Boşluklar (vaka bulunamadı)

1. **App. 1-5 koni–silindir bağlantısı takviyesi** (Q, ΔΔ, A_rL, A_rs; internal) ve **App. 1-8** (dış basınç): yayınlanmış, sayısal çıktısı olan örnek bulunamadı (PV Elite/Hexagon dokümanları yalnız formül sunuyor). K2-18 yalnız gerilme yaklaşımı.
2. **UG-32(g) iç-çap biçimi**: kaynaklar dış-çap 1-4(e) biçimini kullanıyor (K2-05, K2-07, K2-15) → doğrudan UG-32(g) karşılaştırması FORMÜLASYON_FARKI olarak kalır.
3. **Bombe (head) nozulu**: PVE-S3 (K2-09), PVE-S13 (K2-10), IJERT (K2-17) var; **torisferik/F&D üzerinde sürekli pedli** yalnız K2-17 (SI, orta güven).
4. **UG-28 dış basınç, L/Do ≥ 50 sonsuz-uzun ve Do/t < 10 kalın cidar**: K2-16 yalnız L/D = 50 sonsuz-uzun denemesi veriyor; Do/t < 10 vakası yok.
5. **Eğik/teğetsel nozul F faktörü**, **büyük açıklık App. 1-7**: kaynaklar (K2-03, K2-09) var ama suite kapsamı dışı — yalnız aritmetik kontrol.

## Telif ve güven notları

- Hiçbir tablo, grafik veya paragraf kopyalanmadı; yalnız girdi sayıları, yayınlanmış sonuç sayıları ve kısa formülasyon notları yazıldı.
- B değerleri HA-1/CS-2 malzeme grafiğinden kaynağın okuduğu değerlerdir; grafik yeniden üretilmedi. Aynı grafik okuması sayısal tutarsızlık yaratabilir; asıl kontrol A ve 4B/(3Do/t) aritmetiğidir.
- Güven: PVE belgelerinin tamamı birincil PDF'ten metin katmanıyla okundu → yüksek. Paget belgesi (üretici PDF yerine SlideShare metin dökümü) ve IJERT makalesi (basılı formüllerde tutarsızlık) → orta.
- K2-13'te faktör tablosunun (F, V, f, Y, T, U) bir kısmı PDF'te sütun kayması nedeniyle güvenilir eşleşemedi; yalnız eşleşmesi doğrulanan değerler yazıldı (bkz. notta).
