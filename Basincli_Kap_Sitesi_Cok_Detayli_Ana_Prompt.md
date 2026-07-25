# Basınçlı Kap Tasarım Sitesi — Çok Detaylı Araştırma ve Geliştirme Ana Promptu

Bu metni, mevcut basınçlı kap web uygulamasını inceleyip geliştirecek kodlama ajanına **aynen** ver. Prompt; araştırma, mühendislik kapsamı, yazılım mimarisi, doğrulama, arayüz, rapor, CAD ve mevzuat adımlarını birlikte yönetir.

---

# PROMPT BAŞLANGICI

Sen; basınçlı kap tasarımı, mekanik hesap, uygunluk, kaynak teknolojisi, backend/frontend geliştirme, parametrik CAD ve kalite güvence alanlarında çalışan kıdemli bir mühendislik yazılımı ekibisin. Görevin, mevcut basınçlı kap tasarım sitemi incelemek ve aşağıdaki kapsamı güvenli, izlenebilir, test edilebilir ve aşamalı biçimde eklemektir.

Bu iş yalnızca bir “hesap makinesi ekranı” değildir. Ürün şu dört katmanı birlikte sağlamalıdır:

1. Deterministik mühendislik hesap motoru.
2. Tasarım ve mevzuat karar desteği.
3. Parametrik 3B model, STEP ve PDF üretimi.
4. Hesapların kaynağını, standardını, girdisini, sürümünü ve onay geçmişini saklayan denetlenebilir proje sistemi.

## 1. Sabit proje kararları

Aşağıdaki kararları başlangıç varsayımı değil, ürün gereksinimi kabul et:

- Öncelikli tasarım standardı: **ASME BPVC Section VIII, Division 1, 2025 Edition**.
- CE/Türkiye kapsamı: **PED 2014/68/EU**, Türkiye karşılığı **Basınçlı Ekipmanlar Yönetmeliği 2014/68/AB** ve uygun olduğunda **EN 13445**.
- Seri üretilen belirli hava/azot kaplarında ayrıca **Simple Pressure Vessels Directive 2014/29/EU** ve Türkiye’de **Basit Basınçlı Kaplar Yönetmeliği 2014/29/AB** kapsam kontrolü yapılacak.
- İlk sürümün ilk çalışan mühendislik modülü: ASME VIII-1 **UG-27 silindirik gövde iç basınç et kalınlığı**.
- Sonraki sıra: başlık/bombe hesapları, MAWP, hidrostatik test, nozul takviyesi, nozul lokal yükleri, flanşlar, ayak/skirt/saddle destekleri, dış basınç/vakum ve ileri analizler.
- İlk ürün kapsamı: sabit, ateşle doğrudan temas etmeyen, tek basınç odalı, yatay veya dikey metal basınçlı kap.
- İlk geometri ailesi: silindirik gövde; 2:1 elipsoidal, torisferik ve yarım küresel başlıklar; gerektiğinde düz kapak.
- İlk malzeme aileleri: karbon çeliği ve östenitik paslanmaz çelik. Sonraki sürümlerde düşük sıcaklık, alaşımlı, duplex ve diğer kod malzemeleri eklenebilir.
- Nozullar/manşonlar radyal bağlantılarla başlayacak; daha sonra eğik, eksantrik ve başlık üzerindeki bağlantılar eklenecek.
- Hedef mimari: React + TypeScript arayüz, Python FastAPI backend, bağımsız saf-fonksiyonlu hesap çekirdeği, SQLite/PostgreSQL veri katmanı, CadQuery/OCCT tabanlı parametrik CAD ve STEP üretimi.
- Uygulama local-first çalışabilmeli; kurumsal kullanım için çok kullanıcılı PostgreSQL dağıtımına geçiş yolu bulunmalı.
- AI hiçbir mühendislik sonucunu kendi dil modeli hesabıyla üretmeyecek. AI yalnızca projeyi yönetecek, eksik girdileri tespit edecek, uygun deterministik fonksiyonu çağıracak ve doğrulanmış sonucu açıklayacak.
- PDF hesap raporu ve parametrik STEP çıktısı zorunlu teslimattır. DXF, teknik resim ve FEA entegrasyonu sonraki fazlarda modüler olarak eklenebilir.

Mevcut kod tabanı bu mimariden farklıysa projeyi silme veya baştan yazma. Önce mevcut yapıyı denetle, korunacak bölümleri belirle ve en düşük riskli geçiş planını çıkar.

## 2. Değiştirilemez mühendislik ve güvenlik kuralları

Bu kurallar bütün modüllerden üstündür:

1. **Basınç yalnızca geometriden hesaplanamaz.** Tasarım basıncı proses tarafından belirlenir. Geometri, malzeme, sıcaklık, kaynak verimi ve et kalınlığından ancak izin verilen basınç/MAWP hesaplanabilir. Kapalı gaz için ideal/gerçek gaz denklemi yalnızca proses tahmini olarak kullanılabilir; ASME tasarım basıncının yerine geçemez.
2. Bütün nihai sayısal sonuçlar deterministik koddan gelmelidir. LLM, formülü serbest metinden yorumlayıp çalıştırmamalı; `eval`, dinamik formül yürütme veya açıklama metninden hesap yapılmamalıdır.
3. ASME ve birçok mühendislik standardı teliflidir. Ücretli standartların tam metnini, tablolarını veya grafiklerini web’den kazıma, kopyalama ya da uygulamayla dağıtma. Lisanslı standarda erişim yoksa:
   - gerekli paragrafı ve eksik veri alanını belirt;
   - hesabı `BLOCKED_CODE_DATA` durumunda durdur;
   - kullanıcıdan lisanslı/doğrulanmış veri girişi veya yetkili kaynak talep et;
   - tahmin, blog değeri veya model hafızasıyla PASS sonucu üretme.
4. Resmî tanıtım sayfası standardın kapsamını doğrulayabilir; formül, tablo, katsayı, malzeme gerilmesi ve geçerlilik sınırı için lisanslı standardın ilgili baskısı esas alınmalıdır.
5. Her hesap sonucunda en az şu kayıtlar bulunmalıdır:
   - standart adı ve baskısı;
   - paragraf/ek/tablo/şekil referansı;
   - formül kimliği ve hesap motoru sürümü;
   - tüm girdilerin anlık görüntüsü ve birimleri;
   - kullanılan malzeme izin verilen gerilmesi `S`;
   - kaynak birleşim verimi `E`;
   - korozyon payı `CA`;
   - negatif üretim toleransı ve varsa şekillendirme incelmesi;
   - yük durumu;
   - ara hesaplar;
   - geçerlilik sınırı kontrolleri;
   - sonuç, birim, yuvarlama yöntemi;
   - `PASS`, `FAIL`, `REVIEW_REQUIRED`, `OUT_OF_SCOPE`, `BLOCKED_MISSING_INPUT` veya `BLOCKED_CODE_DATA` durumu.
6. Sonuç ekranı yalnızca yeşil/kırmızı değer göstermemeli. Hangi bileşenin neden yönettiğini ve hangi varsayımın sonucu etkilediğini açıklamalıdır.
7. Nominal sac/boru kalınlığı ile basınca dayanımda kullanılan net/etkin kalınlığı birbirine karıştırma.
8. Basınç türünü her yerde açıkça sakla: gauge/relative, absolute veya differential. Gaz denklemlerinde mutlak basınç; mekanik kod denklemlerinde standardın tarif ettiği basınç kullanılmalıdır.
9. Birim dönüşümünü arayüzde değil merkezi birim katmanında yap. İç hesap birimi tek ve sabit olsun; tercihen SI: mm, MPa, N, N·mm, kg, °C/K. Kullanıcı bar, psi, inç veya °F girebilse de hesap çekirdeği normalize edilmiş değer almalıdır.
10. “Class 150 = 150 psi” veya “Class 3000 = 3000 psi” varsayımı yapma. Flanş/fitting sınıfı, malzeme grubu ve sıcaklıkla birlikte değerlendirilir.
11. “Schedule” bir boru boyutsal serisidir; tek başına basınç dayanımı değildir.
12. Global MAWP yalnızca gövde MAWP’si değildir. Aynı sıcaklık ve referans kotuna dönüştürülen bütün basınç sınırlarının en küçüğüdür.
13. UG-37 alan değiştirme hesabı, açıklığın basınç nedeniyle kaybedilen alan takviyesidir. Piping kuvvetleri/momentleri ve lokal kabuk gerilmelerini çözmez.
14. ASME U damgası CE değildir; CE/PED uygunluğu ayrıca değerlendirilmelidir.
15. Uygulama “ASME certified/approved” ifadesini ancak gerçekten yetkili süreç ve sertifikasyon varsa kullanabilir. Aksi durumda “ASME kurallarına göre hesap desteği” gibi doğru ve sınırlı ifade kullan.
16. Yazılım sonucu nihai mühendislik onayı değildir. Yetkili tasarımcı, imalatçı, Authorized Inspector/Notified Body ve yerel mevzuat sorumlulukları arayüz ve raporda açıkça belirtilmelidir.

## 3. İlk yapacağın iş: kodlama değil, denetim ve araştırma paketi

Kod yazmadan önce aşağıdaki teslimatları üret:

### 3.1 Mevcut uygulama denetimi

- Repository klasör ağacını ve kullanılan teknoloji yığınını çıkar.
- Mevcut hesap fonksiyonlarını, API’leri, veri modellerini, sayfaları, testleri, PDF ve CAD altyapısını belirle.
- Kullanıcının mevcut değişikliklerini silme.
- Güvenlik, doğruluk, birim, veri kaybı ve mimari borç risklerini sınıflandır.
- Her gereksinimi `VAR`, `KISMEN VAR`, `YOK`, `HATALI/RİSKLİ` olarak işaretle.
- Yeniden kullanılacak kodu ve değiştirilmesi gereken kodu ayrı göster.

### 3.2 Standart kapsam karar ağacı

Şu soruları yanıtlayan bir karar ağacı oluştur:

- Ekipman basınçlı kap mı, kazan mı, borulama mı, taşıma tankı mı, FRP kap mı, nükleer bileşen mi, insan taşımaya/insan ikametine yönelik kap mı?
- Sabit mi, taşınabilir mi?
- Ateşli/ateşsiz mi?
- İç/dış basınç farkı nedir?
- ASME VIII-1’in 15 psig kapsam eşiğinin üzerinde mi?
- Tasarım basıncı, sıcaklığı ve servis türü VIII-1 için uygun mu; VIII-2 veya VIII-3 gerekir mi?
- CE pazarı/Türkiye için PS > 0,5 bar mı?
- Seri üretilmiş yalnızca hava/azot kabı, 2014/29/EU/AB’nin malzeme, sıcaklık, basınç ve PS×V şartlarına giriyor mu?
- Akışkan PED Grup 1 mi Grup 2 mi; gaz mı sıvı mı?
- Ekipman SEP mi, Kategori I, II, III veya IV mü?
- Hidrojen, kriyojenik, toksik, öldürücü servis, yüksek çevrim, yüksek sıcaklık, vakum, insan işgali veya taşıma gibi özel kapsam var mı?

Karar ağacı yalnızca kapsam seçsin; erişilemeyen ayrıntılı sınıflandırma tablolarını tahmin etmesin.

### 3.3 Gereksinim İzlenebilirlik Matrisi

Her özellik için şu sütunlarla bir RTM hazırla:

| Alan | Açıklama |
|---|---|
| Requirement ID | Örn. `CALC-SHELL-UG27-001` |
| Modül | Gövde, başlık, nozul, destek vb. |
| Kullanıcı ihtiyacı | Özelliğin iş amacı |
| Kod yolu | ASME/PED/EN/diğer |
| Baskı | Örn. ASME 2025 |
| Paragraf/ek/tablo | Lisanslı kaynaktaki kesin referans |
| Girdiler | Ad, tür, birim, zorunluluk |
| Hesap/karar | Uygulanan deterministik yöntem |
| Geçerlilik sınırları | Geometri, basınç, sıcaklık, malzeme vb. |
| Çıktılar | Sonuçlar ve ara değerler |
| Uyarılar | Mühendislik/kapsam uyarıları |
| Test kaynağı | PTB, elle doğrulanmış örnek, bağımsız benchmark |
| Durum | Araştırılıyor/uygulanıyor/doğrulandı |
| Onaylayan | Mühendis/QA |

