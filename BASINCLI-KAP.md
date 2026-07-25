Projenin doğru tanımı

Bu proje yapılabilir ve doğru mimariyle PV Elite / COMPRESS benzeri, açık kaynak bir basınçlı kap tasarım sistemi ortaya çıkarılabilir. Ancak uygulamayı yalnızca “et kalınlığı hesaplayan bir program” olarak değil, şu dört parçanın birleşimi olarak düşünmek gerekir:

Standartlara göre hesap motoru
Parametrik basınçlı kap ve nozul modelleyici
PED/CE uygunluk ve dokümantasyon sistemi
PDF rapor ve STEP üretim sistemi

En kritik nokta şu:

CE bir hesap standardı değildir.

Avrupa tarafında yasal çerçeve PED 2014/68/EU, teknik tasarım yolu ise çoğunlukla EN 13445 – Ateşle temas etmeyen basınçlı kaplar standardıdır. PED, azami izin verilen basıncı 0,5 barın üzerinde olan sabit basınçlı ekipmanların tasarım, üretim ve uygunluk değerlendirmesini kapsar.

ASME VIII Div.1 ile EN 13445 aynı hesap içinde karıştırılmamalıdır. Kullanıcı proje başında bir tasarım rotası seçmelidir:

ASME VIII Division 1
EN 13445 + PED
İleride: ASME VIII + PED gap analysis

ASME kullanılarak Avrupa için kap üretmek mümkündür; ancak ASME harmonize Avrupa standardı olmadığı için otomatik “uygunluk varsayımı” sağlamaz. Üreticinin PED’nin temel güvenlik gereklerini nasıl karşıladığını teknik dosyada göstermesi ve gerekli kategorilerde onaylanmış kuruluşun bu çözümü değerlendirmesi gerekir. Farklı standartların bazı parçaları birlikte kullanılacaksa izin verilen gerilme, güvenlik katsayısı ve muayene kapsamı gibi konularda tutarlılık analizi yapılmalıdır.

1. Uygulamanın başlangıç kapsamı

İlk sürümde kapsamı fazla genişletmemek gerekir.

V1’de desteklenecek kaplar
Sabit, metalik ve ateşle temas etmeyen basınçlı kap
Tek basınç odası
Yatay veya dikey kap
Silindirik gövde
Elipsoidal bombe
Torisferik bombe
Yarım küresel bombe
Düz kapak daha sonraki küçük bir modül olarak
İç basınç
Hidrostatik test
Karbon çeliği ve paslanmaz çelik
Radyal nozullar
Manşon, muf, manway ve flanşlı nozul
Takviye pedi
Kaynak verimi veya birleşim katsayısı
İç ve dış korozyon payı
PDF hesap raporu
STEP modeli
İlk sürümün dışında bırakılacaklar
Kazanlar ve ateşle ısıtılan ekipmanlar
Taşınabilir gaz tüpleri ve ADR kapsamındaki kaplar
Kompozit Type III/IV hidrojen tankları
Çok odalı kaplar
Ceketli kaplar
Eşanjör tüp demetleri ve tüp aynası hesabı
Yüksek sıcaklık sünme hesabı
Kapsamlı yorulma analizi
Rüzgâr ve deprem
Nozula gelen harici boru yükleri
Tam Design by Analysis
Kriyojenik özel kurallar

PED’nin kapsam dışı bıraktığı ekipmanlar ve taşınabilir basınçlı ekipmanlar ayrıca ele alınmalıdır; uygulama proje başlangıcında kapsam kontrolü yapmalıdır.

2. EN 13445 ve PED tarafında uygulanacak yapı

EN 13445 tek bir doküman değildir. Uygulamanın standart paketleri şeklinde çalışması gerekir.

Standart bölümü	Uygulamadaki karşılığı
EN 13445-1	Genel kapsam ve kurallar
EN 13445-2	Malzemeler
EN 13445-3	Tasarım ve hesaplar
EN 13445-4	İmalat
EN 13445-5	Muayene ve test
EN 13445-6	Sfero dökme demir kaplar, sonraki sürüm
EN 13445-8	Alüminyum kaplar, sonraki sürüm
EN 13445-10	Nikel ve nikel alaşımları, sonraki sürüm

