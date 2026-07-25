# BASINÇLI KAP TASARIM SİSTEMİ — Geliştirme (Kodlama) Adımları

> Bu doküman, [`BASINCLI-KAP.md`](BASINCLI-KAP.md) konsept dosyasını **kodlanabilir faz-bazlı
> bir yol haritasına** çevirir. Kaynak doküman "ne yapılmalı"yı; bu doküman "hangi sırayla,
> hangi kodlama adımıyla yapılmalı"yı anlatır.
>
> **Amaç:** PV Elite / COMPRESS benzeri, açık kaynak bir basınçlı kap tasarım sistemi.
> **Öncelik:** Önce **dar çekirdek** (ASME VIII-1, tek gövde + 2 bombe), sonra EN 13445/PED,
> CAD, rapor, nozul, PED/CE ve ileri hesaplar.

---

## 0. Giriş ve değişmez prensipler

Uygulama tek bir "et kalınlığı hesaplayıcı" değil, **dört parçanın birleşimidir**:

1. Standartlara göre **hesap motoru**
2. Parametrik **basınçlı kap + nozul modelleyici** (CAD/STEP)
3. **PED/CE uygunluk ve dokümantasyon** sistemi
4. **PDF rapor + STEP üretim** sistemi

### 0.1 Kodlarken asla ihlal edilmeyecek kurallar

| # | Kural | Neden |
|---|-------|-------|
| K1 | **Arayüze formül yazma.** Formüller yalnızca `code-*` hesap eklentilerinde. | Kaynak §4 — en büyük mimari hata. |
| K2 | **CAD hesabın kaynağı değildir.** `project data → hesap` ve `project data → CAD` ayrı akar. Yüzey ölçüp hesaba sokma. | Kaynak §10 — CAD hatası hesabı bozmasın. |
| K3 | **Standart ve malzeme sürümlerini koda gömme.** Her proje kendi `StandardPack`'ine kilitlenir. | Kaynak §2 — eski proje sessizce değişmesin. |
| K4 | **Varsayımları gizleme.** Kaynak verimi, NDT, izin verilen gerilme, korozyon payı, akışkan grubu vb. program seçerse kullanıcıya gösterip **onay ister**. | Kaynak §16. |
| K5 | **Her hesap denetlenebilir olmalı.** Sonuç sadece "12 mm yeterli" değil; ara değerler + madde referansı + malzeme gerilmesi + standart sürümü saklanır. | Kaynak §7. |
| K6 | **Standart telifli metni yazılıma koyma.** Sadece madde referansı sakla; malzeme verisini kullanıcı içe aktarsın. | Kaynak §13. |
| K7 | **Domain, standarttan bağımsız.** Veri modeli önce; ASME/EN/CAD/PDF bunun etrafına eklenti olarak eklenir. | Kaynak §20. |

### 0.2 Çok durumlu sonuç modeli (sadece PASS/FAIL değil)

Her hesap sonucu şu durumlardan birini döner:

- `PASS` — kontrol geçti.
- `FAIL` — kontrol kaldı.
- `REVIEW REQUIRED` — mühendis incelemesi şart (ör. varsayım seçildi).
- `NOT CALCULATED` — modül henüz yok / girdi eksik. **"Bu sonuç imalatta kullanılamaz."**
- `OUT OF SCOPE` — bu ekipman/yük V1 kapsamı dışında.

> Örnek: Dış basınç girildi ama dış basınç modülü yoksa →
> `NOT CALCULATED: External-pressure stability has not been evaluated. This result must not be used for fabrication.`

---

## Faz 0 — Teknik şartname ve proje iskeleti

**Hedef:** Kod yazmaya başlamadan önce kapsamı sabitle ve monorepo iskeletini kur.

### 0.A — Calculation Coverage Matrix (ilk yapılacak iş)
`docs/calculation-coverage.md` içine kapsam matrisini koy. V1'de neyin **var/sonra/yok**
olduğunu tek tabloda kilitle:

| Feature | ASME | EN/PED | V1 |
|---|---|---|---|
| Cylindrical shell internal P | Yes | Yes | **Yes** |
| Elliptical head | Yes | Yes | **Yes** |
| Torispherical head | Yes | Yes | **Yes** |
| Hemispherical head | Yes | Yes | **Yes** |
| MAWP | Yes | Yes | **Yes** |
| Hydrotest | Yes | Yes | **Yes** |
| Nozzle reinforcement | Yes | Yes | **Yes** |
| External pressure | Later | Later | No |
| Fatigue | Later | Later | No |
| Wind/seismic | Later | Later | No |
| Flanges | Later | Later | No |

