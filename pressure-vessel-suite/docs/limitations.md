# Limitations and Out-of-Scope Items

> Bu doküman, V1 sürümünün kapsam dışı bıraktığı özellikleri ve bilinen sınırlamaları listeler.

> **Güncel durum (Revizyon 3.3, 2026-09-25):** Bu belge tarih sırasıyla kayıt tutar; üstü çizili
> maddeler kapatılmıştır. Her hesabın etiketli güncel durumu için bkz.
> [`calculation-coverage.md`](calculation-coverage.md). Tarihli denetim belgesi:
> [`audit-verification-2026-09-20.md`](audit-verification-2026-09-20.md) (2026-09-20 anını anlatır).

## Phase C — Global load and support baseline (2026-09-20)

- **B-23:** `calc_core.load_engine` transfers six-component loads to the base, validates combination factors, and records a governing envelope. It is not a code-specific stability check; orchestrator results remain `REVIEW_REQUIRED`.
- **B-24:** `domain.global_loads` provides transparent preliminary equivalent-static wind and seismic models. Site spectra, modal/torsional response, vortex shedding and edition-specific factors remain out of scope.
- **Support orchestration (2026-09-25):** `check_supports` envelopes load cases instead of summing them (wind/seismic/hydrotest alternatives never add; only cases linked by `concurrent_with` and not in `NON_CONCURRENT_LOAD_PAIRS` combine), uses SRSS for Mx/My, and reports the governing case/source. Fz sign is undefined in the domain: K4 assumes Fz>0 downward. Compression uses hydrotest weight (metal + water, rho=1000 kg/m3 assumed); `empty_weight_N` is placed in the payload for uplift, but each calculator must read it. The position-interval gate now applies to saddles only; skirt/leg may sit on shell, head or cone. Horizontal-force moments need `elevation_mm` above the support base, otherwise the moment is 0 and an assumption is written; the lever/direction combination of Fx,Fy with Mx,My is added arithmetically (conservative).
- **Saddle (Zick) rewrite (2026-09-25):** `check_saddle` now follows the Zick 1951 / Moss PVDM 3-10 structure (M1, M2 with head depth H and tangent-to-tangent L, S1 tension/compression, shell and head shear, horn circumferential membrane + K6 bending, shell-bottom K7, each with its own allowable). The K1/K2/K3/K6/K7 coefficient tables are NOT embedded (K6): they are user inputs on the saddle (`zick_K*`, `saddle_stiffened`); missing values give `BLOCKED_CODE_DATA`, ring/head-stiffened cases use K1 = π (K2 = 1/π for a ring). Three or more saddles are `OUT_OF_SCOPE`; wear plate, ring design, UG-23(b) buckling and saddle/foundation are not checked, tension and compression share one K1 (K1' not separated), and the result stays `REVIEW_REQUIRED` even when every check passes. No published worked example with numbers could be retrieved, so tests use hand calculations and beam-statics limit cases.
- **B-25:** Support leg distribution radius and anchor tension/shear demand are recorded; missing anchor data cannot produce final `PASS`. Skirt buckling is now checked against a user-entered UG-23(b) B factor (`Support.skirt_allowable_compressive_MPa`, read from the licensed chart; not embedded, K6); without B the skirt result is `BLOCKED_CODE_DATA` unless stress already exceeds S (then FAIL). Skirt tension uses S·E with E defaulting to an assumed 0.6 (K4, written to the result) and uplift raises an anchor/base-plate warning because no skirt anchor check exists; skirt diameter is the MEAN diameter. Base ring, concrete bearing, detailed Zick and lifting-lug checks remain open.

## V1 kapsam dışı (Later)

| Kategori | Özellik | Gerekçe |
|---|---|---|
| Yük | Rüzgâr ve deprem | Koda özgü yük üretimi sonraki sürüm; `domain/global_loads.py` ön yardımcıları hesap hattında çağrılmıyor (B-24) |
| Yük | Nozula gelen harici boru yükleri | Sonraki sürüm |
| Yük | Yorulma analizi | Sonraki sürüm |
| Yapı | Düz kapak / kör flanş | ASME düz kapak UG-34(c)(2)/(3) hesaplanıyor (`C` kullanıcı girdisi, ön kontrol); EN'de düz kapak ve kör flanş (Appendix 2) yok |
| Yapı | Konik bölüm | ASME'de kalınlık + MAWP hesaplanıyor ve arayüzde koni formu var (`pages.tsx`); koni uç birleşimi (App 1-4/1-5) çözümü yok (`OUT_OF_SCOPE`); EN'de koni yok |
| Yapı | Çoklu gövde kesiti / 2'den fazla bombe / çoklu malzeme-kaynak | 2026-09-08 notu kısmen eskidi: arayüzde `addShell`/`addCone` ve `component_sequence` var; şematik/önizleme hâlâ `shell_sections[0]`, `heads[0]` kullanıyor. Kalan sınırların tam dökümü doğrulanamadı |
| Yük | Yük durumları (15 zorunlu şablon) | `domain/load_cases.py` var, arayüz yok (Faz 4) |
| Uyumluluk | PED / uyumluluk ekranı, DoC, isim plakası | Güncel: `services.py:generate_report_html` `project.fluid` varsa `ped_result` + ESR matrisini rapora veriyor (PED ön kontrol). DoC, isim plakası, risk analizi, teknik dosya çıktıları API/arayüz/rapora bağlı değil |
| Hesap rotası | EN 13445 kapsamı dar | Kapatıldı (2026-09-20, B-22): API standarda göre motor seçiyor, arayüzde "Hesap Standardı" seçicisi var. EN'de nozul, dış basınç, flanş, pnömatik test, MDMT, destek yok (`calculation-coverage.md` §2) |
| Kalıcılık | Proje kalıcılığı | `apps/api/store.py` bellek-içi; sunucu yeniden başlayınca projeler kaybolur (Faz 4) |
| Çıktı | PDF raporu | WeasyPrint bağlı değil (Faz 4) |
| Arayüz | Sihirbaz adım validasyonu | `App.tsx` her adıma serbest atlıyor; `defaultProject()` tüm alanları geçerli doldurduğu için çökme riski düşük — ertelendi (Faz 4) |
| Yapı | Ceketli kaplar | Kapsam dışı |
| Yapı | Çok odalı kaplar | Kapsam dışı |
| Yapı | Eşanjör tüp demetleri | Kapsam dışı |
| Analiz | Design by Analysis | Sonraki sürüm |
| Malzeme | Otomatik malzeme veritabanı | Sonraki sürüm |
| Malzeme | Sünme / yüksek sıcaklık | Sonraki sürüm |
| Malzeme | Kompozit Type III/IV | Kapsam dışı |
| Akışkan | Kriyojenik özel kurallar | Kapsam dışı |
| Düzen | Taşınabilir gaz tüpleri / ADR | Kapsam dışı |
| Düzen | Ateşle temas eden ekipmanlar | Kapsam dışı |

## Paket durumu — yazıldı mı, hesap hattına BAĞLI mı?

⚠️ Bu iki şey aynı değildir. Bir paket yazılmış, testleri geçiyor olabilir ama
orkestratörden hiç çağrılmıyorsa hiçbir sonuç üretmez. 2026-07-26 denetiminde
`mdmt` ve `supports` tam olarak bu durumdaydı ve bu tablo ikisine de ✅ diyordu.
Aşağıdaki "Bağlı" sütunu `tests/wiring/test_no_ghost_features.py` tarafından
makine olarak doğrulanır.

| Özellik | Paket | Yazıldı | Hesap hattına bağlı |
|---|---|---|---|
| Dış basınç / vakum (UG-28) | `external-pressure/` | ✅ Faz 5 | ✅ — **ve erişilebilir (Faz 4):** arayüzde dış basınç/vakum/A-B faktör alanları var. A/B girilmezse `BLOCKED_CODE_DATA` görünür (K6) |
| Destek / saddle (Zick) | `supports/` | ✅ Faz 5 | ✅ (2026-07-26) |
| MDMT / UCS-66 | `mdmt/` | ✅ | ✅ (2026-07-26) |
| Nozul takviye + çakışma | `nozzles/` | ✅ | ✅ |
| Kaynak doğrulama | `welds/` | ✅ | ✅ |
| **Flanş tasarımı (Appendix 2)** | `flanges/` | ✅ Faz 5 | ⚠️ Bağlı: UI→domain→orkestratör; Y/f/W/M kullanıcı girdisi (K6, Appendix 2 çalışma sayfasından); biri boşsa `BLOCKED_MISSING_INPUT`, hepsi girilince sonuç en iyi ihtimalle `REVIEW_REQUIRED` (formüller basitleştirilmiş, rijitlik/conta kontrolü yok) |
| FEA doğrulama laboratuvarı | `fea/` | ⚠️ iskelet | ❌ **BAGLI DEGIL: fea** |
| PED sınıflandırma motoru | `ped-2014-68-eu/` | ✅ Faz 4 | ayrı akış (rapor) |
| EN 13445 hesap rotası | `code-en-13445/` | ✅ Faz 4 | ✅ (kod seçimiyle) |
| ESR matrisi + DoC + isim plakası | `compliance/` | ✅ Faz 4 | ayrı akış (rapor) |
| StandardPack sürüm kilidi | `standards/manifests/` | ✅ Faz 4 | ✅ |

**`BAGLI DEGIL: <paket>`** işareti makine tarafından okunur; bir paketi bağlamadan
bu satırı silmek testi kırar.

### Flanş bağlantı durumu (güncellendi 2026-09-25)

Eski başlık "Flanş neden bağlı değil" güncel değildi: `Flange` domain modeli (`geometry.py`),
`orchestrator.py` D1 adımı ve arayüz flanş formu mevcut; `design_code.calculate_flange` çağrılıyor.
`Y`, `f` (lisanslı çizelgeden) ile `W`, `M` (Appendix 2 çalışma sayfasından) **kullanıcı girdisidir**
(K4/K6); program `W`/`M`'yi türetmez (conta çapı, moment kolları, conta sıkma yükü hesabı hesap
hattında çağrılmıyor). Biri boşsa sonuç `BLOCKED_MISSING_INPUT`; hepsi girilince olumlu sonuç
`REVIEW_REQUIRED`, aşım `FAIL` (sahte `PASS` üretilmez). Not: `Y`/`f`/`W`/`M` alanları ve durum kapısı
çalışma ağacında commit edilmemiş, başka bir çalışmada süren değişikliklerdir. Ayrıca bkz. B-11.