Bu bölüm adları Avrupa Birliği Resmî Gazetesi’ndeki harmonize standart listesinde açıkça yer almaktadır.

Standart sürümleri uygulamaya sabit gömülmemelidir. Harmonize standart listesi 2025’te yeniden yayımlandı ve Ocak 2026’da tekrar değiştirildi; örneğin EN 13445-5 için değişiklik ve EN 13445-11 gibi yeni referanslar geldi. Her proje, başladığı tarihte kullanılan standart ve değişiklik paketine kilitlenmelidir.

Örnek:

StandardPack
  code_family: EN_13445
  base_edition: 2021
  amendments:
    - EN_13445_2_A1_2023
    - EN_13445_4_A1_2023
    - EN_13445_5_A1_2024
  ped_directive: 2014_68_EU
  harmonised_list_date: 2026-01-13

Bu sayede eski bir proje yeni standart güncellemesi yüzünden sessizce değişmez.

3. PED/CE sınıflandırma motoru

Uygulamanın ayrı bir PED Classification Engine modülü olmalıdır.

Kullanıcıdan şu bilgiler alınır:

Ekipman türü: vessel, piping, safety accessory, pressure accessory
PS: azami izin verilen basınç
V: iç hacim
DN
TS minimum ve maksimum sıcaklık
Akışkan gaz, buhar veya sıvı mı?
TS sıcaklığındaki buhar basıncı
Akışkanın CLP tehlike sınıfları
Akışkan Grup 1 veya Grup 2
Isıtılan ekipman olup olmadığı
Tek kap mı, assembly mi?

PED sınıflandırması yalnızca kimyasal adına bakılarak yapılmamalıdır. Akışkan grubu CLP tehlike sınıflarına göre belirlenir; birden çok akışkan varsa en yüksek kategoriyi oluşturan akışkan esas alınır.

Motorun çıktısı:

PED kapsamı: Evet
Ekipman türü: Vessel
Akışkan fazı: Gas
Akışkan grubu: Group 2
Sınıflandırma tablosu: Annex II Table 2
PS × V: 1.250 bar·L
PED sonucu: Category II
Uygunluk modülleri: A2 / D1 / E1
Onaylanmış kuruluş: Gerekli
CE işareti: Uygulanabilir

PED kategoriye göre uygunluk modüllerini belirler:

PED sonucu	Kullanılabilen temel modüller
SEP	CE işareti yok
Kategori I	A
Kategori II	A2, D1 veya E1
Kategori III	B+D, B+F, B+E, B+C2 veya H
Kategori IV	B+D, B+F, G veya H1

Kategori ve modül eşleştirmeleri PED Madde 13–14 ve Ek II’de tanımlanmıştır. SEP sınırlarında kalan ekipman PED kapsamında “sound engineering practice” ile üretilir fakat PED kaynaklı CE işareti taşımaz.

CE modülü hesap yapmaktan fazlasını üretmeli
PED kapsam değerlendirmesi
SEP/Kategori I–IV
Kullanılabilecek modüller
Onaylanmış kuruluş gerekliliği
Temel güvenlik gerekleri kontrol listesi
Risk analizi formu
Uygulanan harmonize standartlar
Kısmen uygulanan standartlar
Karşılanmayan veya manuel değerlendirilecek maddeler
EU Declaration of Conformity taslağı
İsim plakası bilgileri
Kullanım ve güvenlik talimatı şablonu
Teknik dosya indeksi

PED üreticiden risk ve tehlike analizi, hesap sonuçları, muayene ve test raporları ile kullanılan standartların teknik dosyada gösterilmesini ister. Belgelerin ve uygunluk beyanının 10 yıl saklanması da gereklidir.

4. Ana yazılım mimarisi

En doğru yapı local-first web uygulaması olur:

┌──────────────────────────────────────┐
│ React / TypeScript kullanıcı arayüzü │
│ Formlar + 2D şema + 3D görüntüleyici │
└──────────────────┬───────────────────┘
                   │ REST / WebSocket
┌──────────────────▼───────────────────┐
│ Python FastAPI uygulama servisi      │
├──────────────────────────────────────┤
│ Project / Revision Service           │
│ Calculation Orchestrator             │
│ PED Compliance Service               │
│ Report Service                       │
│ CAD Service                          │
└──────────┬────────────┬──────────────┘
           │            │