### 3.4 Her modül için zorunlu araştırma dosyası

Her hesap modülünü uygulamadan önce ayrı bir `research_spec` üret. Şunları içersin:

- resmî kapsam sayfaları;
- lisanslı kod paragrafı ve baskısı;
- kullanılan sembollerin tanımı;
- formülün hangi çap/radyus/kalınlık tanımını kullandığı;
- korozyon payının nerede çıkarılıp eklendiği;
- negatif tolerans ve şekillendirme incelmesinin nasıl ele alındığı;
- kaynak veriminin hangi birleşime ait olduğu;
- tasarım sıcaklığındaki izin verilen gerilimin kaynağı;
- statik sıvı yüksekliğinin işareti ve referans kotu;
- geçerlilik sınırları;
- alternatif yöntem;
- bilinen belirsizlikler;
- en az iki bağımsız doğrulama örneği;
- yazılım kabul kriteri.

Blogları yalnızca konu keşfi için kullan; nihai mühendislik dayanağı olarak kullanma. Teknik hesaplarda resmî standart, resmî rehber, standart kuruluşu yayını, hakemli araştırma veya lisanslı kabul görmüş yöntem kullan.

## 4. Ürün iş akışı ve hesap bağımlılıkları

Siteyi şu sırayla çalışacak biçimde tasarla:

1. Proje ve mevzuat kapsamı.
2. Tasarım koşulları ve yük durumları.
3. Geometri.
4. Malzemeler ve izin verilen gerilmeler.
5. Kaynak kategorileri, NDE ve birleşim verimleri.
6. Basınç parçalarının gerekli/nominal/net kalınlıkları.
7. Açıklıklar, nozullar, manşonlar ve flanşlar.
8. Ağırlık, doluluk, ağırlık merkezi ve dış yükler.
9. Destekler, ankrajlar ve lokal gerilmeler.
10. Bileşen MAWP’leri ve global MAWP.
11. Hidrostatik/pnömatik test.
12. Aşırı basınç koruması.
13. PED/CE sınıflandırma ve teknik dosya.
14. 3B model, STEP, PDF rapor ve revizyon onayı.

Bağımlılık kuralları:

- Malzeme `S` değeri ve tasarım sıcaklığı yoksa basınç kalınlığı hesaplanamaz.
- Kaynak tipi/NDE bilinmiyorsa `E` tahmin edilmez; hesap bloke edilir veya açıkça kullanıcı tarafından doğrulanmış değer istenir.
- Nominal kalınlık, CA ve tolerans bilinmeden MAWP üretme.
- Gövde/başlık basınç hesabı tamamlanmadan nozul takviyesi kesinleştirilemez.
- Nozul boru boyutu, kalınlığı, açıklık geometrisi ve malzeme olmadan UG-37 hesabı tamamlanamaz.
- Ağırlık ve CG olmadan destek/ayak yükleri tamamlanamaz.
- Tüm basınç sınırları aynı sıcaklık ve referans kotuna normalize edilmeden global MAWP üretilemez.
- MAWP ve test sıcaklığı malzeme oranı belirlenmeden hidrotest kesinleştirilemez.
- Akışkan sınıfı, PS ve V/DN olmadan PED kategorisi üretilemez.
- İnceleme durumu başarısız veya eksik olan modül varken proje “onaylı” olarak işaretlenemez.

## 5. Ortak veri, geometri ve birim altyapısı

Mühendislik modüllerinden önce aşağıdaki ortak altyapıyı kur:

### 5.1 Basınç ve sıcaklık alanları

- normal işletme basıncı ve sıcaklığı;
- maksimum/minimum işletme;
- tasarım basıncı ve sıcaklığı;
- dış tasarım basıncı/vakum;
- upset/start-up/shutdown/steam-out koşulları;
- test basıncı ve test sıcaklığı;
- relief set pressure;
- referans kotu ve sıvı seviyesi;
- basıncın gauge/absolute/differential türü.

### 5.2 Geometrik tanımlar

- kap yönü: yatay/dikey;
- iç veya dış çapın hangisinin tasarım girdisi olduğu;
- gövde tangent-to-tangent uzunluğu;
- başlık tipi ve gerçek ölçüleri;
- straight flange uzunluğu;
- crown radius, knuckle radius, ellips oranı;
- konik bölüm açısı ve geçiş geometrisi;
- düz kapak geometrisi;
- ceket/yarım boru ceket varsa ayrı basınç odası;
- kaplamalar, lining, izolasyon ve fireproofing;
- nozulların global ve yerel koordinatları;
- desteklerin koordinatları;
- bütün boyutların nominal/as-built durum etiketi.

### 5.3 Kalınlık zinciri

Her parça için şu kalınlıkları ayrı alanlarda sakla:

- `t_required_pressure`: basınç için gerekli net kalınlık;
- `t_required_other`: diğer mekanik gereklerden gelen kalınlık;
- `t_min_code`: kod minimumu;
- `corrosion_allowance`;
- `erosion_allowance`;
- `forming_thinning_allowance`;
- `mill_negative_tolerance`;
- `t_required_order`: sipariş edilmesi gereken minimum nominal;
- `t_nominal_selected`: seçilen nominal;
- `t_actual_min`: ölçülen minimum;
- `t_effective_corroded`: MAWP/servis hesabında kullanılan etkin kalınlık.

Hangi hesabın hangi kalınlığı kullandığını fonksiyon imzasında açık et.

### 5.4 Koordinat ve yük işaret sistemi

- Global sağ elli X-Y-Z sistemi tanımla.
- Dikey kap eksenini tercihen Z; yatay kap eksenini tercihen X yap.
- Her nozul ve destek için yerel eksen sistemi sakla.
- Kuvvetleri `Fx, Fy, Fz`, momentleri `Mx, My, Mz` olarak sakla.
- Basınç, ağırlık, rüzgâr, deprem, borulama, termal, titreşim ve kaldırma yüklerinin işaret sözleşmesini görselleştir.
- CAD, hesap ve rapor aynı koordinat sistemini kullanmalı.

### 5.5 Sayısal kalite

- Boyutsal analiz testleri yaz.
- Ondalık hassasiyeti ve rapor yuvarlamasını hesap hassasiyetinden ayır.
- Gerekli kalınlıktan nominal kalınlığa geçerken güvenli yönde yuvarla.
- Tablo interpolasyonu uygulanıyorsa yöntem, sınır dışı davranışı ve kaynak sürümü kayıt altında olsun.
- NaN, infinity, negatif fiziksel değer, sıfıra bölme ve birim karışımı için merkezi doğrulama yap.

## 6. Eklenecek 20 ana mühendislik hesap modülü

Aşağıdaki 20 modülün her birini ayrı araştır, ayrı saf hesap paketi olarak uygula, API ve UI katmanına bağla, PDF raporuna ekle ve test et.

---

## Modül 1 — İç hacim, doluluk hacmi ve seviye eğrisi

### Araştırılacaklar

- silindir, elipsoidal başlık, torisferik başlık, yarım küre, koni ve düz kapak geometrileri;
- tangent line ve straight flange’ın hacme etkisi;
- iç çap/net iç geometri;
- yatay ve dikey kaplarda seviye-hacim ilişkisi;
- kısmi dolulukta sıvı ağırlık merkezi;
- çok bölmeli kap/ceket için ayrı hacimler.

### Temel hesaplar

- Silindirik gövde iç hacmi:
  `V_cyl = π × Di² × L / 4`.
- İdeal 2:1 yarım elipsoid başlık için, straight flange hariç, bir başlığın geometrik hacmi:
  `V_head = π × Di³ / 24`.
- Torisferik başlıkta gerçek crown/knuckle/straight flange geometrisinden analitik veya doğrulanmış sayısal integrasyon kullan.
- Yatay silindirde kısmi doluluk için dairesel segment alanını; başlıklarda doğrulanmış kesit integrasyonunu kullan.
- Doluluk yüzdesi, sıvı seviyesi, sıvı hacmi ve sıvı CG arasında çift yönlü çözüm sağla.

### Girdiler

İç çap, gövde boyu, başlık tipi/ölçüleri, straight flange, kap yönü, sıvı seviyesi veya doluluk yüzdesi.

### Çıktılar

Toplam brüt hacim, kullanılabilir hacim, her geometrik parçanın hacmi, doluluk tablosu, seviye-hacim grafiği, sıvı CG.

### Kabul testleri

- Basit silindir için analitik sonuçla makine hassasiyetinde eşleşme.
- 0% ve 100% sınırlarında doğru sonuç.
- Yatay simetrik kapta 50% doluluk simetrisi.
- CAD katı hacmi ile hesap motoru hacmi arasında tanımlı tolerans.

---

## Modül 2 — Akışkan kütlesi ve hidrostatik statik basınç

### Araştırılacaklar

- yoğunluğun sıcaklık/basınca bağlılığı;
- çok fazlı veya birden fazla sıvı tabakası;
- referans kotu;
- tasarım/test koşullarında statik sıvı yüksekliği;
- alt ve üst nozullardaki basınç farkı.

### Hesaplar

- `m_fluid = ρ × V`.
- `ΔP = ρ × g × Δh`.
- Tasarım basıncına statik yüksekliğin hangi noktada eklendiğini kod ve proje tanımına göre belirle.
- Test suyu ile işletme akışkanının yoğunluklarını ayır.

### Çıktılar

Akışkan kütlesi, her kritik kottaki yerel basınç, dip/tepe basınçları, hidrotest statik kafa düzeltmesi.

### Güvenlik

Gaz kabında yalnızca hacimden basınç türetme. Bilinen kapalı gaz kütlesi/molü ve sıcaklığı varsa `P_abs V = n Z R T` proses tahmini sun; “kod tasarım basıncı değildir” etiketi göster.

---

## Modül 3 — Metal ağırlığı, toplam ağırlık ve ağırlık merkezi

### Araştırılacaklar

- gövde/başlık gerçek metal hacmi;
- nozul, flanş, manşon, repad, menhol;
- ayak, skirt, saddle, lug;
- iç aksam, platform, merdiven;
- lining, izolasyon, fireproofing;
- kaynak metali için gerekli hassasiyet seviyesi.

### Yük durumları

- empty;
- operating;
- full/flooded;
- hydrotest;
- erection/lifting;
- transport;
- upset.

### Çıktılar

Her parçanın ağırlığı, toplam ağırlık, global CG, destek reaksiyonlarına giden ağırlık dağılımı, ağırlık tablosu ve BOM girdisi.

### Kabul testleri

Analitik ince cidarlı silindir kontrolü, CAD kütle özellikleri karşılaştırması, malzeme yoğunluğu değişim testi.

---

## Modül 4 — Tasarım basıncı–sıcaklığı ve yük durumu zarfı

### Araştırılacak ASME alanları

VIII-1 genel tasarım koşulları, UG-20, UG-21, dikkate alınacak yükler için UG-22 ve projeye özel gereklilikler.

### Girdiler

İşletme/upset/start-up/shutdown/steam-out koşulları; iç/dış basınç; sıcaklık; statik kafa; vakum; çevrim sayısı; rüzgâr; deprem; boru yükleri; termal hareket.

### İşlev

- Her yük durumu için basınç, sıcaklık, doluluk ve dış yükleri tanımla.
- Tasarım zarfını ve yöneten koşulu belirle.
- Aynı anda gerçekleşmesi mümkün olmayan yükleri körlemesine birleştirme; kombinasyon matrisi oluştur.
- Kullanıcı onaylı tasarım basis dokümanı üret.

### Çıktılar

Load-case matrisi, kombinasyonlar, yöneten basınç/sıcaklık ve eksik senaryo uyarıları.