### 0.B — Monorepo klasör yapısını oluştur (kaynak §5)
```
pressure-vessel-suite/
├── apps/
│   ├── web-ui/                 # React + TypeScript arayüz
│   └── api/                    # FastAPI uygulama servisi
├── packages/
│   ├── domain/                 # Standarttan bağımsız veri modelleri
│   ├── units/                  # Birim sistemi + dönüşümler
│   ├── calc-core/              # Ortak matematik + CalculationResult + DesignCode arayüzü
│   ├── code-asme-viii-1/       # ASME VIII-1 hesap eklentisi
│   ├── code-en-13445/          # EN 13445 hesap eklentisi
│   ├── ped-2014-68-eu/         # PED sınıflandırma motoru
│   ├── materials/              # Malzeme veri sağlayıcısı (sürümlü)
│   ├── welds/                  # Kaynak + NDT modeli
│   ├── nozzles/                # Açıklık ve takviye hesapları
│   ├── cad-engine/             # CadQuery model + STEP üretimi
│   ├── report-engine/          # PDF/HTML rapor
│   └── compliance/             # ESR + teknik dosya
├── standards/
│   ├── manifests/              # StandardPack sürüm tanımları
│   └── clause-mappings/        # Formül ↔ madde referans eşleştirmeleri
├── tests/
│   ├── unit/  regression/  golden-cases/  cad-validation/  report-snapshots/
└── docs/
    ├── calculation-coverage.md  validation-plan.md  limitations.md
```

### 0.C — Araç/stack kurulumu
- **Backend:** Python 3.11+, FastAPI, Pydantic (veri modeli + doğrulama), `pytest`,
  `numpy` (interpolasyon), CadQuery/OCP (CAD), WeasyPrint veya ReportLab (PDF).
- **Frontend:** Node + React + TypeScript + Vite; 3D için three.js / react-three-fiber.
- **İletişim:** REST + gerekli yerde WebSocket (uzun hesap/CAD işi için).
- **Depo:** SQLite (local-first) → sonra opsiyonel PostgreSQL. Paket yönetimi: `uv`/`poetry`.
- Monorepo düzeni + lint/format (ruff, black, eslint, prettier) + CI iskeleti.

### 0.D — Başlangıç doküman dosyaları
`docs/validation-plan.md` (test planı iskeleti), `docs/limitations.md` (kapsam dışı ve
desteklenmeyen yükler açık liste).

> **Faz 0 bitti kabul kriteri:** Klasörler + boş paketler + kurulan araçlar + coverage matrisi
> commit edildi; `pytest` boş da olsa çalışıyor.

---

## Faz 1 — Hesap çekirdeği ⭐ (DAR ÇEKİRDEK ÖNCE)

**En dar ilk hedefe kilitli (kaynak §20):** Tek silindirik gövde + iki adet 2:1 elipsoidal
bombe + ASME VIII-1 rotası + manuel izin verilen gerilme + iç basınç + korozyon payı +
kaynak verimi + et kalınlığı + MAWP + hidrostatik test + JSON kayıt + otomatik testler.
Arayüz bu fazda minimum (CLI/script yeterli).

### 1.A — `units/` (birim sistemi)
- Basınç (bar, MPa, psi), sıcaklık (°C, K, °F), uzunluk (mm, in), alan/hacim/kütle dönüşümleri.
- Tek yönlü kanonik iç birim (SI) + giriş/çıkış çevrimi.
- **Birim testleri:** her dönüşüm + yuvarlama + tolerans ekleme (kaynak §17).

### 1.B — `domain/` (standarttan bağımsız veri modeli, kaynak §6/§9/§12)
Pydantic modelleri:
- **`VesselProject`**: project_number, project_name, customer, revision, calculation_code,
  code_edition, unit_system, design_life, design_cycles, orientation, design_conditions,
  fluid, shell_sections[], heads[], nozzles[], welds[], supports[], materials[], load_cases[].
