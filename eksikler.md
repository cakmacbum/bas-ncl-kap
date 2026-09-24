# Basınçlı Kap Suite — PV Elite Seviyesine Göre Ayrıntılı Teknik Boşluk Analizi

> **Denetim tarihi:** 20 Eylül 2026  
> **Hedef:** Önce güvenilir ASME VIII-1 çekirdeği, ardından aşamalı PV Elite seviyesi  
> **Kıyaslar:** Hexagon PV Elite 28 (birincil), Codeware COMPRESS ve Bentley AutoPIPE Vessel  
> **Not:** İnceleme mevcut çalışma ağacına göre yapılmış, kullanıcı değişikliklerine dokunulmamıştır.

> **Güncel durum (2026-09-23):** Aşağıdaki ilk denetim ve P0 maddeleri tarihsel başlangıç bulgularıdır.
> Bu dosyanın sonundaki **§14 Güncel çalışma ağacı denetimi** eski iddiaları yeniden sınıflandırır,
> kapatılan kod-yolu kusurlarını işaretler ve güncel çalışma ağacında saptanan yeni yüksek riskleri
> kaydeder. Bu güncelleme salt-okunur kod incelemesi ve resmi kaynak araştırmasıdır; testler
> çalıştırılmadı, yetkili standart metinleriyle normatif uygunluk incelemesi yapılmadı.

## 1. Yönetici özeti

Bu proje basit bir hesap makinesi değildir. Standarttan bağımsız domain modeli, hesap orkestratörü,
ASME VIII-1 ve EN 13445 eklentileri, PED sınıflandırması, nozul takviyesi, dış basınç, MDMT,
destekler, CAD, raporlama ve izlenebilir sonuç modeli gibi doğru mimari temeller içerir. Denetim
sırasında testler izin verilen bir geçici klasörle çalıştırılmış ve **567 test geçmiş, 1 koşullu PDF
testi atlanmıştır**.

Buna rağmen ürün bugün PV Elite veya COMPRESS ile aynı güven düzeyinde değildir. En büyük fark
formül sayısından çok şu mühendislik zincirlerinin tamamlanmamış olmasıdır:

1. **Standart seçimi uygulanmıyor:** Arayüz EN 13445 seçtirirken API her projeyi ASME VIII-1 ile
   hesaplıyor. Yanlış standardın doğruymuş gibi raporlanması mevcut en kritik kusurdur.
2. **Yaklaşık yöntemler `PASS` üretebiliyor:** MDMT, bombe dış basıncı ve bazı destek hesapları
   açıkça basitleştirilmiştir. Uyarı yazılması, nihai tasarım kararını güvenilir yapmaz.
3. **Kod/malzeme verisi kullanıcıya bırakılmıştır:** Allowable stress, akma/çekme, elastisite,
   UCS-66 eğrisi ve UG-28 A/B faktörleri doğrulanmış sürümlü veri tabanından gelmemektedir.
4. **Gerçek yük analizi eksiktir:** Rüzgâr, deprem, taşıma, kaldırma, boru/nozul yükleri, yük
   kombinasyonları, lokal gerilme ve yorulma uçtan uca bağlı değildir.
5. **Doğrulama dardır:** ASME iç basınç ve bir nozul örneğinde değerli golden testler vardır;
   EN, dış basınç, MDMT, destek, flanş, PED ve CAD için aynı düzeyde bağımsız doğrulama yoktur.

**Sonuç:** Proje dar kapsamlı ASME VIII-1 ön boyutlandırma ve yazılım geliştirme platformu olarak
umut vericidir. Yetkili mühendis incelemesi olmadan imalat, CE/PED uygunluk kararı veya resmi tasarım
raporu üretmek için hazır değildir. EN seçimi, yaklaşık `PASS` sonuçları ve manuel kod verileri
düzeltilmeden “PV Elite alternatifi” diye sunulmamalıdır.

## 2. Yöntem, olgunluk ve öncelik

### 2.1 Olgunluk ölçeği

| Seviye | Anlamı |
|---:|---|
| 0 | Kabiliyet yok |
| 1 | Veri modeli, ekran veya iskelet var; mühendislik sonucu yok |
| 2 | İzole formül/paket var; tam hatta bağlı veya normatif doğrulanmış değil |
| 3 | Domain → hesap → API → UI → rapor zincirine bağlı; kapsamı sınırlı |
| 4 | Bağımsız yayınlanmış örnekler ve sınır durumlarıyla doğrulanmış dar kapsam |
| 5 | Sürümlü kod/malzeme verisi, geniş V&V, uzman onayı ve değişiklik kontrolü |