**Güncelleme (2026-09-25):** gerilme formülleri Appendix 2-7 standart formuna getirildi
(`S_H = f·M/(L·g1²·B)`, `S_R = (1.33·t·e+1)·M/(L·t²·B)`, `S_T = Y·M/(t²·B) − Z·S_R`; `K, Z, h0, e, d, L`
kodda hesaplanır). `F, V, T, U` (Şekil 2-7.1) ve `g1` (`hub_large_thickness`) kullanıcı girdisidir; biri
boşsa `BLOCKED_MISSING_INPUT`. Yapılan kontroller: `S_H ≤ 1.5·S_f`, `S_R`, `S_T`, `(S_H+S_R)/2`,
`(S_H+S_T)/2 ≤ S_f`. Yapılmayan: `S_H ≤ 2.5·S_n` (S_n girdisi yok), rijitlik (2-14), Wm1/Wm2, cıvata alanı.
Gevşek (loose) flanş `OUT_OF_SCOPE` (integral formüller geçerli değil).

### FEA neden bağlı değil

Bilinçli karar (Faz 2): FEA bir **doğrulama laboratuvarıdır**, ürün özelliği değil.
Offline çalışır, çıktısı `docs/` altına yazılır, kullanıcıya "FEA onayladı" denmez.
Ayrıca çözücü (CalculiX) kurulu değil.

## Bilinen sınırlamalar

- **Malzeme girişi:** V1'de kullanıcı izin verilen gerilme, akma ve çekme dayanımlarını manuel girer.
  Otomatik malzeme veritabanı veya lisanslı paket import'u yoktur.
- **Statik sıvı yüksekliği:** V1'de hesaba dahil değildir.
- **FEA:** İskelet modülü — çözücü (CalculiX / Code_Aster) kurulu değilse `REVIEW_REQUIRED` durumu döner; sahte PASS üretmez.
- **CAD — torisferik bombeler:** Görsel amaçlı yaklaşık elipsoidal profil revolve edilir; gerçek torisferik geometri (crown + knuckle) henüz yok.
- **CAD — düz flanş:** Union-tabanlı mimari (plaka + skirt); diğer bombelerden farklı strateji, daha kırılgan.

### Bağımsız doğrulama turu 1'de ortaya çıkanlar (2026-07-26)

Kaynak: [`validation/asme-worked-examples.md`](validation/asme-worked-examples.md).

