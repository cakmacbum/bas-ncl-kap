# Denetim Raporu Doğrulama Eki — 20 Eylül 2026

> Bu belge [kapsam/boşluk raporunu](../../eksikler.md) düzeltir ve tamamlar. Ana rapora
> dokunulmamıştır; bu sayfa yalnızca bağımsız doğrulama bulgularını taşır.

## Amaç ve kapsam

Önceki `eksikler.md` raporu dosya:satır düzeyinde yeniden okundu. Bu ekin amacı:

- rapordaki iki olgusal hatayı açıkça düzeltmek,
- raporda kaçan üç gerçek kusuru kalıcı olarak kaydetmek,
- hesap sonucu üreten yollarla yalnız testte çalışan paketleri ayırmak,
- sonraki kod düzeltme turu için kanıt, etki ve kapanış ölçütü vermektir.

İlk doğrulama turunda hesap kodu değiştirilmedi; sonraki kapanış turunda B-20/B-21/B-22 ile
MDMT ve dış basınç güvenlik politikaları kodlandı. `eksikler.md` değiştirilmedi. Kod dışı doğrulama için iki
ampirik kontrol yapıldı: üretim `check_supports` payload’ının birebir kopyasıyla skirt/leg
sonuçları çalıştırıldı; UG-33 bombe formülü docstring’i ile uygulanan katsayı karşılaştırıldı.

## Taban doğrulama durumu

> Güncel durum notu: Bu belge ilk bağımsız doğrulama anını da tarihsel olarak saklar. O turdaki
> MDMT ve dış basınç `PASS` riski, sonraki kod turunda yaklaşık yöntemler için `REVIEW_REQUIRED`
> politikasıyla kapatıldı; B-20/B-21/B-22 de aynı kod turunda düzeltildi.

- İlk bağımsız doğrulama tabanı: **567 test geçti / 1 test atlandı**. Atlanan test opsiyonel PDF/WeasyPrint yoludur.
- TypeScript: `tsc --noEmit` **0 hata**.
- Bu güncel sürüm, ilk doğrulama bulgularını ve sonraki kod/UI kapanışlarını birlikte izler; `eksikler.md` değiştirilmedi.
- Paket testlerinin yeşil olması üretim orkestrasyonunun bağlı olduğunu kanıtlamaz; bu ekin ana
  konusu tam olarak bu “izole test / kırık wiring” ayrımıdır.

## Doğrulanan önceki bulgular

| Rapor maddesi | Durum | Kanıt/yorum |
|---|---|---|
| MDMT P0-02 | **Doğru; kapatıldı** | `(t-38)×0.5` basitleştirmesi korunuyor ancak sonuç artık nihai `PASS` değil `REVIEW_REQUIRED`; gerçek UCS-66 eğrisi hâlâ eksik. |
| Dış basınç P0-03 | **Doğru; kısmen kapatıldı** | A/B kullanıcı girdisi, çapraz kontrol ve stiffening ring eksikleri sürüyor; basitleştirilmiş uygun sonuç artık `REVIEW_REQUIRED`, bombe katsayısı B-21 ile düzeltildi. |
| Torisferik P0-05 | **Doğru** | `code-asme-viii-1/design_code.py:22-38` varsayılan yarıçap davranışı; B-06 ile de kayıtlı. |
| P0-06 çoklu model | **Kısmen doğru** | Ana hesap döngüsü bileşenleri dolaşıyor; ilk-eleman kısayolları hidro/pnömatik malzeme, kaynak referansı, destek gövdesi ve vakum yollarıyla sınırlı. UI ise `pages.tsx:217-238` ile diziyi tek elemana indiriyor; API’den gelen çok kesitli proje UI’da açılırsa veri kaybı var. |

## Düzeltilen önceki iddialar

### 1. P0-01’in kullanıcı arayüzü kısmı yanlış ifade edilmiş

Önceki rapor, `pages.tsx` kullanıcının ASME VIII-1 veya EN 13445 seçebildiğini söylüyordu.
Bu, ilk doğrulama anı için doğru değildi: `apps/web-ui/src/pages.tsx:89-91` dropdown’unda tek seçenek
**ASME VIII Division 1** vardı. Kapanış turunda EN 13445 seçimi uyarıyla eklendi.
Sonuç `code` alanının ASME olarak etiketlenmesi de bu gözlemi destekliyor.

Gerçek kusur daha dar ama daha kesin tanımlanmalıdır: API’ye `calculation_code = EN 13445`
gönderilirse backend bu alanı okumaz ve sessizce ASME VIII-1 motorunu çalıştırır. B-22’de
bu sessiz istek-yoksayma olarak kayda geçirilmiştir.

