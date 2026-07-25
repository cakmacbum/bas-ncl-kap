# ASME VIII-1 — Yayınlanmış Örneklerle Karşılaştırma

Tur 1 · 2026-07-26 · Kaynak politikası: [`README.md`](README.md)

## Kullanılan kaynaklar

| Kod | Kademe | Künye |
|---|---|---|
| **PVE-FT** | K-A | Pressure Vessel Engineering Ltd., *Firetube* örnek hesap seti. Yazılım: **PV Elite 2017** (Intergraph). ASME VIII-1, 2015. `pveng.com/wp-content/uploads/2017/07/11110c-1_code_calculations.pdf` — erişim 2026-07-26 |
| **PVE-S13** | K-A | Pressure Vessel Engineering Ltd., *Sample 13 — Sample Tower*, Job PVE-3602. Yazılım: **Advanced Pressure Vessel 10.1.5** (Computer Engineering Inc.). ASME VIII-1, 2007 Ed. + 2008 Add. ASME Code Stamped, P.Eng imzalı. `pveng.com/wp-content/uploads/2016/06/Sample13_Spreadsheet.pdf` — erişim 2026-07-26 |

İki kaynak **iki ayrı ticari yazılımın** çıktısıdır — yani birbirinden de bağımsızdır.
Birim dönüşümü tam: `1 in = 25.4 mm`, `1 psi = 0.006894757293168361 MPa`.

## Özet

| No | Madde | Kaynak | Yayın | Suite | Fark | Karar |
|---|---|---|---|---|---|---|
| V-01 | UG-27(c)(1) çevresel | PVE-FT s.6 | 0.1004 in | 0.1004 in | −0.023% | ✅ DOĞRULANDI |
| V-02 | UG-27(c)(2) boyuna | PVE-S13 s.4 | 0.3560 in | 0.3560 in | +0.005% | ✅ DOĞRULANDI |
| V-03 | UG-27(c)(2) boyuna | PVE-S13 s.6 | 0.4778 in | 0.4778 in | +0.005% | ✅ DOĞRULANDI |
| V-04 | UG-32(d) eliptik | PVE-FT s.3 | 0.2237 in | 0.2227 in | −0.446% | ⚠️ FORMÜLASYON_FARKI |
| V-05 | UG-32(d) eliptik | PVE-S13 s.28 | 0.6120 in | 0.6064 in | −0.922% | ⚠️ FORMÜLASYON_FARKI |
| V-06 | UG-27(c)(1) çevresel | PVE-S13 s.4 | 0.7244 in | 0.7218 in | −0.359% | ⚠️ FORMÜLASYON_FARKI |
| V-07 | UG-99(b) + UG-100 test | PVE-FT s.4 | 284.44 / 240.68 psig | 162.50 / 137.50 psig | **−42.9% / −42.9%** | 🔴 **SAPMA → düzeltildi** |
| V-08 | MAWP, silindirik | PVE-FT s.24 | 816.88 psig | 816.82 psig | −0.008% | ✅ DOĞRULANDI |
| V-09 | MAWP, eliptik bombe | PVE-FT s.3 | 218.80 psig | 218.80 psig | −0.000% | ✅ DOĞRULANDI |

**Sonuç:** 4 doğrulandı · 3 formülasyon farkı (hata değil) · **1 gerçek sapma bulundu ve
düzeltildi**.

---

## V-01 · UG-27(c)(1) — Silindirik gövde, çevresel gerilme

```
Girdi     P = 125 psi · R = 16.0000 in (iç) · S = 20000 psi · E = 1.00 · CA = 0
Formül    t = P·R / (S·E − 0.6·P)        [aynı form — kaynak da UG-27(c)(1) kullanmış]
Kaynak    PVE-FT s.6 (nozul boynu)  →  0.1004 in
Suite     0.100376 in = 2.54956 mm
Fark      −0.023 %   (kaynağın 4 haneye yuvarlamasıyla açıklanır)
Karar     DOĞRULANDI  — ikinci teyit: V-06 aynı formülü farklı sayılarla sınıyor
```