Bir testin bulunması seviye 4 anlamına gelmez. Test kodun kendi denklemine göre yazılmışsa yalnız
implementasyonu korur; standardın doğru yorumlandığını kanıtlamaz.

### 2.2 Öncelik

| Öncelik | Kriter |
|---|---|
| **P0** | Kabul edilen girdide yanlış standarda/yaklaşıma dayanarak yanlış `PASS` riski |
| **P1** | Güvenilir ASME VIII-1/PED MVP’si için zorunlu |
| **P2** | PV Elite ile temel ticari rekabet için gerekli |
| **P3** | İleri ürün kapsamı ve farklılaştırma |

### 2.3 Kanıt sınırı

- Repo iddiaları dosya adına göre değil gerçek çağrı zincirine göre değerlendirilmiştir.
- Rakip özelliklerinde güncel resmi üretici kaynakları esas alınmıştır.
- Lisanslı ASME/EN tam metinleri sağlanmadığından bu rapor kod uygunluk sertifikası değildir.
  “Normatif teyit gerekli” maddeleri lisanslı metin ve yetkin mühendis incelemesi ister.
- Kullanıcının Basınçlı Kaplar El Kitabı, baskı/bölüm/sayfa bilgisiyle ek doğrulama kaynağı olabilir;
  güncel normatif standardın yerini tutmaz.

## 3. Gerçek kabiliyet envanteri

| Alan | Repo durumu | Olgunluk | Güvenli yorum |
|---|---|---:|---|
| ASME VIII-1 gövde iç basıncı | UG-27 iki yön, kalınlık/MAWP, golden testler | 4 dar | En güçlü bölüm |
| ASME bombeler | 2:1 eliptik, torisferik, yarım küre | 3–4 dar | Yalnız desteklenen geometri |
| Koni/düz kapak | Backend formülleri var | 2–3 | UI ve geometri seçenekleri eksik |
| EN 13445 | Gövde/bombe/test paketleri var | 2 | API ASME’ye sabit; gerçek EN sonucu değil |
| Nozul takviyesi | Radyal UG-37/40, bir yayınlanmış örnek | 4 çok dar | Eğik/büyük açıklığa uygun değil |
| Dış basınç/vakum | UI bağlı, A/B manuel, bombe yaklaşık | 2–3 | Tam UG-28/33 sayılamaz |
| MDMT | UCS-66 akışı, doğrusal kalınlık yaklaşımı | 2 | Yalnız ön kontrol |
| Destekler | Eyer/etek/ayak paketleri ve UI | 2 | Tam Zick/AISC/ankraj hesabı değil |
| Flanş | İzole Appendix 2 benzeri paket | 2 | Domain/UI/orkestratöre bağlı değil |
| Yük durumları | 15 şablon ve modeller | 1–2 | Global analiz üretmiyor |
| FEA | Geometri/yüz etiketi/adapter iskeleti | 1 | Gerçek çözüm ve kabul yok |
| Malzeme | Manuel model ve genel interpolasyon | 1–2 | Kod malzeme veri tabanı değil |
| PED | Sınıflandırma/belge paketleri | 2–3 | Ana UI/rapor akışı ve uzman onayı eksik |
| CAD | Temel STEP/STL ve 3B görünüm | 2–3 | Analiz/imalat geometrisi değil |
| Rapor | 23 bölüm HTML, traceability/hash | 3 | PDF koşullu, kapsam beyanı eksik |
| Kalıcılık | JSON yardımcıları; API bellekte | 2 | Çok kullanıcılı proje sistemi değil |

## 4. P0 — Önce kapatılması gereken riskler

### P0-01 — EN 13445 seçimi ASME VIII-1 çalıştırıyor

**Kanıt:** `apps/web-ui/src/pages.tsx` standart seçimi sunar; `apps/api/services.py` içindeki
`run_calculation()` koşulsuz `ASMEVIII1DesignCode` oluşturur.

**Risk:** Kullanıcı EN projesinde ASME sonuçlarını EN sonucu sanabilir. Proje etiketi ile gerçek
motorun farklı olması izlenebilirlik açısından da kritik uygunsuzluktur.

**Kapatma:** Standarda göre açık plugin seçimi; desteklenmeyen EN işlevinde sessiz ASME fallback
yerine `BLOCKED/NOT_CALCULATED`; API/UI/rapor motor kimliği testi; EN golden-case seti.

### P0-02 — MDMT tam UCS-66 değildir

**Kanıt:** `packages/mdmt/src/mdmt/mdmt_calc.py`, 38 mm üzeri düzeltmeyi `(t-38)×0.5` biçiminde
“basitleştirilmiş doğrusal yaklaşım” olarak tanımlar.

