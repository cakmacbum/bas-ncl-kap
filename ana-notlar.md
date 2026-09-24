# Basınçlı Kap Suite — PV Elite Seviyesine Giden Ana Notlar

Güncelleme: 20 Eylül 2026

## 1. Mevcut durum

Proje bugün dar kapsamlı ASME VIII-1 ön boyutlandırma ve doğrulama geliştirme sürümüdür.
Temel gövde/bombe iç basınç hesapları, radyal nozul ön kontrolü, hesap orkestrasyonu,
traceability ve test altyapısı güçlü başlangıç noktalarıdır.

Son doğrulama: **571 pytest geçti / 1 atlandı**, `tsc --noEmit`: **0 hata**.

### Kapatılan kritik maddeler

- **B-20:** Skirt/leg destek payload wiring’i, UI ölçüleri, malzeme aktarımı ve entegrasyon testleri.
- **B-21:** UG-33 bombe dış basıncı `8Bt/(3D)` yerine `2Bt/D`; dış çap etiketi düzeltildi.
- **B-22:** `calculation_code` ile açık ASME/EN motor seçimi; sessiz ASME fallback kaldırıldı.
- **P0-02:** Yaklaşık MDMT hesabı artık nihai `PASS` değil `REVIEW_REQUIRED`.
- **P0-03:** Basitleştirilmiş dış basınç hesabı artık nihai `PASS` değil `REVIEW_REQUIRED`.
- **UI:** EN 13445 dropdown’a uyarı mesajıyla eklendi ve wiring testiyle korundu.

Bu kapanışlar tam normatif kapsam anlamına gelmez. Tam UCS-66, UG-28/UG-33 chart yöntemi,
stiffening ring ve gerçek yük analizleri hâlâ eksiktir.

## 2. Faz A — Güvenli ASME çekirdeği

Amaç, eksik veya yaklaşık bir yöntemin kullanıcıya nihai tasarım onayı gibi görünmesini engellemektir.

### A1 — Büyük güvenlik açıkları

#### B-14 — Basınç tahliye sistemi

UG-125–136 kapsamında emniyet vanası/patlama diski, set basıncı, MAWP ilişkisi,
accumulation ve blowdown hesabı yoktur. Yeni `pressure-relief` domain/paket, UI formu,
orchestrator bağlantısı, sonuç grubu ve rapor bölümü gerekir. Bu mevcut açıkların en büyük
tek güvenlik kalemidir.

#### P0-06 — Çoklu bileşen veri kaybı

UI ve bazı backend yolları `shell_sections[0]`, `materials[0]`, `welds[0]` gibi ilk eleman
basitleştirmeleri kullanır. Karar verilmelidir: V1 tek bileşenle sınırlandırılıp fazlası
reddedilecek veya her section/head/material/weld kendi koşullarıyla hesaplanacaktır.

Hedef: API’den gelen çoklu verinin UI’da tek elemana düşmemesi; her sonuçta component ID,
malzeme, kaynak, elevation ve tasarım koşulu izlenebilir olmasıdır.

#### B-06/P0-05 — Torisferik geometri

İç/dış çap ayrımı, crown radius ve knuckle radius açıkça modellenmelidir. Standart ASME F&D
geometrisi seçilmedikçe sessiz varsayım yapılmamalıdır. Özel geometri için kullanıcı girdisi,
uygulanabilirlik kontrolü ve dış çap temelli golden case gerekir.

#### P0-04 — Destek güvenliği

Skirt/leg wiring tamamlanmış olsa da destek fiziği hâlâ basittir. Tamamlanana kadar destek
sonuçları `REVIEW_REQUIRED` olmalıdır. Saddle/Zick, skirt buckling/base ring/anchor,
leg member buckling, foundation bearing ve local shell stress ayrı doğrulanmalıdır.

### A2 — Sonuç statüsü standardı

