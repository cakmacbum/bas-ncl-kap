# V1 — Torisferik hamut: analitik (P03) vs FEA (P12) vs bağımsız kabuk çözümü

Tarih: 2026-10-31. Gösterge amaçlı doğrulama — ASME tasarım onayı değildir.

## Problem
D=1000 / t=10 / P=1 MPa torisferik bombede hamut tepe von Mises gerilmesi: P03 `stress/analyticField.ts` ≈715 MPa,
P12 FEA ≈237 MPa. Hangisi doğru?

## Geometri ve ortak varsayımlar
İç çap Di=1000 mm, taç iç yarıçapı L=1000 (Rc/D=1), hamut iç yarıçapı rk = 0,06/0,10/0,17·D, t=10 (t/D=0,01),
korozyon 0, P=1 MPa, ν=0,3 (E gerilmeyi etkilemez). Silindir tanjant boyu 3000 (yarı boy 1500, simetri düzlemi).
Değer: duvar yüzeyi en büyük von Mises (iç/dış yüzey, düzlem gerilme; FEA'da σr dahil, ihmal edilebilir).

## Referans A — yayımlanmış sonuç
**Kullanılmadı.** Aranan kaynaklar: Galletly (1959, "Torispherical shells — a caution to designers", ASME J. Eng.
Ind.), Reuss ("Elastic stresses in torispherical pressure vessel heads", Periodica Polytechnica Mech. Eng.),
Ranjan & Steele (1976, J. Eng. Mech. Div. ASCE). Bu geometri için sayısal değerin künyesi (tablo/şekil no ile)
doğrulanamadı: Reuss makalesi taranmış PDF (metin çıkarılamadı), diğerleri ücretli. Nitel bulgu (kaynak özetleri):
tepe gerilme hamutta, iç yüzeyde, meridyen eğilmesi kaynaklı çekme — referans B ile aynı (aşağıya bakınız).

## Referans B — eksenel simetrik ince kabuk (Reissner–Meissner/Love) sayısal çözümü
`tools/verification/torispherical_shell.py`: taç küre + hamut torus + silindir, orta yüzey (iç + t/2), sınırlarda
süreklilik; birinci mertebe sistem (u_r, u_z, χ, H, M_s), `scipy.integrate.solve_bvp` (tol 1e-6).
İç tutarlılık (`tests/unit/test_torispherical_reference.py`, 7 test): silindir uzak alanı P·R/t ve P·R/2t (1e-4),
küre membranı P·L/2t (1e-4), yarımküre–silindir Geckeler kesmesi Q0=p/(8β) (%0,02), sınır/tolerans duyarsızlığı
(<%0,1), tepe iç yüzeyde meridyen çekme, rk ve t ile tutarlı eğilimler.

## Karşılaştırma (hamut tepe von Mises, MPa)

| rk/D | B kabuk | FEA P12 | FEA−B | P03 eski (membran R1=rk) | P03 eski−B |
|-----:|--------:|--------:|------:|-------------------------:|-----------:|
| 0,06 | 227,4 | 236,7 | +4,1 % | 715,0 | +214 % |
| 0,10 | 173,5 | 177,9 | +2,5 % | 407,3 | +135 % |
| 0,17 | 112,2 | 114,2 | +1,8 % | 215,7 | +92 % |

Bölge ayrıntısı (B, MPa): taç (taç–hamut birleşimine yakın) en büyük 186,2 / 132,0 / 82,5 — eski P03 orada yalnız
P·L/2t ≈ 50 veriyordu (eğilme modelsiz, **güvensiz tarafta**). Silindir tarafı en büyük B 109,6 / 60,1 / 49,8;
P03 122,4 / 68,7 / 43,3 (%−13…+14) ve FEA 108,3 / 55,8 / 48,1 ile uyumlu → silindir tarafı korunur.
Kaynak test: `apps/web-ui/src/__tests__/feaKnuckleCompare.test.ts` (tabloyu yazdırır, FEA–B %15 içinde).

## Karar
FEA (P12) B ile ≤%4,1 tutarlı → **P03 hamut hesabı hatalı.** Neden: hamutta membran teorisi (R1=rk, R2≈L) çevresel
basmayı σθ = P·R2/t·(1 − R2/2rk) ile verir (rk=0,06D'de ≈ −730 MPa). Kısa, sığ hamutta bu membran durumu kurulamaz;
kabuk eğilerek yükü taç ve silindire dağıtır (B'de membran σθ en düşük −97 MPa, tepe iç yüzey meridyen eğilmesi).
Aynı nedenle taç tarafındaki birleşim eğilmesi de P03'te yoktu.

Düzeltme (kaynaklı kapalı form bulunmadığından yeni formül konmadı):
- `analyticField.ts`: torisferik hamut + taçta taç–hamut teğet noktasından 2,5·√(L·t) içi → `vm=hoop=axial=NaN`,
  `zone="unknown"` (düşük güven). `maxVm` yalnız güvenilir bölgelerden (skala sahte 715'ten kurtulur).
- `heatmap.tsx`: NaN noktalar gri; HUD değer yerine "—" ve "Düşük güven — FEA kullanın"; hamut uyarısı NaN noktada da.
- `knuckleNote.ts` (P13) uyarı metni doğrulama sonucuna göre güncellendi.

## Kalan belirsizlik
- Referans A (yayımlanmış sayı) yok; B ve FEA birbirinden bağımsız iki sayısal yöntem (ince kabuk ODE / 2B Q8 sürekli
  ortam), aynı geometri tanımını (iç yüzey yarıçapları) paylaşır.
- Yalnız t/D=0,01, Rc/D=1 denendi; kalın bombede (t/D≳0,05) ince kabuk teorisi zayıflar.
- Korozyonlu / farklı kalınlıklı hamut ve nozul-hamut etkileşimi doğrulanmadı.