**Risk:** Gevrek kırılma düşük olasılıklı ama yüksek sonuçludur. Eğriyi doğrusal yaklaşıkla
değiştirmek sınırda yanlış impact-test muafiyeti/MDMT kabulü yaratabilir.

**Kapatma:** Lisanslı UCS-66/UCS-66.1 verisi, tüm muafiyet/indirimler, ürün formu, kalınlık, PWHT
ve baskı yönetimi. Tamamlanana kadar sonuç `REVIEW_REQUIRED` olmalıdır.

### P0-03 — Dış basınç tam kod yöntemi değildir

**Kanıt:** UI `A/B` faktörünü kullanıcıdan ister; `packages/external-pressure/.../formulas.py`
bombe hesabını basitleştirilmiş UG-33 olarak tanımlar. Stiffening ring uçtan uca modellenmez.

**Risk:** Burkulma; etkin boy, kusur, sıcaklık ve rijitleştiriciden güçlü etkilenir. Yanlış A/B veya
etkin boy tehlikeli bir `PASS` üretebilir.

**Kapatma:** Baskıya bağlı chart motoru, Do/t ve L/Do sınırları, iteratif rating/kalınlık, ring
atalet/aralık hesabı, tam bombe yöntemleri ve ticari/yayınlanmış karşılaştırmalar.

### P0-04 — Destek hesapları fazla basitleştirilmiştir

**Kanıt:** `packages/supports` sınırlı kapalı formüller kullanır. Ayak hesabında gerçek ayak yerleşim
yarıçapı yerine ayak çapı ve sayısından türetilen yaklaşık `r_dist` vardır; etek hesabı temel
eksenel/eğilme gerilmesiyle sınırlıdır.

**Risk:** Bolt circle, ağırlık merkezi, yatay yük, burkulma, taban plakası, ankraj, beton basıncı ve
yerel kabuk etkisi olmadan `PASS` alınabilir. Eyer paketi de tam Zick olarak bağımsız doğrulanmamıştır.

**Kapatma:** Gerçek destek koordinatları/yük yolu, tüm yük durumları, burkulma/ankraj/temel ve yerel
kontroller. O zamana kadar destek sonucu `REVIEW_REQUIRED` olmalıdır.

### P0-05 — Torisferik varsayılan emniyetsiz yönde sapabilir

`docs/limitations.md` B-06 ve golden kıyaslar, taç yarıçapı girilmezse iç çap varsayımının standart
ASME F&D dış çap yaklaşımından yaklaşık %0,5 emniyetsiz yönde sapabildiğini kaydeder.

**Kapatma:** İç/dış çap ile crown/knuckle yarıçapını açık modellemek; standart F&D seçeneğinde
doğrulanmış dış geometri; özel geometri yoksa sessiz varsayım yapmamak.

### P0-06 — Çoklu modelde bazı yollar ilk elemanı kullanıyor

UI `shell_sections[0]`, `materials[0]`, `welds[0]` üzerine kuruludur. Bazı kaynak/nozul/test yolları
ilk gövde veya malzeme basitleştirmesi yapar. Domain çoklu girdiyi kabul edip yalnız ilkini işlerse
sessiz kısmi hesap oluşur.

**Kapatma:** Ya V1 şemasını tek gövde/malzeme/kaynakla sınırlandırıp fazlasını reddetmek ya da her
bileşeni kendi malzeme, kaynak, statik kafa ve yük konumuyla değerlendirmek.

## 5. Matematik ve mühendislik boşlukları

### 5.1 İç basınç, kalınlık ve MAWP

**Güçlü taraflar:** UG-27 iki gerilme yönü, korozyon/mill tolerance kavramları, ters MAWP,
governing component ve dar kapsamta yayınlanmış PV Elite kıyasları.

| Eksik | Etki | Öncelik |
|---|---|---:|
| Dış çap form alternatifleri/App. 1-1 ve 1-4 | Ticari yazılımla sistematik fark | P1 |
| 2:1 dışı eliptik bombe | Genel elipsoid hesaplanamaz | P1 |
| Dairesel olmayan düz kapak/`Z` | UG-34 kapsamı dar | P1 |
| Koni geçiş discontinuity/U-2(g) | Büyük açı/geçişte membran hesabı yetersiz | P1 |
| Eccentric cone/reducer | Sık proses geometrileri yok | P2 |
| Çoklu çap/kesit/stacked vessel | Kolon/reaktör modeli eksik | P2 |
| Design ve rating mode ayrımı | Minimum seçim ile mevcut ekipman rating karışıyor | P2 |