┌──────────▼──────┐ ┌───▼──────────────┐
│ Hesap çekirdeği │ │ CadQuery / OCCT   │
│ ASME / EN       │ │ STEP üretimi      │
└──────────┬──────┘ └──────────────────┘
           │
┌──────────▼───────────────────────────┐
│ SQLite / PostgreSQL                  │
│ Proje + malzeme + standart sürümleri │
└──────────────────────────────────────┘

İlk geliştirme sırasında tarayıcıda çalışır; daha sonra Windows kurulum dosyası hâline getirilebilir.

Neden hesap çekirdeği ayrı olmalı?

Aynı hesap motoru şu ortamlarda kullanılabilir:

Masaüstü uygulaması
Web uygulaması
Komut satırı
Otomatik test sistemi
İleride SolidWorks veya FreeCAD eklentisi

Arayüzün içine formül yazılması en büyük mimari hata olur.

5. Depo ve klasör yapısı
pressure-vessel-suite/
│
├── apps/
│   ├── web-ui/                 # React kullanıcı arayüzü
│   └── api/                    # FastAPI
│
├── packages/
│   ├── domain/                 # Ortak veri modelleri
│   ├── units/                  # Birim sistemi
│   ├── calc-core/              # Ortak matematik ve sonuç nesneleri
│   ├── code-asme-viii-1/       # ASME hesap eklentisi
│   ├── code-en-13445/          # EN hesap eklentisi
│   ├── ped-2014-68-eu/         # PED sınıflandırması
│   ├── materials/              # Malzeme veri sağlayıcısı
│   ├── welds/                  # Kaynak ve NDT modeli
│   ├── nozzles/                # Açıklık ve takviye hesapları
│   ├── cad-engine/             # CadQuery model üretimi
│   ├── report-engine/          # PDF rapor
│   └── compliance/             # ESR ve teknik dosya
│
├── standards/
│   ├── manifests/              # Standart sürüm tanımları
│   └── clause-mappings/        # Formül–madde eşleştirmeleri
│
├── tests/
│   ├── unit/
│   ├── regression/
│   ├── golden-cases/
│   ├── cad-validation/
│   └── report-snapshots/
│
└── docs/
    ├── calculation-coverage.md
    ├── validation-plan.md
    └── limitations.md
6. Ortak veri modeli

Hesap standarttan bağımsız bir veri modeliyle başlamalıdır.

VesselProject
VesselProject
  project_number
  project_name
  customer
  revision
  calculation_code
  code_edition
  unit_system
  design_life
  design_cycles
  orientation
  design_conditions
  fluid
  shell_sections[]
  heads[]
  nozzles[]
  welds[]
  supports[]
  materials[]
  load_cases[]
DesignConditions
DesignConditions
  operating_pressure
  design_pressure
  maximum_allowable_pressure_ps
  operating_temperature
  design_temperature
  minimum_design_temperature
  external_pressure
  vacuum_condition
  hydrotest_temperature
  corrosion_allowance_internal
  corrosion_allowance_external

Burada çalışma basıncı, tasarım basıncı ve PS aynı değer kabul edilmemelidir.

ShellSection
ShellSection
  inside_diameter
  outside_diameter
  tangent_length
  nominal_thickness
  material_id
  weld_joint_id
  internal_corrosion_allowance
  external_corrosion_allowance
  mill_tolerance
  forming_thinning
Head
Head
  type:
    - elliptical
    - torispherical
    - hemispherical
    - flat
  inside_diameter
  crown_radius
  knuckle_radius
  straight_flange_length
  nominal_thickness
  material_id
  weld_joint_id
Nozzle
Nozzle
  tag
  nozzle_type
  host_component_id
  axial_position
  circumferential_angle
  inclination_angle
  outside_diameter
  inside_diameter
  neck_thickness
  inside_projection
  outside_projection
  material_id
  corrosion_allowance
  reinforcement_pad
  weld_definition
  flange_definition
  external_loads

Nozul konumu üç koordinatla tanımlanmalıdır:

Gövde boyunca eksenel mesafe: z
Saat yönü veya çevresel açı: θ
Nozul eğim açısı: α