- **B-02 — Eliptik bombede yalnızca 2:1 destekleniyor.** `head_elliptical_thickness`
  `K = 1.0`'ı sabit alıyor; `Head` modelinde bombe derinliği / en-boy oranı alanı yok.
  2:1 dışında bir elipsoidal bombe (ör. `K = 0.99`, karşılaştırma kaynağında görüldü)
  girilirse sessizce 2:1 gibi hesaplanır. UG-32(d) zaten yalnız 2:1'i kapsar; genel oran
  **Appendix 1-4(c)** ister ve o da yok. Kullanıcı 2:1 dışı bombe giremediği için bugün
  yanlış sonuç riski yok — ama bombe oranı girdisi eklenirse **önce** bu kapatılmalı.
  **Güncelleme (2026-09-25, kodda doğrulandı):** `Head.crown_depth` alanı ve
  `formulas.head_elliptical_thickness_general` eklendi; **kalınlık** yolu `crown_depth` verilince
  genel `K`'yı kullanıyor. **MAWP** yolu (`calculate_mawp` -> `mawp_from_ellipsoidal_head`) ise
  `crown_depth`'i hâlâ kullanmıyor, 2:1 varsayıyor: iki yol tutarsız, bağımsız doğrulama yok.
- **B-03 — Dış çap alternatifleri (App 1-1(a)(1), 1-4(c)) implement edilmemiş.**
  Karşılaştırılan iki ticari yazılım da varsayılan olarak bu formları kullanıyor. Suite'in
  iç çap formları %0.4-0.9 **daha ince** kalınlık üretiyor. Küçük ama sistematik ve
  emniyetsiz yönde; imalatçı çıktıyı ticari yazılımla karşılaştırırsa fark görecektir.
- **B-04 — UG-34(c)(3) (dairesel olmayan düz kapak, `Z` faktörü) yok.** Yalnız
  UG-34(c)(2) dairesel kapak var.
  **Güncelleme (2026-09-25, kodda doğrulandı):** `Head.flat_z_factor` ve
  `formulas.flat_head_thickness_non_circular` eklendi; `Z` girilirse kalınlık yolu UG-34(c)(3)
  kullanıyor. Bağımsız yayınlanmış vaka yok (ön kontrol); MAWP yolu `Z` kullanmıyor.
- ~~**B-05 — UG-32(e) torisferik ve UG-32(f) yarım küre bağımsız teyit almadı.**~~
  **Kapatıldı (tur 2, 2026-07-26):** torisferik anma tablosuyla 90 nokta üzerinden,
  yarım küre bombe tipi karşılaştırmasıyla doğrulandı.
- **B-06 — Torisferik taç yarıçapı varsayılanı iç çaptır, standart ASME F&D dış çap kullanır.**
  Kullanıcı taç yarıçapını girmezse `L = D` (iç çap) varsayılıyor; yayınlanmış karşılaştırma
  taç yarıçapının **dış çapa** eşit olduğunu gösteriyor (tur 2, V-14). Fark %0.5 mertebesinde
  ve emniyetsiz tarafta. `Head` modelinde dış çap alanı olmadığı için bu turda değiştirilmedi;
  varsayım kullanıldığında uyarı veriliyor. Taç yarıçapı girildiğinde sorun yok.
  **Güncelleme (2026-09-25, kodda doğrulandı):** `Head.outside_diameter` eklendi ve
  `design_code._torispherical_radii` girilmeyen taç yarıçapı için artık `L` = dış çap (yoksa
  iç çap + 2 x nominal kalınlık) ve `r = 0,06 L` (standart F&D) kullanıyor; varsayım ve uyarı
  sonuca yazılıyor. Bu varsayılanın `design_code` yolunda uçtan uca testi doğrulanamadı.

- **B-07 — Nozul takviyesi yalnız radyal nozul içindir.** UG-37'nin eğik nozul `F`
  faktörü uygulanmıyor (`F = 1.0` alınıyor); eğik nozul girilirse uyarı veriliyor.
  **Güncelleme (2026-09-25):** kod şimdi `1/cos(a)` izdüşümü kullanıyor ve olumlu sonucu
  `REVIEW_REQUIRED` yapıyor (B-30); UG-37 eğik/hillside yöntemi hâlâ yok.
- **B-08 — Appendix 1-7 büyük açıklık kontrolü yok.** Karşılaştırma kaynağı aynı nozul
  için App 1-7'yi de uyguluyor; suite yalnız UG-37/UG-40 alan değiştirme yöntemini yapıyor.
  Büyük açıklıklarda (yaklaşık `d > D/2` veya `d > 40 in`) bu ek kontrol gerekir.

### Doğrulama turu 4 — kod denetimi (2026-07-26)

Dört sapma bulunup düzeltildi (V-16…V-19). Aşağıdaki B-09…B-13 kalemleri de aynı turda
tespit edildi; **Faz 3'te (2026-07-26) beşi de ele alındı** — üstü çizili olanlar kapatıldı,
B-09'da yalnız varsayımın kaydı sağlandı, değerin doğrulaması hâlâ açık:

- ~~**B-09 — EN 13445 torisferik bombede sessiz varsayılan.**~~ **Varsayım artık kayda geçiyor (2026-07-26):** `_torispherical_radii_en` `add_assumption` + `add_warning` yazıyor. **Değerin kendisi (`r = 0.10 D`, Korbbogen/DIN 28011) hâlâ doğrulanmadı** — kapatmak için yayınlanmış bir EN 13445 vakası gerekir. Eski açıklama: ASME tarafında V-12'de
  düzeltilen desen (`r = D/10` sessizce varsayılıyor) EN paketinde duruyor. EN'in Korbbogen
  (DIN 28011) standardında `r = 0.1D` **doğru** olabilir — ama doğrulanmadı ve her hâlükârda
  varsayımın kayda geçmesi gerekir (K4). Kapatmak için yayınlanmış bir EN 13445 vakası şart.
- ~~**B-10 — Mill tolerans varsayılanı 5 yerde sessiz.**~~ **Kapatıldı (2026-07-26):** beş yerin tamamı `add_assumption` yazıyor. Eski açıklama: Değer sektörde
  tipik; risk sayısal değil, izlenebilirlik. `add_assumption` eklenmeli.
- ~~**B-11 — Flanş `Y` faktörü sessizce 5.0 varsayılıyor.**~~ **Kapatıldı (2026-07-26):** varsayılan kaldırıldı, `Y` verilmezse `BLOCKED_MISSING_INPUT`. Eski açıklama: (`flange_calc.py`). Appendix 2
  tablosundan `K = A/B` ile okunan bu faktör geniş bir aralıkta değişir. Paket henüz
  orkestratöre bağlı olmadığı için üretilen hiçbir sonucu etkilemiyor; bağlanmadan
  önce düzeltilmeli.