### 2. P0-04’ün “yanlış PASS” yönü skirt/leg için yanlış

Önceki rapor destekleri genel olarak fazla basitleştirilmiş ve yanlış `PASS` üretebilir diyordu.
Skirt ve leg için üretim payload’ı gerçekte eksik olduğundan sonuç **yanlış PASS değil,
her seferinde `NOT_CALCULATED`** olmaktadır. Rapordaki fiziksel eleştiri yine geçerlidir:
`r_dist = D_leg × n / (2π)` gerçek kap/bolt-circle geometrisinden bağımsızdır ve bağlansa bile
geçerli bir destek modeli sayılamaz. Saddle yolu bu payload kusurundan ayrıdır.

## Kaçırılan kusur 1 — B-20: skirt/leg üretim hesabı ölü

### Kanıt

`code-asme-viii-1/src/code_asme_viii_1/design_code.py:990-1005` civarında `check_supports`
payload’ı oluşturuluyor. Ancak:

- `supports/src/supports/support_calc.py:212` `skirt_material_id` okuyor;
- `supports/src/supports/support_calc.py:329` yine `skirt_material_id` okuyor;
- aynı yollar `support.diameter_mm` ve `support.thickness_mm` bekliyor;
- üretim payload’ı bu üç anahtarı göndermiyor;
- ayak sayısı üretimde `payload["leg_count"]` adıyla yazılıyor;
- hesaplayıcı `support.get("n_legs", 4)` okuyor.

Bu nedenle kullanıcı UI’da `sup.material_id`, çap, kalınlık veya ayak sayısı girse bile skirt/leg
hesaplayıcısına ulaşmıyor. Elle `skirt_material_id` içeren test payload’ı kullanan
`tests/faz5/test_faz5_supports.py:257` bu entegrasyon kusurunu yakalayamıyor; `check_leg_support`
için ayrıca üretim hattını doğrulayan test yok.

### Ampirik sonuç

Üretim payload’ının birebir kopyasıyla yapılan çalıştırma:

```text
SKIRT -> CalculationStatus.NOT_CALCULATED
LEG   -> CalculationStatus.NOT_CALCULATED
```

Beklenen davranış gerçek destek girdileriyle hesap sonucu üretmekken, mevcut davranış her iki yol
için de `Skirt material '' not found.` türü not-calculated sonucudur.

### Etki

- **Etki yönü:** sonuç üretilememesi; “özellik bağlı” görünmesine rağmen hesap ölü.
- **Güvenlik:** UI’da destek tanımlayan kullanıcı destek kontrolünün yapılmadığını sonuç grubundan
  açıkça anlayabilir; ancak ürün kapsamı ve rapor iddiası olduğundan ciddi kapsam yanıltmasıdır.
- **Kapsam:** Saddle yolu ayrıca incelenmelidir; B-20 yalnız skirt/leg payload ve anahtar sözleşmesidir.

### Kapatma yolu (sonraki kod turu)

1. Üretim payload’ı ile `SupportCalculator` sözleşmesini tek şemada birleştir: material ID,
   diameter, thickness, n_legs, base plate ve gerekli moment alanları açıkça taşınsın.
2. `leg_count`/`n_legs` tek bir kanonik ada indirilsin; geriye dönük JSON migration kararı verilsin.
3. UI’dan gelen skirt/leg örneğiyle orkestratör entegrasyon testi ekle; sonuç status’ü
   `NOT_CALCULATED` kalırsa test fail olsun.
4. Test sonucunun hesaplanması wiring düzeltmesidir; fiziksel destek formülünün yeterliliği ayrı
   bir P0/P1 mühendislik doğrulama işidir.

> **Kapanış durumu:** Factory, ASME/EN API testi ve uyarılı EN UI seçimi uygulandı. Aşağıdaki
> kapatma maddeleri tarihsel kabul kriteridir; açık kalan iş yalnız tam EN kapsamı ve normatif doğrulamadır.

### Tahmini büyüklük

**Küçük-orta:** payload mapping ve entegrasyon testi yaklaşık bir kod turu; gerçek skirt/leg,
ankraj, burkulma ve temel doğrulaması ayrı ve daha büyük bir mühendislik işidir.

## Kaçırılan kusur 2 — B-21: UG-33 bombe dış basıncı emniyetsiz katsayı kullanıyor

### Kanıt