Örneğin:

N1:
  host: SHELL-01
  z: 850 mm
  theta: 90 deg
  alpha: 0 deg
  DN: 50
  neck_thickness: 5.0 mm

Bombe üzerindeki nozul için konum, düz eksenel mesafe yerine bombe yüzey parametresi veya merkezden açıyla tanımlanmalıdır.

7. Hesap motorunun yapısı

Her standart ayrı bir “code plugin” olmalıdır.

class DesignCode:
    def calculate_shell(self, input_data): ...
    def calculate_head(self, input_data): ...
    def calculate_nozzle(self, input_data): ...
    def calculate_mawp(self, project): ...
    def calculate_test_pressure(self, project): ...
    def validate_weld(self, weld): ...

ASME ve EN sınıfları bunu ayrı şekilde uygular:

ASMEVIII1DesignCode
EN13445DesignCode
Her hesap sonucu denetlenebilir olmalı
CalculationResult
  calculation_id
  code
  edition
  clause_reference
  formula_reference
  input_snapshot
  material_properties_used
  intermediate_values[]
  final_result
  allowable_limit
  utilization_ratio
  status
  warnings[]
  assumptions[]
  rounding_rule

Örnek:

Component: Shell S-01
Calculation: Internal pressure thickness
Code: ASME VIII-1 2025
Reference: UG-27
Required pressure thickness: 7.42 mm
Corrosion allowance: 2.00 mm
Negative tolerance allowance: 1.11 mm
Total required nominal thickness: 10.53 mm
Selected thickness: 12.00 mm
Utilization: 87.8 %
Status: PASS

Formül sonucunu yalnızca 12 mm yeterli şeklinde saklamak hatalıdır. Ara değerler, kullanılan malzeme gerilmesi ve standart sürümü de saklanmalıdır.

8. Uygulanacak hesap sırası
A. Ön kontroller
Birim kontrolü
Eksik veri kontrolü
Geometri geçerliliği
Standart kapsam kontrolü
PED kapsam kontrolü
Akışkan sınıflandırması
Tasarım yük durumlarının oluşturulması
B. Malzeme değerleri
Tasarım sıcaklığındaki izin verilen gerilme
Akma ve çekme dayanımları
Test sıcaklığı özellikleri
Elastisite modülü
Gerekliyse sürünme verileri
Minimum sıcaklık ve tokluk kontrolü
Malzeme belge tipi
Ürün formu ve kalınlık aralığı

PED, malzemenin tüm çalışma ve test koşullarında yeterli süneklik ve tokluğa sahip olmasını, akışkana kimyasal olarak dayanmasını ve teknik dosyada malzeme uygunluğunun gösterilmesini ister. Kategori II–IV ana basınç taşıyan parçalar için özel ürün kontrol sertifikası da gerekir.

C. Basınç taşıyan parçalar
Silindirik gövde et kalınlığı
Elipsoidal bombe
Torisferik bombe
Yarım küresel bombe
Konik bölüm, sonraki sürüm
Düz kapak
İç basınç
Dış basınç ve vakum, sonraki sürüm
Statik sıvı yüksekliği
Korozyon payı
Negatif sac toleransı
Şekillendirme incelmesi
Kaynak verimi veya joint coefficient

PED yalnızca iç basıncı değil; dış basınç, sıcaklık, içeriğin ağırlığı, rüzgâr, deprem, destek ve boru reaksiyonları, korozyon ve yorulma gibi yükleri de dikkate almayı ister. Bu nedenle ilk sürümün sonuç raporunda desteklenmeyen yükler açık biçimde belirtilmelidir.

D. Nozul ve açıklıklar

ASME rotasında en az:

Açıklığın izin verilip verilmediği
Açıklığın etkin çapı
Gerekli takviye alanı
Gövde veya bombeden gelen mevcut alan
Nozul boynundan gelen alan
İç ve dış çıkıntı katkısı
Takviye pedi katkısı
Kaynak metali katkısı
Takviye sınırları
Nozul boynu minimum kalınlığı
Birbirine yakın açıklıkların çakışması
Nozulun kaynak dikişine yakınlığı
Bombe knuckle bölgesi kısıtlamaları

