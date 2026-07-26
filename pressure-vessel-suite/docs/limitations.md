# Limitations and Out-of-Scope Items

> Bu doküman, V1 sürümünün kapsam dışı bıraktığı özellikleri ve bilinen sınırlamaları listeler.

## V1 kapsam dışı (Later)

| Kategori | Özellik | Gerekçe |
|---|---|---|
| Yük | Rüzgâr ve deprem | Sonraki sürüm |
| Yük | Nozula gelen harici boru yükleri | Sonraki sürüm |
| Yük | Yorulma analizi | Sonraki sürüm |
| Yapı | Düz kapak / kör flanş | Sonraki sürüm |
| Yapı | Konik bölüm | Sonraki sürüm |
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
| Dış basınç / vakum (UG-28) | `external-pressure/` | ✅ Faz 5 | ✅ |
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

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 2.5 — Faz 3: hayalet özellikler kapatıldı, B-09…B-13 ele alındı (2026-07-26)*
