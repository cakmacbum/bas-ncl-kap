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

## Bu turda kapatılamayanlar

| No | Madde | Durum | Gerekli |
|---|---|---|---|
| — | UG-32(e) torisferik (`M` faktörü) | `KAYNAK_BEKLİYOR` | Torisferik bombeli yayınlanmış hesap seti |
| — | UG-32(f) yarım küre | `KAYNAK_BEKLİYOR` | Yarım küre bombeli yayınlanmış hesap seti |
| — | UG-27 kalın cidar (`t > R/2`) | `KAYNAK_BEKLİYOR` | Kalın cidarlı vaka; iki kaynak da ince cidarlı |
| — | UG-37/40 nozul takviyesi | Tur 2 | PVE-FT s.6'da tam veri var (Ar=7.160, A1=5.320, A2=0.779, A3=0.820, A4=0.250 in²) — bu tura alınmadı |

`M` faktörü ve yarım küre doğrulanmadan **torisferik ve yarım küre bombeli projeler
bağımsız teyit almamış sayılır**; `validation-plan.md` tablosunda `sembolik` kalır.