EN rotasında da aynı işlevler EN 13445-3’ün açıklık ve nozul kurallarıyla ayrı hesaplanmalıdır.

Nozul ekranında alan hesabının grafik olarak gösterilmesi çok faydalı olur:

Gerekli alan:          420 mm²
Gövde fazlası:         165 mm²
Nozul boynu katkısı:   138 mm²
Takviye pedi:          154 mm²
Kaynak katkısı:         28 mm²
Toplam mevcut alan:    485 mm²
Sonuç: PASS
E. MAWP

MAWP tek bir gövde formülünden alınmamalıdır.

Her basınç taşıyan parça için ayrı hesaplanır:

Shell MAWP
Left head MAWP
Right head MAWP
Nozzle N1 limit
Nozzle N2 limit
Flat cover limit
Flange limit

Global MAWP:

Global MAWP = minimum(component MAWP values)

Rapor, hangi parçanın limitleyici olduğunu açıkça göstermelidir.

F. Test basıncı

ASME ve PED/EN test basıncı ayrı algoritmalardır.

PED’ye göre hidrostatik test basıncı en az:

Ekipmanın çalışma sırasında maruz kalacağı azami yükün 1,25 katına karşılık gelen değer veya
PS’nin 1,43 katı

değerlerinden büyük olanına göre belirlenir. Hidrostatik test zararlı veya uygulanamaz olduğunda eşdeğerliği gösterilen başka testler ve ilave NDT önlemleri gerekir.

ASME tarafı kendi test basıncı ve sıcaklığa bağlı gerilme oranı kurallarıyla ayrı hesaplanmalıdır.

9. Kaynak modülü

Kaynak, yalnızca 3D modelde görünen bir dikiş olmamalıdır.

WeldJoint modeli
WeldJoint
  joint_id
  joint_type
  connected_components[]
  weld_category
  weld_process
  full_or_partial_penetration
  joint_efficiency
  joint_coefficient
  nde_method
  nde_extent
  wps_number
  pqr_number
  welder_qualification
  pwht_required
  pwht_procedure

Uygulama şunları kontrol etmelidir:

Seçilen NDT kapsamıyla kaynak verimi uyumlu mu?
Tam nüfuziyet gerekli mi?
Nozul kaynağı tipi hesapta kabul edilen tip mi?
WPS/PQR bilgileri girilmiş mi?
Kaynakçı yeterliliği eklenmiş mi?
PWHT gerekliliği manuel veya otomatik değerlendirilmiş mi?
Kaynak ile açıklıklar çakışıyor mu?

PED, basınç dayanımına katkıda bulunan kalıcı birleştirmelerin yetkin personel ve uygun prosedürlerle yapılmasını ister. Kategori II–IV’te prosedür ve personel üçüncü tarafça onaylanmalı; kategori III–IV NDT personeli de tanınmış üçüncü taraf onayına tabi olabilir.

10. Parametrik 3D ve STEP motoru

Bu iş için en uygun açık kaynak çekirdeklerden biri CadQuery + OpenCascade/OCP’dir.

CadQuery:

Python ile parametrik katı model oluşturur
OpenCascade tabanlıdır
STEP ve DXF üretebilir
Ölçüler değiştiğinde model yeniden oluşturulabilir
CAD üretim sırası
1. İç veya dış çapa göre ana gövde oluştur
2. Gövde et kalınlığını uygula
3. Sol ve sağ bombeyi oluştur
4. Gövdeyle birleştir
5. Nozul merkez eksenlerini oluştur
6. Nozul borularını oluştur
7. Gövdedeki delikleri kes
8. Takviye pedlerini oluştur
9. Flanşları ekle
10. Kaynak temsillerini ekle
11. Geometri geçerlilik kontrolü
12. STEP export
CAD hesabın kaynağı olmamalı

Hesap motoru geometrik ölçüleri üretir; CAD motoru bu ölçülerden model oluşturur.

Yanlış:

CAD modelindeki yüzeyi ölç → hesaba sok

Doğru:

Project data → hesap motoru
Project data → CAD motoru

Böylece CAD hatası hesap sonuçlarını değiştirmez.