## V-02 · UG-27(c)(2) — Silindirik gövde, boyuna gerilme

```
Girdi     P = 284.00 psi (250 tasarım + 34 statik kafa) · R = 42.1250 in · S = 19700 psi · E = 0.85
Formül    t = P·R / (2·S·E + 0.4·P)      [aynı form]
Kaynak    PVE-S13 s.4 (Shell 1)  →  0.3560 in  (+ 0.1250 korozyon = 0.4810 in)
Suite     0.356018 in
Fark      +0.005 %
Karar     DOĞRULANDI
```

Not: karşılaştırma **korozyon payı eklenmeden önceki** ham formül sonucu üzerinden yapıldı;
korozyon toplaması ayrı bir adım ve `shell_required_nominal_thickness` ile sınanıyor.

## V-03 · UG-27(c)(2) — İkinci sayısal vaka

```
Girdi     P = 267.00 psi · R = 60.1250 in · S = 19700 psi · E = 0.85
Kaynak    PVE-S13 s.6 (Shell 2)  →  0.4778 in
Suite     0.477813 in
Fark      +0.005 %
Karar     DOĞRULANDI  — V-02 ile birlikte iki ayrı vaka → kabul kuralı sağlandı
```

## V-04 / V-05 · Eliptik bombe — iç çap ve dış çap formları

```
V-04  Girdi   P = 125 psi · Do = 72.000 in · t = 0.3900 in → Di = 71.220 in · S = 20000 psi · E = 1.00
      Kaynak  PVE-FT s.3, Appendix 1-4(c):  t = P·Do·K / (2·S·E + 2·P·(K−0.1))  →  0.2237 in
      Suite   UG-32(d):                     t = P·Di / (2·S·E − 0.2·P)          →  0.2227 in
      Fark    −0.446 %

V-05  Girdi   P = 284.00 psi · Do = 86.000 in · t = 1.0000 in → Di = 84.000 in · S = 19700 psi · E = 1.00
      Kaynak  PVE-S13 s.28, Appendix 1-4(c)  →  0.6120 in
      Suite   UG-32(d)                       →  0.6064 in
      Fark    −0.922 %
```

**Karar: FORMÜLASYON_FARKI — hata değil.** Her iki ticari yazılım da varsayılan olarak
**Appendix 1-4(c)** dış-çap alternatifini kullanıyor; suite **UG-32(d)** iç-çap formunu
kullanıyor. İkisi de Kod'a uygun ama cebirsel olarak birebir eşdeğer değil.

⚠️ Fark yönü önemli: suite **daha ince** kalınlık üretiyor (%0.4–0.9 daha az). Küçük ama
sistematik ve emniyetsiz yönde. Kayıt: [`limitations.md`](../limitations.md) B-03.

## V-06 · Çevresel gerilme — iç yarıçap ve dış yarıçap formları

```
Girdi     P = 284.00 psi · Ro = 43.0000 in · Ri = 42.1250 in · S = 19700 psi · E = 0.85
Kaynak    PVE-S13 s.4, Appendix 1-1(a)(1):  t = P·Ro / (S·E + 0.4·P)  →  0.7244 in
Suite     UG-27(c)(1):                      t = P·Ri / (S·E − 0.6·P)  →  0.7218 in
Fark      −0.359 %
Karar     FORMÜLASYON_FARKI — V-04/V-05 ile aynı sebep
```

## V-07 · UG-99(b) hidrostatik + UG-100 pnömatik test basıncı 🔴

```
Girdi     MAWP = 218.80 psig · P_tasarım = 125 psig · Sa/S = 1.00
Kaynak    PVE-FT s.4:  hidro 1.3 × MAWP × Sa/S = 284.44 psig
                       pnöm. 1.1 × MAWP × Sa/S = 240.68 psig
Suite     (düzeltme öncesi)  1.3 × P_tasarım = 162.50 psig · 1.1 × P_tasarım = 137.50 psig
Fark      −42.9 %  — suite Kod'un istediğinden DÜŞÜK test basıncı üretiyordu
```