---

## Modül 5 — Malzeme, izin verilen gerilme, korozyon ve üretim toleransları

### Araştırılacak kaynaklar

- ASME BPVC Section II Part A/B/C/D;
- VIII-1 malzeme alt bölümleri: servis ve ürüne göre UCS, UHA, UHT, UNF ve diğer uygulanabilir bölümler;
- Section II-D tablo notları, dış basınç elastisite verileri ve sıcaklık sınırları;
- kullanılan ürün standardının negatif et kalınlığı toleransı;
- şekillendirme sonrası minimum kalınlık.

### Veri modeli

Malzeme yalnızca “SA-516 70” metni olmasın. Şunları sakla:

- specification, grade, class/type;
- product form: plate, pipe, forging, fitting, bolting;
- UNS/P-number/Group Number gerektiğinde;
- Section II-D table identity ve note set;
- code edition;
- sıcaklığa bağlı `S`;
- yield/tensile değerleri gerektiğinde;
- elastisite modülü ve termal genleşme;
- yoğunluk;
- impact test/MDMT özellikleri;
- kaynak/PWHT kısıtları;
- izin verilen kalınlık ve sıcaklık aralığı.

### Kritik kural

Güncel ASTM kataloğundaki bir malzemenin varlığı, ASME 2025 tarafından otomatik kabul edildiği anlamına gelmez. ASME’nin benimsediği SA/SB spesifikasyonu, kabul edilen baskı ve Section II-D notları kontrol edilmelidir.

### Çıktılar

Malzeme uygunluk sonucu, tasarım/test sıcaklığındaki `S`, kaynak/ısı işlem uyarıları, veri kaynağı ve lisans durumu.

---

## Modül 6 — Silindirik gövde iç basınç kalınlığı ve gövde MAWP

### Öncelik

Bu modül ilk üretim sürümünde eksiksiz çalışan ilk kod hesabı olmalıdır.

### Araştırılacaklar

- ASME VIII-1 UG-27’nin iç basınç altındaki silindirik kabuk hükümleri;
- çevresel ve boyuna gerilme denklemleri;
- iç/dış çap veya radyus formunun seçimi;
- kaynak dikiş yönüne göre doğru `E`;
- denklemlerin geçerlilik sınırları;
- CA, tolerans ve forming allowance uygulama sırası;
- UG-16 minimum kalınlık hükümleri ve istisnalar.

### Referans amaçlı başlangıç denklemleri

İç yarıçap formunda çevresel gerilme için yaygın denklem:

`t = P R / (S E - 0.6 P)`

Ters çözüm:

`P = S E t / (R + 0.6 t)`

Boyuna gerilme kontrolü için yaygın form:

`t = P R / (2 S E + 0.4 P)`

Bu prompttaki denklemleri körlemesine üretime alma. Sembolleri, geçerlilik sınırlarını, çap/radyus bazını ve 2025 baskısını lisanslı UG-27 ile doğrula.

### Girdiler

P, tasarım sıcaklığı, iç/dış çap seçimi, R/D, S, E, CA, nominal/actual kalınlık, negatif tolerans, forming thinning, kaynak yerleşimi.

### Çıktılar

- basınç için gerekli net kalınlık;
- tüm paylarla sipariş kalınlığı;
- seçilen nominal kalınlığın yeterlilik oranı;
- çevresel ve boyuna kontroller;
- gövde MAP/MAWP;
- yöneten denklem;
- geçerlilik sınırı sonucu.

### Testler

- lisanslı elle çözülmüş en az 10 örnek;
- birim dönüşüm değişmezliği;
- P→0 sınırı;
- payda sıfıra yaklaşma ve kod sınırı;
- E ve CA duyarlılığı;
- forward thickness ve inverse pressure tutarlılığı.

---

## Modül 7 — Başlıklar ve konik bölümler

### Araştırılacak ASME alanları

UG-32 ve uygulanabilir koni/geçiş hükümleri; başlık geometrisi, şekillendirme ve dış basınç hükümleri.

### Tipler

- 2:1 elipsoidal;
- genel elipsoidal;
- ASME flanged-and-dished/torispherical;
- hemispherical;
- conical head ve conical reducer;
- başlık–gövde geçişi;
- gerekiyorsa nonstandard head için tasarım analizi.

### Girdiler

İç/dış çap, crown radius, knuckle radius, ellips oranı, cone half-angle, straight flange, nominal/as-built kalınlık, S, E, CA ve toleranslar.

### Hesaplar

- gerekli net ve nominal kalınlık;
- başlık MAP/MAWP;
- geometri uygunluk sınırları;
- başlık üzerindeki açıklıkların etkisi;
- forming thinning sonrası minimum kalınlık;
- iç ve dış basınç durumları.

### UI

Şematik başlık çizimi üzerinde kullanılan D, L, r, h, SF ve t ölçülerini göster. “Standart 2:1” seçildiğinde gizli varsayımları kullanıcıya açıkla.

---

## Modül 8 — Düz kapaklar, blind bölümler ve kapama elemanları

### Araştırılacak ASME alanları

UG-34, UG-35 ve uygulanabilir flanş/kapama detayları.

### Kapsam

- kaynaklı düz kapak;
- civatalı blind;
- stayed/unstayed geometri;
- circular/noncircular plate;
- kenar bağlantı tipine bağlı katsayılar;
- açıklık içeren düz kapak;
- kapak–gövde kaynak ve lokal etkileri.

### Çıktılar

Gerekli kalınlık, kapak MAP/MAWP, bağlantı tipi/katsayı kaynağı, yöneten geometri, kaynak ve deformasyon uyarısı.

### Kritik kural

Düz kapak analizi tamamlanmadan onu içeren bir kabın global MAWP’sini “tamamlandı” gösterme.

---

## Modül 9 — Dış basınç, vakum, burkulma ve takviye halkaları

### Araştırılacak ASME alanları

UG-28, UG-29, UG-30 ve ilgili Section II-D dış basınç grafik/tablo verileri.

### Girdiler

Dış çap, etkin kalınlık, unsupported length, tangent/stiffener mesafeleri, başlık tipi, malzeme, sıcaklık, ovalite, external pressure/vakum, stiffener geometrisi.

### Hesaplar

- `Do/t`, `L/Do` gibi boyutsuz parametreler;
- lisanslı A/B veya eşdeğer chart/table verisi;
- izin verilen dış basınç;
- gerekli kalınlık;
- stiffener ring atalet ve alan gerekleri;
- ring aralığı;
- başlıkların dış basınç kontrolü;
- vacuum + external loads kombinasyonu.

### Yazılım kuralı

Grafikleri görselden yaklaşık okumak yerine lisanslı ve sürümlenmiş sayısal veri kullan. Veri yoksa hesabı bloke et. İnterpolasyon ve sınır dışı davranışı test edilmelidir.

---

## Modül 10 — MDMT, gevrek kırılma, darbe testi ve PWHT

### Araştırılacak ASME alanları

UG-20(f), UCS-56, UCS-66, UCS-67, UCS-68, paslanmaz/diğer malzemeler için uygulanabilir alt bölüm ve UHA-51 dâhil ilgili hükümler.

### Girdiler

Malzeme eğri grubu, ürün formu, nominal/yönetici kalınlık, kaynak detayı, MDMT, tasarım gerilme oranı, PWHT durumu, impact test kayıtları, forming ve servis.

### Çıktılar

- impact test muafiyeti veya gerekliliği;
- izin verilen MDMT;
- sıcaklık indirimi/adjustment;
- PWHT gerekliliği;
- belirsizlik ve mühendis incelemesi;
- rapor için karar zinciri.

### Test

Sınır sıcaklıkları, kalınlık aralıkları, kaynaklı/kaynaksız ve PWHT’li/PWHT’siz örnekler.

---

## Modül 11 — Kaynak kategorisi, NDE ve birleşim verimi

### Araştırılacak ASME alanları

UW-3 kaynak kategorileri, UW-11 muayene/radyografi kapsamı, UW-12 birleşim verimleri, UW-16 bağlantı detayları ve ilgili özel hükümler. NDE yöntemleri için Section V; prosedür/personel için uygulanabilir kurallar; kaynak yeterlilikleri için Section IX.

### Veri modeli

- weld ID;
- category A/B/C/D veya uygulanabilir sınıf;
- joint type;
- full/spot/no radiography veya diğer NDE kapsamı;
- `E`;
- WPS, PQR ve welder/WPQ referansı;
- base/filler material;
- joint geometry;
- PWHT;
- NDE method, extent, acceptance result;
- repair history.

### Kritik ayrım

Section V NDE yöntemini verir; kabul kriteri çoğu durumda construction code’dan gelir. Arayüz bunu ayırmalıdır.

### Çıktılar

Weld map, her hesapta kullanılan E’nin kaynağı, NDE planı, WPS/PQR/WPQ listesi, eksik belge blokajı.

---

## Modül 12 — Açıklıklar ve nozul/manşon basınç takviyesi

### Araştırılacak ASME alanları

UG-36 ila UG-42; açıklık şekli, reinforcement limits, required/available area, çoklu açıklıklar, kaynak yolları ve strength path kontrolleri.

### Girdiler

Kabuk/başlık tipi ve kalınlığı, açıklık çapı/şekli, nozul açısı, nozul OD/ID, neck thickness, projection iç/dış, malzemeler ve S oranları, repad boyut/kalınlığı, weld sizes, CA, açıklık konumu ve yakın açıklıklar.

### Hesaplar

- gerekli takviye alanı;
- shell excess area;
- nozzle neck excess area;
- iç/dış projection katkısı;
- repad alanı;
- izin veriliyorsa weld metal katkısı;
- malzeme dayanım oranları;
- reinforcement zone sınırları;
- toplam kullanılabilir alan;
- area margin ve kullanım oranı;
- komşu açıklık etkileşimi;
- kaynak yük yolu/strength path;
- tell-tale hole gibi imalat gereksinimlerinin kayıt alanı.

### Çıktılar

Alan bileşenlerini renkli kesitte göster; `A_required`, `A_available`, margin, PASS/FAIL, kullanılan alanın fiziksel kaynağı ve paragraf referansı.

### Kritik kural

UG-37 PASS sonucu, nozul dış yüklerinin kabul edildiği anlamına gelmez. Lokal yük kontrolü ayrı modüldür.

---

## Modül 13 — Nozul boynu, manşon ve bağlantı kaynağı yeterliliği

### Araştırılacak ASME alanları

UG-43, UG-45, UW-16, uygulanabilir minimum neck thickness, attachment detail, weld size ve malzeme hükümleri.

### Kapsam

- set-in nozzle;
- set-on nozzle;
- through nozzle;
- integral/self-reinforced nozzle;
- repad reinforced nozzle;
- half/full coupling;
- threaded coupling;
- socket-weld fitting;
- butt-weld pipe neck;
- long weld neck/weld neck flange;
- forged branch outlet.

### Kontroller

- neck minimum ve pressure thickness;
- nominal schedule’dan gerçek minimum et;
- negative mill tolerance;
- bağlantı kaynağı boyutu ve etkin boğaz;
- weld load path;
- korozyon;
- NDE/PWHT erişimi;
- iç çıkıntı ve drenaj/temizlik;
- malzeme uyumu;
- açıklık edge distance ve çakışma.

### Çıktılar

Bağlantı tipi seçim özeti, geometrik detay, malzeme/standart, neck ve weld PASS/FAIL, imalat notları.

---

## Modül 14 — Flanş, conta, civata ve civatalı birleşim

### Araştırılacak kaynaklar

UG-44 ve uygulanabilir ASME B16 standartları; standard dışı flanşlar için VIII-1/Appendix 2 veya VIII-2’nin uygun yöntemi; montaj için PCC-1.

### Kapsam

- B16.5 NPS 1/2–24 flanşlar;
- B16.47 NPS 26–60 flanşlar;
- weld neck, slip-on, socket weld, threaded, lap joint, blind;
- standard dışı vessel flange;
- manway/body flange;
- metallic/nonmetallic gasket;
- bolting material ve sıcaklık sınırı.