### 5.2 Test basıncı ve statik sıvı yüksekliği

ASME hidro/pnömatik formülleri ve MAWP bazlı düzeltme vardır; yoğunluk girilirse statik kafa
eklenebilir. Eksikler:

- Test sıcaklığında her bileşenin ayrı stress ratio kontrolü; ilk malzeme yeterli değildir.
- Sıvı seviyesi, bileşen kotu ve nozzle elevation ilişkisi tam değildir.
- Empty/operating/flooded/hydrotest konfigürasyonları ayrı yük durumları değildir.
- Yeni ve korozyonlu durum için bütünsel hydrotest stress kontrolü yoktur.
- Pnömatik test enerji/risk ve prosedür kontrolleri yoktur.

### 5.3 Nozul ve açıklıklar

| Kabiliyet | Proje | Rakip seviyesi | Boşluk |
|---|---|---|---|
| Radyal takviye | Var, dar doğrulanmış | Var | Güçlü başlangıç |
| Eğik/hillside | Açı var, takviyede `F=1` | Chord/governing planes | Gerçek yöntem yok |
| Büyük açıklık | Yok | App. 1-7 ve eşdeğerleri | Mevcut yöntem yetersiz |
| Yakın/çoklu açıklık | Geometrik clash | Kod interaction | Clash kod yeterliliği değildir |
| Boyun minimumu | Basit UG-45(a) | Tam tablo/schedule | Normatif veri eksik |
| Kaynak dayanımı | Kısmi | Ayrıntılı weld size/strength | Bağlantı kapsamı dar |
| Dış kuvvet/moment | Yok | WRC 107/297/537 vb. | Kritik ticari fark |
| Lokal yorulma | Yok | Basınç/termal cycle | Yok |

Gerekli matematik: eğik silindir-kabuk kesişimi, takviye düzlemi taraması, lokal kabuk gerilmesi,
yük koordinat dönüşümü, gerilme sınıflandırması ve çevrim hasarı.

### 5.4 Flanş, conta ve cıvata

`packages/flanges` kuvvet, cıvata yükü, moment ve birkaç gerilme denklemi içerir; fakat domain’de
flanş tipi, A/B/C/G çapları, hub profili, gasket `m/y`, cıvata malzemesi/alanı, bolt circle, facing
ve seating/operating durumları yoktur. Paket hatta bağlı değildir; bazı katsayılar yaklaşıktır.

Gerekli sıra:

1. B16.5/B16.47 rating ile özel Appendix 2 tasarımını ayır.
2. Conta/cıvata kataloglarını baskı ve sıcaklıkla sürümle.
3. Operating ve seating yükleri, gerekli/mevcut bolt area ve moment kollarını tamamla.
4. Hub faktörleri ve rigidity’yi tam uygula; yaklaşık sabitleri kaldır.
5. Boru yükü ve tightness/leakage etkisini ekle.
6. Sonraki fazda Appendix Y/full-face, PCC-1 Appendix O ve EN 1591 ekle.

### 5.5 Dış basınç ve rijitleştiriciler

Bu alan formülden çok **eğri seçimi + iterasyon + geometri sınıflandırmasıdır**:

- Etkin boyu tangent/stiffener/nozzle sınırlarından otomatik çıkarma
- Silindir, koni ve bombe için ayrı yöntem
- Malzeme/sıcaklık/baskıya bağlı A/B sağlayıcı
- Chart dışı değerde bloklama; extrapolation yapmama
- Gerekli kalınlık/MAEP için kararlı iterasyon ve yakınsama kaydı
- Ring alanı, etkili kabuk alanı, gerekli atalet ve birleşim
- Vacuum + jacket + local external pressure kombinasyonları
- Yuvarlaklık/imalat kusurunun QC ile bağlantısı

### 5.6 Global yapısal yükler

`domain/load_cases.py` 15 şablon içerir ama gerçek analiz motoruna bağlı değildir. Eksik fizik:

- Kap, sıvı, izolasyon, platform, iç eleman ve boru kütlesinin kot bazlı dağılımı
- Ağırlık merkezi, kesme, moment, eksenel kuvvet ve sehim diyagramları
- Kodlara göre rüzgâr ve deprem; vortex shedding/dinamik büyütme
- Blast/wave veya kullanıcı lateral profili
- Empty, erected, operating, shutdown, flooded, hydrotest, transport ve lifting
- Eşzamanlı olmayan yüklerin kombinasyonu
- Her kesitte membran + bending + dış basınç etkileşimi ve governing case

Bu, PV Elite/AutoPIPE Vessel farkının en büyük kısmıdır. İç basınç kalınlığı uzun dikey kolonun
güvenli tasarımını tek başına sağlamaz.