- ~~**B-12 — MDMT basitleştirilmiş düzeltmesi kullanıcıya yansımıyor.**~~ **Kapatıldı (2026-07-26):** basitleştirme `add_assumption` + `add_warning` ile sonuca yazılıyor; modül artık hesap hattına da bağlı. **Yaklaşımın kendisi sürüyor.** Eski açıklama: (`mdmt_calc.py`:
  `(t − 38)×0.5`). Gerçek UCS-66 eğrileri doğrusal değil. Basitleştirme yalnız kaynak kodu
  yorumunda yazıyor, `CalculationResult`'a uyarı olarak yansımıyor. Paket henüz orkestratöre
  bağlı değil.
- ~~**B-13 — Bazı formüllerde `C` parametresi ölü.**~~ **Kapatıldı (2026-07-26):** ölü `C` (ve EN'de `e`) parametreleri imzalardan kaldırıldı, çağrı yerleri ve testler güncellendi. Eski açıklama: `head_elliptical_thickness`,
  `head_hemispherical_thickness`, `cone_thickness` imzalarında `C` var ama gövdede
  kullanılmıyor. Sayısal etkisi yok, ama V-16/V-17'deki kafa karışıklığının kök
  nedenlerinden biri: okuyan "korozyon burada işleniyor" sanıyor.

### Faz 4 — Arayüz / gerçek uyumu (2026-09-08)

Faz 3, hesap hattına **bağlı olmayan** paketleri kapattı. Bu turun sorusu bir
katman yukarıdaydı: hesap hattına bağlı bir paketin arayüzde **kullanıcı
tarafından tetiklenebilir** olup olmadığı. İki paket bu yüzden "yazıldı, bağlı,
ama erişilemez" durumundaydı:

- **Dış basınç/vakum (`external-pressure`):** `check_external_pressure`
  orkestratörden çağrılıyordu (bu yüzden `test_no_ghost_features.py`'yi
  geçiyordu), ama `external_pressure`/`vacuum_condition` için arayüzde form
  yoktu ve `strain_factor_A`/`allowable_stress_B` kodda `0.0` sabitti. **Bu
  turda kapatıldı:** Tasarım Koşulları adımına dış basınç/vakum/akışkan
  yoğunluğu alanları, Geometri adımına gövde/bombe bazında UG-28 A/B faktör
  alanları eklendi.
- **Destekler (`supports`):** aynı durum — `check_supports` bağlıydı, form
  yoktu, `supports: []` sabitti. **Bu turda kapatıldı:** Geometri adımına
  eyer/etek/ayak editörü eklendi.

Ayrıca dört ayrı **K4 ihlali** (backend uyarı/hata üretiyor, arayüz hiç
göstermiyor) kapatıldı: `CalcPayload.errors` hiç render edilmiyordu; 9/10 sonuç
grubu boşken sessizce kayboluyordu (`emptyNote` artık zorunlu); `pressure_consistency`
ve `material_check` üretiliyor ama gösterilmiyordu; akışkan yoğunluğu
girilmediğinde statik kafa düzeltmesi sessizce atlanıyordu.

Yeni koruyucu test: [`tests/wiring/test_ui_parity.py`](../tests/wiring/test_ui_parity.py).
`test_no_ghost_features.py`'nin sormadığı soruyu sorar — *"kullanıcı
tetikleyebiliyor mu?"* Üç kontrol: her `ResultGroup` çağrısında `emptyNote` var
mı, domain'in hesabı etkileyen her alanı arayüzde var mı (yoksa gerekçeli
`ARAYUZDE_YOK`'ta mı), `CalcPayload`'ın her alanı render ediliyor mu.

Bu turda bilinçli olarak **yapılmadı** (yukarıdaki "V1 kapsam dışı" tablosuna
eklendi): koni formu, çoklu gövde kesiti/bombe/malzeme/kaynak, yük durumları,
PED/uyumluluk ekranı, EN 13445 rotası, kalıcılık, PDF çıktısı, sihirbaz adım
validasyonu. Ayrıca `Head.external_corrosion_allowance` alanının forma
eklenmediği bu turda ortaya çıktı (`test_ui_parity.py` ARAYUZDE_YOK) — küçük,
bilinçli bir dışta bırakma.

### Kapsam denetimi — TS/MMO kaynağıyla karşılaştırma (2026-09-08)

Kaynak: TMMOB MMO *Periyodik Kontrol Mühendis El Kitabı-II — Basınçlı Kaplar*
(Kasım 2001, MMO/2001/272-2). Suite'in `clause_reference` envanteri bu kaynaktaki
kurallarla karşılaştırıldı. **Hiçbir mevcut hesap yanlış çıkmadı** — kitap gerçek
kalınlık formülü vermiyor (TS 3362 yalnız güvenlik katsayısı seçimini veriyor).
Bulunan altı kalem, ASME VIII-1'de karşılığı olup suite'te henüz olmayan kontroller:

- **B-14 — UG-125…UG-136 (basınç tahliye) yalnız ön kontrol düzeyinde.** *Güncelleme (2026-09-25,
  kodda doğrulandı): `pressure-relief` paketi var, orkestratör J adımından çağrılıyor ve arayüzde
  tahliye paneli var; ayar/patlama basıncı <= MAWP, birikme yüzdesi ve kapasite alanı varlığı
  denetleniyor. Kapasite boyutlandırması, senaryo/blowdown analizi ve cihaz türü doğrulaması yok.
  Aşağıdaki eski açıklama başlangıç durumunu anlatır.* Eski başlık: hiç yok. Kap MAWP'si hesaplanıyor, tahliye
  cihazı (emniyet vanası/patlama diski) set basıncı, accumulation (≤%10, UG-125(c)),
  blowdown hiç kontrol edilmiyor. En büyük eksik; yeni bir paket (`pressure-relief`)
  gerektirir. Faz 4 dersi geçerli: paketi bağlamak yetmez, aynı turda arayüz formu ve
  `ResultGroup` de yapılmalı, yoksa `test_ui_parity.py` düşürür.
- ~~**B-15 — UG-16(b) mutlak minimum kalınlık kontrolü yok.**~~ **Kapatıldı
  (2026-09-08):** `ASMEVIII1DesignCode._apply_ug16b_minimum` — gövde, bombe ve koni
  kalınlık hesaplarının hepsinde, seçilen nominal kalınlıktan korozyon payı
  düşüldükten sonra kalan net kalınlık 1,5 mm'nin altındaysa sonuç FAIL'e çevrilir
  ve uyarı yazılır. Eski açıklama: yalnız basınçtan gelen gerekli kalınlık
  hesaplanıyordu, taban değer ayrıca kontrol edilmiyordu.
- ~~**B-16 — UG-45 nozul boyun minimum kalınlığı yok.**~~ **Kapatıldı (basitleştirilmiş,
  2026-09-08):** `nozzles.reinforcement.calculate_reinforcement` — nozulun kendi
  UG-27(c)(1) tipi iç basınç kalınlığı (`trn`, zaten A2 alanı için hesaplanıyordu)
  ile karşılaştırılıp boyun kalınlığı bunun altındaysa uyarı ekleniyor. **Tam UG-45
  değil** — Tablo UG-45 (standart boru schedule minimumu) telifli veri olduğu için
  gömülmedi (K6); yalnız (a) bacağı kontrol ediliyor ve bu açıkça sonuca yazılıyor.
- ~~**B-17 — UG-46 muayene açıklığı gereksinimi yok.**~~ **Kapatıldı (basitleştirilmiş,
  2026-09-08):** `nozzles.clash_check.check_inspection_opening` — proje-seviyesi
  kontrol, `clash_check` grubuna ekleniyor. **Tam Tablo UG-46 değil** (telifli, K6) —
  yaygın eşik (iç çap > 610 mm → adam deliği gerekir) aşılıp manway tanımlı değilse
  kesin FAIL değil REVIEW_REQUIRED döner.
- **B-18 — UG-80/UG-81 imalat toleransları kontrol edilmiyor.** Yuvarlaklık, bombe
  biçim toleransı — tasarım hesabından çok imalat/QC alanı; düşük öncelik.
- **B-19 — UW-13 bombe-gövde bağlantı detayı doğrulanmıyor.** UW-11/UW-12 var,
  bağlantı biçimi (çift köşe kaynağı sınırı vb.) ayrı kontrol değil.

### Bağımsız denetim doğrulaması (2026-09-20)

Ana kıyas raporu [`../../eksikler.md`](../../eksikler.md), dosya:satır okuması ve iki ampirik
çalıştırmayla yeniden doğrulandı. İki önceki ifade düzeltildi: UI bugün EN 13445 seçtirmiyor;
destek skirt/leg yolları da yanlış `PASS` değil, üretim payload’ı eksik olduğu için sürekli
`NOT_CALCULATED`. Aşağıdaki üç yeni kusur sonraki kod turu için kayda alındı:

- ~~**B-20 — Skirt/leg destek sonuçları üretimde daima `NOT_CALCULATED`.**~~
  **Kapatıldı (2026-09-20; doküman 2026-09-25'te doğrulandı):** `design_code.check_supports`
  payload'ı artık `skirt_material_id` (= `sup.material_id`), `diameter_mm`, `thickness_mm`,
  `n_legs` (= `leg_count`), `leg_diameter_mm`, `leg_thickness_mm`, `support_radius_mm` ve ankraj
  alanlarını gönderiyor; üretim wiring testleri
  `tests/faz5/test_faz5_supports.py::test_production_support_payload_wires_skirt` ve
  `test_production_support_payload_wires_leg_count_and_geometry`. Skirt/leg sonuçları
  `REVIEW_REQUIRED` (olumlu) / `FAIL` verir; eksik girdide `NOT_CALCULATED` kalır. Destek
  alanında ayak planı çalışması sürüyor. Eski açıklama:
  `design_code.check_supports` payload’ı `skirt_material_id`, `support.diameter_mm` ve
  `support.thickness_mm` göndermiyor; üretimde `leg_count` yazılırken calculator `n_legs` okuyor.
  UI’daki `sup.material_id` bu hatta ulaşmıyor. `tests/faz5/test_faz5_supports.py` elle
  `skirt_material_id` içeren payload kullandığı için yeşil; üretim wiring testi ve
  `check_leg_support` entegrasyon testi yok. Saddle yolu bu bulgudan ayrıdır.
- ~~**B-21 — UG-33 bombe dış basıncı silindir katsayısını kullanıyor.**~~
  **Kapatıldı (2026-09-20):** `formulas.py` bombe yaklaşımı `P_allow = 2Bt/D`; dış çap etiketi
  düzeltildi. Tam UG-33/UG-28 çizelge yöntemi yok (sonuç `REVIEW_REQUIRED`). Eski açıklama:
  `external-pressure/src/external_pressure/formulas.py:169-170` `8Bt/(3D)` uygular.
  Aynı dosyanın bombe docstring’indeki `B×t/(0.5D)` yaklaşımına göre sonuç `4/3` yani
  **%33,3 daha yüksek ve emniyetsiz** allowable verir. Bu kayıt ASME metnini kopyalamaz;
  UG-28(d)/UG-33 atıflarıyla yapılan katsayı analizidir (K6). Ek olarak `head.type` formüle
  girmiyor ve `ext_pressure.py:254` dış çap ara değerini “Inside diameter” etiketliyor.
- ~~**B-22 — `project.calculation_code` backend’de sessizce yok sayılıyor.**~~
  **Kapatıldı (2026-09-20):** `apps/api/services.py` seçilen standarda göre ASME veya EN motoru
  kurar, tanınmayan kodda hata verir. Eski açıklama:
  `apps/api/services.py:48-51` koşulsuz `ASMEVIII1DesignCode` kuruyor; EN paketinin design
  code’u mevcut olsa da çağrılmıyor. API’ye EN 13445 isteği geldiğinde hata/uyarı olmadan ASME
  sonucu dönüyor. `docs/calculation-coverage.md:65` içindeki “her ikisi de aktif” ifadesiyle
  bu üretim durumu çelişiyor; `calculation-coverage.md` Rev 3.0 (2026-09-25) bu satırı kaldırdı.

#### 2026-09-20 kod turu kapanış durumu

- B-20 payload wiring, destek ölçüleri ve gerçek orkestratör entegrasyon testleriyle kapatıldı.
- B-21 bombe katsayısı `2Bt/D` olarak düzeltildi; dış çap etiketi ve golden test güncellendi.
- B-22 API standarda göre ASME veya EN motorunu seçiyor; EN API regresyon testi eklendi.
- Tam normatif dış basınç, destek, ankraj ve EN kapsamı hâlâ ayrı doğrulama işidir.

K6: Telifli çizelge veya madde metni kopyalanmadı; B-21 yalnızca atıf ve bizim katsayı/etki
analizimizi kaydeder.

Ayrıca **kaynağın kendi sorunları** not edildi: kitap içi çelişki (min kalınlık için
iki farklı değer), B kısmının 34. sayfasında bir güvenlik kuralını tersine çeviren
dizgi/OCR hatası, mülga mevzuat referansları (İSİG Tüzüğü, RG 2000/24226). Bu
kaynak normatif referans olarak değil, kapsam denetimi girdisi olarak kullanıldı.
Detaylı karşılaştırma matrisi (K6 gereği kodda değil) kasada:
`vault/wiki/projeler/basincli-kap/basincli-kap-ts-karsilastirma.md`.

**Bilinçli olarak yapılmayacak:** TS 3362'yi üçüncü hesap rotası yapmak — kitap
formül vermiyor (implement edilecek bir şey yok), EN 13445 rotası zaten arayüzden
seçilemezken üçüncü bir kod eklemek Faz 3/4'te kapatılan hayalet özellik desenidir.

### Canlı arayüz denetimi (2026-09-22)

- ~~**B-26 — Mill (sac) negatif toleransı korozyon payına uygulanmıyordu; emniyetsiz
  yönde.**~~ **Kapatıldı (2026-09-22):** `shell_required_nominal_thickness`
  `t_required / factor + C` hesaplıyordu; korozyon payı ve şekillendirme incelmesi
  bölmenin dışında kalıyordu. Mill negatif toleransı **sipariş edilen nominal
  kalınlığın tamamına** uygulandığı için doğru biçim
  `(t_required + C + forming_thinning) / factor`'dır. Düzeltildi:
  `code-asme-viii-1/formulas.py` ve `code-en-13445/formulas.py`.

  **Etki (varsayılan proje: t_req=4,388 mm, C=2,0 mm, factor=0,875):** üretilen
  nominal kalınlık 7,015 mm → **7,301 mm** (%3,9 artış, emniyetli yöne). Eski
  değerle 7,015 mm sipariş edilseydi en kötü teslim 6,138 mm, korozyon sonrası
  4,138 mm kalır ve basınç için gereken 4,388 mm'yi **0,25 mm karşılamazdı**.
  EN 13445 tarafında aynı düzeltme: 6,088 mm → 6,310 mm.

  **Neden testler yakalamamıştı:** `test_asme_golden.py` içindeki golden test,
  yanlış formülü docstring'inde açıkça yazıp değeri sabitlemişti (implementasyona
  göre yazılmış test). Düzeltmeyle birlikte formülden bağımsız bir kabul testi
  eklendi: `factor × t_nominal − C >= t_required` (ömür sonu kalınlık kontrolü).
  `mill_tolerance_factor = 1.0` durumunda sonuç değişmez (geriye dönük uyumlu).

- **Canlı arayüz denetimi temiz.** Altı adımın tamamı (proje → koşullar → geometri →
  hesap → 3B → rapor) çalıştırıldı: konsol hatası yok, tüm ağ istekleri başarılı,
  sunucu logunda hata yok, HTML rapor ve STEP çıktısı üretildi.

- ~~**MAWP sac toleransı ve şekillendirme incelmesi:**~~ **Düzeltildi (2026-09-30):** MAWP
  artık `t_min = nominal × (1 − mill_tolerance/100) − forming_thinning` kalınlığını kullanır;
  formülde korozyon payı ayrıca düşülür. Bu, proje için seçilmiş en düşük teslim/şekillendirme
  sonrası et politikasıdır; ASME lisanslı metninden normatif yorum iddiası değildir.

### Emniyet denetimi turu (2026-09-25)

- ~~**B-27 — Ayak (leg) kesiti dolu daire kabul ediliyordu; emniyetsiz yönde.**~~
  **Kapatıldı (2026-09-22):** `check_leg_support` ayak alanını `3.14159·(D/2)²` ile
  hesaplıyor, `leg_thickness_mm`'i hiç kullanmıyordu; oysa `leg_diameter_mm` dış çaptır
  (boru). Gerilme olduğundan düşük çıkıyordu. Halka kesit (`leg_pipe_section_area`)
  kullanılıyor; D=100 mm, t=10 mm örneğinde gerilme **2,78×** arttı. Formüller K1 gereği
  `supports/formulas.py`'ye taşındı.

- ~~**B-28 — Hidrostatik/pnömatik test basıncı `S_test = S_design` (LSR=1) varsayımıyla
  düşük çıkabiliyordu; emniyetsiz yönde.**~~ **Kapatıldı (2026-09-25):**
  UG-99(b) `HTP = 1,3 × MAWP × LSR`, UG-100 `1,1 × MAWP × LSR`; LSR, basınç parçalarındaki
  **en küçük** `S_test/S_design` oranıdır (bağımsız kaynaklarla teyit edildi). Kod oranı
  hep 1 alıyor ve bunu "konservatif" diye yazıyordu; oysa oran normalde ≥ 1 olduğundan
  bu, test basıncını **düşük** verir (örnek: 148/138 = 1,072 → %7,2 eksik test).
  Düzeltme: `MaterialProperty.allowable_stress_test_temp` (arayüzde "Test Sıcaklığında S").
  - Tüm basınç malzemelerinde girilmişse LSR gerçek orandan hesaplanır → `PASS`.
  - Tasarım sıcaklığı = test sıcaklığı ise `S_test = S_design` gerçek eşitliktir → `PASS`.
  - Aksi halde LSR=1 yalnız yedek değerdir → **`REVIEW_REQUIRED`** + "emniyetsiz yön" uyarısı.
  - EN 13445-5 10.2.3.3.1: `max(1,25·Ps·fa/ft ; 1,43·Ps)`. fa/ft uygulanmıyor; 1,43·Ps oran
    ≤ 1,144 iken her seçim yönünde belirleyicidir. Oran eksikse veya > 1,144 ise
    `REVIEW_REQUIRED` (oranın en büyük/en küçük seçilmesi lisanslı metinle doğrulanmadı — K3/K4).
  - **Bilinçli davranış değişikliği:** test gerilmesi girilmemiş, tasarım ≠ test sıcaklığı
    olan mevcut projelerde test sonucu `PASS` yerine `REVIEW_REQUIRED` görünür
    (varsayılan projede: 200 °C / 20 °C). Değer aynı kalır. Canlı doğrulama: 3,53 MPa
    `İNCELEME GEREKLİ` → S_test=148 girilince 3,79 MPa `GEÇTİ` (el hesabı 1,3·2,72·148/138).
  - **Açık:** UG-99(b)'nin "test basıncı hiçbir bileşende test gerilme sınırını aşmamalı"
    kontrolü (bileşen bazlı) yapılmıyor.

- ~~**B-29 — WRC katsayısında eksik bileşen sessizce sıfır sayılıyordu.**~~
  **Kapatıldı (2026-09-25):** `supports/wrc.py` bir nokta/yük için tek katsayı girilince
  diğerlerini 0 katkı alıyordu → lokal gerilme eksik tahmin edilebilirdi. Artık aktif yük
  için dört bileşenin (Nx, Ny, Mx, My) hepsi zorunlu; `None` = "okunmadı" ve hesap
  `ValueError` ile bloklanır, gerçek sıfır açıkça `0.0` girilir. **Not:** WRC modülü henüz
  hesap hattına/arayüze bağlı değil (ayak planı Faz 2.4/3).

- ~~**B-30 — Eğik nozulda `1/cos(α)` izdüşümüyle nihai `PASS` verilebiliyordu.**~~
  **Kapatıldı (2026-09-25):** `nozzles/reinforcement.py` kodun kendi yorumu "eğik nozul
  takviyesini kapsamıyoruz" derken α > 0 için izdüşümle `PASS` üretiyordu. İzdüşüm, UG-37
  eğik/hillside yöntemi ve Şekil UG-37 F faktörüyle aynı şey değildir. Artık α > 0 ve yeterli
  alan durumunda sonuç `REVIEW_REQUIRED` + uyarı; yetersiz alan (`FAIL`) aynen kalır. Sayısal
  değerler (gerekli alan ∝ 1/cos α) değişmedi. **Açık:** eğik/hillside yönteminin kendisi
  yok — lisanslı UG-37 metniyle doğrulanmalı.

- ~~**B-31 — Malzeme S değerinin sıcaklığı/kalınlık aralığı hiç doğrulanmıyordu.**~~
  **Kapatıldı (2026-09-25):** sonuçlar "S, tasarım sıcaklığında girildi" varsayımını yazıyor
  ama `MaterialProperty.temperature` ve `thickness_min/max` hiçbir yerde kıyaslanmıyordu;
  yanlış sıcaklıktaki S ile sayısal `PASS` çıkabilirdi. `_apply_material_data_check`
  (gövde, bombe, koni kalınlığı ve MAWP): sıcaklık uyuşmazlığı veya nominal kalınlığın
  malzeme aralığı dışında olması → uyarı + `PASS` → `REVIEW_REQUIRED` (`FAIL` korunur).
  Arayüzde malzeme formuna "S Değerinin Sıcaklığı" ve "Kalınlık Aralığı" alanları eklendi
  (aksi halde uyarı giderilemezdi). **Sınır:** kıyas, girilen S'nin tablo değeri olduğunu
  kanıtlamaz; yalnız hangi sıcaklık için girildiği beyanını denetler. Test/tasarım
  sıcaklığı ve `MaterialDataPack` interpolasyonunun motora bağlanması hâlâ açık.
  **Kullanıcı etkisi:** tasarım sıcaklığı değiştirilirse S yeniden girilip "S Değerinin
  Sıcaklığı" güncellenmedikçe sonuçlar `İNCELEME GEREKLİ` görünür (bilinçli).

- **Temizlik notu (2026-09-25):** TypeScript'te kullanılmayan öğeler `pages.tsx` dışında
  temizlendi (`schematic.tsx`, `livePreview.tsx`, `GeometryAgentDrawer.tsx`); `pages.tsx`'te 7
  öğe (`StatusBadge`, `CALC_TYPE_TR`, `tr`, kullanılmayan `index`/`i` parametreleri) ayak
  formu çalışması bitince temizlenecek.
- **Açık karar — `calc_core.validate_suite()` bağlı değil.** Yayın öncesi kapı olarak
  tasarlanmış ama hiçbir yerden çağrılmıyor. Bağlamadan önce politika kararı gerekir:
  `validate_result` "uyarılı `PASS` yayınlanamaz" der; oysa pnömatik testte zorunlu güvenlik
  ve MDMT notları uyarı olarak yazılır ve `PASS` ile birlikte gelir → bağlanırsa yanlış alarm
  (test/tasarım sıcaklığı eşitken ölçüldü). Bilgi notu ile durum-düşüren uyarı ayrımı gerekir.
  **Güncelleme (2026-09-25, çalışma ağacı):** `apps/api/services.py` artık `validate_suite`'i
  bilgilendirici bir `verification` bölümü olarak çağırıyor (hesabı değiştirmez/engellemez);
  değişiklik commit edilmemiş. Yukarıdaki "hiçbir yerden çağrılmıyor" bu değişiklik öncesini anlatır;
  yayın kapısı olarak bağlama politika kararı hâlâ açık.

- ~~**B-32 — Ayak reaksiyonunda moment terimi gerçek değerin yarısıydı; emniyetsiz.**~~
  **Kapatıldı (2026-09-25):** `leg_reaction_extremes` `N = W/n ± M/(n·r)` kullanıyordu. Eşit
  aralıklı n ≥ 3 ayak için en yüklü ayak `W/n + 2M/(n·r)` (= `4M/(n·D)`, D = 2r; Moss PVDM)
  taşır — eski terim yarı yarıya eksikti. n = 2 (moment düzleminde) `M/(n·r)` kalır; tek ayak
  moment taşıyamaz (hata). Yeni test, ayakları çemberde tek tek yerleştirip moment yönünü tarayan
  bağımsız statik hesapla n = 3…8 için formülü doğrular (eski test, yanlış formülü sabitlemişti:
  120000/80000 yerine doğrusu 140000/60000). **Not:** n = 2'de momentin ayakları birleştiren
  doğruya dik yönü taşınamaz — yerleşim mühendis tarafından doğrulanmalı.

- ~~**B-33 — Taban plakası alanı, ayak çelik gerilmesinde kullanılıyordu; emniyetsiz.**~~
  **Kapatıldı (2026-09-25):** `base_plate_area_mm2` verilince `N_max / A_taban` çelik izin
  gerilmesiyle kıyaslanıyordu; büyük plaka girmek ayağı "daha güvenli" gösteriyordu. Artık ayak
  gerilmesi daima halka kesitten (`N_max / A_leg`); plaka alanı yalnız `P_bearing` (temel
  yataklık basıncı) ara değerini verir ve beton/grout izin verilen basınç girdisi olmadığından
  **kontrol edilmez** (uyarı yazılır). Arayüz yardım metni düzeltildi.

- **Engineering source review:** primary-source review is recorded in `docs/validation/engineering-source-review-2026-09-30.md`. Zick?s original S3 labels do not yet map cleanly to the app?s head-shear S3; K1-prime and Moss/Megyesy coefficient mapping remain unverified. Skirt B-factor needs a matching chart readback and E=0.6 depends on joint detail. Blodgett base formulas pass an integral check; WRC force/moment dimensions are consistent, but coefficient surfaces and a published numeric reproduction remain open. These checks stay REVIEW REQUIRED.
- **Ayak (leg) sistemi eklendi:** U profil/boru/kutu/köşebent kesiti, ped, taban plakası, üç köşe kaynağı,
  WRC lokal gerilme; dört ayrı sonuç (`leg_section_check`, `leg_weld_check`, `base_plate_check`,
  `wrc_local_stress`) ve arayüz formu. `leg_stress` özeti hiçbir zaman nihai PASS vermez. **Açık/yorum:**
  temas oranı yorumu (kaynaklı kontur oranı), kaynak grubu idealizasyonu, WRC'de doğrudan kayma gerilmesi
  hesaplanmıyor, ped gövde kalınlığına eklenmiyor, yatay yük yönü bilinmediğinden muhafazakâr birleşim,
  Blodgett Sw ifadeleri türetmeyle doğrulandı (kaynak tablosu görülmedi), WRC boyut analizi bültenle
  karşılaştırılmadı, `anchor_bolt_diameter_mm` hesapta kullanılmıyor.
- **MAWP mill tolerance/forming thinning:** corrected on 2026-09-30 and the same 20-case inputs were rerun through the calculation service. All 20 API values match the independent reference within 0.0005 MPa; see `test-sonuc.1.md`.


### 30.09.2026 sonrası açık kalanlar

- **EN 13445 B-31 metadata gate:** on 2026-09-30, the entered design-stress temperature and nominal thickness range are checked for shell, head, and MAWP results. Metadata mismatch changes PASS to REVIEW REQUIRED. This does not verify the manually entered stress against a licensed EN material table; independent published-case validation remains open.

- **Support load pairing (updated 2026-09-30):** support checks now preserve each valid `concurrent_with`/`LoadCombination` group and apply its factors to forces and moments. Hydrotest water weight is paired only with a HYDROTEST case. Operating/fluid cases without resolvable mass, ambiguous wind/seismic empty-vs-operating weight, and manual moments without a paired vertical load produce REVIEW REQUIRED. **Still open:** report empty-tank leg stress as a separate result.
- **UG-99(b) test gerilmesi:** test basıncı ve statik yükler üretiliyor, ancak bileşen bazında test gerilmesi/
  kapasite sınırı denetlenmiyor. Sınır ve yöntem lisanslı geçerli baskı ve mühendis kararıyla teyit edilmeden
  otomatik PASS üretilmemeli.
- **Kaynak doğrulaması:** Zick S3/S5, K1′, etek UG-23(b) geometrisi/verimi ve WRC boyut analizi için
  erişilebilir güvenilir ve bağımsız doğrulama örneği tamamlanmadı. Mevcut çıktılar bu nedenle mühendis
  incelemesi gerektirir.
- **Ankraj çapı:** alan arayüzde bilgi girdisi olarak sunulur; kapasite dişli çekme alanı varsaymadan,
  kullanıcı girdisi izinli çekme/kesme kuvvetleriyle hesaplanır. Gerçek ankraj dayanımı ayrıca doğrulanmalı.
- **Güvenlik anahtarı:** sohbette açığa çıkan OpenRouter anahtarının sağlayıcı panelinden yenilenmesi gerekir;
  bu çalışma alanından sağlayıcı hesabına erişim yok.

### STEP içe aktarma (2026-10-06)

- **B-34 — STEP içe aktarma kapsamı (yeni özellik, bilinçli dar).** `POST /api/import/step` +
  `cad_engine.step_import.recognize_step`. STEP'ten yalnız tek eksenli dönel kap tanınır: tek silindir
  gövde + iki bombe (2:1 eliptik / gerçek küre+torus torisferik / yarım küre / düz) + radyal gövde nozulları.
  Koni, bombe nozulu, eğik/ofset nozul, çoklu gövde, destek → `unrecognized` (PARTIAL), sessizce yok sayılmaz.
  Malzeme, tasarım basıncı/sıcaklığı, kaynak verimi ve korozyon payı dosyada **yoktur**, hiç önerilmez.
  Her değer kullanıcı onayından geçer (K2: CAD hesabın kaynağı değildir); STEP nozulları her zaman yeni nozul
  olarak eklenir, mevcut nozul ezilmez. Tanıma ayrı süreçte, 30 s zaman aşımı, eşzamanlı en çok 2.
- **B-35 — Düz flanş çoğu dosyadan okunamaz.** Bombe eteği gövde silindiriyle tek yüze birleşmişse
  (suite'in kendi STEP çıktısı dahil) `straight_flange_length` null döner, değer elle girilir. Dikiş varsa
  sf ≤ min(0.25·L, max(150 mm, 0.1·D)); daha uzaktaki dikiş course dikişi sayılır, sf önerilmez.
- **B-36 — Suite'in torisferik CAD çıktısı gerçek torisferik değil.** `vessel_builder` torisferik bombeyi
  derinliği Rc/rk'den hesaplanmış elips olarak çiziyor (vessel_builder.py:172-197). Bu yüzden suite'in kendi
  torisferik STEP'i geri yüklenince "desteklenmeyen h/D oranı" ile PARTIAL döner (dürüst davranış); dışarıya
  verilen STEP'in bombe profili de imalat profiliyle birebir değildir. **Açık.**
- **B-37 — STL hesap girdisi değildir.** STL yalnız "Yüklenen model" sekmesinde görüntülenir; ölçü çıkarılmaz.
- Global hata işleyicisi (`apps/api/main.py`) 500 yanıtlarında `{tip}: {mesaj}` döndürüyor; ayrıntı sızıntısı
  riski — STEP ucunda kapatıldı, genel işleyicide açık.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 3.3 (2026-09-25 doküman tutarlılık düzeltmesi dahil: B-20/B-21/B-22 kapatıldı olarak işaretlendi, B-02/B-04/B-06/B-07/B-14 kod durumu notları, kapsam/paket tabloları, Phase C başlık/sıra) — 2026-09-25 emniyet denetimi: eğik nozul PASS (B-30) ve malzeme sıcaklık/kalınlık doğrulaması (B-31) kapatıldı; test basıncı LSR varsayımı (B-28) ve WRC eksik katsayı (B-29) kapatıldı, ayak kesit kusuru (B-27) kaydedildi; 2026-09-22: mill toleransı (B-26).*