**Kök neden:** `design_code.py` her iki test hesabına da `dc.design_pressure` veriyordu.
UG-99(b) tabanı **MAWP**'dir; endnote tasarım basıncını yalnızca **MAWP hesaplanmadığında**
kabul eder. Bu suite MAWP'yi hesaplıyor (`orchestrator.get_global_mawp()`), dolayısıyla
muafiyet geçerli değil. MAWP ≥ P_tasarım olduğu için sapma **her zaman emniyetsiz yönde**.

İkinci vaka aynı hatayı büyüterek gösteriyor — PVE-FT s.24 gövdesi (MAWP 816.88, P_tasarım 15):
yayın 1061.94 psig, eski suite davranışı 19.50 psig (**−98.2 %**).

**Düzeltme (2026-07-26):**
- `formulas.hydrotest_pressure_asme` / `pneumatic_test_pressure`: ilk parametre
  `design_pressure` → `pressure_basis`; docstring tabanı MAWP olarak sabitliyor.
- `design_code.py`: `input_data["global_mawp"]` varsa taban MAWP; yoksa tasarım basıncına
  düşer **ve** K4 varsayımı + uyarısı kaydeder (endnote muafiyeti, sessiz değil).
- `orchestrator.py`: statik kafa düzeltmesi test hesaplarından **öne** alındı — taban nihai
  MAWP olsun diye; `global_mawp` her iki teste de geçiriliyor.

Düzeltme sonrası: suite 284.44 / 240.68 psig → yayınla **tam uyum**.

**Not:** Bu davranışı hiçbir mevcut test kapsamıyordu — 483 test düzeltmeden önce de sonra da
yeşildi. Regresyon testi `test_published_examples.py::test_v07_*` ile eklendi.

## V-08 / V-09 · MAWP geri hesabı

```
V-08  Girdi   Do = 14.000 in · t = 0.3281 in → Ri = 6.6719 in · S = 17100 psi · E = 1.00
      Kaynak  PVE-FT s.24  →  816.88 psig      Suite  816.82 psig      Fark −0.008 %
V-09  Girdi   Do = 72.000 in · t = 0.3900 in → Di = 71.220 in · S = 20000 psi · E = 1.00
      Kaynak  PVE-FT s.3   →  218.80 psig      Suite  218.80 psig      Fark −0.000 %
Karar DOĞRULANDI (iki vaka)
```

MAWP tarafında iç/dış çap formülasyonları cebirsel olarak neredeyse örtüşüyor — kalınlık
tarafındaki %0.4–0.9 fark burada görülmüyor.

---

---

# Tur 2 · 2026-07-26 — torisferik ve yarım küre

Tur 1'in iki açık maddesi (`UG-32(e)`, `UG-32(f)`) için kaynak arandı ve bulundu.

## Ek kaynaklar

| Kod | Kademe | Künye |
|---|---|---|
| **PVE-FD** | K-A | Pressure Vessel Engineering Ltd., *F&D Heads 2.02* anma tablosu, S = 16000 psi. `pveng.com/wp-content/uploads/2016/06/FDHeads202_16ksi.pdf` — erişim 2026-07-26 |
| **PVE-CMP** | K-A | Pressure Vessel Engineering Ltd., *Comparison Between Head Types: Hemi, SE, F&D and Flat*. `pveng.com/home/asme-code-design/comparison-between-head-types-hemi-se-fd-and-flat/` — erişim 2026-07-26 |

Değerlendirilip **kullanılmayan** kaynak: `cis-inspector.com` torisferik/yarım küre
sayfaları — interaktif hesaplayıcı, sabit yayınlanmış sayı içermiyor.

## Özet