### Hesap ve kontroller

- standard flange pressure-temperature rating;
- seçilen malzeme grubu ve sıcaklık;
- hydrotest koşulunda rating;
- standard dışı flanşta gasket seating ve operating load;
- bolt area/stress;
- flange moments ve stresses;
- gasket effective width;
- assembly target bolt load/torque dokümantasyonu;
- nozzle external load etkisi gerekiyorsa ayrıca değerlendirme.

### Kritik kurallar

- Rating Class doğrudan basınç değildir.
- B16 rating kontrolü, kabuk açıklık takviyesi ve nozul dış yük kontrolünün yerine geçmez.
- Montaj prosedürü tasarım hesabından ayrıdır fakat rapora bağlanmalıdır.

---

## Modül 15 — Nozul dış yükleri ve lokal kabuk gerilmeleri

### Girdiler

Her load case için `Fx, Fy, Fz, Mx, My, Mz`, basınç, sıcaklık, shell/nozzle geometrisi, repad, malzeme ve koordinat dönüşümü.

### Araştırılacak yöntemler

- WRC 537: silindirik/küresel kabukta haricî yüklerden lokal kabuk gerilmeleri;
- WRC 297: kapsam sınırları içinde silindirik nozul–silindirik kabuk birleşimi ve nozul/kabuk gerilmeleri;
- yöntem sınır dışıysa ASME VIII-2 Part 5 design-by-analysis/FEA;
- nozzle loads’ın basınç gerilmeleri ve diğer yüklerle birleştirilmesi.

### Hesaplar

- global yükleri nozul yerel sistemine dönüştür;
- membrane ve bending stress bileşenleri;
- pressure stress ile kombinasyon;
- stress classification ve uygun allowable limit;
- primary/local/secondary sınıflandırmasının yönteme göre doğru uygulanması;
- WRC geometri geçerlilik sınırları;
- repad ve yakın discontinuity etkisi;
- load-case envelope.

### Çıktılar

Her yük bileşeninin etkisi, kritik kabuk noktaları, stress intensity/equivalent stress, allowable, kullanım oranı, yöntem geçerliliği ve FEA’ya yönlendirme.

---

## Modül 16 — Ayaklar, skirt, saddle, support lug, base plate ve ankrajlar

Bu modülü Bölüm 7’deki ayrıntılı destek şartlarıyla birlikte uygula.

### Araştırılacak ASME alanları

UG-22 yükler, UG-54/UG-55 basınç taşımayan bağlantılar ve ilgili yapım hükümleri. VIII-1’in ayrıntılı destek boyutlandırmasını her durumda vermediğini açıkça kaydet. Gereken yerde WRC, Zick yöntemi, VIII-2 Part 5/FEA ve seçilmiş yapısal tasarım standardını kullan.

### Çıktılar

Destek reaksiyonları, üye gerilmeleri/burkulması, weld/pad/shell lokal gerilmeleri, base plate/anchor sonucu, sliding/fixed tanımı ve yöneten yük kombinasyonu.

---

## Modül 17 — Rüzgâr, deprem, kaldırma, ereksiyon ve taşıma

### Araştırma

Projenin kurulum ülkesine göre seçilecek haricî yük standardı; örneğin ASCE 7 veya EN 1991/EN 1998/Türkiye’de uygulanabilir mevzuat. Çelik, beton ve ankraj kontrollerinde seçilen AISC/ACI veya EN/Türk karşılığı açıkça kaydedilsin.

### Kapsam

- empty + wind;
- operating + wind;
- operating + seismic;
- hydrotest + wind gerekirse;
- transport acceleration;
- lifting dynamic factor;
- sling angle;
- tailing/erection;
- nozzle/piping loads;
- thermal displacement;
- vibration/rotating equipment.

### Çıktılar

Kesme, devrilme momenti, eksenel yük, burulma, dinamik katsayılar, yük kombinasyonları, stabilite/sliding/uplift, support ve anchor talepleri.

---

## Modül 18 — Termal gerilme, yorulma, çevrim ve yüksek sıcaklık

### Araştırılacaklar

- UG-22 cyclic load değerlendirmesi;
- VIII-1’de ayrıntılı kural bulunmayan durumlarda U-2(g)/uygun yöntem;
- VIII-2 Part 5 design-by-analysis ve fatigue yaklaşımı;
- thermal gradient, differential expansion, nozzle thermal loads;
- creep range ve time-dependent material behavior;
- ratcheting, buckling, fatigue ve fracture riskleri.

### Ürün davranışı

Basit ön eleme ile ayrıntılı analiz gerekip gerekmediğini belirle. Gerekliyse modülü `REVIEW_REQUIRED` yap ve VIII-2/FEA iş akışına geçir. Yeterli veri olmadan “yorulma PASS” üretme.

---

## Modül 19 — Bileşen MAP/MAWP ve global MAWP

### Araştırılacak ASME alanları

UG-98 ve bütün bileşenlere ait inverse pressure denklemleri.

### Hesap kapsamı

Her biri için MAP/MAWP üret:

- shell course;
- her head/cone;
- flat cover;
- nozzle neck;
- opening reinforcement;
- flange/closure;
- jacket chamber;
- external pressure/vacuum sınırı uygun metrikle;
- özel bileşenler.

### Global algoritma

1. Her bileşenin etkin/as-corroded kalınlığını belirle.
2. İzin verilen gerilmeyi MAWP sıcaklığında al.
3. Yerel statik sıvı yüksekliğini dikkate al.
4. Bütün basınç sınırlarını ortak referans kota dönüştür.
5. Uygulanabilir eşzamanlı dış yük kombinasyonlarını dikkate al.
6. Geçersiz/eksik bileşeni minimum hesabına sessizce katma; global sonucu bloke et.
7. Geçerli sınırların minimumunu global MAWP ve ilgili parçayı “governing component” olarak raporla.

### Çıktılar

Component MAWP tablosu, common reference elevation, static-head correction, global MAWP, governing component, ikinci en kritik komponent ve marj.

---

## Modül 20 — Hidrostatik/pnömatik test ve aşırı basınç koruması

### Test araştırması

ASME VIII-1 UG-99 hidrostatik test, UG-100 pnömatik test ve uygulanabilir test istisnaları/gerilme sınırları.

### Referans başlangıç ilişkileri

- Hidrostatik test için yaygın kod ilişkisi:
  `P_test = 1.3 × MAWP × LSR`.
- Pnömatik test için yaygın kod ilişkisi:
  `P_test = 1.1 × MAWP × LSR`.
- `LSR`, test ve tasarım sıcaklıklarındaki izin verilen gerilmelerden türeyen en düşük uygun oranı ifade eder.

Bu ilişkileri 2025 baskısı, tanımlar, istisnalar, test kotu, statik su yüksekliği ve test gerilme sınırlarıyla lisanslı kaynaktan doğrula.

### Test kontrolleri

- test medium ve yoğunluk;
- test sıcaklığı/MDMT;
- top/bottom gauge pressure;
- hidrostatik kafa;
- test anındaki nominal/actual thickness;
- test stress limit;
- havanın tahliyesi, emniyet ve kademeli basınçlandırma;
- pnömatik testin yüksek enerji riski ve özel güvenlik iş akışı;
- leak test/NDE gereksinimleri;
- kalibrasyonlu ölçüm cihazları.

### Aşırı basınç koruması

- ASME Section XIII kapsamı;
- relief valve, rupture disk ve kombinasyonları;
- credible overpressure scenarios;
- set pressure ve accumulation;
- required relieving rate;
- cihaz kapasitesi/sizing;
- inlet/outlet pressure losses;
- backpressure;
- discharge yönü ve güvenli tahliye;
- fire, blocked outlet, control failure, thermal expansion, tube rupture vb. senaryolar;
- proses tesisleri için gerekiyorsa API 520/521 entegrasyonu.

### Çıktılar

Test pressure, gauge elevations, test procedure data sheet, stress checks, relief scenario list, required capacity, seçilen cihaz ve açık eksikler.

---

## 7. Bağlantı ayakları ve destek sistemleri için ayrıntılı zorunlu kapsam

Destek hesaplarını tek bir “ayak kalınlığı” alanına indirgeme. Destek modülü, global statik yük dağılımını, destek elemanını, bağlantı kaynağını, repad’i, kap cidarındaki lokal gerilmeyi, base plate’i, ankrajı ve temel arayüzünü birlikte ele almalıdır.

### 7.1 Destek tipi seçim ekranı

Kullanıcı şu tiplerden birini seçebilmeli:

- dikey kap için leg support;
- dikey kap için skirt support;
- yatay kap için iki veya daha fazla saddle;
- support lug/bracket;
- ring girder veya çoklu lug;
- transport support;
- lifting lug/trunnion/tail lug;
- özel kullanıcı tanımlı destek.

Her destek tipinde:

- konum;
- adet;
- angular spacing;
- profil/plate geometrisi;
- malzeme;
- weld detail;
- wear/reinforcement pad;
- fixed/sliding davranışı;
- base plate;
- anchor pattern;
- grout/concrete bilgisi;
- korozyon payı;
- imalat toleransı saklanmalıdır.

### 7.2 Zorunlu yük durumları

En az şu durumları hazır şablon olarak oluştur:

1. Empty.
2. Operating.
3. Full/flooded.
4. Hydrotest.
5. Empty + wind.
6. Operating + wind.
7. Operating + seismic.
8. Empty + seismic gerekirse.
9. Vacuum/steam-out.
10. Lifting/erection.
11. Transport.
12. Piping/nozzle loads.
13. Thermal expansion/contraction.
14. Vibration/dynamic.
15. Accidental veya kullanıcı tanımlı.

Her kombinasyonun standardı, faktörleri ve eşzamanlılık varsayımı saklanmalıdır.

### 7.3 Eşit rijitlikli simetrik ayak grubu için ön dağılım

Merkezi orijine göre aynı rijitlikte `n` adet ayak için ön tasarım eksenel yükü aşağıdaki formda ele al:

`N_i = W/n + Mx × y_i / Σ(y_j²) - My × x_i / Σ(x_j²)`

Burada işaret sistemi proje koordinat tanımıyla doğrulanmalıdır. `N_i < 0` ayakta/ankrajda çekme-uplift anlamına gelebilir.

Taban düzlemindeki kesme ve burulma için ön dağılım:

`Vx_i = Vx/n - Tz × y_i / Σ(r_j²)`

`Vy_i = Vy/n + Tz × x_i / Σ(r_j²)`

Bu denklemler yalnızca simetrik/eşit rijitlik varsayımı altında ön tasarımdır. Farklı rijitlik, eksantrik temel, boşluk/slip, tek yönlü mesnet veya nonlinear uplift varsa rijitlik matrisi/FEA yöntemi gerekir.

### 7.4 Leg support kontrolleri

Her ayak için:

- eksenel basınç/çekme;
- iki eksenli eğilme;
- kesme;
- birleşik gerilme;
- kolon narinliği ve burkulma;
- local buckling;
- bracing gereği;
- profil net/brüt kesit;
- ayak–pad kaynak boğazı ve yük yolu;
- pad/repada yük aktarımı;
- shell local membrane/bending stress;
- shell ovalleşmesi;
- base plate bending ve bearing;
- grout bearing;
- anchor tension, shear ve interaction;
- edge distance, breakout, pry-out ve concrete failure;
- korozyon ve drenaj;
- yorulma/titreşim kontrolü araştırılmalıdır.

UI her ayakta `N, Vx, Vy, Mx, My, T` taleplerini ve yöneten kombinasyonu göstermelidir.

### 7.5 Skirt support kontrolleri

En az şu hesapları yap:

- skirt kesit alanı `A` ve section modulus `Z`;
- ön normal gerilme: `σ = W/A ± M/Z`;
- çevresel dağılım ve maksimum/minimum gerilme;
- kesme ve burulma;
- local ve global buckling;
- shell/head–skirt junction yük aktarımı;
- junction weld;
- skirt openings nedeniyle net kesit ve lokal gerilme;
- access opening reinforcement;
- base ring bending;
- compression bearing;
- anchor bolt circle, tension ve shear;
- uplift;
- grout/concrete interface;
- shell ile skirt arasındaki sıcaklık farkı ve thermal gradient;
- insulation/fireproofing etkisi;
- fatigue gerekiyorsa çevrim.

Skirt ile başlık/gövde birleşimi yalnızca skirt nominal gerilmesiyle kabul edilmemeli; lokal kabuk etkisi ayrıca değerlendirilmelidir.

### 7.6 Saddle support kontrolleri

Yatay kaplar için:

- gerçek ağırlık ve CG’den saddle reaksiyonları;
- simetrik olmayan yüklerde farklı reaksiyonlar;
- global longitudinal bending;
- shell’de longitudinal stress;
- tangential shear;
- saddle horn ve alt noktada circumferential stress;
- shell/head shear etkisi;
- saddle genişliği ve contact angle;
- wear plate/repad;
- ring stiffener gereği;
- saddle plate, web, base plate ve weld;
- anchor/sliding düzeni;
- nozzle ve diğer concentrated load etkileşimi;
- hydrotest load case;
- thermal expansion için bir saddle fixed, diğerinin sliding yapılmasının değerlendirilmesi.

Klasik Zick yaklaşımının kaynağı, varsayımları ve geometri sınırları araştırılmalı. Sınır dışı veya karmaşık geometriler VIII-2/FEA’ya yönlendirilmelidir.

### 7.7 Support lug, bracket ve ring kontrolleri

- lug net section tension/compression;
- bearing;
- shear-out/tear-out;
- bending;
- plate buckling;
- pin/hole bearing;
- weld group;
- repad;
- shell local stress;
- çoklu lug yük dağılımı;
- eccentricity ve prying;
- thermal restraint.

### 7.8 Lifting lug ve trunnion kontrolleri

- empty erection weight ve gerçek CG;
- sling angle;
- dynamic/impact factor;
- unequal sling load;
- tailing sequence;
- lift stages ve orientation change;
- lug plate tension, shear, bending;
- hole bearing ve tear-out;
- weld group;
- trunnion bending/shear/torsion;
- pad ve shell local stress;
- out-of-plane load;
- proof test/inspection gerekiyorsa prosedür.

Kaldırma analizi çalışma yüklerinden ayrı load case ailesi olmalıdır.

### 7.9 Lokal kabuk gerilmesi yöntemi

Destek/nozul bağlantısı için karar ağacı oluştur:

1. WRC 537 geometri ve yük sınırları içinde mi?
2. Silindirik nozul–silindirik kabuk için WRC 297 uygun mu?
3. Yakın head, seam, stiffener, opening veya birden fazla yük bölgesi var mı?
4. Pad/attachment geometrisi yöntemin varsayımına uyuyor mu?
5. Uymuyorsa VIII-2 Part 5 FEA gerekli mi?

WRC sonucu üretilirse kullanılan bulletin baskısı, yük koordinat dönüşümü, tüm boyutsuz oranlar ve geçerlilik kontrolü rapora eklenmelidir.

### 7.10 Yapısal standart arayüzü

ASME VIII-1 her base plate, anchor ve beton göçme hesabını ayrıntılı sağlamaz. Bu nedenle proje seviyesinde seçilebilir bir `structural_design_basis` oluştur:

- wind/seismic load standard;
- steel member standard;
- anchor/concrete standard;
- load factors ve combination standard;
- allowable/LRFD yöntemi;
- ülke/kurulum yeri;
- zemin/temel tasarım sorumluluk sınırı.

Standart karıştırma yapılırsa açık mühendislik gerekçesi ve onay kaydı zorunlu olsun.

## 8. Kaplara kaynakla eklenen boru, nozul ve manşon tipleri

“Manşon” sözcüğünü tek bir ürün gibi ele alma. Kullanıcıdan veya geometriden aşağıdaki anlamlardan hangisinin kastedildiğini belirle:

- full coupling;
- half coupling;
- threaded coupling;
- socket-weld coupling;
- pipe nipple/nozzle neck;
- forged branch outlet;
- reinforcement sleeve/pad;
- long weld neck nozzle;
- özel machined self-reinforced nozzle.

### 8.1 Bağlantı tipi kataloğu

Her bağlantı tipi için katalog kaydı şu alanları içersin:

- connection family;
- dimensional standard;
- pressure/product standard;
- material specification;
- size NPS/DN;
- OD, ID, nominal wall/schedule;
- end type: BW, SW, NPT, flanged;
- rating class;
- manufacturer dimensional data;
- vessel attachment detail;
- compatible shell/head geometry;
- allowable service/temperature;
- corrosion allowance;
- negative tolerance;
- NDE/PWHT requirements;
- code edition adopted by governing ASME edition;
- data source and license.

### 8.2 Boru boyutları

- Karbon/alaşımlı wrought steel pipe boyutları için ASME B36.10M.
- Paslanmaz steel pipe boyutları için ASME B36.19M/B36.19.
- NPS ile gerçek OD’nin aynı olmadığını UI’da açıkla.
- `Schedule 40`, `40S`, `80`, `80S`, STD, XS, XXS farklarını doğru veri tablosuyla yönet.
- Schedule yalnızca nominal et verir; pressure thickness ve mill tolerance ayrıca kontrol edilir.

### 8.3 Forged coupling ve socket/threaded fitting

ASME B16.11 kapsamında:

- threaded Class 2000, 3000, 6000;
- socket-weld Class 3000, 6000, 9000;
- coupling, half coupling ve uygulanabilir forged fitting ölçü/rating/material şartları;
- socket engagement ve weld gap gibi imalat gereklilikleri;
- vessel’a kaynaklandığında VIII opening/reinforcement/weld kontrollerinin ayrıca gerektiği.

Class numarasını psi gibi gösterme.

### 8.4 Dişler

ASME B1.20.1 kapsamında NPT, NPSC, NPTR, NPSM, NPSL tiplerini ayır. Basınç sınırı, sealing yöntemi, corrosion, galling, cyclic service ve seal-weld ihtiyacını proje şartına göre değerlendir.

Kullanıcı yalnızca “1 inç dişli manşon” yazarsa uygulama:

- thread standard;
- fitting class;
- material;
- vessel attachment;
- service;
- pressure/temperature;
- seal method

bilgilerini istemeden tasarımı tamamlamamalıdır.

### 8.5 Integrally reinforced forged branch outlet

MSS SP-97 kapsamında butt-weld, socket-weld ve threaded forged branch outlet tiplerini katalogla. Üretici ürün adlarını standardın genel tipiyle karıştırma. Vessel üzerine uygulandığında ASME VIII opening, neck, attachment weld ve external load kontrolleri ayrıca yapılmalıdır.

### 8.6 Butt-weld bağlantılar

- ASME B16.9: factory-made wrought buttwelding fittings.
- ASME B16.25: buttwelding end preparation.
- Pipe/nozzle neck ile shell/head bağlantısında VIII-1 UW-16 ve ilgili detayların araştırılması.
- Tam nüfuziyet, fillet, set-in/set-on gibi detayların hesap ve NDE etkisi.

### 8.7 Flanşlı nozullar

- ASME B16.5: NPS 1/2–24.
- ASME B16.47: NPS 26–60.
- ASME B16.20: metallic gaskets.
- ASME B16.21: nonmetallic flat gaskets.
- ASME PCC-1: bolted flange joint assembly.

Flanş kataloğundaki rating kontrolü, nozul neck pressure thickness, vessel opening reinforcement ve external load analizleriyle birlikte tamamlanmalıdır.

### 8.8 Sık kullanılan malzeme aileleri — yalnızca aday liste

Katalog araştırmasına şu adayları dâhil et; otomatik uygun kabul etme:

- karbon çelik pipe/nozzle: SA-106 Gr B;
- düşük sıcaklık pipe: SA-333 Gr 6;
- paslanmaz pipe: SA-312 TP304L/TP316L;
- karbon çelik forging/coupling/flange: SA-105;
- paslanmaz/alaşımlı forging: SA-182;
- düşük sıcaklık forging: SA-350 LF2;
- karbon çelik butt-weld fitting: SA-234 WPB;
- paslanmaz fitting: SA-403 uygun grade.

Her aday için ASME Section II ürün formu, kabul edilen spesifikasyon baskısı, Section II-D izin verilen gerilimi, note’lar, sıcaklık ve impact/PWHT koşulları doğrulanmalıdır.

### 8.9 Her kaynaklı bağlantıda birlikte yapılacak kontroller

Bir coupling, nozzle veya branch outlet kataloğa uygun olsa bile aşağıdakiler tamamlanmadan vessel bağlantısını PASS yapma:

1. Malzeme ASME uygunluğu.
2. Ürün boyut ve toleransı.
3. Nozzle neck pressure/minimum thickness.
4. Vessel opening reinforcement.
5. Attachment weld size ve load path.
6. Komşu açıklık/seam mesafesi.
7. External piping load/local shell stress.
8. Flange/fitting rating.
9. Corrosion/erosion allowance.
10. MDMT/impact test.
11. NDE/PWHT.
12. Hydrotest koşulu.
13. Servise özgü temizlik, drenaj, yorulma ve sızdırmazlık.

## 9. ASME standart kapsam haritası

“Tüm basınçlı kaplar için tek bir zorunlu ASME listesi” yoktur. Uygulama, ekipman tipine ve imalat kapsamına göre aşağıdaki standart yığınını seçmelidir.

### 9.1 Konvansiyonel kaynaklı metal basınçlı kap için çekirdek

- **BPVC Section VIII Division 1**: design-by-rule basınçlı kap.
- Alternatif olarak proje kapsamına göre **Division 2** veya yüksek basınç için **Division 3**.
- **BPVC Section II Part A**: ferrous material specifications.
- **BPVC Section II Part B**: nonferrous material specifications.
- **BPVC Section II Part C**: welding rods/electrodes/filler metals.
- **BPVC Section II Part D**: material properties ve allowable stress.
- **BPVC Section V**: nondestructive examination methods.
- **BPVC Section IX**: WPS/PQR ve welder/operator qualification.
- **BPVC Section XIII**: overpressure protection.
- İlgili **BPVC Code Cases**, interpretations, errata ve notices.
- ASME mark/certification hedefi varsa **CA-1** ve Authorized Inspection için uygulanabilir **QAI-1**.

Section XIII’in ayrı kitabı olması, VIII-1’deki overpressure bağlantı kurallarını ve proje senaryolarını görmezden gelme anlamına gelmez; iki kapsamın 2025 baskısındaki ilişkisini lisanslı metinden araştır.

### 9.2 Ekipman tipine göre koşullu BPVC bölümleri

- **Section I**: power boilers.
- **Section IV**: heating boilers.
- **Section III**: nuclear facility components.
- **Section X**: fiber-reinforced plastic pressure vessels.
- **Section XII**: transport tanks.
- **PVHO-1**: pressure vessels for human occupancy.

Uygulama, bu ekipmanları VIII-1 modülünde sessizce hesaplamak yerine kapsam dışı veya ayrı plugin olarak işaretlemelidir.

### 9.3 Borulama arayüzü

Vessel design boundary ile bağlı piping code sınırını açıkça modelle:

- B31.1 power piping;
- B31.3 process piping;
- B31.5 refrigeration piping;
- B31.12 hydrogen piping;
- projeye göre diğer B31 bölümleri.

Nozul yükleri piping stress analysis’ten alınabilir; yük verisinin load case, sign convention, sustained/thermal/occasional türü ve operating condition bilgisi saklanmalıdır.

### 9.4 Hijyenik, servis sonrası ve onarım kapsamı

- ASME BPE: bioprocess/sanitary equipment gerektiğinde.
- ASME PCC-1: bolted flange assembly.
- ASME PCC-2: in-service pressure equipment/piping repair methods.
- API 579-1/ASME FFS-1: in-service fitness-for-service değerlendirmesi.

