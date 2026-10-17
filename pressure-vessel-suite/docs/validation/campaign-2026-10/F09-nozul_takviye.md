# F09 — Nozul takviyesi katalog kıyası

## Sonuç

Toplam 32 vaka: 28 DOĞRULANDI, 2 SAPMA, 0 FORMÜLASYON_FARKI, 2 KAPSAM_DIŞI. 30 vaka sayısal kıyaslandı; hedef 20 aşıldı.

Katalog sözleşmesine göre `nozzle_reinforcement` satırındaki `A_required` alanı kıyaslandı. Harness çalışması hatasız tamamlandı. İki kapsam dışı vaka `type-socket_weld` ve `type-threaded`; hedef hesap satırı oluşmadı.

## Tur 2 düzeltmesi

Önceki dağılım: 0 DOĞRULANDI, 0 FORMÜLASYON_FARKI, 30 SAPMA, 2 KAPSAM_DIŞI. Oracle gövde gerekli kalınlığını UG-27(c)(1) yerine yanlış basınç/kalınlık bağıntısıyla buluyordu. Oracle, korozyonlu iç yarıçapı `R = D_i/2 + CA` alarak `t_r = P·R/(S·E − 0.6P)` biçiminde düzeltildi; run girdisinden CA ve malzeme için varsa kaynak verimi geçiriliyor. Yeni dağılım: 28 DOĞRULANDI, 2 SAPMA, 0 FORMÜLASYON_FARKI, 2 KAPSAM_DIŞI.

## Kalan SAPMA'lar

Kıyas farkı `(suite − oracle) / oracle`; alanın büyük olması muhafazakâr yöndedir.

| Vaka | Girdi | Suite A_required (mm²) | Oracle (mm²) | Fark | Muhtemel neden / yön |
|---|---|---:|---:|---:|---|
| eff-0.7 | M1 `weld_joint_efficiency=0.7`; temel gövde D_i=1000 mm, CA=2 mm, P=1.2 MPa | 230.376 | 329.850 | −30.157% | Suite alanı E=0.7'ye göre değişmiyor; verim girdisinin hesaba katılmaması olası. Suite daha düşük alan veriyor: emniyetsiz yön. |
| eff-0.85 | M1 `weld_joint_efficiency=0.85`; temel gövde D_i=1000 mm, CA=2 mm, P=1.2 MPa | 230.376 | 271.282 | −15.079% | Suite alanı E=0.85'e göre değişmiyor; verim girdisinin hesaba katılmaması olası. Suite daha düşük alan veriyor: emniyetsiz yön. |

## Temiz oda

Oracle UG-27(c)(1) bağıntısı ve UG-37(c) gerekli alan tanımıyla bağımsız kuruldu. Suite hesap uygulaması okunmadı; yalnız sonuç kataloğu, izin verilen fixture/örnekler, harness ve API çıktısı kullanıldı.

SONUÇ: DOĞRULANDI=28 · SAPMA=2 · FORMÜLASYON_FARKI=0 · KAPSAM_DIŞI=2