| No | Madde | Kaynak | Yayın | Suite | Fark | Karar |
|---|---|---|---|---|---|---|
| V-10 | UG-32(f) yarım küre | PVE-CMP | 0.2474 in | 0.2473 in | −0.053% | ✅ DOĞRULANDI |
| V-11 | UG-32(e) torisferik MAWP | PVE-FD (90 nokta) | tablo | — | tipik %0.03-0.05, en büyük %0.29 | ✅ DOĞRULANDI |
| V-13 | UG-32(d) eliptik, **iç çap formu** | PVE-CMP | 0.4947 in | 0.4945 in | −0.033% | ✅ DOĞRULANDI |
| V-14 | UG-32(e) taç yarıçapı = dış çap | PVE-CMP | 0.8901 in | 0.8943 in (L=Do) | +0.469% | ⚠️ Varsayılan gözden geçirilmeli |
| V-12 | Varsayılan büküm yarıçapı | — | — | — | **%13** | 🔴 **SAPMA → düzeltildi** |

## V-11 · UG-32(e) torisferik — anma tablosunun tamamı

```
Geometri  ASME F&D: taç yarıçapı L = anma çapı, büküm yarıçapı r = 0.06 L
          → M = (3 + √(1/0.06)) / 4 = 1.770621
Kaynak    PVE-FD, S = 16000 psi, 5 çap (12/18/24/30…") × 18 kalınlık × E = 1.00 ve 0.85
Tarama    90 nokta karşılaştırıldı
Sonuç     tipik fark %0.03-0.05 · en büyük mutlak fark %0.29
```

**Tablodaki kalınlıklar yuvarlanmış kesirlerdir.** `0.063` aslında `1/16`, `0.313` aslında
`5/16`. Yazılı değerle karşılaştırıldığında en büyük fark %0.771'e çıkıyor; kesrin kendisi
kullanılınca %0.29'a düşüyor. Yani sapmanın kaynağı suite değil, tablonun basım hassasiyeti.

Testte çap/kalınlık/E boyunca yayılmış 14 temsilci nokta sabitlendi.

## V-10 · UG-32(f) yarım küre · V-13 · UG-32(d) iç çap formu

```
Ortak girdi  Do = 48 in · Di = 47 in · P = 420 psi · SA-516-70 · S = 20000 psi @100°F · E = 1.00
V-10  yarım küre  UG-32(f), R = 23.5 in   yayın 0.2474 in   suite 0.2473 in   −0.053 %
V-13  2:1 eliptik UG-32(d), D = 47 in     yayın 0.4947 in   suite 0.4945 in   −0.033 %
```

V-13 önemli: Tur 1'deki V-04/V-05 kaynakları **dış çap** alternatifini kullanıyordu, bu yüzden
`FORMÜLASYON_FARKI` olarak kaydedilmişti. PVE-CMP **iç çap** formunu kullanıyor — yani
UG-32(d) artık doğrudan, formülasyon belirsizliği olmadan doğrulanmış durumda.

## V-14 · Taç yarıçapı dış çaptır

```
Aynı kap için F&D bombe   yayın 0.8901 in
  L = Do = 48 in  →  suite 0.8943 in   +0.469 %   ✔ uyuyor
  L = Di = 47 in  →  suite 0.8756 in   −1.625 %   ✘ uymuyor
```

ASME F&D bombesinde taç yarıçapı **dış çapa** eşittir. Suite'in `L = D` (iç çap) varsayılanı
bu yüzden hafif emniyetsiz tarafta kalıyor — kayıt: [`limitations.md`](../limitations.md) B-06.
Bu turda değiştirilmedi: `Head` modelinde dış çap alanı yok, iç çaptan türetmek `nominal_thickness`
bağımlılığı getirir. Kullanıcı taç yarıçapını girdiğinde sorun yok; varsayılan durumda uyarı var.

## V-12 · Varsayılan büküm yarıçapı 🔴

```
Girdi     Di = 1000 mm, kullanıcı büküm yarıçapı GİRMEDİ
Eski      r = D/10 (%10)  →  M = 1.540569  →  t = 0.7619 in eşdeğeri
Doğru     r = 0.06 D (%6) →  M = 1.770621  →  t = 0.8756 in eşdeğeri
Fark      Eski varsayılan standart ASME F&D bombeye göre %13.0 DAHA İNCE
```