- `PASS`: Normatif yöntem ve gerekli veri tam.
- `FAIL`: Normatif yöntemle yetersizlik.
- `REVIEW_REQUIRED`: Yaklaşık veya kısmi yöntem.
- `BLOCKED_MISSING_INPUT`: Kullanıcı girdisi eksik.
- `BLOCKED_CODE_DATA`: Standart tablosu/verisi eksik.
- `OUT_OF_SCOPE`: Modül desteklenmiyor.

Her sonuçta kod/baskı, motor/build, material pack, clause/formula reference, input snapshot,
intermediate değerler, varsayımlar ve applicability sınırları bulunmalıdır.

## 3. Faz B — Normatif ASME VIII-1 kapsamı

### B1 — Malzeme ve kod verisi

Manuel stress girdilerinden sürümlü veri paketine geçilmelidir:

- ASME II-D allowable stress.
- Yield/tensile ve elastisite modülü.
- Ürün formu, kalınlık ve sıcaklık aralıkları.
- UCS-66 curve group.
- PWHT, impact ve weld kısıtları.
- Kaynak, checksum, edition ve proje snapshot’ı.

### B2 — İç basınç ve geometri

- B-02: Genel eliptik bombe oranları ve Appendix 1-4.
- B-03: Dış çap alternatifleri.
- B-04: Dairesel olmayan flat head ve `Z` faktörü.
- Koni geçişleri ve U-2(g) discontinuity.
- Eccentric cone/reducer.
- Design mode/rating mode ayrımı.
- Çoklu çap, section ve stacked vessel.

### B3 — Nozul ve açıklıklar

- B-07: Eğik/hillside nozzle gerçek `F` faktörü.
- B-08: Büyük açıklık Appendix 1-7.
- Yakın ve çoklu açıklık etkileşimi.
- Normatif UG-45 schedule minimumları.
- Nozzle weld/local stress.
- WRC 107/297/537 dış yükleri.
- Nozzle pressure, thermal ve fatigue cycles.

### B4 — Dış basınç

- A/B değerleri serbest kullanıcı sayısı yerine chart/data lookup ile sağlanmalı.
- Malzeme, sıcaklık, Do/t ve L/Do bağıntıları uygulanmalı.
- Chart dışı değerler extrapolation olmadan bloklanmalı.
- Silindir, koni ve her bombe tipi ayrı yönteme sahip olmalı.
- Iteratif required thickness/MAEP ve yakınsama geçmişi raporlanmalı.
- Stiffening ring spacing, effective shell width, required inertia ve ring-shell interaction.
- Vacuum, jacket ve local external pressure kombinasyonları.

### B5 — Flanş, conta ve cıvata

- Flange domain modeli orchestrator’a bağlanmalı.
- B16.5/B16.47 rating ile Appendix 2 tasarımı ayrılmalı.
- Gasket `m/y`, seating/operating yükleri.
- Bolt material, area, circle ve preload.
- Hub factors, rigidity ve tightness/leakage.
- EN 1591 için ayrı Avrupa flange rotası.

## 4. Faz C — Gerçek yükler ve taşıyıcı sistem

### C1 — Global load engine

Empty, erected, operating, shutdown, flooded, hydrotest, transport ve lifting durumları;
iç ekipman/platform/izolasyon/boru ağırlıkları; elevation tabanlı ağırlık merkezi;
axial force, shear, moment, deflection diyagramları; yük kombinasyonları ve governing case.

### C2 — Wind/seismic/dynamic

Kod seçilebilir rüzgâr hesabı, deprem spektrumu, vortex shedding, dinamik büyütme,
blast/wave veya kullanıcı tanımlı lateral profil.

### C3 — Destek, ankraj ve kaldırma

- Skirt: buckling, base ring, anchor bolt circle, bolt tension/shear, concrete bearing.
- Saddle: tam Zick, wear plate, horn angle ve ring/stiffener.
- Leg/lug/trunnion: gerçek koordinatlar, member buckling ve bağlantılar.
- Lifting lug: rigging geometry, rotational lift ve local shell reinforcement.
- Foundation load summary.

## 5. Faz D — EN 13445 ve PED

EN motoru artık seçilebilir, ancak kapsamı tamamlanmış değildir.