`packages/external-pressure/src/external_pressure/formulas.py:145` docstring’i bombe için
`P_allow = B × t / (0.5 × D)`, yani `2Bt/D`, yaklaşımını belgeliyor. Aynı dosyanın
169-170. satırlarında uygulama şöyledir:

```python
# UG-33 basitleştirilmiş: P_allow = 4Bt / (3×0.5D) = 8Bt / (3D)
P_allow = 8.0 * B * t / (3.0 * D)
```

Bu `8Bt/(3D)` katsayısı silindir bağıntısındaki `4B/3` faktörünü bombe yoluna taşıyor. Bombe için
belgelenen `2Bt/D` ile oran:

```text
(8/3 Bt/D) / (2 Bt/D) = 4/3 = 1,333…
```

Sonuç, dosyanın kendi docstring’inde tarif ettiği yaklaşımdan **%33,3 daha yüksek** izin verilen
dış basınçtır; sapma emniyetsiz yöndedir. Bu rapor ASME metnini kopyalamaz: burada yazılan,
UG-28(d)/UG-33 atıflarıyla yapılan fark ve katsayı analizidir (K6).

### İkincil kanıtlar

- `ext_pressure.py:221-229` bilinçli olarak dış çapı geçiriyor;
- `ext_pressure.py:254` ara değeri “Inside diameter” diye etiketliyor;
- `head.type` formülü seçmiyor; yarım küre ve 2:1 eliptik bombe aynı bağıntıya gidiyor.

### Ampirik/etki özeti

Formül aynı pozitif `B`, `t`, `D` girdileriyle çalıştırıldığında uygulanan değer dokümante edilen
`2Bt/D` değerinin 1,333 katıdır. Bu nedenle hata `NOT_CALCULATED` değil, doğrudan **emniyetsiz
allowable external pressure** üretir.

### Kapatma yolu (sonraki kod turu)

1. Bombe yolunu doğru kod rotasına ayır; silindirik UG-28 katsayısını bombe yolundan çıkar.
2. `head.type` için en azından desteklenen geometriye göre farklı hesap/uygulama sınırı koy;
   bilinmeyen tipte blokla.
3. `D`/`Do`/`Ro` isimlerini tek anlamlı hale getir; ara değer etiketini gerçek çapla eşleştir.
4. Docstring, formül birim testi, küresel ve 2:1 eliptik golden case ekle.
5. Tam chart/iteratif UG-28/UG-33 yöntemi tamamlanana kadar sonucu nihai `PASS` sayma.

### Tahmini büyüklük

**Küçük düzeltme + orta doğrulama:** katsayı düzeltmesi tek satırlık olabilir; ancak geometriye
özgü bağımsız test, uygulanabilirlik sınırı ve tam dış basınç yöntemi ayrı iştir.

## Kaçırılan kusur 3 — B-22: `calculation_code` backend’de sessizce yok sayılıyor

### Kanıt

`apps/api/services.py:48-51` koşulsuz olarak `ASMEVIII1DesignCode` kuruyor. Backend içinde
`project.calculation_code` okunmuyor. Buna karşılık `packages/code-en-13445/src/code_en_13445/
design_code.py:58` tasarım kodu arayüzüne uygundur; paket tamamlanmış görünse de çağıran yoktur.

API’ye:

```json
{"calculation_code": "EN 13445"}
```

gönderilirse hata veya uyarı oluşmadan ASME VIII-1 sonucu döner. Orchestrator da proje kodu ile
seçilen design-code `code_name` değerinin tutarlı olduğunu doğrulamaz.

### Etki

- **Etki yönü:** yanlış standardın sessizce uygulanması; sonuç sayısal olarak geçerli görünür.
- **UI düzeltmesi:** İlk doğrulama anında kullanıcı dropdown’dan EN seçemiyordu; kapanış turunda
  EN seçimi uyarıyla açıldı. Backend sözleşmesindeki sessiz yoksayma da B-22 ile kapatıldı.
- `docs/calculation-coverage.md:65` satırı backend/UI kapsamıyla güncellendi; EN’in tamamlanmamış
  modülleri hâlâ `REVIEW_REQUIRED`/`NOT_CALCULATED` olarak işaretlenir.

### Kapatma yolu (sonraki kod turu)

1. `calculation_code` için açık factory/registry: ASME VIII-1 → ASME plugin, EN 13445 → EN plugin.
2. Bilinmeyen veya desteklenmeyen kodda `BLOCKED_MISSING_INPUT`/`BLOCKED_CODE_DATA`; ASME’ye
   sessiz fallback yok.