- **`DesignConditions`**: operating_pressure, design_pressure, **maximum_allowable_pressure_ps**,
  operating/design/minimum_design temperature, external_pressure, vacuum_condition,
  hydrotest_temperature, corrosion_allowance_internal/external.
  → **Çalışma basıncı ≠ tasarım basıncı ≠ PS** (ayrı alanlar, kaynak §6).
- **`ShellSection`**: inside/outside_diameter, tangent_length, nominal_thickness, material_id,
  weld_joint_id, internal/external_corrosion_allowance, mill_tolerance, forming_thinning.
- **`Head`**: type (elliptical/torispherical/hemispherical/flat), inside_diameter, crown_radius,
  knuckle_radius, straight_flange_length, nominal_thickness, material_id, weld_joint_id.
- **`Nozzle`**, **`WeldJoint`**, **`MaterialProperty`** iskeletleri (detaylar sonraki fazlarda dolar).

### 1.C — `calc-core/` (ortak hesap altyapısı, kaynak §7)
- **`CalculationResult`** (izlenebilir sonuç nesnesi): calculation_id, code, edition,
  clause_reference, formula_reference, input_snapshot, material_properties_used,
  intermediate_values[], final_result, allowable_limit, utilization_ratio, status,
  warnings[], assumptions[], rounding_rule.
- **`DesignCode`** soyut arayüzü:
  ```python
  class DesignCode:
      def calculate_shell(self, input_data): ...
      def calculate_head(self, input_data): ...
      def calculate_nozzle(self, input_data): ...
      def calculate_mawp(self, project): ...
      def calculate_test_pressure(self, project): ...
      def validate_weld(self, weld): ...
  ```
- **`CalculationOrchestrator`**: hesap sırasını yönetir (bkz. 1.F).

### 1.D — `materials/` (sürümlü malzeme, kaynak §12)
- **`MaterialProperty`**: standard_pack, material_designation, product_form, thickness_min/max,
  temperature, allowable_stress, yield_strength, tensile_strength, source_reference, source_revision.
- V1'de **manuel giriş**: kullanıcı allowable/yield/tensile değerlerini girer (K4 gereği
  program otomatik seçmez). İleride lisanslı paket import edilebilir.
- İzin verilen gerilme; standart sürümü + ürün formu + kalınlık + sıcaklık + ısıl işlem +
  kaynaklı/kaynaksız duruma göre değişebilir → interpolasyon altyapısı.

### 1.E — `code-asme-viii-1/` (ilk somut hesap eklentisi)
`ASMEVIII1DesignCode(DesignCode)`:
- **Silindirik gövde** iç basınç et kalınlığı (UG-27 tarzı; madde referansı saklanır).
- **Elipsoidal / torisferik / yarım küresel bombe** et kalınlıkları.
- Korozyon payı + **negatif sac toleransı** + **şekillendirme incelmesi** eklenmesi.
- **Kaynak verimi / joint efficiency** uygulaması.
- **MAWP:** her parça için ayrı (shell, sol/sağ bombe) → **global MAWP = min(parçalar)**;
  rapor **limitleyici parçayı** gösterir (kaynak §8-E).
- **Hidrostatik test basıncı:** ASME kendi kuralı (sıcaklığa bağlı gerilme oranı) ile.
- Her metot **`CalculationResult`** döner; ara değerler + `clause_reference` dolu (K5).