- EN shell/head yöntemleri için golden case.
- EN torispherical geometri doğrulaması.
- EN dış basınç, nozzle ve flange.
- EN fatigue ve material data.
- EN load combinations.
- PED category, Essential Safety Requirements ve notified body iş akışı.
- Declaration of Conformity, nameplate ve technical file.
- PED çıktılarının immutable hesap revision’ına bağlanması.

Desteklenmeyen EN modülleri `NOT_CALCULATED` veya `OUT_OF_SCOPE` kalmalı; ASME’ye fallback
yapılmamalıdır.

## 6. Faz E — Doğrulama ve ürünleştirme

### E1 — Verification & validation

Her modül için applicability, bağımsız el hesabı, normal/sınır/fail/block golden case,
PV Elite/COMPRESS karşılaştırması, tolerans politikası, monotonicity/property testleri,
unit conversion, NaN/inf, tekillik ve yakınsama testleri gerekir. Yetkin mühendis sign-off’u,
verification manual ve CI regression lock zorunludur.

### E2 — Kalıcı ürün altyapısı

Transactional database, immutable calculation run, revision/audit history, migration,
backup/restore, RBAC, approval/sign-off, structured logging, monitoring, error tracking,
dosya eki ve teknik belge yönetimi.

### E3 — Raporlama ve imalat

Guaranteed PDF/Word, component-level traceability, governing load tabloları, deficiency list,
review/approval, ASME Data Report/PED technical file, gerçek torisferik CAD, GA/detail drawing,
weld symbols, BOM ve hesap-çizim revision matching.

## 7. Şimdilik ertelenecek kapsam

ASME VIII-2 Class 1/2, gerçek FEA/DBA, fatigue/creep-fatigue, UHX/TEMA heat exchanger,
jacket/multi-chamber, API 650, API 579, bellows, geniş uluslararası kod ailesi,
optimizasyon ve çift yönlü piping/CAD/thermal entegrasyonu; ASME VIII-1 çekirdeği ve yük
motoru güvenilir olmadan başlanmamalıdır.

## 8. Öncelik sırası

1. B-14 basınç tahliye.
2. P0-06 çoklu bileşen veri kaybı.
3. B-06 torisferik geometri.
4. Sürümlü malzeme ve kod veri paketi.
5. Tam dış basınç ve stiffening ring.
6. Eğik/büyük nozul, WRC ve local stress.
7. Flanş domain bağlantısı.
8. Global yükler, destek/ankraj/temel.
9. EN 13445/PED kapsamı.
10. V&V, rapor, kalıcılık ve ürünleştirme.
11. VIII-2, FEA ve ileri ürün aileleri.

## 9. PV Elite seviyesine ulaşma kabul kriteri

Ürün ancak şu koşullar birlikte sağlandığında PV Elite seviyesinde ASME tasarım platformu
olarak değerlendirilebilir:

- İlan edilen ASME kapsamı normatif veriyle hesaplanıyor.
- Yaklaşık yöntemler nihai `PASS` üretmiyor.
- Çoklu bileşen ve yük durumları veri kaybetmiyor.
- Relief, nozzle, external pressure, flange ve support yolları bağlı.
- Material/code pack’ler sürümlü ve izlenebilir.
- Her modülün bağımsız golden case’i mevcut.
- Yetkin basınçlı kap mühendisi sign-off veriyor.
- Hesap, rapor, çizim ve revision birbirine bağlanıyor.
- Desteklenmeyen kapsam kullanıcıya açıkça gösteriliyor.

## 10. Bugünkü güvenli kullanım sınırı

Program, desteklenen geometrilerde dar kapsamlı ASME VIII-1 ön boyutlandırma, eğitim,
prototipleme ve hesap geliştirme için kullanılabilir.

Bağımsız doğrulama olmadan EN/PED/CE kararı, dış basınç veya MDMT muafiyeti, destek/ankraj,
rüzgâr/deprem/taşıma/kaldırma, eğik/büyük nozul, flange, fatigue, FEA/DBA, imalata esas
çizim/BOM veya resmi tasarım raporu için kullanılmamalıdır.