**Kök neden:** `design_code.py` iki yerde (kalınlık ve MAWP) `r = D/10` varsayıyordu.
Daha büyük büküm yarıçapı → daha küçük `M` → daha ince bombe. UG-32(e)'nin geometrik
asgarisi %6'dır ve standart ASME F&D bombesi tam olarak %6 bükümlüdür. Fiziksel bombe
%6 bükümlüyken %10 varsayarak hesaplamak **emniyetsiz taraftadır**.

Üstelik varsayım **sessizdi** — sonucu %13 değiştiren bir varsayım hiçbir yere kaydedilmiyordu
(K4 ihlali).

**Düzeltme (2026-07-26):** İki kopya `_torispherical_radii()` yardımcısında birleştirildi.
Varsayılan `r = 0.06 L` (standart ASME F&D). Varsayım kullanıldığında `add_assumption` +
`add_warning` yazılıyor. Ayrıca `r < 0.06 L` girilirse UG-32(e) asgarisi ihlali uyarısı
veriliyor — sessizce düzeltilmiyor (K4).

**Not:** Bu davranışı da hiçbir mevcut test kapsamıyordu; 495 test düzeltmeden önce de sonra
da yeşildi. Tur 1'deki UG-99(b) bulgusuyla aynı desen.

---

---

# Tur 3 · 2026-07-26 — UG-37/UG-40 nozul takviyesi

Kaynak: **PVE-FT s.5-6**, nozul "Neck". Tam alan dökümü yayınlanmış — bu yüzden tek vaka
beş ayrı ara değeri birden sınıyor.

```
Girdi   Ana bileşen : 2:1 eliptik bombe, Do = 72.000 in, t = 0.3900 in, CAS = 0
        Nozul       : ID 32.000 in, tn = 0.5000 in, CAN = 0, insert tipi
        Çıkıntılar  : dışa HO = 2.881 in, içe H = 0.8200 in
        Kaynak      : Wo = 0.5000 in, Wi = 0
        Malzeme     : gövde ve nozul SA-516 70, S = SN = 20000 psi → fr = 1.00
        P = 125 psig, ES = EN = 1.00, ped YOK
```

## V-15 · Sonuç

| Alan | PV Elite | Suite (önce) | Suite (sonra) | Not |
|---|---|---|---|---|
| Ar | 7.160 in² | 7.158 | 7.158 | ✅ zaten doğruydu |
| A1 | 5.320 in² | **0.213** | 5.322 | 🔴 **−%96** |
| A2 | 0.779 in² | 0.717 | 0.779 | 🔴 −%8 |
| A3 | 0.820 in² | **0.000** | 0.820 | 🔴 **−%100** |
| A4 | 0.250 in² | 0.125 | 0.250 | 🔴 −%50 |
| **Toplam** | **7.170 in²** | **1.055** | **7.171** | 🔴 **−%85** |
| **Karar** | **YETERLİ** | **YETERSİZ** | **YETERLİ** | 🔴 karar ters çıkıyordu |

UG-40 sınırları da doğrudan yayınlanmış ve artık birebir tutuyor:
`DL = 64.000 in` (etkin malzeme çap sınırı), `TLNP = 0.975 in` (pedsiz dik yön sınırı).

## Kök nedenler — beş ayrı hata

**1. UG-40 paralel sınırı yanlıştı (A1, −%96).** Kod, açıklık ekseninden itibaren
`max(d, Rn + tn + t)` kadar uzanır; toplam genişlik bunun iki katıdır. Suite
`d + 2t + tn` hesaplıyordu — yani `d`'nin üstüne yalnızca birkaç milimetre ekliyordu.
Bu vakada 64.000 in yerine 33.28 in kullanılmış oluyordu.

