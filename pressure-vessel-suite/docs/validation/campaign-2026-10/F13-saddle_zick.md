# F13 — Yatay kap saddle, Zick

## 1. Özet

32 girdi varyantı oluşturuldu; her biri için dört nicelik kaydı toplam 128 satırdır. Bu çalıştırmada API'den eşleşen `saddle_stress` sonucu alınamadı; dolayısıyla sayısal kıyas yapılamadı.

| Etiket | Satır |
|---|---:|
| DOĞRULANDI | 0 |
| FORMÜLASYON_FARKI | 0 |
| SAPMA | 0 |
| TEK_KAYNAK | 0 |
| KAYNAK_BEKLİYOR | 128 |
| KAPSAM_DIŞI | 0 |

Varyant matrisi L, A/R, kontak genişliği/açısı, halka girdisi ve geçersiz katsayı/açı durumlarını içerir. Boş/dolu yük durumu bağımsız olarak değiştirilmedi; bu nedenle yük ekseni kapsamı eksiktir.

## 2. Oracle denklemleri

Yerel `oracle.py` SI birimlerinde şu kapalı biçimleri uygular: S1_saddle = |M1|/(K1·R²·t); S1_mid = |M2|/(π·R²·t); S3 = K2·Q/[2t(b+1.56√(Rt))]; S4 = Q/[4t(b+1.56√(Rt))]+3K6Q/(2t²). K değerleri dışarıdan açık girdi olmalıdır; orakıl katsayı tablosu içermez.

Bu sadeleştirilmiş M1/M2 yük modeli saha dağıtılmış yük durumları için yalnız screening niteliğindedir ve yayımlanmış Zick vakasının tüm girdi koşullarını karşılamaz. Suite satırları bulunamadığından formül doğrulaması oluşmadı.

## 3. SAPMA tablosu

SAPMA yok. API sonucu eşleşmediğinden suite ve oracle sayısal değerleri yoktur; fark yüzdesi ve emniyetli/emniyetsiz yön tayin edilemez. `results.json` bu satırları KAYNAK_BEKLİYOR olarak işaretler.

## 4. Yayınlanmış vakalar

| Kaynak | Kullanım | Sonuç |
|---|---|---|
| K3-01, Pressure Vessel Engineering, PVE-4293, PV Elite 2012, PDF s.34–37 | Zick eyer; S1/S2/S3/S4 referansları dokümanda mevcut | Girdiler ve katsayı adlandırması, API proje değerleriyle birebir eşleşmediği için bu ailede kıyaslanmadı. Kaynakta K1–K7 eşlemesinin farklı raporlar arasında değişebileceği özellikle belirtiliyor. |

## 5. Kapsam dışı ve bloklanan vakalar

API'den `SHELL-01` ve `saddle_stress` eşleşmesi üretmeyen 32 vaka sonuçsuz kaldı; ayrı bir suite status taşınmadığından `judge` kaynak bekliyor etiketi verdi. İki ilave vaka eksik K1 ve 160° açı sınırını taşır; bunlar beklenen BLOCKED davranışını doğrulayacak bir API satırı üretmedi. Harness/API hata ayrıntısı sonuç nesnesine eklenmediği için blok nedenini bu çıktıdan belirlemek mümkün olmadı.

## 6. Temiz oda beyanı

Oracle sıfırdan ve bu aile klasöründe yazıldı. Yasaklı kod/standart implementasyonları açılmadı veya okunmadı; harness ve istenen domain modelleri dışında yalnız izin verilen K3 kaynak notu incelendi. Suite değerleri yalnız API katmanından talep edildi. `.project-ai/ORKESTRA.md` verilen proje kökünde bulunamadı; bu sözleşme belgesi ayrıca doğrulanamadı.
