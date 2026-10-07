# F09b ? Nozul takviyesi katalog k?yas?

## Sonu?

Toplam 32 vaka: 0 DO?RULANDI, 0 FORM?LASYON_FARKI, 30 SAPMA, 0 KAPSAM_DI?I. 30 vaka say?sal k?yasland?; hedef 20 a??ld?.

Katalog s?zle?mesiyle `nozzle_reinforcement` sat?r? ve `A_required` ara de?eri kullan?ld?. Varyantlar `example_nozzle_reinforcement()` tabanl?d?r. Oracle, UG-37(c) gerekli alan?n? ba??ms?z bas?n?/izin verilebilir gerilme ba??nt?s?yla hesaplar.

## SAPMA tablosu

K?yas y?n?: fark y?zdesi = (suite ? oracle) / oracle. Gerekli alan?n suite de?eri daha y?ksek oldu?unda sonu? emniyetli y?nde muhafazak?rd?r. T?m k?yaslanabilir vakalarda SAPMA emniyetli y?ndedir; farklar %1,278?%2,158 aral???ndad?r.

| Vaka(lar) | Fark (%) | Y?n |
|---|---:|---|
| ratio-0.05-pad-0 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.05-pad-1 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.1-pad-0 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.1-pad-1 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.2-pad-0 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.2-pad-1 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.35-pad-0 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.35-pad-1 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.5-pad-0 | 1.278 | emniyetli (suite alan? y?ksek) |
| ratio-0.5-pad-1 | 1.278 | emniyetli (suite alan? y?ksek) |
| type-flanged | 1.278 | emniyetli (suite alan? y?ksek) |
| type-slip_on | 1.278 | emniyetli (suite alan? y?ksek) |
| type-manway | 1.278 | emniyetli (suite alan? y?ksek) |
| eff-0.7 | 1.278 | emniyetli (suite alan? y?ksek) |
| eff-0.85 | 1.278 | emniyetli (suite alan? y?ksek) |
| eff-1.0 | 1.278 | emniyetli (suite alan? y?ksek) |
| neck-4 | 1.278 | emniyetli (suite alan? y?ksek) |
| neck-8 | 1.278 | emniyetli (suite alan? y?ksek) |
| neck-15 | 1.278 | emniyetli (suite alan? y?ksek) |
| pad-od-100 | 1.278 | emniyetli (suite alan? y?ksek) |
| pad-od-250 | 1.278 | emniyetli (suite alan? y?ksek) |
| pad-od-600 | 1.278 | emniyetli (suite alan? y?ksek) |
| PUB-K2-02-PVE-S5 | 2.158 | emniyetli (suite alan? y?ksek) |
| PUB-K2-17-IJERT | 1.278 | emniyetli (suite alan? y?ksek) |
| proj-0 | 1.278 | emniyetli (suite alan? y?ksek) |
| proj-10 | 1.278 | emniyetli (suite alan? y?ksek) |
| proj-100 | 1.278 | emniyetli (suite alan? y?ksek) |
| proj-250 | 1.278 | emniyetli (suite alan? y?ksek) |
| proj-500 | 1.278 | emniyetli (suite alan? y?ksek) |
| proj-1000 | 1.278 | emniyetli (suite alan? y?ksek) |

## Kapsam d??? vakalar

`type-socket_weld` ve `type-threaded` i?in API hedef hesap sat?r? ?retmedi; katalog s?zle?mesine g?re say?sal k?yas yap?lamad?. Di?er 30 varyantta durum PASS ve ara de?er mevcut.

## Yay?nlanm?? vakalar

`PUB-K2-02-PVE-S5` ve `PUB-K2-17-IJERT` API ?zerinden ?al??t?r?ld? ve say?sal k?yasland?. Kaynak girdileri `sources-K2.md` K2-02 ve K2-17 kay?tlar?d?r. Her ikisi de oracle fark? nedeniyle SAPMA s?n?f?nda, emniyetli y?ndedir.

## Temiz oda beyan?

Oracle ba??nt?s? UG-37(c) / UG-40 geometrik s?n?rlar? temel al?narak ba??ms?z yaz?ld?. Yasakl? hesap implementasyonlar? okunmad?; yaln?z g?revde izin verilen sonu? katalo?u, ?rnekler, harness ve API ??kt?lar? kullan?ld?.