CAD doğrulamaları
Model tek veya beklenen sayıda solid mi?
Negatif hacim oluşmuş mu?
Nozul gerçekten gövdeyi kesiyor mu?
Nozul deliği takviye pedinden büyük mü?
Nozullar birbirine giriyor mu?
Nozul bombe teğet çizgisini geçiyor mu?
Minimum kenar mesafeleri sağlanıyor mu?
Hesaplanan iç hacim ile CAD hacmi tolerans içinde mi?
Modelde açık kabuk veya bozuk yüzey var mı?

FreeCAD de OpenCascade tabanlı açık kaynak parametrik modelleyicidir ve STEP, IGES, DXF gibi formatları destekler. İlk çekirdek için CadQuery, kullanıcıya sonradan elle düzenleme imkânı sunmak için FreeCAD tercih edilebilir.

11. PDF rapor yapısı

Rapor “tek sayfalık sonuç çıktısı” olmamalıdır.

Bölüm yapısı
1. Kapak
2. Proje ve revizyon bilgileri
3. Kullanılan standartlar ve sürümleri
4. Tasarım temeli
5. Akışkan ve çalışma koşulları
6. PED kapsam ve kategori hesabı
7. Malzeme listesi
8. Ana geometri
9. Gövde hesapları
10. Bombe hesapları
11. Nozul ve açıklık hesapları
12. Kaynak ve NDT özeti
13. MAWP
14. Test basıncı
15. Ağırlık ve hacim
16. Nozul schedule
17. Kaynak haritası
18. İsim plakası bilgileri
19. PED temel güvenlik gerekleri matrisi
20. Uyarılar ve kapsam dışı kontroller
21. 2D görünüşler
22. 3D model görünüşleri
23. Hesap onay ve imza bölümü

Her raporda şu izlenebilirlik bilgileri bulunmalıdır:

Software version
Calculation engine version
Standard pack version
Material database version
Project revision
Calculation date
Input file hash
Report hash

Böylece üç ay sonra aynı proje yeniden açıldığında sonuçların neden değiştiği anlaşılır.

12. Malzeme veri tabanı

En zor konulardan biri budur.

İlk sürümde kullanıcı şu değerleri manuel girebilir:

Material: P355NH
Design temperature: 150 °C
Allowable stress: kullanıcı girişi
Yield strength: kullanıcı girişi
Tensile strength: kullanıcı girişi
Material certificate: 3.1
Source document: EN 10028-3 / project material specification

Daha sonra lisanslı malzeme paketleri eklenebilir.

Malzeme verisi sürümlü olmalı
MaterialProperty
  standard_pack
  material_designation
  product_form
  thickness_min
  thickness_max
  temperature
  allowable_stress
  yield_strength
  tensile_strength
  source_reference
  source_revision

İzin verilen gerilme yalnızca malzeme adına bağlı değildir. Şunlara da bağlı olabilir:

Standart sürümü
Ürün formu
Kalınlık aralığı
Isıl işlem durumu
Tasarım sıcaklığı
Kaynaklı veya kaynaksız durum
13. Standartların telif konusu

Açık kaynak bir yazılım yazılabilir; fakat EN 13445 ve ASME metinlerini, tablolarını ve bütün malzeme verilerini izinsiz olarak yazılım paketinin içine koymak ayrı bir konudur.

CEN-CENELEC, Avrupa standartlarının telif hakkıyla korunduğunu ve kısmen dahi çoğaltma veya dağıtım için ilgili ulusal standart kuruluşundan izin gerektiğini açıkça belirtiyor.

Bu nedenle güvenli mimari:

Standart metnini yazılım içine koyma
Yalnızca madde referanslarını sakla
Formülleri mühendislik uzmanıyla doğrula
Kullanıcıdan lisanslı malzeme verisi içe aktarmasına izin ver
Ticari dağıtım öncesi TSE/CEN ve ASME lisans şartlarını kontrol et
PDF raporda standardın uzun metnini kopyalama
Hesap yöntemlerini kendi açıklamalarınla göster

ASME’nin güncel Section VIII Division 1 ürünü 2025 sürümü olarak yayımlanmıştır ve tasarımın yanında üretim, muayene, test ve sertifikasyon kurallarını da kapsar.

14. GitHub ve açık kaynak projelerden alınabilecekler
CadQuery

