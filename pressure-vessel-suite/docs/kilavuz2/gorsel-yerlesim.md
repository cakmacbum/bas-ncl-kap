# Kullanılmayan görseller: yerleşim önerisi

Kaynak: kilavuz2.html içinde geçmeyen 22 PNG. Hepsi tek tek açılıp incelendi.

| dosya | ne gösteriyor | karar | parça + bölüm | figcaption önerisi |
|---|---|---|---|---|
| 04-yeni-proje-sablon-vakum-tanki.png | Vakumlu Proses Tankı şablonu uygulanmış Adım 1 (şablon notları, dikey kap önizlemesi) | KULLAN (düşük öncelik, 03'ün eşi) | G1 `<h3>Başlangıç Şablonları</h3>` | Vakum şablonu uygulandığında çıkan "girmeniz gerekenler" notlarına (malzeme S değerleri, dış basınç UG-28) bakın. |
| 21-onizleme-olculu-kesit.png | Ölçülü Kesit sekmesi: 2B şema, ölçü çizgileri, seçili nozul turuncu/mavi vurgulu | KULLAN | G1 `<h3>Önizleme ve Görselleştirme</h3>` | Ölçülü Kesit sekmesinde z, t, Ø ve teğet boyu ölçülerine bakın; bir alana tıklayınca ilgili ölçü vurgulanır. |
| 22-onizleme-kesin-model.png | Kesin Model sekmesi: ayaklı dikey kabın gri/mavi 3D CAD modeli | KULLAN | G1 `<h3>Önizleme ve Görselleştirme</h3>` (21'in yanına) | Kesin Model sekmesi imalat geometrisini gösterir; seçili destek (ayaklar) mavi renkte görünür. |
| 30-girdiler-ayak-baglanti-kesit.png | Destek ayrıntıları, "Bağlantı ve Kesit" açık: kesit tipi, ayak sayısı 4, çap 114,3, et 8, K | KULLAN | G3 §3.4 Destek Ayrıntıları, `<dt>` Ayak Bağlantı Yeri / Ayak Kesit Tipi / Ayak Sayısı yanına | "Bağlantı ve Kesit" akordeonunda ayak kesit tipi, sayısı, çapı ve etkin boy faktörü K girilir. |
| 31-girdiler-ayak-takviye-pedi.png | "Takviye Pedi" açık: boy 250, en 180, kalınlık 12, temas oranı | KULLAN | G3 §3.4, `<dt>` Bağlantı Pedi Boyu/Eni/Kalınlığı, Ped Temas Oranı | Takviye Pedi akordeonunda ayağın kap cidarına bağlandığı pedin ölçüleri ve temas oranı girilir. |
| 32-girdiler-ayak-taban-plakasi.png | "Taban Plakası" açık: plaka ölçüleri, Fy, yataklık, ankraj alanları (tümü 0, boş form) | KULLAN (alanlar boş ama etiketler okunur; kırpılırsa daha iyi) | G3 §3.4, `<dt>` Taban Plakası Boyu / Ankraj Cıvatası Adedi yanına | Taban Plakası akordeonu: plaka, akma dayanımı, temel yataklık basıncı ve ankraj izinleri burada girilir. |
| 33-girdiler-ayak-kaynaklar.png | "Kaynaklar" açık: Ped-Gövde, Ayak-Ped, Ayak-Taban kaynak bacakları, Fexx, asgari bacak (hepsi 0) | KULLAN (aynı not) | G3 §3.4, `<dt>` Ped-Gövde Kaynak Bacağı / Elektrot Dayanımı Fexx | Kaynaklar akordeonunda üç köşe kaynak bacağı, Fexx ve asgari köşe kaynak bacağı girilir. |
| 34-girdiler-ayak-wrc.png | "WRC Katsayıları" açık: ML/MC β ve A-D noktaları x yük bileşeni tablosu (boş hücreler) | KULLAN | G3 §3.4, `<dt>` WRC Katsayıları / ML Eğrisi β | WRC Katsayıları tablosunda A-D noktaları için P, ML, MC, VL, VC satırlarına lisanslı bülten değerleri girilir; boş bırakılanlar 0 sayılır. |
| 40b-sonuc-kpi-ve-tablolar.png | Sonuç ekranı: KPI satırı + Ön Kontroller + Et Kalınlığı tablosu (KLV-201) | ATLA: 40 ve 41'in tekrarı | - | - |
| 42-sonuc-satir-acik.png | Sonuç satırı SHELL-01 açık: P, R, S, E, C, t_circ, t_required ara değerleri | KULLAN | G3 `<h2 id="g3-2">Adım 4 - Hesap Sonuçları</h2>` (ara değer / satır açma anlatımı) | Satırın solundaki oka tıklayınca ara değerler (P, R, S, E, C, gerekli kalınlık) açılır. |
| 44-3d-model-kesit.png | "Kesit" modu: model neredeyse görünmüyor, küçük bombe parçası, panel üst üste biniyor | ATLA: bozuk/okunaksız çekim | - | - |
| 46-rapor-html-1.png | HTML raporu 1. bölüm: kapak, proje bilgisi, standartlar, tasarım temeli, malzeme listesi | KULLAN | G3 `<h2 id="g3-4">Adım 6 - Rapor & Çıktı</h2>` (45'in altı) | Raporun ilk sayfası: kapak, proje ve revizyon bilgileri, tasarım temeli ve malzeme listesi. |
| 47-rapor-html-2.png | Rapor: gövde/bombe, nozul takviye alan analizi, MAWP, hidrotest tabloları | KULLAN (isteğe bağlı) | G3 §Adım 6 (46'dan sonra) | Raporda her hesap, madde referansı, gerekli/seçilen kalınlık ve PASS durumuyla tablo halinde verilir. |
| 48-rapor-html-3.png | Rapor: ağırlık-hacim, nozul schedule, kaynak haritası, isim plakası, sarı uyarı kutuları | KULLAN | G3 §Adım 6; ayrıca D2 `<h2 id="d2-6">Önemli uyarılar</h2>` olabilir | Rapor sonundaki 20. bölümde sarı kutular, mühendis incelemesi gerektiren uyarıları listeler. |
| 49-rapor-sayfa-tam-acinim.png | Adım 6 tam sayfa: gömülü rapor, Açınım şablonları (gövde halkası, bombe petalleri, nozul), DXF indir | KULLAN | G3 §Adım 6, `<dt>` Kaynak ağzı payı / Bombe petal sayısı / DXF indir | Açınım şablonlarında kaynak ağzı payı ve petal sayısını girip her parça için DXF indirin. |
| 52-yatay-girdiler-eyer-zick.png | Destek ayrıntıları, Eyer: sarma açısı, eyer düzleminde halka, Zick K1/K2/K3/K6/K7 (0, "BLOKLU" notları) | KULLAN | G3 §3.4, `<dt>` Sarma Açısı / Eyer Düzleminde Halka / Zick K1 | Eyer için Zick K katsayıları 0 ise hesap BLOKLU kalır; K1-K7 değerlerini tablodan girin. |
| 53-yatay-onizleme-3d.png | KLV-202 yatay kap 3D önizleme (eyerler mavi/kahve); 50'nin aynı ekranı | ATLA: 50 ile aynı görünüm, tekrar | - | - |
| 54-yatay-sonuc-ozet.png | Yatay tank Yayın Öncesi Doğrulama: kırmızı hash satırları "geçti" | ATLA: anlamsız hash listesi, kırmızı renk yanıltıcı | - | - |
| 55-yatay-sonuc-tam.png | Yatay tank tüm sonuçlar (1600x6648) | ATLA: 41'in tekrarı, sayfaya sığınca okunmuyor | - | - |
| 62-etek-girdiler-destek.png | Destek ayrıntıları, Etek: ortalama çap 1000, B 100, E, et 8, devirme momenti | KULLAN | G3 §3.4, `<dt>` Etek Ortalama Çapı / Etek İzin Verilen Basma B / Etek Kaynak Verimi E | Etek için ortalama çap, izin verilen basma B, kaynak verimi E ve et kalınlığı girilir. |
| 63-etek-girdiler-taban-halkasi.png | Koni birleşimi ve etek taban halkası: halka çapları, cıvata dairesi/adedi/çapı, beton f'c | KULLAN | G3 `<h3>3.9. Koni Birleşimi ... Etek Taban Halkası</h3>` (39'un yanına) | Etek kolonda taban halkası ölçüleri, cıvata bilgileri ve beton f'c bu akordeonda girilir. |
| 64-etek-sonuc-tam.png | Etek kolon tüm sonuçlar (1600x6236) | ATLA: 41'in tekrarı, okunaksız | - | - |

Toplam: 16 KULLAN, 6 ATLA (40b, 44, 53, 54, 55, 64).

## PDF sayfa bulguları (onizleme/g-sayfa-29/47/59/62.png)
- s29: sorun yok; gövde formu net okunuyor, altta yaklaşık %15 boşluk.
- s47: eyer formu net; kırmızı "zorunlu" hata alanları görünüyor (örnek veri boş), altta ~%20 boşluk. Tablo yok, taşma yok.
- s59: nozul ayrıntıları görseli çok uzun (480x~3400); sayfaya sığması için küçülmüş, yazılar OKUNAMIYOR. Sayfa üstü/altı boş, figcaption altta, tanım listesi sayfa sonunda başlıyor. Çözüm: görseli CSS ile max-height veya iki parçaya bölme.
- s62: aynı sorun (Flanşlar formu), yazılar okunamayacak kadar küçük. Kesik tablo yok, taşma yok.
- Genel: uzun dar form görselleri (59, 62 ve 32/33/34 gibi) PDF'de okunmuyor; kırpma gerekli.
