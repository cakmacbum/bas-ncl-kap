# F20 — Her şey dahil uçtan uca tanklar

## 1. Özet

30 vaka `results.json` içinde üretilir. Etiket dağılımı: DOĞRULANDI 3, FORMÜLASYON_FARKI 6, SAPMA 10, TEK_KAYNAK 7, KAYNAK_BEKLİYOR 3, KAPSAM_DIŞI 1. Sınıflandırma geometrik hacim oracle'ı ile API hacim değerini karşılaştırır. Hatalı API vakası KAPSAM_DIŞI etiketlenir.

## 2. Oracle formülleri

1. Silindir: `V = π (Di/2)² L`, mm³ → m³ dönüşümü `10⁹` ile.
2. Yarımküre: `V = 2πr³/3`.
3. 2:1 elipsoid bombe: `V = 4πr²(r/2)/3 = 2πr³/3`.
4. Düz kapak hacmi sıfır varsayılır; torisferik özel profil, kesin profil integrali olmadan oracle dışıdır.
5. İç basınç bağlam kontrolü için ince cidar bağıntısı: `t = PR/(SE − 0.6P)`; suite kalınlık/MAWP çıktısı API'den alınır, bu ilişki bağımsız bir tam kod oracle'ı değildir.
6. Metal kütlesi karşılaştırması yapılmaz; bileşen geometrisi ve şekillendirme etkileri tüm temellerde aynı kapsamda belirlenemedi.

## 3. SAPMA tablosu

Her vaka için suite hacmi, bağımsız hacim değeri ve fark `results.json` içindedir. Emniyetsiz/emniyetli yön, bu kampanyada hacim büyüklüğü tasarım emniyetini temsil etmediğinden uygulanamaz. Varyantlar basınç, bombe, nozul ve dayanak seçimlerini tarar; sapma etiketi ve sayısal farklar üretilen JSON'a bırakılmıştır.

## 4. Yayınlanmış vakalar

K1–K4 kaynak dosyaları gözden geçirildi. Bu geniş özellik ailesiyle doğrudan eşleşen ve girdileri tam olarak yeniden kurulabilen yayınlanmış basınçlı tank bütüncül hacim vakası belirlenemedi. Bu nedenle yayınlanmış sonuç uydurulmadı; K1/K4 worked-example basınç kalınlığı satırları proje geometrisi/malzeme girdileri eşleşmediğinden karşılaştırmaya alınmadı.

## 5. Kapsam dışı ve bloklanan vakalar

Negatif tasarım basıncı Pydantic/API tarafından reddedilirse vaka `KAPSAM_DIŞI` olur. Harici basınç ve vakum varyantlarında UG-28 çizelge faktörleri temel veride bulunmadığından bloklanma beklenir. Saddle Zick K katsayıları baz projede verilmediği için destek sonuçları kapsam dışında veya inceleme gerektirir. Torisferik ve üç nozul hacim değerleri fitting katkılarını kapsamaz; yorum notuyla değerlendirilmelidir. HTML rapor/STEP üretimi ölçümü bu koşuda yapılmadı.

## 6. Temiz oda beyanı

Yasaklı hesap paketleri okunmadı. Harness, domain şemaları, API servis sarmalayıcısı ve izinli doğrulama kaynakları kullanıldı. Kaynak uygulamanın hesap motoru koduna bakılmadı; suite değerleri yalnız API sonucundan alınır.
