# T62 özeti — karar dosyaları

Kaynak başına bir satır; v2 bulunan kaynaklarda karar kaynağı v2 dosyasıdır. Birimler vaka/satır düzeyindedir ve farklı birimler birleştirilmez.

| kaynak | birim | GEÇERLİ_OLUMLU | GEÇERLİ_BULGU | İNCELEME | KAPSAM_DIŞI |
|---|---|---:|---:|---:|---:|
| tools/campaign/tur2/t01_metamorfik/results_v2.json (`cases[].result/status`) | vaka | 120 | 0 | 0 | 120 |
| tools/campaign/tur2/t02_birim_tutarlilik/results.json (`vakalar[].durum`) | vaka | 11 | 10 | 0 | 0 |
| tools/campaign/tur2/t04_fuzz/results_v2.json (`vakalar[].sonuc`) | vaka | 300 | 0 | 0 | 0 |
| tools/campaign/tur2/t11_yatay_tank_tarama/results_v2.json (`durum_v2`) | vaka | 0 | 27 | 36 | 81 |
| tools/campaign/tur3/mega_destek/results_v2.json (`durum_v2`) | vaka | 110 | 0 | 0 | 0 |
| tools/campaign/tur3/mega_govde/results_v2.json (`durum_v2`) | vaka | 110 | 0 | 0 | 0 |
| tools/campaign/tur3/mega_nozul/results_v2.json (`durum_v2`) | vaka | 110 | 0 | 0 | 0 |
| tools/campaign/tur3/mega_yuk/results_v2.json (`durum_v2`) | vaka | 110 | 0 | 0 | 0 |
| tools/campaign/tur5/bombe_tarama/results.json (`durum`) | vaka | 300 | 0 | 0 | 0 |
| tools/campaign/tur5/mass_govde_20261017.csv (`verdict`) | satır | 359 | 641 | 0 | 0 |

## T02 karar alanı kanıtı

`durum` karar alanı olarak kullanıldı. İki örnek: `BASE`: `durum=PASS`, `sonuc=GEÇTİ`; `IMPERIAL-01`: `durum=FAIL`, `sonuc=BULGU`. Bu örnekler alanların burada aynı kararı ifade ettiğini gösterir; tabloda karar alanı sözleşmesine uygun olarak `durum` sayıldı.

## Çelişkiler

Kanıtlanmış çelişki yok (0). Bu kaynak kümesinde iki karar dosyasının aynı vaka kümesi için farklı karar verdiğini gösteren vaka eşlemesi sunulmadı. Eski/v2 dosyaları çelişki karşılaştırması olarak kullanılmadı; eski/v2 çifti bulunan T01, T04, T11 ve Mega kaynaklarında karar kaynağı v2 dosyasıdır.

SONUÇ: kaynak=10 · çelişki_kanıtlı=0
