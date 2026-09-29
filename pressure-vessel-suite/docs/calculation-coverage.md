# Calculation Coverage Matrix

> Bu matris her hesabın **üretim yolundaki** (arayüz -> API -> `CalculationOrchestrator` ->
> standart eklentisi) gerçek durumunu gösterir. Durumlar kod okunarak doğrulanmıştır
> (2026-09-25). Eski sürümdeki "Yes / Active" etiketleri kaldırıldı: bir paketin yazılmış
> olması ve testlerinin geçmesi, sonucunun imalata esas alınabileceği anlamına gelmez.
>
> **Genel hüküm:** Ürün bugün ASME VIII-1 için **dar kapsamlı ön boyutlandırma / mühendis
> incelemeli prototip** olarak kullanılmalıdır. İmalata esas tasarım raporu, PED/CE kararı
> veya bağımsız mühendis onayı yerine geçmez. Testlerin geçmesi (708 passed / 1 skipped,
> 2026-09-25) regresyon kanıtıdır; standarda uygunluk kanıtı değildir.

## Durum etiketleri

| Etiket | Anlamı |
|---|---|
| **Hesaplandı ve doğrulandı** | Formül üretim yolunda çalışıyor **ve** yayınlanmış sonuçlarla karşılaştırıldı (`docs/validation/README.md` kabul kuralı: +-%1, en az iki bağımsız teyit). Sonuç `PASS`/`FAIL` verebilir. Yine de girdi doğruluğu ve malzeme değerleri kullanıcı/mühendis sorumluluğundadır. |
| **Ön kontrol (REVIEW_REQUIRED üretir)** | Hesap çalışır ama nihai `PASS` **üretmez** (olumlu sonuç `REVIEW_REQUIRED`'a düşer) **ya da** bağımsız doğrulaması eksiktir. Mühendis incelemesi zorunludur. Bu satırlarda bağımsız doğrulama eksikliği ayrıca yazılıdır. |
| **Bloklu (girdi/lisanslı veri bekliyor)** | Gerekli girdi veya lisanslı çizelge verisi (K6: repoda tutulmaz) yoksa `BLOCKED_MISSING_INPUT` / `BLOCKED_CODE_DATA` / `NOT_CALCULATED` döner; sayısal sonuç yayımlanmaz. |
| **Yok** | Bu sürümde uygulanmamış ya da üretim akışına bağlı değil (`OUT_OF_SCOPE` / `NOT_CALCULATED` veya hiç sonuç satırı yok). |

Kanıt sütunundaki yollar `packages/` altına göredir. `V-xx` numaraları
[`validation/asme-worked-examples.md`](validation/asme-worked-examples.md) kayıtlarıdır;
`B-xx` numaraları [`limitations.md`](limitations.md) kayıtlarıdır.

## 1. ASME VIII-1 rotası (`code-asme-viii-1`)

Ortak statü kapıları (aşağıdaki gövde/bombe/koni satırları için geçerli):
`ASMEVIII1DesignCode._apply_ug16b_minimum` (UG-16(b): net kalınlık < 1,5 mm ise `PASS` -> `FAIL`)
ve `_apply_material_data_check` (B-31: girilen S'nin sıcaklığı tasarım sıcaklığından farklıysa
ya da nominal kalınlık malzeme aralığı dışındaysa `PASS` -> `REVIEW_REQUIRED`; `FAIL` korunur).

| Hesap | Durum | Kanıt (dosya:fonksiyon) | Doğrulama / not |
|---|---|---|---|
| Silindirik gövde, iç basınç (UG-27) | **Hesaplandı ve doğrulandı** | `code-asme-viii-1/design_code.py:calculate_shell_thickness` + `formulas.py:shell_thickness_internal_pressure` | V-01, V-02, V-03 (+-%0,03). İç çap formu kullanılır; dış çap alternatifi yok, ticari yazılımlara göre %0,4-0,9 daha ince kalınlık (B-03, emniyetsiz yön). Kalın cidar (`t > R/2`) doğrulanmadı. |
| Eliptik bombe 2:1 (UG-32(d)), kalınlık | **Hesaplandı ve doğrulandı** | `design_code.py:calculate_head_thickness` + `formulas.py:head_elliptical_thickness` | V-13 (iç çap formu), V-04/V-05 (dış çap formu, formülasyon farkı). |
| Eliptik bombe, 2:1 dışı (`crown_depth` girilirse) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `formulas.py:head_elliptical_thickness_general` | Bağımsız doğrulama yok. **Tutarsızlık gözlemi:** kalınlık yolu `crown_depth` kullanır ama `calculate_mawp` yolu `mawp_from_ellipsoidal_head(D, t, S, E, C)` ile her zaman 2:1 varsayar. Ayrı doğrulama gerektirir (B-02). |
| Torisferik bombe (UG-32(e)), kalınlık ve MAWP | **Hesaplandı ve doğrulandı** | `design_code.py:_torispherical_radii` + `formulas.py:head_torispherical_thickness_full`, `mawp_from_torispherical_head` | V-11 (90 noktalı anma tablosu), V-14. Girilmezse varsayılan standart F&D (`L` = dış çap, `r = 0,06 L`) kullanılır; varsayım ve uyarı sonuca yazılır (K4). Bu varsayılanın `design_code` yolundaki uçtan uca testi doğrulanamadı. |
| Yarım küre bombe (UG-32(f)) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `formulas.py:head_hemispherical_thickness`, `mawp_from_hemispherical_head` | Tek yayınlanmış vaka (V-10, `TEK_KAYNAK` kuralı). Statü kapıları dışında `REVIEW_REQUIRED` zorlaması yok. |
| Düz kapak (UG-34(c)(2)/(3)) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:calculate_head_thickness` (`HeadType.FLAT`), `formulas.py:flat_head_thickness`, `flat_head_thickness_non_circular` | Bağlantı katsayısı `C` girilmezse `BLOCKED_MISSING_INPUT`. Yayınlanmış vaka yok; yalnız iç tutarlılık (V-17). (Eski matristeki "Flat covers - No" ifadesi güncel değildi.) |
| Konik bölüm (UG-32(g)), kalınlık ve MAWP | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:calculate_cone_thickness`, `calculate_mawp` (cone dalı) | Yayınlanmış vaka yok; yalnız iç tutarlılık (V-19). Arayüzde koni formu var (`apps/web-ui/src/pages.tsx`). |
| Koni uç birleşimi (Appendix 1-4/1-5) | **Yok** | `design_code.py:check_junctions` | Girdi/topoloji kaydedilir; gerilme çözümü uygulanmadı -> `OUT_OF_SCOPE`, girdi eksikse `BLOCKED_MISSING_INPUT`. `analysis_status=SUPPORTED` beyanı hesabı etkinleştirmez. |
| Korozyon payı (iç ölçü yönü) | **Hesaplandı ve doğrulandı** | `design_code.py:calculate_shell_thickness` (`D + 2C`) | V-16 (+%0,005). |
| Negatif mill toleransı, şekillendirme incelmesi | **Ön kontrol (REVIEW_REQUIRED üretir)** | `formulas.py:shell_required_nominal_thickness` | B-26 düzeltmesi formülden bağımsız kabul testiyle korunur; yayınlanmış vaka yok. Tolerans girilmezse %12,5 varsayılır ve sonuca yazılır (B-10). |
| MAWP - silindir, eliptik 2:1, torisferik | **Hesaplandı ve doğrulandı** | `design_code.py:calculate_mawp` + `formulas.py:mawp_from_shell`, `mawp_from_ellipsoidal_head`, `mawp_from_torispherical_head` | V-08, V-09, V-11. |
| MAWP - yarım küre, düz kapak, koni | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:calculate_mawp` | Yayınlanmış vaka yok / tek vaka. Global MAWP = geçerli bileşen sonuçlarının minimumu (`orchestrator.py:get_global_mawp`); bloklu bileşen minimuma sessizce katılmaz. |
| Statik sıvı yüksekliği düzeltmesi | **Ön kontrol (REVIEW_REQUIRED üretir)** | `orchestrator.py:_apply_static_head_correction` | Yoğunluk girilmezse (0) düzeltme uygulanmaz ve bu MAWP sonucuna varsayım olarak yazılır. Bağımsız doğrulama yok. |
| Hidrostatik test (UG-99(b)) ve pnömatik test (UG-100) - `S_test` bilinen veya test = tasarım sıcaklığı | **Hesaplandı ve doğrulandı** | `design_code.py:calculate_hydrotest_pressure`, `calculate_pneumatic_test_pressure`, `_test_stress_ratio` | V-07 (LSR = 1 vakası). B-28: LSR = basınç parçalarındaki en küçük `S_test/S_design`; `MaterialProperty.allowable_stress_test_temp` girilmişse `PASS`. Açık: bileşen bazlı test gerilme sınırı kontrolü yok. |
| Hidrostatik/pnömatik test - test sıcaklığındaki S girilmemiş, tasarım != test sıcaklığı | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:_test_stress_ratio` (`complete=False`), `_apply_test_stress_ratio` | LSR = 1 yalnız yedek değerdir ve test basıncını olması gerekenden düşük verebilir; sonuç `REVIEW_REQUIRED` + "emniyetsiz yön" uyarısı. Varsayılan projede (200 C / 20 C) bu durum görünür. |
| Malzeme izin verilen gerilme değeri (S) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:_apply_material_data_check` | S kullanıcı tarafından manuel girilir. Kıyas yalnız girilen S'nin **beyan edilen** sıcaklığını ve kalınlık aralığını denetler; değerin tablo değeri olduğunu kanıtlamaz (B-31). |
| Malzeme veritabanı / sıcaklık interpolasyonu | **Bloklu (girdi/lisanslı veri bekliyor)** | `materials/data_pack.py:MaterialDataPack`, `materials/interpolation.py` | Lisanslı veri paketi yok; `code-asme-viii-1` ve `calc-core` bu paketi çağırmaz (yalnız `external-pressure/chart_lookup.py` içe aktarır). Hesap motoru tek `allowable_stress` değerini kullanır. |
| Nozul takviyesi, radyal (UG-37/UG-40 alan yerine koyma) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `nozzles/reinforcement.py:calculate_reinforcement`, `build_reinforcement_calculation_result`; `design_code.py:calculate_nozzle` | Radyal nozulda `PASS`/`FAIL` üretebilir. Tek yayınlanmış vaka (V-15, `TEK_KAYNAK`); büyük açıklık (App 1-7), UG-45(b), harici yükler, kaynak dayanımı yok (B-08). Kod/baskı izi `ASME VIII-1 / 2025` sabit. |
| Nozul takviyesi, eğik (`inclination_angle` > 0) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `nozzles/reinforcement.py:calculate_reinforcement` (`angle > 0.0` dalı) | B-30: yeterli alanda `PASS` yerine `REVIEW_REQUIRED` + uyarı; yetersiz alanda `FAIL`. Eğik/hillside yöntemi ve `F` faktörü uygulanmıyor (`1/cos(a)` izdüşümü yaklaşıklığı). |
| Nozul boynu minimum kalınlığı (UG-45) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `nozzles/reinforcement.py:calculate_reinforcement` (`trn` karşılaştırması) | Yalnız (a) bacağı; Tablo UG-45 telifli, gömülmedi (K6). İhlal **uyarı** yazar, tek başına durumu düşürmez (B-16). |
| Muayene açıklığı (UG-46) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `nozzles/clash_check.py:check_inspection_opening` | Yalnız iç çap eşiği + manway varlığı; eşik aşılıp manway yoksa `REVIEW_REQUIRED` (B-17). |
| Nozul çakışma / geometri kontrolleri | **Ön kontrol (REVIEW_REQUIRED üretir)** | `nozzles/clash_check.py:build_clash_check_result`, `validate_nozzle_clash` | Geometrik kural kontrolü; bağımsız doğrulama yok. |
| Nozula gelen harici kuvvet/moment, WRC-107/537 yerel gerilme | **Yok** | `supports/wrc.py` (yardımcı) | B-29: eksik katsayı `ValueError` ile bloklanır; ancak WRC modülü hesap hattına veya arayüze **bağlı değil** (`wrc` içe aktarımı orkestratör/eklentide yok). |
| Flanş (Appendix 2) - üretim yolu, `Y`/`f`/`W`/`M` girilmemiş | **Bloklu (girdi/lisanslı veri bekliyor)** | `orchestrator.py` (D1) -> `design_code.py:calculate_flange` -> `flanges/flange_calc.py:check_flange_stress` | Biri boşsa `BLOCKED_MISSING_INPUT` (sahte `PASS` üretilmez). `Y`, `f` (lisanslı çizelge) ve `W`, `M` (Appendix 2 çalışma sayfası) **kullanıcı girdisidir** (`Flange.flange_factor_Y/f`, `bolt_load_W_N`, `moment_M_Nmm`). Not: bu alanlar ve durum kapısı çalışma ağacında **commit edilmemiş** güncel değişikliktir (üzerinde çalışma sürüyor). |
| Flanş gerilme kontrolü - `Y`, `f`, `W`, `M` girilmişse | **Ön kontrol (REVIEW_REQUIRED üretir)** | `flanges/flange_calc.py:check_flange_stress`, `flanges/formulas.py` | Yalnız `S_H`, `S_R`, `S_T`, `S_avg` basitleştirilmiş formüllerle kıyaslanır; olumlu sonuç `REVIEW_REQUIRED`, aşım `FAIL`. Rijitlik (App 2-14), conta yerleşme/işletme, cıvata alanı, `S_T`/`S_H` sınırları yok; `W`/`M` türetimi (`flange_moment`, `calculate_moment_from_pressure`) hesap hattında çağrılmıyor -> **Yok**. B16.5/B16.47 basınç sınıfı rotası da yok. |
| Dış basınç / vakum - gövde ve bombe (UG-28/UG-33) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `external-pressure/ext_pressure.py:check_shell_external_pressure`, `check_head_external_pressure`, `_guard_preliminary_estimate`; `design_code.py:check_external_pressure` | Olumlu sonuç asla `PASS` değil `REVIEW_REQUIRED`; aşım `FAIL`. A/B faktörleri kullanıcı girdisidir, doğrulanmaz. Bombe katsayısı B-21/V-18 ile düzeltildi ama tam UG-33 yöntemi yok. |
| Dış basınç / vakum - A/B faktörü girilmemiş | **Bloklu (girdi/lisanslı veri bekliyor)** | `design_code.py:check_external_pressure` (`set_blocked_code_data`) | `BLOCKED_CODE_DATA` (K6: Şekil G çizelgesi repoda tutulmaz). |
| Dış basınç - koni, halka rijitleştirici | **Yok** | `design_code.py:check_external_pressure` (koni dalı) | Koni için `OUT_OF_SCOPE`; rijitleştirici halka hesabı yok. |
| MDMT (UCS-66) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `mdmt/mdmt_calc.py:check_mdmt`; `design_code.py:check_mdmt` | Doğrusal kalınlık düzeltmesi ((t-38) x 0,5) basitleştirmedir; sonuç yalnız `REVIEW_REQUIRED` veya `FAIL` (impact test tasarım sıcaklığını kapsamıyorsa). Eğri grubu girilmemişse **Bloklu** (`BLOCKED_MISSING_INPUT`); çözülemeyen bileşen varsa özet MDMT yayımlanmaz (B-12). |
| Destek - eyer (Zick) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `supports/support_calc.py:check_saddle`; `design_code.py:check_supports` | `PASS` -> `REVIEW_REQUIRED` (`check_supports`). Orkestrasyon (tüm destek tipleri): ağırlık iki durumdur — boş metal (`empty_weight_N`) ve hidrotest = metal + su (ρ=1000 kg/m³ K4 varsayımı, `calc_core.volume_mass` iç hacmi); `total_weight_N` basma (hidrotest + varsa Fz>0) ağırlığıdır; işletme sıvısı, izolasyon, platform, iç ekipman yok. Yük durumları TOPLANMAZ: her durum ayrı hesaplanıp zarf (max) alınır, yalnız `concurrent_with` ile açıkça eşzamanlı işaretlenen (ve `NON_CONCURRENT_LOAD_PAIRS` dışındaki) durumlar birleşir; moment √(ΣMx²+ΣMy²) + Σ(H·kaldıraç), yöneten durum/kaynak (manuel/yük durumu) sonuca yazılır. Host: konum-aralığı kapısı yalnız eyerde (host gövde olmalı); etek/ayak host olarak gövde/bombe/koni alabilir (etek çapı host dış çapından ±%15 saparsa uyarı; ayak dağılım yarıçapı host dış çapından büyükse `NOT_CALCULATED`). **Destek/ayak alanında başka bir çalışma sürüyor; kod durumu değişebilir.** **Eyer (Zick, 2026-09-25):** yapı artık Zick 1951 / Moss 3-10'dur: M1/M2 (H = başlık derinliği, L = teğet-teğet, iki uç A ayrı, Q moment dengesinden), S1 çekme/basma, kabuk ve başlık kesmesi (K2/K3), boynuz çevresel (membran + K6 eğilmesi), eyer altı (K7); her kontrol kendi sınırıyla (S·E, 0,5Sy, 0,8S, 1,25S, 1,5S) ayrı kullanım oranıdır. K1/K2/K3/K6/K7 tabloları programda YOKTUR (K6): kullanıcı girer, eksikse `BLOCKED_CODE_DATA`; halka/başlık-yakınlığı (A ≤ R/2) durumunda K1 = π, halkalıda K2 = 1/π kodludur. ≥3 eyer `OUT_OF_SCOPE`; tam katsayı + geçen kontrollerde bile nihai PASS yok (`REVIEW_REQUIRED`); aşınma plakası, halka tasarımı, burkulma B ve eyer/temel kapsam dışıdır. |
| Destek - etek (skirt) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `supports/support_calc.py:check_skirt`; `design_code.py:check_supports` | Aynı kapı. Ankraj: girilmemişse `PASS` üretilemez (B-25). Etek basma/burkulma kontrolü artık kullanıcı girdili UG-23(b) B faktörüyle (`skirt_allowable_compressive_MPa`; çizelge repoda yok, K6) yapılır: min(S, B) sınırı, B girilmezse sonuç `BLOCKED_CODE_DATA` (gerilme S'yi aşıyorsa B'den bağımsız FAIL). Çekme tarafı `M/Z − W_min/A ≤ S·E` (E girilmezse 0,6 VARSAYIMI sonuca yazılır); kaldırma varsa ankraj/taban plakası uyarısı verilir, ankraj etek kontrolü yoktur. Etek çapı ORTALAMA çaptır. Taban halkası, beton ezilmesi, kaldırma kulakları **yok**. |
| Destek - ayak (leg) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `supports/support_calc.py:check_leg_support`; `supports/formulas.py:leg_pipe_section_area`; `design_code.py:check_supports` | B-20 (payload) 2026-09-20'de, B-27 (halka kesit) 2026-09-22'de kapatıldı; üretim wiring testleri `tests/faz5/test_faz5_supports.py::test_production_support_payload_wires_*`. **Ayak-A backend (2026-09-26):** `leg_section_type` doluysa `supports/leg_detail.py` dört ek sonuç üretir: `leg_section_check` (AISC ASD E2/H1, PASS mümkün), `leg_weld_check` (üç köşe kaynağı; asgari bacak girilmezse REVIEW), `base_plate_check` (yataklık + Moss 4-12 kalınlık), `wrc_local_stress` (katsayı kullanıcı girdisi -> yoksa `BLOCKED_CODE_DATA`; D/T dışı `OUT_OF_SCOPE`; geçse bile `REVIEW_REQUIRED`). `leg_stress` özeti alt kontrolleri listeler, nihai PASS vermez. `leg_section_type` boşsa yalnız eski boru-ayak `leg_stress`. **UI (Ayak-B, 2026-09-26):** ayak formu beş alt bölüme ayrıldı (WRC tablosunda boş = okunmadı/null, 0 = gerçek sıfır) ve dört yeni sonuç grubu gösteriliyor; canlı doğrulandı (WRC boşken `Veri Engelli`, girilince hesap). CAD/FEA'da ayak yok. Testler: `tests/faz5/test_leg_detail.py`. |
| Global yükler - yük toplama/kombinasyon zarfı | **Ön kontrol (REVIEW_REQUIRED üretir)** | `calc-core/load_engine.py`; `orchestrator.py:_calculate_global_loads` | Her sonuç `REVIEW_REQUIRED`; koda özgü yapısal/stabilite kontrolü değildir (B-23). |
| Rüzgâr / deprem yük üretimi | **Yok** | `domain/global_loads.py:calculate_wind_load`, `calculate_seismic_load` | Yardımcı fonksiyonlar tanımlı ama hesap hattında çağrılmıyor; koda özgü katsayı ve spektrum yok (B-24). |
| Kaynak doğrulama (UW-11/UW-12, UCS-56 kural denetimi) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `welds/validator.py:validate_weld`, `build_weld_validation_result`; `design_code.py:validate_welds` | Kural tabanlı denetim (NDE-verim uyumu, WPS/PQR, PWHT); `PASS`/`REVIEW_REQUIRED`/`FAIL` üretir. Bağımsız doğrulama yok. Köşe kaynağı dayanımı (`welds/strength.py`) üretimde çağrılmıyor. |
| Basınç tahliye (UG-125..136) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `pressure-relief/calculator.py:PressureReliefCalculator.check`; `calc-core/code_interface.py:check_pressure_relief` | Yalnız ayar/patlama basıncı <= korunan MAWP, birikme yüzdesi ve sertifikalı kapasite **alanının varlığı** denetlenir; kapasite **boyutlandırılmaz**, senaryo/blowdown analizi yok. Üç girdi de varsa `PASS` mümkündür (kapasite yeterliliği kanıtlanmadan). Cihaz türü ile basınç alanı eşleştirilmez. Sistem tanımsızsa `OUT_OF_SCOPE`, cihaz yoksa `BLOCKED_MISSING_INPUT`. |
| Yorulma, sünme / yüksek sıcaklık, jaketli/çok odalı kap, tüp demeti | **Yok** | - | Kapsam dışı / sonraki sürüm (bkz. `limitations.md`). |
| FEA (Design by Analysis) | **Yok** | `fea/fea_adapter.py:run_analysis` | İskelet: çözücü kurulu değilse `REVIEW_REQUIRED`; kurulu olsa da mesh/doğrusallaştırma/kabul `NOT_EVALUATED`. Hesap hattına bağlı değil (bilinçli, Faz 2 kararı). |

## 2. EN 13445 rotası (`code-en-13445`)

Rota API'de açıkça seçilir (`apps/api/services.py`, B-22); ASME'ye sessiz geri dönüş yoktur ve
arayüzde "Hesap Standardı" seçicisi vardır. Kapsam dardır; **EN 13445 seçeneği "tam EN tasarımı"
anlamına gelmez.** Bu rota için bağımsız yayınlanmış vaka karşılaştırması **yoktur**.

| Hesap | Durum | Kanıt (dosya:fonksiyon) | Doğrulama / not |
|---|---|---|---|
| Silindirik gövde (EN 13445-3, 5.4.2) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `code-en-13445/design_code.py:calculate_shell_thickness` | `PASS`/`FAIL` üretebilir ama bağımsız doğrulaması yok; ASME'deki malzeme-veri kapısı (B-31) EN yolunda **uygulanmıyor**. |
| Bombeler - eliptik, torisferik, yarım küre (5.5.x) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:calculate_head_thickness` | Torisferik varsayılanı `r = 0,10 D` doğrulanmadı (B-09, varsayım sonuca yazılır). Düz kapak: `NOT_CALCULATED` (**Yok**). |
| MAWP | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:calculate_mawp` | Koni: `NOT_CALCULATED` (bileşen tipi desteklenmiyor). |
| Koni kalınlığı | **Yok** | - | EN eklentisinde `calculate_cone_thickness` tanımlı değil; orkestratör hesap hatası kaydı düşer (sayısal sonuç yok). |
| Hidrostatik test (PED 10.2.3.3.1) | **Ön kontrol (REVIEW_REQUIRED üretir)** | `design_code.py:calculate_hydrotest_pressure`, `_test_ratio_review_reason` | `fa/ft` uygulanmıyor; oran eksik/eşiğin (1,144) üstünde ise `REVIEW_REQUIRED` (B-28). |
| Pnömatik test | **Yok** | `calc-core/code_interface.py:calculate_pneumatic_test_pressure` (taban sınıf) | `NOT_CALCULATED`. |
| Nozul takviyesi | **Yok** | `design_code.py:calculate_nozzle` | `NOT_CALCULATED`. |
| Dış basınç / vakum | **Yok** | `design_code.py:check_external_pressure` | `NOT_CALCULATED`; ASME UG-28 değerleri kullanılmaz. |
| Flanş, yorulma | **Yok** | `design_code.py:calculate_flange`, `calculate_fatigue` | `NOT_CALCULATED` / `OUT_OF_SCOPE`; yorulma girdi yoksa `BLOCKED_MISSING_INPUT`. |
| Yük kombinasyonları | **Yok** | `design_code.py:check_load_combinations` | Her kombinasyon için açık `NOT_CALCULATED`. |
| MDMT, destekler, kaynak doğrulama, nozul çakışması, koni uç birleşimi | **Yok** | `calc-core/code_interface.py` (taban sınıf, boş liste döner) | EN eklentisi bu kancaları geçersiz kılmaz: **hiç sonuç satırı üretilmez** (sessiz yokluk). Basınç tahliye kontrolü taban sınıftan geldiği için EN projesinde de (ASME UG-125 etiketiyle) çalışır. |

## 3. PED / CE kapsamı

Bu bölüm yazılımın **kategori/şablon/kayıt** üretmesini anlatır; PED uygunluğu veya CE kararı
değildir (üretici risk analizi, uygulanabilir tüm ESR'ler, uygunluk değerlendirme modülü ve
gerekiyorsa onaylanmış kuruluş süreci gerçek proje kanıtlarıyla kapatılmalıdır).

| Özellik | Durum | Kanıt | Not |
|---|---|---|---|
| PED sınıflandırma (SEP -> Kat. IV), modül eşlemesi | **Ön kontrol (REVIEW_REQUIRED üretir)** | `ped-2014-68-eu/engine.py:PEDClassificationEngine.classify`, `tables.py`; `apps/api/services.py:generate_report_html` | Yalnız rapor akışında ve `project.fluid` tanımlıysa çalışır; hacim tüm bileşenleri kapsamıyorsa bloklanır. Ek II eşiklerinin bağımsız doğrulaması bu turda **doğrulanamadı**. |
| ESR matrisi | **Ön kontrol (REVIEW_REQUIRED üretir)** | `compliance/esr_matrix.py:ESRMatrix.default_for_vessel` | Varsayılan şablon; rapor §ESR'ye bağlanır. Uygulanabilirlik kararı mühendisindir. |
| AB Uygunluk Beyanı, isim plakası, risk analizi, teknik dosya dizini | **Yok** | `compliance/declaration.py`, `risk_analysis.py`, `technical_file.py` | Modeller/şablonlar paket içinde var; API, arayüz ve rapor üreticisine **bağlı değil**. |
| StandardPack sürüm kilidi / manifest | **Ön kontrol (REVIEW_REQUIRED üretir)** | `standards/manifests/*.json`, `standards_manifests.py` | Sürüm izi kaydı; lisanslı standart verisi içermez. |

## 4. Paket özeti (Faz 5)

| Paket | Üretim hattındaki durum |
|---|---|
| `external-pressure/` | Bağlı; olumlu sonuç `REVIEW_REQUIRED`, A/B yoksa **Bloklu**. |
| `flanges/` | Bağlı; `Y`/`f`/`W`/`M` kullanıcı girdisi, eksikse **Bloklu**, tamsa `REVIEW_REQUIRED`/`FAIL` (üzerinde çalışma sürüyor, commit edilmemiş). |
| `supports/` | Bağlı; sonuçlar `REVIEW_REQUIRED`. `wrc.py`, `sections.py`, taban plakası yardımcıları hesap hattında **çağrılmıyor**. **Ayak planı devam ediyor.** |
| `mdmt/` | Bağlı; asla nihai `PASS` yok. |
| `pressure-relief/` | Bağlı; yalnız ön kontrol, boyutlandırma yok. |
| `fea/` | Bağlı **değil**, iskelet. |
| `compliance/`, `ped-2014-68-eu/` | Yalnız rapor akışında (ESR + PED sınıflandırma). |

Test sayıları bu tabloda tutulmaz (eski sürümdeki sayılar güncel değildi); güncel sayı için
`pytest` çalıştırılır.

## 5. V1 kapsam notları

- **Tasarım rotası:** ASME VIII-1 veya EN 13445; EN rotası yukarıdaki tabloda görüldüğü gibi dar
  kapsamlıdır. Arayüzde EN seçimi uyarı ile sunulur.
- **Malzeme:** Manuel giriş (S, akma, çekme, isteğe bağlı test sıcaklığında S, S'nin sıcaklığı ve
  kalınlık aralığı). Otomatik malzeme veritabanı yok (yukarıya bakın).
- **Nozul:** Radyal nozullar için alan yerine koyma; eğik nozul `REVIEW_REQUIRED`.
- **Kap tipi:** Sabit, metalik, ateşle temas etmeyen, tek basınç odası.
- **Yön:** Yatay veya dikey.
- **FEA:** İskelet; sahte `PASS` üretmez.
- **Hâlâ eksik (Yok):** yorulma, sünme, düz kapak/koni için EN, nozul harici yükleri/WRC, rüzgâr-deprem
  yük üretimi, flanş `M`/`W` türetimi ve rijitlik kontrolü, dış basınç çizelge verisi, lisanslı malzeme veri paketi,
  DoC/isim plakası/teknik dosya çıktıları.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 3.0 - 2026-09-25: her satır kod okunarak dört etikete
(Hesaplandı ve doğrulandı / Ön kontrol / Bloklu / Yok) bağlandı; "Yes" etiketleri kaldırıldı.
Bir önceki revizyon 2.0 (2026-07-24) Faz 4/5 durumunu "Yes" olarak gösteriyordu. Destek/ayak
alanındaki çalışma ve flanş `Y`/`f`/`W`/`M` alanları commit edilmemiş değişikliklerdir; durumları kod
değiştikçe yeniden doğrulanmalıdır.*