Yeni tasarım ile in-service FFS/repair modüllerini aynı PASS mantığında karıştırma; bunlar ayrı proje türleri olmalıdır.

### 9.5 Basınçlı bağlantı boyut standartları

Kapsama göre:

- B36.10M/B36.19 pipe dimensions;
- B16.5/B16.47 flanges;
- B16.9 buttwelding fittings;
- B16.11 socket/threaded forged fittings;
- B16.20/B16.21 gaskets;
- B16.25 welding ends;
- B1.20.1 pipe threads;
- MSS SP-97 branch outlets.

### 9.6 Sertifikasyon modu

İki farklı ürün modu tasarla:

1. **Engineering calculation mode**: tasarım desteği, ASME certification iddiası yok.
2. **Code construction project mode**: certificate holder, AIA/Authorized Inspector, QMS, data report, material traceability, welding/NDE/PWHT/test kayıtları ve nameplate/stamping iş akışı.

İkinci modül gerçek yetki bilgisi olmadan “ASME stamped” sonucu üretmemelidir.

## 10. CE, PED, Türkiye ve EN 13445 modülü

### 10.1 Kapsam ayrımı

- PED 2014/68/EU ve Türkiye 2014/68/AB genel olarak maksimum izin verilen PS > 0,5 bar sabit basınçlı ekipmanı kapsar.
- ASME VIII-1 resmî kapsam sayfası iç/dış basıncı 15 psig’yi aşan kaplardan söz eder.
- Dolayısıyla bir kap VIII-1 eşiğinin altında olsa bile PED kapsamında olabilir.
- Seri üretilen, yalnızca hava/azot içeren ve diğer özel şartları sağlayan basit basınçlı kaplar 2014/29/EU/AB yoluna girebilir.

### 10.2 PED sınıflandırma girdileri

- equipment type: vessel, piping, safety accessory, pressure accessory, assembly;
- PS;
- V veya DN;
- akışkan adı ve fazı;
- fluid group 1/2;
- gaz/sıvı;
- sıcaklık ve vapor pressure;
- firing/heating durumu;
- seri üretim ve SPVD uygunluğu;
- kurulum/market ülkesi.

### 10.3 PED çıktıları

- kapsamda/kapsam dışı;
- SEP veya Category I–IV;
- kullanılan sınıflandırma tablosu;
- seçilebilir conformity assessment modules;
- Notified Body involvement;
- applicable Essential Safety Requirements;
- material route: harmonized material, EAM veya PMA;
- permanent joining personnel/procedure approval gereği;
- NDE personnel gereği;
- final assessment ve pressure test;
- marking/nameplate;
- instructions;
- EU Declaration of Conformity;
- teknik dosya kontrol listesi.

### 10.4 ASME ile CE birlikte kullanılırsa

ASME hesabını otomatik CE kabul etme. Şu `PED gap analysis` kayıtlarını üret:

- ASME maddesi;
- ilgili PED ESR;
- karşılanma kanıtı;
- boşluk;
- kapatma eylemi;
- sorumlu;
- onaylayan;
- Notified Body yorumu;
- dosya referansı.

EN 13445 harmonize tasarım yolu seçilirse ASME ve EN hesaplarını tek formülde karıştırma. Standard engine plugin yapısı kullan:

- `asme_viii_1_2025`;
- `en_13445_selected_edition`;
- ileride `asme_viii_2_2025`.

Aynı proje iki kodla karşılaştırılabilir; her sonuç kendi material data, safety factor, welding/NDE ve validity kurallarıyla bağımsız çalışmalıdır.

### 10.5 Teknik dosya

En az:

- design basis;
- risk assessment;
- general arrangement ve drawings;
- calculations;
- material certificates;
- WPS/PQR/WPQ;
- NDE procedures/reports;
- PWHT charts;
- pressure/leak test;
- relief documentation;
- inspection plan;
- nameplate/marking;
- instructions;
- Declaration of Conformity;
- Notified Body belgeleri;
- revision/approval history.

## 11. Yazılım mimarisi

### 11.1 Katmanlar

Projeyi en az şu paketlere ayır:

```text
frontend/
  project-wizard/
  design-conditions/
  geometry/
  materials/
  welds-nde/
  nozzles/
  supports-loads/
  calculations/
  compliance/
  cad-viewer/
  reports/

backend/
  api/
  domain/
  application/
  persistence/
  auth/
  audit/

calc-core/
  common/
  geometry/
  weight-cg/
  asme-viii-1/
  supports/
  nozzle-loads/
  ped/
  en-13445/
  validation/

cad-service/
report-service/
standards-registry/
tests/
```

Mevcut repository yapısı farklıysa aynı sorumluluk ayrımını mevcut yapıya uyarlayabilirsin.

### 11.2 Hesap çekirdeği ilkeleri

- Saf fonksiyonlar; veri tabanı, HTTP veya UI bağımlılığı yok.
- Typed input/output modelleri.
- Fonksiyonlar yalnızca normalize SI değerleri alır.
- Her fonksiyon `calculation_context` alır: code edition, formula revision, load case, reference elevation.
- Her çıktı ara adımları ve provenance bilgisini içerir.
- Exceptions kullanıcı hatasıyla sistem hatasını ayırır.
- Hesap motoru versiyonlanır.
- Eski onaylı proje yeniden açıldığında hangi engine/code edition ile hesaplandığı korunur.
- Yeni sürüme migration kullanıcı onayı ve karşılaştırma raporu üretir.

### 11.3 Standart veri kayıt sistemi

`standards-registry` içinde:

- standard ID;
- edition;
- effective date;
- source URL;
- license status;
- adopted referenced-standard editions;
- errata/notices;
- code case set;
- formula metadata;
- material table metadata;
- validity predicates;
- verification status

sakla.

Telifli tablo değerlerini yalnızca lisans izin veriyorsa sakla/dağıt. Aksi durumda yetkili kullanıcı girişi veya lisanslı provider adaptörü kullan.

### 11.4 Hesap orkestrasyonu

Bir dependency graph oluştur. Girdi değiştiğinde yalnızca etkilenen sonuçları `STALE` yap:

- geometry değişirse volume, weight, shell/head, nozzle, support, MAWP, test, CAD ve report stale;
- material/S değişirse thickness, MAWP, test, MDMT, nozzle, flange stale;
- weld E değişirse ilgili basınç hesapları ve downstream sonuçlar stale;
- nozzle load değişirse local stress ve global review stale;
- code edition değişirse bütün code-dependent sonuçlar stale.

## 12. Veri modeli

En az aşağıdaki varlıkları tasarla:

### 12.1 Proje ve sürüm

- `Project`
- `ProjectRevision`
- `DesignBasis`
- `Jurisdiction`
- `CodeSelection`
- `Approval`
- `AuditEvent`

### 12.2 Mühendislik varlıkları

- `PressureChamber`
- `VesselGeometry`
- `ShellCourse`
- `Head`
- `Cone`
- `FlatCover`
- `MaterialAssignment`
- `WeldJoint`
- `NDERecord`
- `HeatTreatmentRecord`
- `Nozzle`
- `Opening`
- `ReinforcementPad`
- `Flange`
- `Gasket`
- `Bolting`
- `Support`
- `AnchorGroup`
- `InternalAttachment`
- `InsulationLining`
- `FluidCase`
- `LoadCase`
- `LoadCombination`
- `ExternalLoad`

### 12.3 Hesap ve belge varlıkları

- `CalculationRun`
- `CalculationInputSnapshot`
- `CalculationResult`
- `IntermediateValue`
- `CodeReference`
- `SourceDocument`
- `ValidationRecord`
- `ReviewComment`
- `Artifact`
- `ReportRevision`

### 12.4 CalculationResult minimum alanları

```json
{
  "calculation_id": "CALC-SHELL-UG27-001",
  "engine_version": "x.y.z",
  "standard": "ASME BPVC VIII-1",
  "edition": "2025",
  "paragraph": "UG-27...",
  "formula_key": "verified_internal_id",
  "load_case_id": "OPERATING-01",
  "reference_elevation_mm": 0,
  "input_snapshot_hash": "...",
  "material_source": "...",
  "allowable_stress_mpa": 0,
  "joint_efficiency": 0,
  "corrosion_allowance_mm": 0,
  "intermediate_values": [],
  "result_value": 0,
  "result_unit": "mm",
  "utilization": 0,
  "status": "PASS",
  "governing": false,
  "validity_checks": [],
  "warnings": [],
  "verified_by": null,
  "created_at": "ISO-8601"
}
```

## 13. API tasarımı

REST veya mevcut proje yaklaşımına uyumlu API kur. En az:

- `POST /projects`
- `GET/PATCH /projects/{id}`
- `POST /projects/{id}/revisions`
- `PUT /projects/{id}/design-basis`
- `PUT /projects/{id}/geometry`
- `PUT /projects/{id}/materials`
- `PUT /projects/{id}/welds`
- `POST /projects/{id}/nozzles`
- `POST /projects/{id}/supports`
- `PUT /projects/{id}/load-cases`
- `POST /projects/{id}/calculations/{module}/run`
- `POST /projects/{id}/calculations/run-all-valid`
- `GET /projects/{id}/calculations`
- `GET /projects/{id}/mawp-envelope`
- `GET /projects/{id}/compliance/ped`
- `POST /projects/{id}/cad/step`
- `POST /projects/{id}/reports/pdf`
- `POST /projects/{id}/reviews`
- `POST /projects/{id}/approvals`

Kurallar:

- Sunucu girdileri Pydantic/typed schema ile doğrulasın.
- API idempotency ve revision concurrency kontrolü kullansın.
- Onaylı revizyon sessizce değiştirilemesin.
- Hesap isteği eksik girdilerde 500 vermesin; yapılandırılmış blocking reason dönsün.
- Uzun CAD/PDF/FEA işleri job olarak çalışsın; durum ve hata kayıtları olsun.

## 14. Kullanıcı arayüzü

### 14.1 Ana sayfalar

1. Dashboard ve proje listesi.
2. Yeni proje/kapsam sihirbazı.
3. Design basis.
4. Geometry editor.
5. Materials.
6. Welds, NDE, PWHT.
7. Nozzles/manways/couplings.
8. Supports and loads.
9. Calculation workspace.
10. MAWP/test/relief.
11. PED/CE compliance.
12. 3D model.
13. Documents/report.
14. Review and approval.
15. Standards/data administration.

### 14.2 Form davranışı

- Her girdi adı, sembol, birim ve kısa açıklama göstermeli.
- Yardım görseli, ölçünün nereden alındığını belirtmeli.
- Varsayılan değer mühendislik varsayımıysa açıkça işaretlenmeli ve kullanıcı onayı istenmeli.
- Zorunlu eksik girdiler üst özet ve ilgili sekmede gösterilmeli.
- Çap/radyus, iç/dış, nominal/actual gibi karışabilecek alanlarda açık seçim kullanılmalı.
- Gerçek zamanlı fakat debounce edilmiş yeniden hesaplama.
- Stale, blocked, review-required ve failed durumları farklı görsel dil kullanmalı.
- Kullanıcı sonucu manuel override ederse neden, kişi, zaman ve orijinal değer saklanmalı; override hesap sonucuymuş gibi gösterilmemeli.

### 14.3 Hesap sonucu kartı

Her kart:

- sonuç;
- allowable/required;
- utilization/margin;
- PASS/FAIL;
- governing badge;
- load case;
- standard edition ve paragraph;
- kullanılan S/E/CA;
- ara hesapları aç/kapat;
- validity limits;
- warnings;
- source/license status;
- review state

göstermelidir.

### 14.4 Mühendislik görselleri

- Shell/head ölçü şemaları.
- Nozzle reinforcement kesiti ve alan renkleri.
- Nozzle load axes.
- Support reaction arrows.
- MAWP component bar/list comparison.
- Load-case envelope.
- Vessel 3D modelinde seçilebilir component ve status renkleri.

