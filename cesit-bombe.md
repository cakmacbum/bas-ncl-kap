# Çok Elemanlı Basınçlı Kap Tasarımı — Araştırma ve Uygulama Planı

Tarif edilen tasarım teknik olarak farklı çaplı silindirik gövdelerin konik geçişlerle bağlandığı **çok elemanlı / stacked pressure vessel** modelidir:

```text
Alt bombe
   ↓
Büyük çaplı silindir
   ↓
Konik redüksiyon
   ↓
Küçük çaplı silindir
   ↓
Küçük üst bombe
```

PV Elite kabı tek bir silindir olarak değil; bombe, silindir, koni, gövde flanşı ve etek gibi elemanların aşağıdan yukarıya veya soldan sağa sıralandığı bir eleman zinciri olarak modeller.

Kaynaklar:

- [PV Elite Modeling Basics](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/27/304285)
- [PV Elite Elements Panel](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/27/320186)

## 1. Mevcut projenin durumu

Proje bu konuda tamamen sıfır noktada değildir:

- `Cone` domain modeli `packages/domain/src/domain/geometry.py` içinde bulunmaktadır.
- `VesselProject`, birden fazla gövde, bombe ve koni listesi tutabilmektedir.
- Hesap orkestratörü bütün koniler için kalınlık ve MAWP hesabını çağırmaktadır.
- ASME tarafında temel koni kalınlığı ve MAWP formülleri bulunmaktadır.

Ancak mevcut parçalar gerçek bir kap dizisi oluşturmamaktadır:

- Elemanların hangi sırayla bağlandığını belirten bir topoloji yoktur.
- Arayüzde koni veya ikinci silindir ekleme formu yoktur.
- 2B ve 3B önizleme ilk silindir ile iki bombe varsayımına bağlıdır.
- CAD motoru yalnızca `shell_sections[0]` ve iki bombeyi kullanmaktadır.
- Koni–silindir birleşimlerinin büyük ve küçük uç takviye kontrolleri bulunmamaktadır.
- Koniler için tam dış basınç, takviye halkası ve geçiş bombesi/knuckle hesabı eksiktir.
- UI eşdeğerlik testi, koni formunun henüz kullanıcıya açılmadığını açıkça kaydetmektedir.

### Hesap yolundaki ilk-eleman kısayolları

CAD ve önizlemenin ilk silindir varsayımına ek olarak, hesap yolunda da çok elemanlı kapta
sessizce yanlış sonuç üretebilecek ilk-eleman kısayolları bulunmaktadır:

| Yer | Sorun |
|---|---|
| `design_code.py:643, 734` | Hidrotest/pnömatik test hesabı `materials[0]` kullanıyor; çok malzemeli kapta yanlış `S` ve yanlış test basıncı üretebilir. |
| `design_code.py:943` | Kaynak doğrulamasında referans kalınlık `shell_sections[0]` olarak alınıyor. |
| `design_code.py:1029` | Destek hesabı `shell_sections[0]`'a bağlı. |
| `design_code.py:1172` | Vakum kontrolü `shell_sections[0]` üzerinden yapılıyor. |
| `pages.tsx:265, 273, 275` | UI diziyi tek elemanla değiştiriyor (`setShell`/`setMat`/`setWeld`). |

Özellikle `pages.tsx` deseni kritik bir entegrasyon ön koşuludur: eleman düzenleyici (§3.7)
yazılırken temizlenmezse, kullanıcı ikinci silindiri ekleyip ilk silindirde bir alanı
düzenlediğinde ikinci silindir silinebilir. Bu sorun §3.7'nin sonrasına bırakılamaz.

İlgili mevcut dosyalar:

- `pressure-vessel-suite/packages/domain/src/domain/geometry.py`
- `pressure-vessel-suite/packages/domain/src/domain/project.py`
- `pressure-vessel-suite/packages/calc-core/src/calc_core/orchestrator.py`
- `pressure-vessel-suite/packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py`
- `pressure-vessel-suite/packages/cad-engine/src/cad_engine/vessel_builder.py`
- `pressure-vessel-suite/tests/wiring/test_ui_parity.py`

## 2. Kritik mühendislik ayrımı

Mevcut temel koni kalınlığı hesabı tek başına yeterli değildir.

PV Elite'in konik bölüm modülü şu kontrolleri ayrı ayrı ele alır:

- Koni kalınlığı ve MAWP
- Bağlı iki silindirin kalınlığı
- Büyük ve küçük uçtaki birleşimler
- Koni–silindir birleşim takviyesi
- Knuckle varsa knuckle kalınlığı
- İç ve dış basınç
- Takviye veya stiffening ring

Kaynaklar:

- [PV Elite Conical Sections](https://docs.hexagonppm.com/r/3pz7tgHsJkyFtCf0SJpwvA/Dyv5THU6aQIQ9j82gKnLYg)
- [Reinforcement Calculations Under Internal Pressure](https://docs.hexagonppm.com/r/VqN90f5oNrm6UKoRKjxhBA/nv375AOlNML8CR0ZEdaV7w)

Özellikle koninin büyük ve küçük uçlarında, koniden gelen radyal yük nedeniyle burkulma eğilimi oluşabilir. Bu nedenle yalnızca “koni sacı yeterince kalın mı?” değil, “koni–silindir birleşimi yeterli mi?” sorusu da cevaplanmalıdır.

### Kaynak hesabının kapsamı

“Kaynak hesabı” tek bir kontrol değildir:

1. Boyuna kaynak veriminin parça kalınlığı hesabına etkisi
2. Koni–silindir çevresel birleşim kaynağının verimi, NDE ve PWHT durumu
3. Takviye halkası, nozul veya bağlantı kaynaklarının gerçek kaynak kesiti ve dayanımı

PV Elite koni–silindir çevresel birleşim verimini ayrıca tanımlar:

- [Cone Circumferential Joint Efficiency](https://docs.hexagonppm.com/r/en-US/CodeCalc-Help/26/309758)

## 3. Önerilen uygulama planı

### 3.1. Eleman zinciri ve topoloji modeli

Mevcut ayrı `shell_sections`, `heads` ve `cones` listelerinin üzerine açık bir sıralama modeli eklenmelidir:

```text
NODE-0 ─ HEAD-01  ─ NODE-1
NODE-1 ─ SHELL-01 ─ NODE-2
NODE-2 ─ CONE-01  ─ NODE-3
NODE-3 ─ SHELL-02 ─ NODE-4
NODE-4 ─ HEAD-02  ─ NODE-5
```

Her eleman için en az şu bilgiler tutulmalıdır:

- Eleman kimliği ve tipi
- Başlangıç ve bitiş düğümü
- Başlangıç ve bitiş çapı
- Eksenel uzunluk
- Et kalınlığı
- Malzeme
- İç ve dış korozyon payı
- Boyuna kaynak
- İç ve dış basınç şartları

İlk sürüm yalnızca aynı eksenli, konsantrik elemanları desteklemelidir. Eksantrik redüksiyon sonraki faza bırakılmalıdır.

### 3.2. Birleşim modeli

Parçaların kaynaklarını yalnızca parça üzerindeki tek bir `weld_joint_id` alanıyla temsil etmek yeterli değildir. Ayrı bir `Junction` modeli oluşturulmalıdır:

- Bağlanan iki eleman
- Birleşim konumu
- Kaynak kategorisi
- Kaynak tipi
- Kaynak verimi
- Radyografi/NDE kapsamı
- PWHT durumu
- Knuckle bulunup bulunmadığı
- Takviye halkası geometrisi
- Büyük veya küçük koni ucu bilgisi

Böylece aynı koninin boyuna kaynağı ile büyük ve küçük uç çevresel kaynakları birbirinden ayrılır.

### 3.3. Geometrik doğrulama

Hesaptan önce zincirin fiziksel olarak bağlanabildiği doğrulanmalıdır:

- Komşu uç çapları eşleşiyor mu?
- Bombe çapı bağlı olduğu silindire uyuyor mu?
- Koninin büyük/küçük çap yönü doğru mu?
- Koni uzunluğu, çap farkı ve yarı tepe açısı birbiriyle tutarlı mı?
- Yarı tepe açısı `α > 30°` ise torikonik geçiş (knuckle) veya özel analiz zorunlu mu?
- Yarı tepe açısı `α > 60°` ise dış basınç Appendix 1-8 kapsamı dışına çıkıyor mu?
- Eleman kimlikleri ve düğümleri benzersiz mi?
- Açıkta kalan ara uç var mı?
- Kabın iki terminal kapama elemanı var mı?

Bu iki açı eşiği sert applicability kapısıdır: `α > 30°` için sonuç `OUT_OF_SCOPE` veya
`REVIEW_REQUIRED` olmalı; `α > 60°` için Appendix 1-8 uygulanamaz ve yine
`OUT_OF_SCOPE`/`REVIEW_REQUIRED` üretilmelidir. Mevcut `Cone` modelinin 80°'ye kadar açı
kabul etmesi (`geometry.py:220-223`, `le=80`) bu mühendislik kapsamını genişletmez.

Koni için kullanıcıdan üç bağımsız geometrik değer istemek yerine çaplar ve uzunluktan açının hesaplanması daha güvenli olur. Kullanıcı açı girerse ayrıca tutarlılık kontrolü yapılmalıdır.

### 3.4. Basınç hesaplarının genişletilmesi

Her eleman kendi girdileriyle hesaplanmalıdır:

- Her silindir için ayrı iç basınç kalınlığı ve MAWP
- Her bombe için ayrı hesap
- Her koni için ayrı kalınlık ve MAWP
- Dikey kapta elemanın kotuna bağlı statik sıvı basıncı
- Her elemanın kendi malzemesi, sıcaklığı ve kaynak verimi
- Global MAWP'nin bütün geçerli bileşenler ve birleşim kontrollerinden belirlenmesi

Mevcut koni formülü, lisanslı ASME VIII-1 2025 metnine göre yeniden denetlenmelidir. ASME'nin güncel ürünü 2025 sürümüdür ve tasarımın yanında imalat, muayene, test ve sertifikasyon hükümlerini de kapsar.
Kod `UG-32(g)` atfı kullanıyor; bazı kaynaklarda aynı hüküm `UG-32(f)` olarak numaralandırılabildiğinden, bu ayrıntı lisanslı 2025 metniyle teyit edilmelidir.

- [ASME BPVC Section VIII Division 1 — 2025](https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1)

### 3.5. Koni birleşim kontrolleri

Koni birleşimleri ayrı bir hesap modülü olmalıdır:

- Büyük uç birleşimi
- Küçük uç birleşimi
- İç basınç altında gerekli takviye alanı
- Mevcut silindir ve koniden gelen kullanılabilir alan
- Ek takviye halkası alanı
- Knuckle/toroidal geçiş varsa kalınlık ve MAWP
- İç basınç birleşim hesabı (Appendix 1-5)
- Dış basınç koni–silindir birleşimi (Appendix 1-8): gerekli atalet momenti ve takviye
  Appendix 1-8'den alınmalı; bu hüküm yalnız yarı tepe açısı `α ≤ 60°` için geçerlidir.
- Her uç için bağımsız `PASS`, `FAIL` veya `REVIEW_REQUIRED`

İç basınç (Appendix 1-5) ve dış basınç (Appendix 1-8) ayrı hesaplar olarak uygulanmalıdır;
birinin sonucu diğerinin yerine geçirilemez.

PV Elite de konileri büyük ve küçük uçta ayrı ayrı değerlendirir:

- [PV Elite Optional Steps](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/27/304625)

### 3.6. Dış basınç ve global yükler

Çok parçalı dikey kaplarda yalnız basınç kalınlığı yeterli değildir. Sonraki hesap katmanı şunları kapsamalıdır:

- Her silindir ve koni için dış basınç/vakum
- Desteklenmeyen uzunlukların eleman zincirinden hesaplanması
- Stiffening ring konumları
- Her elemanın boş, işletme ve hidrotest ağırlığı
- Ağırlık merkezi
- Rüzgâr ve deprem momentleri
- Kesit bazında eksenel ve eğilme gerilmeleri
- Çap değişim noktalarındaki süreksizlik etkileri

PV Elite dış basınçta eleman uzunluklarını komşu bombeler ve rijitleştiricilerle birlikte değerlendirir:

- [PV Elite Vessel Analysis Results](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/26/304623)

### 3.7. Kullanıcı arayüzü

Geometri ekranı tek silindir formundan bir **eleman düzenleyiciye** dönüştürülmelidir:

- Bombe ekle
- Silindir ekle
- Koni/redüksiyon ekle
- Gövde flanşı ekle
- Etek ekle
- Yukarı/aşağı taşı
- Kopyala
- Sil
- Seçilen elemanın özelliklerini düzenle

Canlı önizleme her değişiklikte eleman zincirinden üretilmelidir. Bağlantı çapı uyuşmazlığı doğrudan ilgili birleşim üzerinde gösterilmelidir.

### 3.8. CAD, hacim ve nozul yerleşimi

CAD motoru tek silindir yaklaşımından çıkarılıp eksen boyunca profil oluşturan genel bir üreticiye dönüştürülmelidir:

- Silindir → sabit yarıçaplı profil
- Koni → doğrusal çap geçişi
- Bombe → parametrik eğri
- Zincir → ortak eksende sıralanmış cidar profili
- Profilin döndürülmesi → tek ve su geçirmez katı

Hacim, metal hacmi ve ağırlık eleman bazında hesaplanıp toplamlanmalıdır.

Nozullar `host_component_id + local_position` ile tutulmalıdır. İlk sürümde silindir ve bombe nozulları desteklenebilir. Koni üzerindeki nozulların hesabı hazır değilse açıkça `OUT_OF_SCOPE` sonucu üretilmelidir.

### 3.9. Geriye dönük uyumluluk

Eski projeler bozulmamalıdır. Tek silindir ve iki bombe içeren mevcut JSON otomatik olarak şu zincire dönüştürülmelidir:

```text
HEAD-L → SHELL-01 → HEAD-R
```

Birden fazla eleman içeren fakat sırası belirtilmemiş eski veri varsa sessiz tahmin yapılmamalı; proje açık bir migrasyon veya kullanıcı sıralaması istemelidir.

### 3.10. Doğrulama ve kabul kriterleri

En az şu testler eklenmelidir:

- Mevcut basit tank sonuçları sayısal olarak değişmemeli.
- `bombe → büyük silindir → koni → küçük silindir → bombe` örneği uçtan uca çalışmalı.
- Her eleman ayrı kalınlık ve MAWP sonucu üretmeli.
- Global MAWP en zayıf geçerli kontrolü göstermeli.
- Koni büyük ve küçük uç sonuçları ayrı raporlanmalı.
- Uyuşmayan çaplar hesap başlamadan reddedilmeli.
- CAD tek geçerli katı üretmeli.
- Hacim ve ağırlık analitik hesapla karşılaştırılmalı.
- API kaydet/aç işlemi eleman sırasını korumalı.
- Çok elemanlı projede tek bir alan düzenlendiğinde hiçbir eleman kaybolmamalı (regresyon testi).
- Lisanslı ASME 2025 örnekleri ve mümkünse PV Elite/COMPRESS çıktılarıyla kör karşılaştırma yapılmalı.

## 4. Önerilen uygulama sırası

1. Eleman zinciri ve birleşim domain modeli
2. Eski proje migrasyonu ve geometri doğrulama
3. Çoklu silindir, bombe ve koni iç basınç/MAWP hesapları
4. Koni büyük ve küçük uç takviye hesapları
5. Kaynak birleşimi, NDE ve PWHT modeli
6. Hacim, ağırlık ve statik sıvı basıncı
7. 2B/3B önizleme ve CAD
8. Dış basınç, stiffening ring ve global yükler
9. Raporlama ve PV Elite karşılaştırma testleri

## 5. İlk teslimatın önerilen kapsamı

İlk teslimat şu sınırlar içinde tutulmalıdır:

> Aynı eksenli, konsantrik, tek basınç odalı; bombe–silindir–koni–silindir–bombe dizisi ve iç basınç hesabı.

Bu kapsam kullanıcının tarif ettiği kabı gerçekten çalıştırır. Aşağıdaki özellikler daha sonraki fazlara bırakılabilir:

- Eksantrik koni/redüksiyon
- Çok odalı kap
- Jacket
- Koni üzerindeki nozullar
- İleri süreksizlik gerilmesi ve FEA
- ASME VIII Division 2 tasarım-by-analysis

## 6. Güvenlik ve doğrulama notu

Hexagon yardım sayfaları mimariyi ve gerekli hesap ailelerini anlamak için kullanılabilir; ancak bazı sayfalar eski ASME sürümlerine dayanmaktadır. Nihai formüller, sınırlar, istisnalar ve kabul kuralları lisanslı **ASME VIII-1 2025** metni ve yetkin bir basınçlı kap mühendisi tarafından doğrulanmadan ürün “kod uyumlu” olarak sunulmamalıdır.