### 5.7 Destekler ve kaldırma

Tam kapsam için eyerlerde farklı reaksiyon, wear plate, horn angle, ring ve tam Zick; etekte base
ring, anchor bolt circle, bolt tension, concrete bearing, opening/local stress; ayak/brakette gerçek
koordinat, kesit, member buckling ve bağlantı gerekir. Ayrıca çoklu/yaylı eyer, taşıma eyerleri,
support lug, trunnion, lifting lug/ear, rotational lift ve foundation load summary yoktur.

### 5.8 Yorulma, kırılma ve yüksek sıcaklık

`design_cycles` alanı sonuç üretmez. Eksikler: fatigue screening, basınç/sıcaklık/mekanik çevrim
çiftleri, stress range ve concentration, endurance curve/Miner hasarı, nozzle/weld discontinuity,
ASME VIII-2 stress categories, creep ve creep-fatigue. Fracture mechanics ileriki ürün fazıdır.

### 5.9 FEA ve Design by Analysis

`fea` paketinin sahte `PASS` vermemesi doğrudur. Gerçek özellik için doğrulanmış idealizasyon,
mesh convergence, load/boundary mapping, lineer/nonlineer malzeme ve temas; VIII-2 Part 5 plastic
collapse/local failure/buckling/cyclic/ratcheting; stress classification line, singularity yönetimi,
mesh/denge QA’sı ve solver sürüm kilidi gerekir. Solver çalıştırmak tek başına kod analizi değildir.

### 5.10 Malzeme ve kod verileri

`MaterialProvider` manuel kayıtları bellekte tutar. Genel lineer interpolasyon; kod dipnotu, ürün
formu, kalınlık aralığı veya sıcaklık limitini bilmez. Gerekli model:

- Kod/baskı, specification/grade/class, ürün formu ve thickness range
- Design/test sıcaklığında allowable, yield, tensile, elastic modulus
- Dipnot, heat treatment, weld kısıtı ve geçerlilik sınırı
- UCS-66 curve, P-number/group, PWHT/impact bağlantıları
- ASME/ASTM ve EN eşleştirmesini eşdeğerlik iddiası olmadan yönetme
- Lisanslı kaynak, checksum, sürüm ve proje snapshot’ı
- User material için zorunlu kaynak ve mühendis onayı

`2025` manifestinin varlığı hesabın 2025 kod verisini kullandığını kanıtlamaz.

### 5.11 PED ve EN 13445

PED motoru/ESR/DoC/nameplate kodu vardır. Fakat ana API EN motorunu seçmez; uyumluluk sonuçları ana
UI/raporda eksiktir; EN torisferik yöntem basitleştirilmiştir; EN dış basınç, flange, nozzle,
fatigue ve yük rotaları ürün seviyesinde yoktur. PED kategorisi CE uygunluğu değildir: conformity
module, notified body, malzeme, permanent joining ve teknik dosya bütünlüğü ayrıca gerekir.

### 5.12 Eksik büyük ürün aileleri

- Shell-and-tube heat exchanger: tubesheet, channel, baffle, bundle, tie rod, sealing strip
- Conventional/half-pipe jacket ve closure/nozzle penetrations
- Multi-chamber/stacked vessel, branch connection ve rectangular header
- Bellows/flanged-and-flued expansion joint
- API 650 tank ve API 579 fitness-for-service
- İç elemanlar, tray/packing, coil ve lining/cladding

## 6. Matematik dışındaki kritik eksikler

### 6.1 Verification & Validation

Denetim komutu `pytest -q -p no:cacheprovider --basetemp <workspace-temp>` sonucu **567 passed,
1 skipped** olmuştur. Bu iyi bir yazılım tabanıdır; ürün güveni için ayrıca gerekir:

- Her formülde normatif madde, geçerlilik ve bağımsız el hesabı
- Standard/baskı başına parametrik sınır ve discontinuity testleri
- PV Elite/COMPRESS veya yayınlanmış vakalarla kör karşılaştırma
- Beklenen farkları açıklayan tolerance policy
- Property/mutation testleri ve birim/monotonluk kontrolleri
- Kritik değişiklikte bağımsız ikinci kişi incelemesi
- Verification manual ve release qualification raporu
- Bilinen kusur/applicability matrisiyle yayın kapısı

### 6.2 Sonuç ve kullanıcı güvenliği

Çok durumlu sonuç modeli güçlüdür. Kural şu olmalıdır: **yaklaşık veya normatif verisi eksik yöntem
`PASS` üretemez.** Ayrıca hesap öncesi applicability validation, kaynaklı default, her sonuçta gerçek
motor/baskı/data-pack/build kimliği, kritik değişiklikte `OUTDATED` ve mühendis review kaydı gerekir.