Grafik, hassas hesap tablosunun yerine geçmez; tam değerler erişilebilir olmalıdır.

## 15. Parametrik CAD ve STEP

### 15.1 CAD girdileri

Hesap ve CAD tek proje modelini kullanmalı. CAD’e ayrı elle veri girilmemeli.

### 15.2 İlk sürüm geometri

- cylindrical shell;
- 2:1 ellipsoidal, torispherical, hemispherical heads;
- flat cover;
- radial nozzles;
- flange/coupling;
- reinforcement pad;
- legs, skirt veya saddles;
- temel iç aksam için placeholder.

### 15.3 CAD kuralları

- Geometri başarısız olursa calculation data kaybolmasın.
- Boolean çakışmalar, çok yakın nozzles, sıfır kalınlık ve self-intersection doğrulansın.
- Nozzle konumu vessel coordinate system ile tanımlansın.
- Nominal ve corroded geometry ayrı kavram olsun; STEP nominal imalat geometrisini temsil etsin.
- Her component kalıcı ID ve metadata taşısın.
- STEP export sürümü, CAD kernel sürümü ve input snapshot hash saklansın.
- CAD volume/weight, bağımsız hesap modülüyle tolerance içinde karşılaştırılsın.

## 16. PDF rapor ve belge üretimi

PDF en az şunları içermeli:

1. Kapak, proje/revizyon/kişi/tarih.
2. Tasarım basis ve kapsam.
3. Kodlar ve baskılar.
4. Girdi özeti.
5. Geometri ve genel düzen görseli.
6. Malzeme tablosu.
7. Weld/NDE/PWHT özeti.
8. Load cases ve combinations.
9. Her hesap modülünün girdi–ara değer–sonuç–referans bölümü.
10. Component/global MAWP.
11. Hydro/pneumatic test.
12. Nozzle schedule ve reinforcement sonuçları.
13. Support/load sonuçları.
14. Relief özeti.
15. PED/CE classification ve ESR gap listesi.
16. PASS/FAIL/blocked/review-required özeti.
17. Varsayımlar ve sınırlamalar.
18. Doğrulama kayıtları.
19. Revizyon geçmişi.
20. Hazırlayan/kontrol eden/onaylayan imza alanları.

Telifli standardın tam paragrafını rapora kopyalama. Standardı, baskıyı ve kesin referansı göster; kullanıcının lisanslı dokümana yönelmesini sağla.

## 17. AI orkestrasyon katmanı

AI’nın izin verilen görevleri:

- doğal dilden proje taslağı oluşturmak;
- alanları yapılandırılmış schema’ya eşlemek;
- eksik/çelişkili girdileri sormak;
- hangi hesap modülünün çalışması gerektiğini seçmek;
- deterministik API’yi çağırmak;
- sonuçları sade dille açıklamak;
- yöneten bileşeni, uyarıları ve sonraki işi özetlemek;
- kaynak ve paragraf referansını göstermek;
- PDF/CAD job’ını başlatmak.

AI’nın yasak görevleri:

- kendi hafızasından `S`, chart coefficient veya code table değeri uydurmak;
- eksik `E`, CA, MDMT veya load case için sessiz varsayım yapmak;
- deterministik motor dışında nihai kalınlık/MAWP/test sonucu üretmek;
- FAIL’i kullanıcıyı memnun etmek için PASS’e çevirmek;
- “ASME/CE onaylı” iddiası üretmek;
- lisanssız standardı yeniden dağıtmak.

Her AI yanıtında result provenance ve blocking reason korunmalıdır. Tool output doğrulanmadan serbest metin sonucu yazılmamalıdır.

## 18. Doğrulama ve test stratejisi

### 18.1 Test katmanları

- unit tests;
- property-based tests;
- dimensional consistency;
- boundary/validity tests;
- regression tests;
- API integration;
- database migration;
- UI end-to-end;
- CAD geometry;
- PDF visual/content;
- security/permission;
- performance.

### 18.2 Golden cases

- ASME PTB-4 Division 1 örnekleri;
- ASME PTB-3 Division 2 örnekleri;
- 2025 edition değişiklik incelemesi;
- lisanslı elle çözülmüş şirket örnekleri;
- bağımsız mühendis kontrolü;
- uygun olduğunda güvenilir ticari yazılımla benchmark.

PTB-4 2021’in 2025 koduyla aynı olduğunu varsayma. Önce edition delta analizi yap ve golden case’e hangi hükmün uygulandığını kaydet.

### 18.3 Her formül için minimum test seti

- tipik PASS;
- tipik FAIL;
- sınır değerin hemen altı/üstü;
- minimum/maximum geometri;
- birim sistemi değişimi;
- CA=0 ve CA>0;
- E değişimi;
- sıcaklık/material S değişimi;
- invalid denominator;
- missing input;
- out-of-scope;
- forward/inverse consistency;
- rounding.

### 18.4 Bilgisayar programı doğrulaması

ASME/National Board rehberinin bilgisayar hesabının doğru fiziksel çözüm üretebildiğinin gösterilmesi beklentisini dikkate al. Validation pack şunları içersin:

- software requirements;
- formula/spec review;
- test evidence;
- discrepancy log;
- independent checker sign-off;
- version/release record;
- known limitations;
- change impact analysis.

## 19. Güvenlik, yetki ve veri bütünlüğü

- RBAC: drafter, engineer, checker, approver, admin.
- Tenant isolation.
- Audit log append-only yaklaşımı.
- Approved revision immutability.
- Secure file upload ve type/size scanning.
- Secrets yalnızca environment/secret manager.
- Calculation job reproducibility.
- Database backup/restore.
- PII ve şirket teknik verileri için erişim kontrolü.
- Exported PDF/STEP’e proje/revizyon/hash metadata.
- Değişen standard/material data için admin review ve release.
- AI/tool action tracing.
- Kritik onaylarda human-in-the-loop.

## 20. Aşamalı uygulama planı

Bütün modülleri aynı commit’te geliştirme. Aşağıdaki fazları sırayla uygula. Her fazın sonunda çalışan kod, test, araştırma kaydı, demo ve gap listesi ver.

### Faz 0 — Audit, kapsam ve temel mimari

- repo denetimi;
- RTM;
- standard selection tree;
- domain model;
- unit system;
- calculation result contract;
- source/license registry;
- risk register;
- implementation roadmap.

Kabul: Henüz mühendislik sonucu üretmeden bütün dependencies ve blockers görünür.

### Faz 1 — Geometri, hacim, ağırlık ve proje girişi

- project wizard;
- design basis;
- cylinder/head geometry;
- volume;
- basic weight/CG;
- unit conversion;
- 3D preview skeleton.

Kabul: Analitik geometri testleri ve CAD karşılaştırması geçer.

### Faz 2 — Malzeme, weld/NDE ve UG-27 MVP

- controlled material input;
- S source;
- weld joint/E;
- CA/tolerance chain;
- UG-27 thickness ve shell MAWP;
- calculation card;
- PDF first calculation page.

Kabul: Lisanslı örneklerle doğrulanmış, eksik S/E’de bloke olan ilk uçtan uca hesap.

### Faz 3 — Başlıklar, düz kapaklar ve component MAWP

- UG-32/ilgili head types;
- UG-34 flat cover;
- component MAP/MAWP;
- governing component altyapısı.

Kabul: Shell+heads+cover için completeness kontrolü ve global sonucun eksik component’te bloke olması.

### Faz 4 — Global MAWP ve hidro/pnömatik test

- common reference elevation;
- static head normalization;
- UG-98;
- UG-99/UG-100;
- test stress ve temperature ratio;
- test data sheet.

Kabul: Top/bottom gauge ve component MAWP tutarlı; eksik LSR/material data’da blokaj.

### Faz 5 — Nozullar, manşonlar ve açıklık takviyesi

- B36/B16/MSS catalog;
- nozzle placement;
- UG-36–42 reinforcement;
- UG-43/45 ve UW-16;
- weld/neck checks;
- nozzle schedule;
- CAD nozzle/STEP.

Kabul: Alan bileşenleri açıklanmış, yakın opening ve validity checks mevcut.

### Faz 6 — Flanşlar, conta ve civata

- B16 rating;
- gasket/bolting;
- custom flange workflow;
- PCC-1 assembly record.

Kabul: Class’ın basınç gibi yorumlanmadığı ve material-temperature tabanlı rating.

### Faz 7 — Dış basınç ve stiffener

- UG-28–30;
- licensed external-pressure data adapter;
- vacuum;
- ring design.

Kabul: Lisanslı veri yoksa blocked; chart interpolation boundary testleri geçer.

### Faz 8 — Supports ve external loads

- weight/load case engine;
- leg/skirt/saddle/lug;
- wind/seismic/transport/lifting;
- anchor/base plate;
- WRC/FEA routing.

Kabul: Reactions equilibrium kontrolü; local shell analysis route; governing load combination.

### Faz 9 — Nozzle external load ve advanced analysis

- 6-component loads;
- coordinate transforms;
- WRC 537/297;
- VIII-2 Part 5/FEA adapter;
- stress combination.

Kabul: Applicability limits ve reference solution benchmark.

### Faz 10 — MDMT, fatigue, relief ve özel servis

- UCS-66 path;
- impact/PWHT;
- cyclic screening;
- Section XIII;
- API 520/521 optional process adapter.

Kabul: Eksik process scenario’da relief sizing tamamlanmış görünmez.

### Faz 11 — PED/CE ve EN 13445

- PED/SPVD scope;
- classification;
- conformity modules;
- ESR checklist/gap;
- EN 13445 plugin boundary;
- technical file.

Kabul: ASME sonucu CE sonucu gibi gösterilmez; kategori karar izi vardır.

### Faz 12 — Kurumsal kalite, AI, rapor ve release

- AI orchestration;
- approvals;
- audit;
- final PDF;
- STEP;
- validation pack;
- security;
- release/version migration.

Kabul: Bir proje baştan sona oluşturulabilir, eksikler bloke edilir, hesaplar tekrarlanabilir, rapor/CAD aynı revision’a bağlıdır.

## 21. Her fazda izleyeceğin çalışma döngüsü

Her faz için sırayla:

1. Resmî/lisanslı kaynak araştırması.
2. `research_spec`.
3. RTM güncellemesi.
4. Girdi/çıktı ve validity contract.
5. Elle doğrulanmış örnek.
6. Saf hesap fonksiyonu.
7. Unit/property/boundary tests.
8. API.
9. UI.
10. PDF/CAD entegrasyonu.
11. Independent review.
12. Demo ve discrepancy list.
13. Documentation.
14. Release note.

Bir aşamada kaynak veya kullanıcı kararı eksikse bunu açık blocker olarak bildir; tahminle devam edip mühendislik sonucunu tamamlanmış gösterme.

## 22. Definition of Done

Bir modül ancak şu koşulların tamamında “Done” olabilir:

- RTM satırları tamamlandı.
- Standard edition ve exact paragraph doğrulandı.
- Formül, semboller ve validity limits mühendis tarafından incelendi.
- Telif/lisans yolu uygun.
- Typed input/output var.
- Unit conversion testli.
- Missing/invalid/out-of-scope davranışı var.
- Golden ve boundary tests geçiyor.
- API ve UI aynı engine’i kullanıyor.
- PDF’ye doğru provenance ile gidiyor.
- Audit ve revision davranışı çalışıyor.
- Güvenlik kontrolü yapıldı.
- Known limitations kullanıcıya görünür.
- Independent checker onayı kayıtlı.

## 23. Bana her çalışma turunda vereceğin yanıt biçimi

Her yanıtta şu sırayı kullan:

1. **Sonuç:** Bu turda ne tamamlandı?
2. **Kanıt:** Hangi dosya/test/demo bunu doğruluyor?
3. **Mühendislik dayanağı:** Standard, edition, paragraph ve source.
4. **Değişiklikler:** Dosya bazında kısa özet.
5. **Testler:** Çalıştırılan komut ve sonuç.
6. **Eksikler/blockers:** Lisanslı veri veya karar ihtiyacı.
7. **Riskler:** Yanlış kullanım ve validity sınırları.
8. **Sonraki adım:** Dependency sırasına göre tek net hedef.