**2. Kesit iki yanı kapsar — 2 çarpanı eksikti (A2, A4).** Takviye alanları nozul
eksenine paralel bir **kesit düzleminde** hesaplanır ve açıklığın iki yanını birden
sayar. A2'de yükseklik bir kez, A4'te köşe kaynağı yarım üçgen olarak alınmıştı.

**3. İçe giren nozul hiç sayılmıyordu (A3).** Suite A3'ü **takviye pedi** için
kullanıyordu; içe çıkıntıyı A2'ye katıyor, üstelik **fazla kalınlıkla** (`tn − trn`)
çarpıyordu. Kod'a göre içeri giren boru tümüyle takviyedir: **tam kalınlık** (`tn`)
sayılır ve `min(h, 2.5t, 2.5tn)` ile sınırlanır.

**4. Alan adları Kod'la uyuşmuyordu (K5).** UG-37(c) sırası: A1 gövde fazlası,
A2 nozul dışa, A3 nozul içe, A4 kaynak, A5 ped. Suite A3'ü pede vermişti — raporu
Kod'la karşılaştıran bir denetçi yanlış kalemle eşleştirirdi.

**5. 🔴 Ped, UG-40 sınırıyla kırpılmıyordu — bu yön EMNİYETSİZ.** Ped alanı
`(pad_OD − d) × te` ile hesaplanıyordu; sınır kontrolü yoktu. Sınırı aşan geniş bir ped,
işe yaramayan kısmıyla birlikte takviye sayılıyordu. Diğer dört hata mevcut alanı
**eksik** gösterip fazladan ped taktırıyordu (pahalı ama güvenli); bu beşincisi ise
gerçekte yetersiz bir takviyeyi yeterli gösterebilirdi.

**Düzeltme (2026-07-26):** `calculate_reinforcement` UG-37(c)/UG-40'a göre yeniden yazıldı —
dayanım azaltma faktörleri (`fr1`, `fr2`, `fr4`) izin verilen gerilme oranından hesaplanıyor,
UG-40 sınırları (`L_par`, `L_norm`, `L_in`) ayrı ayrı çıkarılıp `dimension_limits` alanına
yazılıyor (K5), beş alan Kod'un kendi adlandırmasıyla üretiliyor, ped sınırı aşarsa kırpılıp
uyarı veriliyor (K4). Eğik nozul için F faktörü yok — uyarı düşülüyor.

---

## Hâlâ kapatılamayanlar

| Madde | Durum | Gerekli |
|---|---|---|
| UG-27 kalın cidar (`t > R/2`) | `KAYNAK_BEKLİYOR` | Kalın cidarlı yayınlanmış vaka; kaynakların tümü ince cidarlı |
| UG-37 eğik nozul `F` faktörü | Kapsam dışı | Suite yalnız radyal nozul takviyesi yapıyor (uyarı veriyor) |
| App 1-7 büyük açıklık kontrolü | Kapsam dışı | PVE-FT bu vakada App 1-7 de uygulamış; suite'te yok |
| UG-34(c)(3) `Z` faktörlü düz kapak | Kapsam dışı | Suite'te bu madde yok (limitations B-04) |
| App 1-1(a)(1) / 1-4(c) dış çap alternatifleri | Kapsam dışı | Suite'te yok (limitations B-03) |

## Üç turun özeti

| Tur | Vaka | Doğrulandı | Sapma |
|---|---|---|---|
| 1 | 9 | 4 (+3 formülasyon farkı) | UG-99(b)/UG-100 test basıncı tabanı |
| 2 | 4 | 3 | Torisferik varsayılan büküm yarıçapı |
| 3 | 1 (5 ara değer) | — | UG-37/40 takviye: beş ayrı hata |

**Üç sapmanın üçü de aynı desende:** formül doğru yazılmıştı, formülün *çevresi* yanlıştı —
yanlış taban, yanlış varsayılan geometri, yanlış sınır. Ve üçünü de mevcut testler
kapsamıyordu: her düzeltmeden önce ve sonra test sayısı değişmedi.
