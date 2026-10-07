# F12 â€” MDMT UCS-66

## 1. Ã–zet

Vaka/sonuÃ§ satÄ±rÄ±: 139. Etiket daÄŸÄ±lÄ±mÄ±: KAPSAM_DIŞI=3, KAYNAK_BEKLİYOR=136

## 2. Oracle formÃ¼lleri

UCS-66: gruba ve yÃ¶neten kalÄ±nlÄ±ÄŸa baÄŸlÄ± muafiyet sÄ±caklÄ±ÄŸÄ±; grafik deÄŸerleri K4 yayÄ±n Ã§Ä±ktÄ±larÄ±ndan alÄ±nmÄ±ÅŸtÄ±r. UCS-66.1: coincident ratio = trÂ·E*/(tg_srâˆ’c), sÄ±caklÄ±k azaltÄ±mÄ± Fig. UCS-66.1'den okunur. FigÃ¼r verisi bu kaynaklarda tam olmadÄ±ÄŸÄ± iÃ§in yeni deÄŸer tÃ¼retilmedi.

## 3. SAPMA tablosu

| case_id | girdiler | suite | oracle | fark % | yÃ¶n | olasÄ± neden |
|---|---|---:|---:|---:|---|---|
SAPMA yok.

## 4. YayÄ±nlanmÄ±ÅŸ vakalar

| Kaynak vakasÄ± | YayÄ±n MDMT | KullanÄ±m |
|---|---:|---|
| K4-09 | -48.333 Â°C | K4 sources-K4.md §B, K4-09 (PVEng/PV Elite, 2015); -55 °F |
| K4-10 | -31.111 Â°C | K4 sources-K4.md §B, K4-10 (PVEng/PV Elite, 2015); -24 °F |
| K4-13 | -98.889 Â°C | K4 sources-K4.md §B, K4-13; -146 °F |
| K4-16 | -19.444 Â°C | K4 sources-K4.md §B, K4-16; -3 °F |

## 5. Kapsam dÄ±ÅŸÄ± ve bloklanan vakalar

Curve ve impact girdisi eksik vakalar API BLOCKED dÃ¶ndÃ¼rÃ¼rse KAPSAM_DIÅI; sayÄ±sal yayÄ±mlanmÄ±ÅŸ eÅŸleÅŸmesi olmayan varyantlar KAYNAK_BEKLÄ°YOR olarak tutulur. Coincident ratio/PWHT girdilerinin MDMT hesabÄ±nda etkili olduÄŸu API Ã§Ä±ktÄ±sÄ±ndan teyit edilmelidir.

## 6. Temiz oda beyanÄ±

Oracle baÄŸÄ±msÄ±z kuruldu; yasaklÄ± uygulama paketleri aÃ§Ä±lmadÄ±. UCS-66.1 grafik noktalarÄ± uydurulmadÄ±; API sonucu yalnÄ±zca harness Ã¼zerinden alÄ±ndÄ±.