### 6.3 Proje, revizyon ve işbirliği

API store bellektedir. JSON yardımcıları çok kullanıcılı depo değildir. Eksikler: şema migration,
transaction, optimistic lock, kullanıcı/rol, immutable calculation run, dosya eki, imza/onay,
backup/restore, retention ve audit log.

### 6.4 CAD, çizim ve imalat

STEP/STL ve önizleme değerlidir; torisferik CAD yaklaşık olabilir, birleşimler imalat ayrıntısı
değildir. Gerekli: gerçek crown/knuckle, çoklu section/chamber/jacket, nozzle cut profile/weld prep,
GA/detail drawings, ölçü/kaynak sembolü, BOM, DXF/DWG ve hesap-çizim revizyon eşliği.

### 6.5 Raporlama

HTML traceability/hash güçlüdür. Eksikler: garantili PDF/Word, bileşen bazlı input→intermediate→limit
zinciri, load/governing tabloları ve diyagramlar, çizimler/deficiency list, kullanılmayan kapsam beyanı,
review/approval ve ASME data report/PED technical-file iş akışı.

### 6.6 Entegrasyon ve işletim

Eksikler: piping load aktarımı, HTRI/Aspen termal veri, plant/CAD çift yönlü model, FEA job yönetimi,
SSO/RBAC, input/file güvenliği, structured logging, metric/trace, hata izleme ve disaster recovery.

## 7. Rakip matrisi

`✓`: resmi kaynakta açık; `△`: kısmi/harici/sınırlı; `—`: projede üretim özelliği değil.

| Kabiliyet | Proje | PV Elite 28 | COMPRESS | AutoPIPE Vessel | Ana fark |
|---|---:|---:|---:|---:|---|
| ASME VIII-1 | ✓ dar | ✓ | ✓ | ✓ | Kapsam/veri/V&V |
| ASME VIII-2 | — | ✓ | ✓ Class 1/2 | ✓ Class 1/2 | Yeni motor + DBA |
| EN 13445 | △ izole | ✓ | ASME odaklı | ✓ | API rotası çalışmıyor |
| PD/AD/CODAP/GOST/GB | — | Bazıları ✓ | — | ✓ | Küresel kod kapsamı |
| Malzeme veri tabanı | — | ✓ | ✓ çoklu baskı | ✓ çoklu standart | Manuel veri riski |
| Tam dış basınç | △ | ✓ | ✓ | ✓ | Chart/iterasyon/ring |
| Eğik/hillside nozul | — | ✓ | ✓ | ✓ | Kesişim/governing plane |
| Büyük açıklık | — | ✓ | ✓ | ✓ | App. 1-7 vb. |
| WRC lokal yük | — | ✓ 107/297/537 | ✓ 107/537 | ✓ 107/297/537 | Piping load yok |
| Appendix 2 flange | △ bağlı değil | ✓ | ✓ | ✓ | Domain/tam faktör yok |
| EN 1591 | — | ✓ | — | ✓ | Avrupa flange yok |
| Tam MDMT/impact | △ yaklaşık | ✓ | ✓ UCS/UHA/UHT | ✓ | Eğri/istisna yok |
| Fatigue | — | ✓ | ✓ | ✓ | `design_cycles` pasif |
| Wind/seismic/vortex/blast | — | ✓ | ✓ | ✓ | Global analiz yok |
| Transport/lifting | — | ✓/△ | ✓ | ✓ | CG/rigging yok |
| Gelişmiş destek | △ | ✓ | ✓ | ✓ | Prototip düzey |
| UHX/TEMA exchanger | — | ✓ | ✓ | ✓ | Ürün ailesi yok |
| Jacket/multi-chamber | — | ✓/△ | ✓ | ✓ | Tek odalı temel model |
| FEA/DBA | İskelet | △ entegre | ✓ gömülü | ✓/entegrasyon | Solver/kabul yok |
| Design/rating optimize | △ | ✓ | ✓ | ✓ | Otomatik seçim zayıf |
| 2B çizim/BOM | — | △ eklenti | ✓ | ✓ | STEP/STL yetmez |
| PDF/Word QA raporu | △ HTML | ✓ | ✓ | ✓ | Teslim zinciri |
| Piping/CAD/thermal entegrasyon | — | ✓ | ✓ | ✓ | Veri alışverişi yok |
| Verification manual | — | Ticari süreç | ✓ resmi | Ticari süreç | Qualification kanıtı yok |