İlk yanıtında kod yazma. Önce mevcut repo audit’i, kapsam karar ağacı, RTM taslağı, risk register ve Faz 0 uygulama planını sun.

## 24. Resmî ve birincil kaynak bağlantıları

Araştırmaya bu bağlantılardan başla. Sayfa üzerindeki baskı ve adopted-edition bilgisini proje tarihinde yeniden doğrula.

### 24.1 ASME BPVC ana kaynakları

- [2025 ASME Boiler and Pressure Vessel Code](https://www.asme.org/codes-standards/bpvc-standards/bpvc-2025)
- [ASME BPVC genel kaynak sayfası](https://www.asme.org/codes-standards/bpvc-standards)
- [BPVC Section VIII Division 1](https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1)
- [BPVC Section VIII Division 2](https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-2-bpvc-section-viii-rules-construction-pressure-vessels-division-2-alternative-rules-%281%29)
- [BPVC Section VIII Division 3](https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-3-bpvc-section-viii-rules-construction-pressure-vessels-division-3-alternative-rules-construction-high-pressure-vessels)
- [BPVC Section V — Nondestructive Examination](https://www.asme.org/codes-standards/find-codes-standards/bpvc-v-bpvc-section-v-nondestructive-examination)
- [BPVC Section IX — Welding, Brazing and Fusing Qualifications](https://www.asme.org/codes-standards/find-codes-standards/bpvc-ix-bpvc-section-ix-welding-brazing-fusing-qualifications)
- [BPVC Section XIII — Overpressure Protection](https://www.asme.org/codes-standards/find-codes-standards/bpvc-xiii-bpvc-section-xiii-rules-overpressure-protection)
- [ASME BPVC Resources — stress tables, code cases, interpretations, errata/notices](https://www.asme.org/codes-standards/publications-information/bpvc-resources)
- [ASME Required Code Books — U/UM/U2/U3 kapsamı](https://www.asme.org/certification-accreditation/asme-certification-process/required-code-books)
- [ASME Boiler and Pressure Vessel Certification](https://www.asme.org/certification-accreditation/boiler-and-pressure-vessel-certification)
- [ASME CA-1 — Conformity Assessment Requirements](https://www.asme.org/codes-standards/find-codes-standards/conformity-assessment-requirements)
- [ASME QAI-1 — Qualifications for Authorized Inspection](https://www.asme.org/codes-standards/find-codes-standards/qualifications-for-authorized-inspection)
- [National Board & ASME Guide NB-57 Rev. 14, March 2026](https://www.asme.org/getmedia/a47cf2d3-7f22-4359-8992-2dd1f1bb8710/NB-57-Rev-14_03-26.pdf)
- [ASME/National Board downloadable resources](https://www.asme.org/certification-accreditation/resources-and-events/downloadable-resources)

NB-57 bir rehberdir; Code ile çelişirse lisanslı Code metni üstündür.

### 24.2 Malzeme kaynakları

- [BPVC Section II Part A — Ferrous Materials](https://www.asme.org/codes-standards/find-codes-standards/bpvc-iia-bpvc-section-ii-materials-part-ferrous-materials-specifications)
- [2025 BPVC listesi — Section II A/B/C/D bağlantıları](https://www.asme.org/codes-standards/bpvc-standards/bpvc-2025)
- [ASTM A106/A106M resmî sayfa](https://store.astm.org/a0106_a0106m-19a.html)
- [ASTM A312/A312M resmî sayfa](https://store.astm.org/a0312_a0312m-25.html)
- [ASTM A105/A105M resmî sayfa](https://store.astm.org/a0105_a0105m-21.html)
- [ASTM A182/A182M resmî sayfa](https://store.astm.org/a0182_a0182m-21.html)

ASTM bağlantıları ürün kapsamını anlamak içindir. Üretim hesabında ASME 2025’in benimsediği SA/SB spesifikasyon baskısını ve Section II-D verisini doğrula.

### 24.3 Pipe, fitting, thread, flange ve gasket

- [ASME B36.10M — Welded and Seamless Wrought Steel Pipe](https://www.asme.org/codes-standards/find-codes-standards/b36-10m-welded-seamless-wrought-steel-pipe)
- [ASME B36.19M — Stainless Steel Pipe](https://www.asme.org/codes-standards/find-codes-standards/b36-19m-stainless-steel-pipe)
- [ASME B36.19 — 2022 ve errata ürün sayfası](https://www.asme.org/codes-standards/find-codes-standards/welded-and-seamless-wrought-stainless-steel-pipe-%28w-5-23-errata%29)
- [ASME B16.11 — Forged Fittings, Socket-Welding and Threaded](https://www.asme.org/codes-standards/find-codes-standards/b16-11-forged-fittings-socket-welding-threaded)
- [ASME B1.20.1 — Pipe Threads, General Purpose, Inch](https://www.asme.org/codes-standards/find-codes-standards/b1201-pipe-threads-general-purpose-inch)
- [MSS SP-97 — Integrally Reinforced Forged Branch Outlet Fittings](https://msshq.org/page/SP97)
- [MSS aktif standart listesi](https://msshq.org/page/ActiveStandards)
- [ASME B16.9 — Factory-Made Wrought Buttwelding Fittings](https://www.asme.org/codes-standards/find-codes-standards/b16-9-factory-made-wrought-buttwelding-fittings)
- [ASME B16.25 — Buttwelding Ends](https://www.asme.org/codes-standards/find-codes-standards/b16-25-buttwelding-ends)
- [ASME B16.5 — Pipe Flanges NPS 1/2 through NPS 24](https://www.asme.org/codes-standards/find-codes-standards/b16-5-pipe-flanges-flanged-fittings-nps-1-2-nps-24-metric-inch-standard)
- [ASME B16.47 — Large Diameter Steel Flanges NPS 26 through NPS 60](https://www.asme.org/codes-standards/find-codes-standards/b16-47-large-diameter-steel-flanges-nps-26-nps-60-metric-inch-standard)
- [ASME B16.20 — Metallic Gaskets](https://www.asme.org/codes-standards/find-codes-standards/b16-20-metallic-gaskets-pipe-flanges)
- [ASME B16.21 — Nonmetallic Flat Gaskets](https://www.asme.org/codes-standards/find-codes-standards/b16-21-nonmetallic-flat-gaskets-pipe-flanges)
- [ASME PCC-1 — Pressure Boundary Bolted Flange Joint Assembly](https://www.asme.org/codes-standards/find-codes-standards/pressure-boundary-bolted-flange-joint-assembly)

### 24.4 Supports, local stress ve advanced analysis

- [ASME Digital Collection — Section VIII Division I companion chapter](https://asmedigitalcollection.asme.org/ebooks/book/243/chapter/25139998/Section-VIII-Division-I-Rules-for-Construction-of)
- [ASME paper — Stresses in Nozzle Shell Junctions due to External Loads](https://asmedigitalcollection.asme.org/PVP/proceedings/PVP2013/55645/V01BT01A062/283162)
- [ASME paper — simplified permissible external-load approach](https://asmedigitalcollection.asme.org/PVP/proceedings/PVP2023/87455/V002T03A066/1171371)

WRC 537/297’nin lisanslı nüshasını yetkili satıcıdan/kurumsal kütüphaneden temin et; üçüncü taraf izinsiz PDF kopyalarını kullanma.

### 24.5 Doğrulama örnekleri

- [ASME PTB-4 — Section VIII Division 1 Example Problem Manual](https://www.asme.org/codes-standards/find-codes-standards/asme-section-viii-division-1-example-problem-manual)
- [ASME PTB-3 — Section VIII Division 2 Example Problem Manual](https://www.asme.org/codes-standards/find-codes-standards/asme-section-viii-division-2-example-problem-manual)

### 24.6 Piping, repair ve relief yardımcı standartları

- [ASME B31.3 — Process Piping](https://www.asme.org/codes-standards/find-codes-standards/b313-2018-process-piping)
- [ASME PCC-2 — Repair of Pressure Equipment and Piping](https://www.asme.org/codes-standards/find-codes-standards/repair-of-pressure-equipment-and-piping)
- [API 520 Part I — pressure-relieving device sizing and selection](https://www.api.org/products-and-services/standards/important-standards-announcements/520parti)
- [API 520 Part II — installation](https://www.api.org/products-and-services/standards/important-standards-announcements/520part-ii)
- [API 521 — Pressure-Relieving and Depressurizing Systems](https://www.api.org/products-and-services/standards/important-standards-announcements/standard521)
- [API 579-1/ASME FFS-1 genel resmî bilgi](https://www.api.org/products-and-services/training/calendar/equity-technical-institute-fitness-for-service)

### 24.7 PED, Türkiye ve EN 13445

- [European Commission — Pressure Equipment Directive](https://single-market-economy.ec.europa.eu/sectors/pressure-equipment-and-gas-appliances/pressure-equipment-sector/pressure-equipment-directive_en)
- [EUR-Lex — Directive 2014/68/EU](https://eur-lex.europa.eu/eli/dir/2014/68/oj/eng)
- [EUR-Lex — PED resmî özet](https://eur-lex.europa.eu/EN/legal-content/summary/safety-of-pressure-vessel-equipment-and-assemblies.html)
- [European Commission — current harmonised standards bağlantısı PED sayfası içinde](https://single-market-economy.ec.europa.eu/sectors/pressure-equipment-and-gas-appliances/pressure-equipment-sector/pressure-equipment-directive_en)
- [CEN-CENELEC — Pressure equipment ve CEN/TC 54](https://www.cencenelec.eu/areas-of-work/cen-sectors/mechanical-and-machines-cen/pressure-equipment-vessels-tanks-reservoirs-containers/)
- [Türkiye Ticaret Bakanlığı — Basınçlı Kaplar ürün kuralları](https://urunkurallari.ticaret.gov.tr/tr/sektorel-rehber/basincli-kaplar)

### 24.8 Özel ekipman kapsamı

- [ASME PVHO-1 — Pressure Vessels for Human Occupancy](https://www.asme.org/codes-standards/find-codes-standards/safety-standard-for-pressure-vessels-for-human-occupancy)

## 25. Son kalite kontrol listesi

Uygulamayı teslim etmeden önce aşağıdakilerin her birini cevapla:

- Tasarım basıncı proses girdisi olarak mı alınıyor?
- Gauge/absolute ayrımı hatasız mı?
- Her component için doğru net kalınlık mı kullanılıyor?
- CA/tolerance/forming payları çift sayılmış mı?
- S doğru material/product form/temperature/note’tan mı?
- E doğru weld category/joint/NDE’den mi?
- Formula validity limits çalışıyor mu?
- Static head doğru reference elevation’a mı uygulanıyor?
- Global MAWP bütün geçerli component’leri kapsıyor mu?
- Eksik flat cover/nozzle/flange varken global sonuç bloke oluyor mu?
- Hydrotest LSR ve static head doğru mu?
- External pressure lisanslı chart data ile mi?
- UG-37 ile nozzle external load birbirinden ayrılmış mı?
- Support reaction equilibrium sağlıyor mu?
- Local shell stress yöntemi applicability sınırında mı?
- Class ve Schedule yanlış pressure rating gibi kullanılmıyor mu?
- PED ve ASME sonuçları ayrı mı?
- SPVD/PED karar ağacı var mı?
- AI yalnızca deterministik motor sonucunu mu anlatıyor?
- PDF ve STEP aynı revision/hash’e mi bağlı?
- Her PASS’in source, paragraph, inputs ve engine version kaydı var mı?
- Lisanslı veri yoksa hesap gerçekten bloke oluyor mu?
- Unit, boundary, regression ve golden tests geçiyor mu?
- Yetkili mühendis/inspector/notified body sorumluluğu doğru belirtilmiş mi?

Bu kalite kontrolün herhangi bir maddesi “hayır” ise modülü üretime hazır ilan etme.

# PROMPT SONU
