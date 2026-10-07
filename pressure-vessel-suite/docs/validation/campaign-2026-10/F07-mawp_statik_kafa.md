# F07 — Global MAWP ve statik sıvı kafası

## 1. Özet

30 vaka çalıştırıldı. Etiket dağılımı: DOĞRULANDI 4, FORMÜLASYON_FARKI 0, SAPMA 24, TEK_KAYNAK 1, KAYNAK_BEKLİYOR 0, KAPSAM_DIŞI 1. Geçersiz malzeme vakası API'de NOT CALCULATED oldu ve `judge` tarafından KAPSAM_DIŞI sayıldı. REVIEW REQUIRED gelen satırlar sayısal kıyasa dahil edildi.

## 2. Oracle formülleri

- UG-27(c)(1), silindir iç çap formu: `P = S·E·t / (R + 0.6t)`. Bu varyantta kaynak verilerindeki `E=1`; etkin et, nominal et × (1 − hadde toleransı) − korozyon payı olarak kuruldu.
- UG-32(d), 2:1 eliptik bombe: `P = 2·S·E·t / (D + 0.2t)`; aynı etkin et yaklaşımı kullanıldı.
- UG-98 / UG-22 statik kafa kontrolü: `ΔP = ρ·g·h`; bileşen yerel basıncı referans datum basıncına bu terim eklenerek, bileşen global basınç kapasitesi ise statik kafa düşülerek bulunur. `g=9.80665 m/s²`.
- K1-01 yayınlanmış değer bağımsız kaynak doğrulaması olarak 308.73 psi = 2.128 MPa alındı. Mevcut aile fixture'ı bu kaynağın tam geometrisi olmadığından, bu satır tek kaynak etiketi taşır.

## 3. SAPMA tablosu

| case_id | Girdiler | Suite (MPa) | Oracle (MPa) | Fark | Yön | Olası neden |
|---|---|---:|---:|---:|---|---|
| V-P1…V-P5, V-RHO1…V-RHO6, H-RHO1…H-RHO4 | Tasarım basıncı 0.8–2.0 MPa veya sıvı yoğunluğu 0–1800 kg/m³; temel tank | 1.7098 | 2.0216 | −%15.42 | Emniyetli (suite daha düşük) | Tahmin: suite temel tankta HEAD-R için etkin et/izin verilen gerilme etkisini oracle'ın basit 2:1 kabulünden daha muhafazakâr alıyor; yoğunluk değişiminin global çıktıyı değiştirmemesi ayrıca kafa datumunun API girdilerinde tanımlanmadığına işaret ediyor. |
| V-T2…V-T5, V-H1…V-H3, H-T1…H-T4 | Bileşen nominal etleri 6–18 mm aralığında; temel tank | Sonuçlar `results.json` içinde | Bağımsız UG-27/UG-32 | Sonuç bazında | Suite/oracle yönü `diff_pct` işaretinden okunur | Tahmin: model kapsamı ve bileşen et hesabında hadde toleransı, şekillendirme incelmesi veya başlık geometrisi kabulleri farklı. Sayısal değerler ve governing bileşen her case kaydında tutuldu. |

Her satırın tam suite/oracle değeri, fark yüzdesi, statüsü ve yöneten bileşeni `tools/campaign/families/f07_mawp_statik_kafa/results.json` içindedir. Negatif fark suite'in daha düşük kapasite verdiğini (emniyetli yönde), pozitif fark daha yüksek kapasite verdiğini (emniyetsiz yönde) gösterir.

## 4. Yayınlanmış vakalar

| case_id | Kaynak | Yayınlanan sonuç | Suite | Fark | Etiket |
|---|---|---:|---:|---:|---|
| PUB-CW-K1-01 | Codeware, COMPRESS Demo Vessel, 2022, ASME VIII-1 2021, s.18–19; `sources-K1.md` K1-01 | Silindir MAWP 308.73 psi = 2.128 MPa; Ps=0.87 psi | 2.1346 MPa | +%0.31 | TEK_KAYNAK |

Atıf: [Codeware COMPRESS Demo Vessel](https://www.codeware.com/prospects/progressive-recovery/Demo-Vessel-Report.pdf). Kaynak girdileri K1-01 kaydından alınmıştır; referans tek yayınlanmış sayısal vaka olduğundan doğrulanmış kabul edilmemiştir.

## 5. Kapsam dışı ve bloklanan vakalar

| case_id | Sonuç | Neden |
|---|---|---|
| INVALID-NO-MATERIAL | KAPSAM_DIŞI | Malzeme kaydı kaldırılınca API satırları NOT CALCULATED; referans sayı üretilemez. |

Bu API modelinde statik sıvı seviyesi/yükseklik koordinatı için ayrı bir girdi bulunmadı. Yoğunluk varyantları koştu, ancak suite global MAWP'yi değiştirmedi; bileşen başına `ρgh` karşılaştırması bu nedenle mevcut girdilerle izole edilemedi. Bu, sonuçların kapsamını sınırlar.

## 6. Temiz oda beyanı

Oracle UG-27(c)(1), UG-32(d) ve `ρgh` denklemlerinden sıfırdan yazıldı. Yasaklı paketler okunmadı. Suite sonucu yalnızca harness'in FastAPI API çıktısından alındı. Harness'e ve kapsam dışındaki dosyalara yazılmadı.