Ana CAD ve STEP motoru için kullanılabilir. Parametrik model üretme ve STEP dışa aktarma yeteneği doğrudan projenin ihtiyacına uygundur.

FreeCAD

STEP modelini açmak, kontrol etmek, elle düzenlemek ve ileride bir çalışma tezgâhı geliştirmek için kullanılabilir.

CalculiX

İleride sonlu elemanlar analizi için kullanılabilecek açık kaynaklı üç boyutlu bir FEA çözücüsüdür. İlk sürümde zorunlu olmamalıdır.

Code_Aster

Daha gelişmiş elastik, plastik, termal ve yorulma analizleri için sonraki aşamada entegre edilebilir. Kaynak kodu ve doğrulama testleri yayımlanmaktadır.

thepvguy/calctoys

ASME basınçlı kap hesaplarına yönelik Python kodları içeriyor ve Unlicense ile yayımlanmış. Ancak geliştiricisi birçok betiğin birlikte çalışmadığını veya zaman zaman hiç çalışmadığını açıkça söylüyor. Bu nedenle yalnızca araştırma ve test fikri kaynağı olmalı; hesaplar kopyalanıp güvenilmemelidir.

Vessel Guard

Python/Tkinter tabanlı, basınçlı kap ve borulama hesapları üzerinde çalışan MIT lisanslı bir proje. Arayüz ve proje organizasyonu incelenebilir; mühendislik doğrulaması yapılmadan formülleri referans kabul edilmemelidir.

Basit pressure-vessel calculator projeleri

GitHub’da yalnızca ince cidarlı silindir gerilmeleri hesaplayan projeler de bulunuyor. Bunlar kaynak, bağlantı, fitting veya karmaşık geometriyi kapsamıyor; yalnızca temel test karşılaştırmaları için yararlıdır.

15. FEA entegrasyonu nasıl olmalı?

FEA, formül hesabının yerine geçmemeli; ek doğrulama modülü olmalıdır.

Parametrik CAD
      ↓
Basitleştirilmiş analiz geometrisi
      ↓
Gmsh mesh
      ↓
CalculiX veya Code_Aster
      ↓
Gerilme sonuçları
      ↓
Stress linearization
      ↓
Code acceptance checks

Daha sonraki aşamalarda:

Nozul birleşimindeki lokal gerilmeler
Destek ve lifting lug gerilmeleri
Termal gradyan
Yorulma
Harici nozul yükleri
Lokal plastikleşme
Burkulma
Tasarım-by-analysis

eklenebilir.

FEA modülü otomatik çalışsa bile mesh kalitesi, sınır şartları ve gerilme sınıflandırması mühendis tarafından incelenmeden “uygun” sonucu vermemelidir.

16. Yazılımda mutlaka olması gereken güvenlik mekanizmaları
Üç durumlu sonuç

Yalnızca PASS/FAIL olmamalıdır:

PASS
FAIL
REVIEW REQUIRED
NOT CALCULATED
OUT OF SCOPE

Örneğin dış basınç girilmiş fakat dış basınç modülü henüz yoksa:

NOT CALCULATED:
External-pressure stability has not been evaluated.
This result must not be used for fabrication.
Varsayımları otomatik gizlememe

Program kendi kendine şu değerleri seçmemeli:

Kaynak verimi
NDT kapsamı
Malzeme izin verilen gerilmesi
Korozyon payı
Akışkan grubu
Tasarım sıcaklığı
Mill tolerance
Test tipi

Seçerse kullanıcıya açıkça göstermeli ve onay istemelidir.

Geometri ve hesap tutarlılığı

Seçilen nominal kalınlık değişirse:

MAWP yeniden hesaplanmalı
Nozul takviyesi yeniden hesaplanmalı
Ağırlık ve hacim güncellenmeli
STEP modeli yeniden oluşturulmalı
PDF rapor eski olarak işaretlenmeli
17. Doğrulama ve test planı

Bu yazılımın en önemli kısmı kod yazmak değil, doğrulamadır.

Test katmanları
Birim testleri
Basınç birimi dönüşümleri
Sıcaklık dönüşümleri
Geometrik alan ve hacim
İnterpolasyon
Tolerans ekleme
Yuvarlama
Golden case testleri

Her standart maddesi için:

Known input
Expected intermediate values
Expected final result
Allowed numerical tolerance
Source and edition
Independent reviewer
Regresyon testleri

Yeni kod değişikliğinden sonra eski onaylı projelerin sonuçları değişiyor mu?

Geometrik testler
STEP açılıyor mu?
Solid geçerli mi?
Hacim doğru mu?
Nozul konumu doğru mu?
Nozul deliği açılmış mı?
Modelde çakışma var mı?
Bağımsız hesap doğrulaması

En kritik hesaplar iki farklı şekilde doğrulanmalıdır:

Python hesap motoru
Bağımsız Excel/Mathcad veya el hesabı

Her ikisinin aynı kodu paylaşmaması gerekir.

Uzman incelemesi

Üretimde kullanılmadan önce:

Basınçlı kap tasarım mühendisi
Kaynak mühendisi
NDT uzmanı
PED/CE uzmanı
Gerekiyorsa onaylanmış kuruluş

tarafından kapsam ve örnek hesaplar incelenmelidir.

18. Geliştirme aşamaları
Aşama 0 — Teknik şartname

Önce bir “Calculation Coverage Matrix” hazırlanmalı:

Feature                         ASME      EN/PED     V1
Cylindrical shell internal P    Yes       Yes       Yes
Elliptical head                 Yes       Yes       Yes
Torispherical head              Yes       Yes       Yes
Hemispherical head              Yes       Yes       Yes
MAWP                            Yes       Yes       Yes
Hydrotest                       Yes       Yes       Yes
Nozzle reinforcement            Yes       Yes       Yes
External pressure               Later     Later     No
Fatigue                         Later     Later     No
Wind/seismic                    Later     Later     No
Flanges                         Later     Later     No
Aşama 1 — Hesap çekirdeği
Birim sistemi
Proje veri modeli
Silindirik gövde
Üç bombe tipi
Korozyon payı
Nominal kalınlık
MAWP
Hidrotest
JSON proje kaydetme
Otomatik testler

Bu aşamada arayüz çok basit olabilir.

Aşama 2 — CAD ve rapor
CadQuery kap modeli
STEP üretimi
Hacim ve ağırlık
HTML/PDF rapor
Proje revizyon sistemi
Aşama 3 — Nozul ve kaynaklar
Nozul konumlandırma
Delik açma
Takviye pedi
Açıklık takviye hesabı
Nozul schedule
Kaynak ve NDT tanımları
Çakışma kontrolü
Aşama 4 — PED/CE
Kapsam
Grup 1/2
Gaz/sıvı ayrımı
SEP/Kategori I–IV
Uygunluk modülleri
ESR matrisi
Teknik dosya
İsim plakası
EU Declaration taslağı
Aşama 5 — İleri hesaplar
Dış basınç ve vakum
Flanşlar
Destekler
Rüzgâr ve deprem
Nozul harici yükleri
Lokal gerilmeler
Yorulma
FEA
19. İlk sürümde yapılacak ekranlar
1. New Project
2. Code & Edition
3. Design Conditions
4. Fluid & PED Classification
5. Vessel Geometry
6. Materials
7. Shell Sections
8. Heads
9. Nozzles
10. Welds & NDT
11. Calculation Results
12. 3D Model
13. PED Compliance
14. Report Export

3D model ekranında kullanıcı nozul eklemek için gövdeye tıklayabilir; ancak konum arka planda kesin olarak z, θ, α koordinatlarına çevrilmelidir.

20. En doğru ilk hedef

İlk çalışan sürüm şu kadar dar tutulmalı:

Tek silindirik gövde
İki adet 2:1 elipsoidal bombe
ASME VIII-1 hesap rotası
Manuel izin verilen gerilme girişi
İç basınç
Korozyon payı
Kaynak verimi
Et kalınlığı
MAWP
Hidrostatik test
İki radyal nozul
STEP
PDF

Bu çekirdek tamamen test edildikten sonra EN 13445/PED eklentisi geliştirilmelidir. İlk kodlama işi kullanıcı arayüzü değil, standarttan bağımsız domain modeli ve test edilebilir hesap çekirdeği olmalıdır. Aksi takdirde proje büyüdüğünde ASME, EN, CAD ve PDF kodları birbirine karışır ve doğrulanamaz hâle gelir.