Her rakip kutusunu kopyalamak yerine önce mevcut kapsam doğru ve bloklayan hale getirilmeli; sonra
global yükler, lokal nozul gerilmesi ve flanş eklenmelidir. Heat exchanger ve çoklu uluslararası kod
daha sonraki ticari genişlemedir.

## 8. Eksik uzmanlık haritası

| Disiplin | Gereken iş | Neden yalnız yazılımcı yetmez |
|---|---|---|
| Kod mühendisi | ASME VIII-1/2, EN applicability/yorum | Hangi durumda formülün kullanılamayacağını belirler |
| Yapısal analiz | Wind/seismic/global model/support/lifting | Yük yolu ve kombinasyon uzmanlığı gerekir |
| Malzeme | Allowable, MDMT, impact, PWHT, creep | Tablo dipnotu ve metalurjik durum kritiktir |
| Kaynak/NDE | UW detayları, E, WPS/PQR, PWHT/NDE | Tasarım kabulü imalatla bağlıdır |
| FEA | Mesh/nonlinear/stress classification/buckling | Solver çıktısı kod sonucu değildir |
| Sayısal yöntem | İterasyon, yakınsama, tolerans | Buckling/optimizasyon/ters çözüm için gerekir |
| PED | Kategori, module, ESR, technical file | CE yalnız hesap değildir |
| QA/V&V | Verification manual, bağımsız test | Geliştirme ekibinden bağımsız güvence gerekir |
| CAD/imalat | Gerçek geometri, çizim/BOM | Görsel ve imalat modeli farklıdır |
| Ürün güvenliği | Yetki/onay/limitation/misuse | Yanlış kullanım da tasarım riskidir |

Minimum çekirdek ekip: deneyimli basınçlı kap mühendisi, hesap geliştiricisi ve bağımsız V&V
sorumlusu. FEA, malzeme, kaynak ve PED uzmanı ilgili fazlarda zorunludur.

## 9. Aşamalı yol haritası

### Faz A — Yanlış sonucu engelle (P0)

1. EN seçimini gerçek plugin’e bağla; desteklenmeyen EN işlevini blokla.
2. MDMT, yaklaşık dış basınç bombe ve destek `PASS` sonuçlarını `REVIEW_REQUIRED` yap.
3. Tek/çoklu bileşen sözleşmesini netleştir; işlenmeyen girdiyi reddet.
4. Torisferik varsayımı ve tüm sessiz defaultları düzelt.
5. Sonuçta motor, baskı, veri paketi ve applicability göster.

**Çıkış:** Kabul edilen hiçbir girdi yanlış standarda düşmez; yaklaşık yöntem nihai `PASS` vermez.

### Faz B — Güvenilir ASME VIII-1 çekirdeği (P1)

1. Lisanslı ASME VIII-1/II-D erişimi ve sürümlü material pack.
2. İç/dış çap, genel elipsoid, koni geçişi ve flat-head kapsamı.
3. Tam UCS-66 ve tam UG-28/33 + stiffening ring.
4. Eğik/hillside nozzle, App. 1-7 ve çoklu açıklık.
5. Flange/gasket/bolt domain’i ve Appendix 2.
6. Her modülde bağımsız golden case ve verification sheet.

**Çıkış:** İlan edilen kapsam normatif veriyle hesaplanır ve tanımlı toleransta doğrulanır.

### Faz C — Gerçek kap yükleri (P1–P2)

Kot bazlı ağırlık/sıvı/ekipman; tüm lifecycle load case’leri; wind/seismic/vortex; shear/moment/
deflection; tam support/anchor/foundation; lifting/rigging; nozzle-load import ve WRC.

**Çıkış:** Her bileşende governing load case raporlanır.

### Faz D — EN 13445 + PED (P1–P2)

EN motorunu tamamen bağla; EN material/nozzle/external pressure/load/flange/fatigue’yi doğrula;
PED/ESR/risk/DoC/nameplate/technical file’ı aynı immutable hesap revizyonuna bağla.

### Faz E — Ürünleştirme (P1–P2)

Transactional DB, immutable run/audit; PDF/Word/deficiency/review; migration/backup/RBAC;
verification manual/release qualification; gerçek CAD, GA/detail ve BOM.

### Faz F — İleri kapsam (P2–P3)

ASME VIII-2 Class 1/2, fatigue, gerçek FEA/DBA, UHX/TEMA, jacket/multi-chamber, pazar gerekirse
PD/AD/CODAP, piping/thermal/CAD entegrasyonu ve tasarım optimizasyonu.

## 10. Zorunlu doğrulama kapısı

Her modül şu teslimler olmadan tamam sayılmamalıdır:

