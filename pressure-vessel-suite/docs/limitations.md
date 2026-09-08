# Limitations and Out-of-Scope Items

> Bu doküman, V1 sürümünün kapsam dışı bıraktığı özellikleri ve bilinen sınırlamaları listeler.

## V1 kapsam dışı (Later)

| Kategori | Özellik | Gerekçe |
|---|---|---|
| Yük | Rüzgâr ve deprem | Sonraki sürüm |
| Yük | Nozula gelen harici boru yükleri | Sonraki sürüm |
| Yük | Yorulma analizi | Sonraki sürüm |
| Yapı | Düz kapak / kör flanş | Sonraki sürüm |
| Yapı | Konik bölüm | Domain + hesap var (`orchestrator.py` kalınlık ve MAWP hesaplıyor), arayüzde form yok (Faz 4) |
| Yapı | Çoklu gövde kesiti / 2'den fazla bombe / çoklu malzeme-kaynak | Arayüz `shell_sections[0]`, tam 2 bombe, `materials[0]`, `welds[0]` ile sınırlı (Faz 4) |
| Yük | Yük durumları (15 zorunlu şablon) | `domain/load_cases.py` var, arayüz yok (Faz 4) |
| Uyumluluk | PED / uyumluluk ekranı, DoC, isim plakası | `apps/api/services.py` rapor üreticisine `traceability`/`ped_result`/`compliance` vermiyor → rapor §6 ve §19 boş kalıyor (Faz 4) |
| Hesap rotası | EN 13445 arayüzden seçilemiyor | `apps/api/services.py` `ASMEVIII1DesignCode`'u sabitliyor, `project.calculation_code` yok sayılıyor (Faz 4) |
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
| **Flanş tasarımı (Appendix 2)** | `flanges/` | ✅ Faz 5 | ❌ **BAGLI DEGIL: flanges** |
| FEA doğrulama laboratuvarı | `fea/` | ⚠️ iskelet | ❌ **BAGLI DEGIL: fea** |
| PED sınıflandırma motoru | `ped-2014-68-eu/` | ✅ Faz 4 | ayrı akış (rapor) |
| EN 13445 hesap rotası | `code-en-13445/` | ✅ Faz 4 | ✅ (kod seçimiyle) |
| ESR matrisi + DoC + isim plakası | `compliance/` | ✅ Faz 4 | ayrı akış (rapor) |
| StandardPack sürüm kilidi | `standards/manifests/` | ✅ Faz 4 | ✅ |

**`BAGLI DEGIL: <paket>`** işareti makine tarafından okunur; bir paketi bağlamadan
bu satırı silmek testi kırar.

### Flanş neden bağlı değil

`FlangeCalculator.check_flange_stress()` tam Appendix 2 geometrisi istiyor: `A`/`B`
çapları, cıvata dairesi, conta boyutları ve konumu, cıvata alanı. Domain'de bunların
**hiçbiri yok** — `Head`/`Nozzle` modellerinde flanş geometrisi tanımlı değil. Bu bir
bağlantı eksiği değil, yazılmamış bir özelliktir; bağlamak için önce domain modeli
gerekir. Ayrıca bkz. B-11.

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
- **B-03 — Dış çap alternatifleri (App 1-1(a)(1), 1-4(c)) implement edilmemiş.**
  Karşılaştırılan iki ticari yazılım da varsayılan olarak bu formları kullanıyor. Suite'in
  iç çap formları %0.4-0.9 **daha ince** kalınlık üretiyor. Küçük ama sistematik ve
  emniyetsiz yönde; imalatçı çıktıyı ticari yazılımla karşılaştırırsa fark görecektir.
- **B-04 — UG-34(c)(3) (dairesel olmayan düz kapak, `Z` faktörü) yok.** Yalnız
  UG-34(c)(2) dairesel kapak var.
- ~~**B-05 — UG-32(e) torisferik ve UG-32(f) yarım küre bağımsız teyit almadı.**~~
  **Kapatıldı (tur 2, 2026-07-26):** torisferik anma tablosuyla 90 nokta üzerinden,
  yarım küre bombe tipi karşılaştırmasıyla doğrulandı.
- **B-06 — Torisferik taç yarıçapı varsayılanı iç çaptır, standart ASME F&D dış çap kullanır.**
  Kullanıcı taç yarıçapını girmezse `L = D` (iç çap) varsayılıyor; yayınlanmış karşılaştırma
  taç yarıçapının **dış çapa** eşit olduğunu gösteriyor (tur 2, V-14). Fark %0.5 mertebesinde
  ve emniyetsiz tarafta. `Head` modelinde dış çap alanı olmadığı için bu turda değiştirilmedi;
  varsayım kullanıldığında uyarı veriliyor. Taç yarıçapı girildiğinde sorun yok.

- **B-07 — Nozul takviyesi yalnız radyal nozul içindir.** UG-37'nin eğik nozul `F`
  faktörü uygulanmıyor (`F = 1.0` alınıyor); eğik nozul girilirse uyarı veriliyor.
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

- **B-14 — UG-125…UG-136 (basınç tahliye) hiç yok.** Kap MAWP'si hesaplanıyor, tahliye
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

Ayrıca **kaynağın kendi sorunları** not edildi: kitap içi çelişki (min kalınlık için
iki farklı değer), B kısmının 34. sayfasında bir güvenlik kuralını tersine çeviren
dizgi/OCR hatası, mülga mevzuat referansları (İSİG Tüzüğü, RG 2000/24226). Bu
kaynak normatif referans olarak değil, kapsam denetimi girdisi olarak kullanıldı.
Detaylı karşılaştırma matrisi (K6 gereği kodda değil) kasada:
`vault/wiki/projeler/basincli-kap/basincli-kap-ts-karsilastirma.md`.

**Bilinçli olarak yapılmayacak:** TS 3362'yi üçüncü hesap rotası yapmak — kitap
formül vermiyor (implement edilecek bir şey yok), EN 13445 rotası zaten arayüzden
seçilemezken üçüncü bir kod eklemek Faz 3/4'te kapatılan hayalet özellik desenidir.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 2.8 — TS/MMO kaynağıyla kapsam denetimi: 6 gerçek eksik tespit edildi (B-14…B-19); üç ucuz olanı (B-15/16/17) basitleştirilmiş şekilde kapatıldı, basınç tahliye (B-14) ve imalat toleransları (B-18/19) açık (2026-09-08)*