3. Orchestrator başlangıcında project code, engine `code_name` ve edition tutarlılık kontrolü.
4. API testinde ASME ve EN payload’larının farklı motor kimliği/sonuç kodu ürettiğini doğrula.
5. UI gerçek EN seçimi eklenene kadar tek ASME seçeneğini “EN rotası API’de henüz açık değil”
   şeklinde dürüstçe sınırlamak veya seçimi tamamen kaldırmak.

### Tahmini büyüklük

**Orta:** factory ve API testleri küçük; EN’in tüm dış basınç/nozul/flange/PED kapsamı ayrı büyük
bir çalışmadır. İlk kapanışın hedefi yanlış motoru çalıştırmayı engellemektir.

## 2026-09-20 kod turu sonucu

Bu ekte kaydedilen üç üretim kusuru sonraki kod turunda kapatıldı:

- B-20: Skirt/leg alanları domain modeline ve UI payload’ına eklendi; material ID, ölçüler ve `n_legs` üretim hattına bağlandı; orkestratör entegrasyon testleri eklendi.
- B-21: Bombe dış basıncı `P_allow = 2Bt/D` olarak düzeltildi; dış çap ara değer etiketi ve golden test güncellendi. Tam UG-33/UG-28 chart yöntemi hâlâ kapsam dışıdır.
- B-22: API `calculation_code` değerine göre ASME veya EN motoru seçiyor; EN API regresyon testi eklendi.

Kod turu sonrası doğrulama: hedefli destek/dış basınç testleri 29 geçti; tam pytest 571 geçti / 1 atlandı; `tsc --noEmit` 0 hata.

## Önceki P0’larla ilişki

P0-02 ve P0-03 aşağıdaki tabloda tarihsel doğrulama bulgusu olarak korunur; güncel davranışları
`REVIEW_REQUIRED` olup tam UCS-66/UG-28/UG-33 normatif yöntemi hâlâ tamamlanmamıştır.

| Önceki madde | Bu ekin kararı |
|---|---|
| P0-01 | UI seçimi iddiası düzeltilir; sessiz backend motor yoksayması B-22’ye taşınır. |
| P0-02 | Yaklaşık MDMT yöntemi korunur; nihai `PASS` riski kaldırıldı, tam UCS-66 doğrulaması açık kaldı. |
| P0-03 | Basitleştirilmiş dış basınç sonucu `REVIEW_REQUIRED`; A/B doğrulaması, stiffening ring ve tam UG-28/UG-33 kapsamı açık kaldı. B-21 katsayı hatası düzeltildi. |
| P0-04 | Genel “yanlış PASS” ifadesi skirt/leg için düzeltilir; B-20 ile daima `NOT_CALCULATED` olduğu kaydedilir. Fiziksel `r_dist` eleştirisi korunur. |
| P0-05 | Aynen korunur; B-06 ile zaten kayıtlıdır. |
| P0-06 | “Kısmen” olarak sınırlandırılır: ana loop doğru, belirli backend kısayolları ve UI tek-eleman veri kaybı devam ediyor. |

## Kapanış ve kalan doğrulama kabul kriterleri

- B-20: UI’dan gerçek skirt ve leg girdisiyle orkestratör `PASS/FAIL/REVIEW_REQUIRED` sonucu üretir;
  boş `skirt_material_id` veya default `n_legs=4` nedeniyle test geçmez.
- B-21: Bombe formülü için docstring, uygulama, unit test ve en az bir bağımsız golden case aynı
  katsayıyı gösterir; silindir ve bombe yolları ayrıdır.
- B-22: ASME ve EN isteği farklı engine kimliğiyle çalışır; desteklenmeyen EN fonksiyonu sessizce
  ASME’ye düşmez.
- `pytest`: güncel sonuç 571 passed / 1 skipped; `tsc --noEmit`: 0 hata.

## İlgili belgeler

- Ana kıyas raporu: [`../../eksikler.md`](../../eksikler.md)
- Kapsam sınırlamaları: [`limitations.md`](limitations.md)
- Hesap kapsam matrisi: [`calculation-coverage.md`](calculation-coverage.md)
- Bağımsız ASME örnekleri: [`validation/asme-worked-examples.md`](validation/asme-worked-examples.md)

---

*Oluşturma: 2026-09-20 · Güncelleme: 2026-09-20 kod kapanış turu · B-20/B-21/B-22, MDMT, dış basınç ve EN UI düzeltmeleri uygulanmıştır · Doğrulama eki*