1. Applicability: girdi aralığı, geometri, madde ve hariç tutmalar.
2. Implementasyonu yazmayan mühendisten bağımsız türetme/el hesabı.
3. Normal, sınır, blok, fail ve birim dönüşümlü golden cases.
4. Mümkünse PV Elite/COMPRESS girdisi ve ayrıntılı fark analizi.
5. Fiziksel monotonluk/property testleri.
6. Tekillik, yakınsama, yuvarlama, uç değer ve `NaN/inf` testleri.
7. Formül/veri sürümü, intermediate ve varsayım traceability’si.
8. Yetkin mühendis sign-off’u.
9. CI’da değişmez regresyon kilidi.
10. Kullanıcıya yayımlanan desteklenen/desteklenmeyen kapsam.

El kitabı görsellerinde kitap adı, kurum/yazar, baskı, yıl, bölüm ve sayfa tutulmalı; OCR tek başına
formül kaynağı olmamalı, sembol ve birimler görselden ikinci kez kontrol edilmelidir.

## 11. Bugünkü güvenli kullanım sınırı

Önerilen etiket:

> **ASME VIII-1 dar kapsamlı ön boyutlandırma ve doğrulama geliştirme sürümü — sonuçlar yetkili
> basınçlı kap mühendisi ve güncel normatif standartla bağımsız doğrulanmalıdır.**

Şimdilik uygun: desteklenen geometride temel ASME iç basınç gövde/bombe kıyası; aynı dar kapsamta
kalınlık/MAWP eğilim çalışması; radyal uygun büyüklükte nozul ön kontrolü; eğitim/prototipleme.

Bağımsız doğrulamasız uygun değil: EN/PED/CE kararı; dış basınç; MDMT muafiyeti; destek/ankraj/
wind/seismic/transport/lifting; eğik/büyük nozzle veya external load; flange, fatigue, FEA/DBA,
heat exchanger; imalata esas çizim/BOM veya resmi rapor.

## 12. Resmi kıyas kaynakları

Erişim tarihi: **20 Eylül 2026**.

1. Hexagon, [PV Elite 28 Help](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/Version-28/990005)
2. Hexagon, [PV Elite Product Sheet](https://bynder.hexagon.com/m/45154a500a6840d2/original/Hexagon_PPM_PV_Elite_Product_Sheet_US.pdf)
3. Hexagon, [PV Elite Optional Analyses](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/Version-28/304625)
4. Hexagon, [PV Elite Local Stress Analysis](https://docs.hexagonppm.com/r/en-US/PV-Elite-Help/26/320411)
5. Hexagon, [CodeCalc FEA and WRC](https://docs.hexagonppm.com/r/en-US/CodeCalc-Help/25/303379)
6. Codeware, [COMPRESS Capabilities](https://www.codeware.com/products/compress/compress-benefits/)
7. Codeware, [COMPRESS Product Overview](https://www.codeware.com/products/compress/)
8. Codeware, [COMPRESS Verification Manual](https://www.codeware.com/prospects/meura/Verification-Manual-2021.pdf)
9. Bentley, [AutoPIPE Vessel](https://www.bentley.com/products/autopipe-vessel)
10. Bentley, [Heat Exchanger Product Sheet](https://www.bentley.com/wp-content/uploads/PDS-AutoPIPE-Vessel-Heat-Exchanger-LTR-EN-LR.pdf)

## 13. Repo içi başlıca kanıtlar

- `pressure-vessel-suite/apps/api/services.py` — motor seçimi
- `pressure-vessel-suite/packages/calc-core/src/calc_core/orchestrator.py` — hesap sırası
- `pressure-vessel-suite/packages/code-asme-viii-1/` ve `code-en-13445/`
- `pressure-vessel-suite/packages/external-pressure/`, `mdmt/`, `nozzles/`, `flanges/`, `supports/`, `fea/`
- `pressure-vessel-suite/packages/materials/` — manuel provider/interpolasyon
- `pressure-vessel-suite/docs/limitations.md` — bilinen kapsam
- `pressure-vessel-suite/docs/validation/asme-worked-examples.md` — yayınlanmış kıyaslar
- `pressure-vessel-suite/tests/wiring/` — bağlantı/UI görünürlüğü

---

**Nihai sıra:** yanlış standardı ve yaklaşık `PASS` sonuçlarını engelle → sürümlü kod/malzeme verisi
kur → ASME VIII-1 dar kapsamını tamamen doğrula → global yük/nozul yükü/flanş/destekleri tamamla →
EN/PED’yi üretime al → kalıcı veri ve profesyonel raporlama → VIII-2, FEA, fatigue ve exchanger.