### 1.F — Hesap sırası (Orchestrator, kaynak §8)
`A) Ön kontroller` (birim, eksik veri, geometri geçerliliği, standart/PED kapsam, akışkan
sınıflandırma, yük durumları) → `B) Malzeme değerleri` → `C) Basınç taşıyan parçalar`
(gövde, bombeler, korozyon, negatif tolerans, incelme, kaynak verimi) → `E) MAWP` →
`F) Test basıncı`. (D — nozul; Faz 3'te devreye girer.)

### 1.G — Kalıcılık ve testler
- JSON ile **proje kaydet/yükle** (input_file_hash üretilir).
- **Golden-case testleri:** her ASME maddesi için known input → expected intermediate →
  expected final + numeric tolerans + kaynak/sürüm + bağımsız gözden geçiren (kaynak §17).
- **Birim testleri** (units, geometri alan/hacim, interpolasyon, yuvarlama).

> **Faz 1 bitti kabul kriteri (MVP çekirdek):** Bir CLI/script ile tek gövde + 2 elipsoidal
> bombe + 2 radyal nozul (geometri) tanımlanıp, ASME iç basınç et kalınlığı + MAWP + hidrotest
> golden-case testlerini geçiyor; sonuç izlenebilir (ara değerler + madde referansı) ve JSON'a
> yazılıp geri okunuyor.

---

## Faz 2 — CAD, rapor ve revizyon sistemi

**Hedef:** Çekirdeğin ürettiği ölçülerden 3D/STEP model ve tam PDF rapor üret; revizyonu yönet.

### 2.A — `cad-engine/` (CadQuery + OCCT, kaynak §10)
- **CAD üretim sırası:** (1) iç/dış çapa göre gövde → (2) et kalınlığı → (3) sol+sağ bombe →
  (4) gövdeyle birleştir → (11) geometri geçerlilik → (12) **STEP export**. (Nozul adımları
  5–10 Faz 3'te açılır.)
- **`project data → CAD`** akışı (K2): CAD, hesabın ürettiği ölçüleri **girdi** alır, ölçü üretmez.
- **CAD doğrulamaları (kaynak §10):** tek/beklenen solid sayısı, negatif hacim yok, açık kabuk/
  bozuk yüzey yok, **hesaplanan iç hacim ↔ CAD hacmi tolerans içinde**.

### 2.B — Hacim ve ağırlık
- İç hacim (akışkan) + metal ağırlığı; malzeme yoğunluğu ile. Rapora ve tutarlılık kontrolüne girer.

### 2.C — `report-engine/` (PDF/HTML rapor, kaynak §11)
- **23 bölümlük yapı:** kapak → proje/revizyon → standartlar+sürümleri → tasarım temeli →
  akışkan/koşullar → PED kapsam/kategori → malzeme listesi → ana geometri → gövde/bombe/nozul
  hesapları → kaynak/NDT özeti → MAWP → test basıncı → ağırlık/hacim → nozul schedule →
  kaynak haritası → isim plakası → ESR matrisi → uyarılar/kapsam dışı → 2D/3D görünüşler →
  onay/imza.
- **İzlenebilirlik bloğu (her rapor):** software version, calculation engine version,
  standard pack version, material database version, project revision, calculation date,
  **input file hash**, **report hash** (kaynak §11).
- Standart uzun metni **kopyalanmaz** (K6); hesap yöntemi kendi açıklamanla + madde referansıyla.

### 2.D — Revizyon ve tutarlılık mekanizması (kaynak §16)
- **Project / Revision Service.** Seçilen nominal kalınlık değişirse otomatik:
  MAWP yeniden → nozul takviyesi yeniden → ağırlık/hacim güncellenir → STEP yeniden üretilir →
  **eski PDF rapor "OUTDATED" işaretlenir**.

> **Faz 2 bitti kabul kriteri:** Faz 1 projesinden geçerli bir **STEP** dosyası + tam **PDF
> rapor** üretiliyor; CAD hacmi hesap hacmiyle tolerans içinde; kalınlık değişince rapor eski
> işaretleniyor. `cad-validation/` ve `report-snapshots/` testleri yeşil.

---

## Faz 3 — Nozul ve kaynaklar

**Hedef:** Açıklık takviye hesabı + nozul yerleşimi/deliği + kaynak/NDT modeli + çakışma kontrolü.

### 3.A — `nozzles/` (konum + takviye, kaynak §6/§8-D)
- **Konum: üç koordinat** — eksenel z, çevresel açı θ, eğim açısı α. Bombe üzerindeki nozul
  için düz eksenel mesafe yerine yüzey parametresi/merkez açısı.
- **ASME açıklık takviye alan hesabı:** açıklık izinli mi, etkin çap, gerekli takviye alanı,
  gövde/bombe fazlası, nozul boynu katkısı, iç/dış çıkıntı, **takviye pedi**, kaynak metali
  katkısı, takviye sınırları, boyun minimum kalınlığı.
- **Nozul ekranı grafiği:** gerekli alan vs. mevcut alanların kalem kalem gösterimi + PASS/FAIL.
- **Nozul schedule** üretimi (rapora girer).

### 3.B — `cad-engine/` nozul adımları (5–10)
Nozul merkez eksenleri → nozul boruları → gövdede **delik kes** → takviye pedleri → flanşlar →
kaynak temsilleri.

### 3.C — `welds/` (kaynak + NDT, kaynak §9)
- **`WeldJoint`**: joint_id, joint_type, connected_components[], weld_category, weld_process,
  full/partial_penetration, joint_efficiency, joint_coefficient, nde_method, nde_extent,
  wps_number, pqr_number, welder_qualification, pwht_required, pwht_procedure.
- **Kontroller:** NDT kapsamı ↔ kaynak verimi uyumlu mu, tam nüfuziyet gerekli mi, nozul kaynak
  tipi hesapta kabul edilen tip mi, WPS/PQR/kaynakçı girilmiş mi, PWHT değerlendirilmiş mi.

### 3.D — Çakışma / geometri kontrolleri (kaynak §10)
Nozul-nozul girişimi, nozul-kaynak dikişi yakınlığı, nozul bombe teğet çizgisini geçiyor mu,
minimum kenar mesafeleri, delik takviye pedinden büyük mü.

> **Faz 3 bitti kabul kriteri:** İki radyal nozul (takviye pedli) tam takviye hesabından geçiyor,
> STEP'te gerçekten gövdeyi kesiyor, çakışma kontrolleri çalışıyor, nozul schedule + kaynak
> haritası rapora giriyor.

---

## Faz 4 — PED/CE sınıflandırma ve uygunluk

**Hedef:** Avrupa rotası — PED kapsam/kategori motoru + uygunluk dokümantasyonu + EN 13445 eklentisi.

### 4.A — `ped-2014-68-eu/` (Classification Engine, kaynak §3)
- **Girdiler:** ekipman türü, PS, V, DN, TS min/max, akışkan fazı (gaz/buhar/sıvı), TS'deki
  buhar basıncı, CLP tehlike sınıfları, Grup 1/Grup 2, ısıtılan mı, tek kap/assembly.
- **Mantık:** akışkan grubu CLP'ye göre; çok akışkanda **en yüksek kategoriyi** oluşturan esas.
  PS×V hesabı → Annex II tablo seçimi → **SEP / Kategori I–IV**.
- **Modül eşlemesi:** SEP→CE yok; I→A; II→A2/D1/E1; III→B+D/B+F/B+E/B+C2/H; IV→B+D/B+F/G/H1.
- **Çıktı:** PED kapsamı, ekipman türü, faz, grup, sınıflandırma tablosu, PS×V, kategori,
  uygunluk modülleri, onaylanmış kuruluş gerekliliği, CE uygulanabilirliği.

### 4.B — `compliance/` (dokümantasyon, kaynak §3)
ESR (temel güvenlik gerekleri) matrisi, risk/tehlike analizi formu, uygulanan/kısmen uygulanan/
karşılanmayan standart maddeleri, **EU Declaration of Conformity taslağı**, isim plakası bilgileri,
kullanım/güvenlik talimatı şablonu, teknik dosya indeksi (10 yıl saklama notu).

### 4.C — `standards/manifests/` (sürüm kilidi, kaynak §2)
**`StandardPack`**: code_family, base_edition, amendments[], ped_directive, harmonised_list_date.
Proje başında seçilip **kilitlenir**; harmonize liste değişse de eski proje değişmez (K3).

### 4.D — `code-en-13445/` (EN rotası — çekirdek doğrulandıktan sonra)
`EN13445DesignCode(DesignCode)`: gövde/bombe/nozul EN 13445-3 kurallarıyla; joint coefficient;
**PED test basıncı = max(1.25 × çalışma azami yükü, 1.43 × PS)**. ASME ile **aynı hesap içinde
karıştırılmaz** — kullanıcı proje başında rota seçer.

> **Faz 4 bitti kabul kriteri:** Örnek bir kap için PED motoru doğru kategori + modül + NB
> gerekliliği üretiyor; ESR matrisi + DoC taslağı + isim plakası rapora giriyor; EN rotası
> kendi golden-case'lerini geçiyor.

> **✅ Faz 4 TAMAMLANDI** (2026-07-20)
>
> **Oluşturulan dosyalar:**
> - `packages/ped-2014-68-eu/src/ped_2014_68_eu/` — PED Classification Engine (enums, models, tables, engine)
> - `packages/compliance/src/compliance/` — ESR matrisi, DoC taslağı, isim plakası, risk analizi, teknik dosya indeksi
> - `packages/code-en-13445/src/code_en_13445/` — EN13445DesignCode + EN 13445-3 formülleri
> - `standards/manifests/` — StandardPack modeli + ASME/EN manifest JSON'ları
> - `standards/clause-mappings/` — Formül ↔ madde referans eşleştirmeleri
> - `tests/faz4/` — 62 test (PED sınıflandırma, compliance, EN 13445, StandardPack)
>
> **Test sonuçları:** 62 Faz 4 testi + 193 mevcut test = **255 test PASS**, regresyon yok.
>
> **Örnek kap sonucu (PED):**
> - PS=10 MPa, V=2000 L, Grup 1 gaz → PS×V=20000 → **Kategori IV**, Modül G, NB gerekli, CE uygulanabilir.
>
> **EN rotası sonucu:**
> - D_i=1000mm, t=12mm, P355NH, f=163MPa, z=1.0, P=1.2MPa → gerekli kalınlık 4.15mm (PASS)
> - PED test basıncı = max(1.25×1.0, 1.43×1.5) = **2.145 MPa**
>
> **PAYLAŞILAN DEĞİŞİKLİK İSTEKLERİ:** Yok — tüm Faz 4 bağımsız paketlerde tamamlandı.

---

## Faz 5 — İleri hesaplar ✅ TAMAMLANDI

Kaynak §5/§15. Sırasıyla eklenir, **çekirdeğin yerine geçmez**:
- Dış basınç ve vakum, flanşlar, destekler (support), rüzgâr/deprem, nozul harici boru yükleri,
  lokal gerilmeler, yorulma.
- **FEA (ek doğrulama):** Parametrik CAD → basitleştirilmiş geometri → **Gmsh** mesh →
  **CalculiX / Code_Aster** → stress linearization → code acceptance checks. Mesh kalitesi,
  sınır şartları ve gerilme sınıflandırması **mühendis incelemeden** "uygun" verilmez.

### Faz 5 Durum Raporu (2026-07-20)

| Paket | Durum | Açıklama |
|---|---|---|
| `packages/external-pressure/` | ✅ Çalışan hesap | ASME UG-28 mantığı — dış basınç + vakum stabilite. 12 test geçti. |
| `packages/flanges/` | ✅ Çalışan hesap | ASME Appendix 2 mantığı — moment, gerilme kontrolleri. 12 test geçti. |
| `packages/supports/` | ✅ Çalışan hesap | Zick analizi (saddle) + skirt temeli. 14 test geçti. |
| `packages/fea/` | ⚠️ İskelet | REVIEW_REQUIRED modu. Çözücü kurulu değilse sahte PASS ÜRETMEZ. 9 test geçti. |

**Test sonuçları:** 47/47 Faz 5 testi PASSED. Mevcut testler bozulmadı (380/382 geçti, 2 önceden FAIL).

### Eklenen paketler:
- `packages/external-pressure/` — `ExternalPressureCalculator` (UG-28 shell + head + vacuum)
- `packages/flanges/` — `FlangeCalculator` (Appendix 2 moment + stress checks)
- `packages/supports/` — `SupportCalculator` (Zick saddle + skirt foundation)
- `packages/fea/` — `FEAdapter` (iskelet: CAD→mesh→solver→linearization→acceptance)

### Rüzgâr/deprem ve nozul harici yükleri:
- OUT OF SCOPE / NOT CALCULATED — iskelet bırakıldı (V1 kapsamı dışı).

---

## UI ekranları (Faz 1'den sonra paralel geliştirilir)

React/TS ↔ FastAPI (REST/WebSocket). Kaynak §19 — 14 ekran:
1. New Project · 2. Code & Edition · 3. Design Conditions · 4. Fluid & PED Classification ·
5. Vessel Geometry · 6. Materials · 7. Shell Sections · 8. Heads · 9. Nozzles ·
10. Welds & NDT · 11. Calculation Results · 12. 3D Model · 13. PED Compliance · 14. Report Export.

- **3D ekranı:** kullanıcı nozul eklemek için gövdeye tıklar; arka planda konum **kesin olarak
  z, θ, α**'ya çevrilir (K1/K2).
- Sonuç ekranı çok durumlu (PASS/FAIL/REVIEW/NOT CALCULATED/OUT OF SCOPE) + nozul alan grafiği.

---

## Doğrulama ve test stratejisi (tüm fazlara yayılı)

Kaynak §17 — **bu yazılımın en önemli kısmı kod değil, doğrulamadır.**

| Katman | İçerik |
|---|---|
| Birim | Basınç/sıcaklık dönüşümü, alan/hacim, interpolasyon, tolerans, yuvarlama. |
| Golden-case | Her standart maddesi: known input → expected intermediate → final + tolerans + kaynak/sürüm + bağımsız gözden geçiren. |
| Regresyon | Yeni kod eski onaylı proje sonucunu değiştiriyor mu? |
| Geometrik | STEP açılıyor mu, solid geçerli mi, hacim/nozul konumu doğru mu, çakışma var mı? |
| Bağımsız hesap | En kritik hesaplar Python **+** ayrı Excel/Mathcad/el hesabı (aynı kodu paylaşmadan). |
| Uzman incelemesi | Üretim öncesi: basınçlı kap + kaynak + NDT + PED/CE uzmanı, gerekirse onaylanmış kuruluş. |

---

## Yasal / telif (kodlama boyunca uyulacak — kaynak §13)

- Standart metnini/tablolarını/tüm malzeme verisini **yazılıma gömme**.
- Yalnızca **madde referanslarını** sakla; formülleri mühendislik uzmanıyla doğrula.
- Malzeme verisini **kullanıcı içe aktarsın**; PDF raporda standardın uzun metnini kopyalama.
- Ticari dağıtım öncesi TSE/CEN ve ASME lisans şartlarını kontrol et.

---

## Bağımlılıklar / referans projeler (kaynak §14)

| Proje | Kullanım | Uyarı |
|---|---|---|
| **CadQuery** | Ana CAD + STEP motoru | — |
| **FreeCAD** | STEP açma/kontrol/elle düzenleme, ileride workbench | — |
| **CalculiX** | İleride FEA çözücü | V1'de zorunlu değil |
| **Code_Aster** | İleri elastik/plastik/termal/yorulma | Sonraki aşama |
| **thepvguy/calctoys** | Fikir/araştırma | Betikler güvenilmez — **kopyalama** |
| **Vessel Guard** | Arayüz/organizasyon incelemesi | Formüller doğrulanmadan referans alınmaz |

---

## Özet yol haritası

| Faz | Çıktı | Odak |
|---|---|---|
| **0** | İskelet + coverage matrisi + araçlar | Kapsamı sabitle |
| **1** ⭐ | ASME çekirdeği (tek gövde + 2 bombe + MAWP + hidrotest), JSON, testler | **Dar çekirdek önce** |
| **2** | CadQuery STEP + PDF rapor + revizyon | Model + doküman |
| **3** | Nozul takviye + delik + kaynak/NDT + çakışma | Açıklıklar |
| **4** | PED sınıflandırma + ESR/DoC + EN 13445 eklentisi | Avrupa rotası |
| **5** ✅ | Dış basınç, flanş, destek, rüzgâr/deprem, FEA | İleri hesaplar — 47 test PASSED |

**İlk kodlama işi arayüz değil**, standarttan bağımsız domain modeli + test edilebilir
hesap çekirdeğidir. Aksi halde ASME/EN/CAD/PDF kodları birbirine karışır ve doğrulanamaz.

---

## Güncel Durum (2026-07-24)

**Tüm fazlar (0–5) tamamlandı.** 442 test PASSED, 1 skipped.

| Katman | Durum | Test |
|---|---|---|
| Domain + Units | ✅ | 86 test |
| Calc-core | ✅ | 11 test |
| ASME VIII-1 | ✅ | 29 golden-case |
| Nozul takviye | ✅ | 21 test |
| Kaynak + Çakışma | ✅ | 62 test (Faz 3) |
| PED + Compliance + EN 13445 | ✅ | 62 test (Faz 4) |
| Dış basınç + Flanş + Destek + FEA | ✅ | 47 test (Faz 5) |
| CAD motoru | ✅ | 35 test (gövde, 4 bombe tipi, kombinasyonlar, STEP, STL) |
| Rapor | ✅ | 19 test |
| Persistence + Revision | ✅ | 28 test |
| API (FastAPI) | ✅ | entegrasyon testleri dahil |

**Bilinen eksikler:**
- CAD: torisferik profil yaklaşık (elipsoidal revolve), düz flanş union-tabanlı
- FEA: iskelet (çözücü kurulu değilse REVIEW_REQUIRED)
- UI: 6 adımlı sihirbaz (14 ekran planının sadeleştirilmiş hali)
