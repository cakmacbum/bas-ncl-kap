# En acil yapılacaklar — 2026-11-10
Öncelik: 🔴 emniyet/doğruluk · 🟠 güven temeli · 🟡 vitrin/altyapı · ⚪ Yusuf kararı/verisi
Yollar `pressure-vessel-suite/` köküne göre (aksi belirtilmedikçe). Satır numaraları 2026-11-10'da koddan okundu; kod değişince kayar, ajan önce fonksiyon adını arasın.

## Neden bu liste
2026-11-10'da site, kuruluş hedefi (PV Elite / COMPRESS benzeri sistem) ve bugünkü gerçek durumla kıyaslandı. Hüküm: ASME iç basınç çekirdeği sağlam; ama ürün "rakip" değil "tamamlayıcı" — ön boyutlandırma + imalatçı çıktıları (STEP, DXF, açınım, BOM) + PED ön hazırlık. Ana hata: çekirdek (malzeme verisi, EN doğrulaması, flanş, yükler) bitmeden genişliğe gidildi (FEM, kaldırma kulağı, maliyet, imalat resmi). Bu liste önce çekirdeği ve vitrin-ürün uyumunu kapatır; bitene kadar yeni özellik yok.

## Önce bunlar — ilk 10
1. Düz kapak MAWP'de çap korozyonsuz, emniyetsiz yön (A1)
2. MAWP satırı MAWP ≪ P iken PASS görünüyor (A2)
3. EN 13445 rotası "deneysel" etiketlenmeli + tarama testi (A4)
4. A05/B05 bağımsız el hesabı + code-reviewer + push (A5)
5. 2026-10 kampanya çıktıları geçersiz, kanıt gibi duruyor (A7)
6. Landing ürünle uyuşmuyor + marka/iletişim dağınık (C1 + C4)
7. Kullanım kılavuzu PDF'i kontrolsüz — dağıtma (A6)
8. Torisferik bombe L/r tanımı: önce madde teyidi, sonra düzelt (A3)
9. Malzeme veritabanı: veri kaynağı kararı + hesap hattına bağlantı (B1)
10. EN 13445-3 metni/çözümlü örnek temini (B2)

Not: planda C2 için "`.env` izleniyorsa 1. sıra" kuralı vardı. Kontrol edildi: `.env` git'te izlenmiyor (`.gitignore:16`), yalnız `.env.example` izleniyor. Sıra değişmedi.

---

## 🔴 P0 — Emniyet ve doğruluk (bu hafta, yeni özellikten önce)

### A1 — Düz kapak MAWP'de çap korozyonsuz (emniyetsiz yön, ~%0,8)
**Sorun:** `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py`, `calculate_mawp`, `HeadType.FLAT` dalı (761–772). Kod önce `D = head.inside_diameter + 2*C` yapıyor (korozyonlu, satır 744 civarı), sonra `d = D - 2 * C` (satır 769) ile yeni çapa geri dönüp bunu `flat_head_mawp`'e veriyor ve ara değeri `d_corroded` diye etiketliyor (772). Kalınlık yolu (aynı dosya 538–563) korozyonlu `D` kullanıyor. Aynı bileşende kalınlık ve MAWP farklı çapla hesaplanıyor. `flat_head_mawp` (`formulas.py:554`) `t_corr = t - CA` düşüyor; yani kalınlık tarafı korozyonlu, çap tarafı değil → MAWP yüksek çıkıyor. Kayıt: `tools/test-ortami/BULGULAR.md` T-02 (site 0,014083 MPa, bağımsız 0,013971 MPa).
**Nasıl:**
1. MAWP dalında `d = D` (korozyonlu) kullan; `d_corroded` ara değeri de bu olsun.
2. `flat_head_mawp` içindeki `CA` kullanımının kalınlık yolunun `CA=0.0` + ortak `shell_required_nominal_thickness` deseniyle tutarlı olduğunu kontrol et (çift düşme/çift ekleme olmasın; V-17 bu yüzden düzeltilmişti).
3. Gidiş-dönüş regresyon testi: CA>0 iken t_required ile hesaplanan MAWP ≈ P (±%0,1).
4. Dairesel olmayan kapak (`flat_z_factor`) için MAWP yolu var mı bak. Kalınlık yolunda `flat_head_thickness_non_circular` var; MAWP dalında karşılığı görünmüyor (doğrulanmadı). Yoksa açık NOT_CALCULATED ver, sessiz geçme.
**Bitti ölçütü:** `tools/test-ortami` kıyasında düz kapak satırları ✅ (≤%0,5); yeni gidiş-dönüş testi yeşil.
**Kim:** Kod işi.

### A2 — MAWP satırı, MAWP ≪ P iken PASS görünüyor (T-03)
**Sorun:** `design_code.py:791` `calculate_mawp` sonunda koşulsuz `result.set_pass()`. Tüm bileşen tiplerini etkiler (gövde, bombe, koni), yalnız düz kapağı değil. MAWP < P karşılaştırması başka yerde de yapılmıyor: `packages/calc-core/src/calc_core/orchestrator.py`'de `design_pressure` yalnız satır ~595'te çalışma basıncı kıyasında geçiyor; `get_global_mawp` (satır 60) yalnız min alıyor. Örnek: MAWP 0,014 MPa, P 1,2 MPa → `mawp` satırı PASS, `thickness` satırı FAIL.
**Nasıl:**
1. MAWP satırının durumu o satırın kendi kontrolünden türesin (DEC-008): MAWP < tasarım basıncı → FAIL (utilization = P/MAWP); aksi PASS.
2. Statik kafa düzeltmesi sonrası (orchestrator ~446–500, `mawp_r.final_result = corrected_mawp`) satırın durumu yeniden değerlendirilsin; düzeltme sonrası MAWP < P ise FAIL.
3. Global MAWP satırı için aynı kural.
4. Arayüz ve raporda "MAWP < P" açıkça yazsın.
5. `tests/wiring` ve rapor snapshot testleri güncellenecek. Aynı kural EN eklentisi `calculate_mawp` (`packages/code-en-13445/src/code_en_13445/design_code.py:545`) için de uygulanacak.
**Bitti ölçütü:** MAWP<P vakasında satır FAIL; mevcut PASS vakaları değişmedi; EN'de aynı.
**Kim:** Kod işi.

### A3 — Torisferik bombe L/r: korozyonlu iç ölçü mü, nominal dış ölçü mü? (T-01, ~%0,67, emniyetli)
**Sorun:** `design_code.py` `_torispherical_radii` (satır 23–65). Kod, taç yarıçapı girilmediğinde `L = dış çap` (kullanıcı verdiyse o, yoksa `ID + 2·t_nominal`) ve `r = 0,06·L` alıyor; fonksiyon docstring'i bunu bilerek yapıyor ("F&D taç yarıçapı dış geometriye göre"). Bağımsız test ortamı ise UG-32(e) ölçülerini korozyonlu istiyor ve `L+CA`, `r+CA` kullanıyor (BULGULAR T-01: site t=10,636 mm, bağımsız 10,565 mm). Yani fark kod hatası mı, tanım farkı mı (F&D varsayılanı L = OD) belli değil. Emniyetli yönde (kalınlık fazla, MAWP düşük); o yüzden A1/A2'den sonra. Çağıran yerler: kalınlık dalı satır 524, MAWP dalı satır 755.
**Nasıl:**
1. Önce madde teyidi (DEC-007): UG-32(e)'nin L ve r için korozyonlu/yeni ölçü kuralını yayınlanmış kaynaktan oku, nota yaz. Kod değiştirmeden önce.
2. Kural "korozyonlu iç ölçü" çıkarsa: kalınlık ve MAWP yolunda aynı `L_c = L + C`, `r_c = r + C` kullan; ara değerlere hem yeni hem korozyonlu değeri yaz.
3. Kural "as-built dış ölçü" çıkarsa: test ortamı `hesap.js`'i bu tanıma çevir, T-01 kapanır.
4. V-11/V-14 vakaları CA=0 ise etkilenmez; CA>0 için bağımsız vaka ekle.
**Bitti ölçütü:** Test ortamı torisferik 9 ⚠️ satırı ✅; madde teyidi kasada.
**Kim:** Önce kaynak okuma (ajan + Yusuf teyidi), sonra kod işi.
**Plandan fark:** İlk planda "kod korozyonsuz kullanıyor" yazıyordu; kod nominal dış çapı bilerek kullanıyor. Madde teyidi şart.

### A4 — EN 13445 rotası "deneysel" etiketlenmeli
**Sorun:** EN formülleri lisanslı metin olmadan bellekten yazıldı (hepsi verified=False). E06'da elipsoidal bombe gereken kalınlığın yarısını veriyordu (1,84 → 4,21 mm; düzeltildi). Benzeri başka hata olmadığının kanıtı yok. Mevcut durum:
- Kapı tek yerde değil: `packages/code-en-13445/src/code_en_13445/design_code.py:_cap_unverified` (satır 1316) PASS'i REVIEW_REQUIRED'a çeviriyor ama her metot onu elle çağırıyor (14 çağrı / 13 `set_pass`). `set_pass` olup kapısı görünmeyenler: 315 (silindir kalınlığı), 700 (MAWP'de kapı yalnız düz/torisferik/elipsoidal bayraklarına bağlı), 792 (hidrotest). Ayrıntı doğrulanmadı; tarama testi bunu kesinleştirir.
- Arayüz: `apps/web-ui/src/pages.tsx:309` seçici etiketi yalnız "EN 13445"; 320'de seçilince uyarı metni var ("kapsamı tamamlanmamış modüller…"). Kalıcı bant ve rapor başlığı yok: `packages/report-engine/src/report_engine/generator.py`'de "deneysel" / EN uyarısı geçmiyor.
**Nasıl:**
1. Seçici etiketi "EN 13445 (deneysel — doğrulanmadı)" (`pages.tsx:309`, gerekirse `i18n.ts`).
2. EN seçiliyken sonuç sayfası üstünde ve raporun başında (generator.py) kalıcı uyarı bandı.
3. Tarama testi: EN rotasında hiçbir hesap tipi (shell, head, mawp, hydrotest, nozzle, cone, pneumatic, junction, external pressure, stress…) verified=False iken PASS dönemez (en fazla REVIEW_REQUIRED). Tek test, tüm EN sonuç tiplerini projeyle çalıştırıp tarar. Kırmızı çıkan satırlar 315/700/792 gibi yerlerde kapıyı ekletir.
4. Landing metni buna uysun (C1).
**Bitti ölçütü:** Tarama testi yeşil; arayüz ve raporda bant görünüyor.
**Kim:** Kod işi.

### A5 — A05 (EN dış basınç 8.5/8.7) ve B05 (EN nozul takviyesi 9.5) incelemesiz; main origin'in 11 commit ilerisinde
**Sorun:** `git log origin/main..main` = 11 commit (doğrulandı). İçinde A05/B05 (agy Gemini yazdı, şef birleştirdi), kılavuz PDF'i ve test-ortami. STATE 2026-11-07: code-reviewer YAPILMADI, A05 el hesabı bağımsız teyit EDİLMEDİ. Kod: `packages/code-en-13445/src/code_en_13445/external_pressure.py`, `openings.py`.
**Nasıl:**
1. A05 için bağımsız el hesabı: referans değer ÖNCE ayrı dosyaya yazılır, API sonra çağrılır (DEC-007, LEARNINGS "bağımsız sütun API kopyası").
2. code-reviewer ajanı A05 + B05 diff'ini incelesin; not kasaya.
3. Tam pytest + vitest + build.
4. Push.
5. Canlıya alma Yusuf onayıyla (A4 bandı canlıya birlikte gitsin).
**Bitti ölçütü:** El hesabı dosyası + inceleme notu kasada; origin/main güncel.
**Kim:** Kod/inceleme işi; canlıya alma onayı Yusuf.

### A6 — Kullanım kılavuzu PDF'i kontrolsüz
**Sorun:** `docs/kilavuz/Vessela-Kullanim-ve-Hesap-Kilavuzu.pdf` (29 s., Gemini yazdı; `kilavuz.html` ve `img/` aynı klasörde, basım `tools/kilavuz/pdf.py`). Formül/sayı satır satır kontrol edilmedi; ekran görüntüleri eksik (hesap sonuçları, 3D, rapor).
**Nasıl:**
1. Kontrol bitene kadar dağıtma, siteye koyma; kapağa "TASLAK — doğrulanmadı".
2. `kilavuz.html`'deki her formülü `formulas.py` ile, her sayısal örneği API çıktısıyla karşılaştıran kontrol tablosu çıkar.
3. EN bölümleri A4 gereği "deneysel" işaretli.
4. Eksik görüntüler için yarım kalan `apps/web-ui/e2e/kilavuz-shots.spec.ts`'i tamamla.
**Bitti ölçütü:** Kontrol tablosunda her satır ✓ veya düzeltildi.
**Kim:** Kod/doküman işi.

### A7 — 2026-10 doğrulama kampanyası çıktıları geçersiz ama kanıt gibi duruyor
**Sorun:** `docs/validation/campaign-2026-10/` (OZET.md: 1302 vaka, 893 "DOĞRULANDI") tutarsız geometriyle (bombe 800 / gövde 1000, ayak 600) üretildi; OZET.md'de geçersizlik notu yok. Landing "independent verification" iddiasını bu tür çalışmalara dayandırıyor.
**Nasıl:**
1. `docs/validation/campaign-2026-10/OZET.md` başına "GEÇERSİZ — yeniden koşulacak (2026-11-10)" notu.
2. `tools/campaign/bases.py` tabanları düzeltilmiş hâliyle kampanyayı yeniden koş. Her vakaya ayrı sahip kimliği; 429'u kapsam dışı sayma. Eski çıktılar arşive (ör. `docs/validation/campaign-2026-10-gecersiz/`).
3. Sonra G01 geometri kapısını sıkılaştır (bileşen sırası tanımsızken zincir kuralları atlanıyor).
**Bitti ölçütü:** Yeni OZET tarihli; eski çıktılar arşivde, işaretli.
**Kim:** Kod işi (koşu); sonuç yorumu Yusuf.

---

## 🟠 P1 — Güven temeli (2–4 hafta)

### B1 — Malzeme veritabanı yok; S elle giriliyor (rakiplere göre en büyük eksik)
**Sorun:** `packages/materials/src/materials/data_pack.py` (`MaterialDataPack`, `interpolate_pack_property`) yazılmış ama hesap hattına bağlı değil: grep'te yalnız `materials/__init__.py` ve `tools/campaign/tur2/t12_malzeme_db/run.py` kullanıyor (doğrulandı). Arayüzde S serbest sayı alanı: `apps/web-ui/src/pages.tsx:975` ("İzin Verilen Gerilme (S)"). Yanlış S → yanlış PASS.
**Nasıl:**
1. Yusuf kararı: veri nereden? ASME II-D ve EN 10028 değerleri lisanslı; ücretsiz herkese açık araçta dağıtımın hukuki durumu netleşmeli. Güvenli yol: değerler repoya girmez (K6). İki kanal: (a) kullanıcı kendi lisanslı tablosunu CSV/JSON içe aktarır; (b) Yusuf'un lisanslı kopyadan girdiği küçük başlangıç seti (en çok kullanılan 10–15 malzeme) özel depoda/Supabase tablosunda, her kayıtta baskı + tablo + satır kaynağı.
2. Bağlantı: malzeme seçilince S(T_tasarım) ve S(T_test) paketten interpolasyonla dolar, `source_reference` sonuca yazılır. Sıcaklık aralık dışıysa BLOCKED (ekstrapolasyon yok — fonksiyon zaten LookupError atıyor).
3. Elle giriş kalır ama sonuç "S kullanıcı girdisi — doğrulanmadı" notuyla REVIEW_REQUIRED'a düşer.
4. Kalınlık aralığı ve ürün formu kontrolü pakete bağlanır (B-31 kapısı).
**Bitti ölçütü:** Paketten seçilen malzemeyle S elle girilmeden hesap; aralık dışı sıcaklık bloklu; el girişi PASS vermiyor.
**Kim:** Önce Yusuf kararı (veri kaynağı/lisans) ve verisi; sonra kod işi.

### B2 — EN 13445-3 formüllerini kaynakla doğrula
**Sorun:** Bkz. A4. Zayıf liste 2026-11-06 EKSIKLER'den.
**Nasıl:**
1. Yusuf: TS EN 13445-3 metnini temin et (TSE) ya da yayınlanmış çözümlü örnek bul (erişilebilirliği doğrulanmalı).
2. Madde madde: E02 koni küçük uç τ/β_H · E03 β polinom katsayıları, eb'deki 111 ve 0,825 · E04 pnömatik formül, fa/fT seçimi, döküm bölenleri, Tablo 5.6-1 · E06 7.5.4 katsayıları ve K aralığı · A05 8.5/8.7 · B05 9.5.
3. Her formül için iki bağımsız sayısal vaka (±%1 kuralı, `docs/validation/README.md`).
4. Ancak o zaman `verified=True` ve A4 etiketi madde madde kalkar.
**Bitti ölçütü:** Her EN formülü için doğrulama kaydı; doğrulanamayan REVIEW_REQUIRED'da kalır.
**Kim:** Yusuf (kaynak temini); sonra kod/doğrulama işi.

### B3 — Bağımsız test ortamını genişlet ve otomatikleştir
**Sorun:** `tools/test-ortami/` (`hesap.js`, `kiyas.js`) kapsamı UG-27, UG-32, UG-34, MAWP, UG-99/100. Nozul, koni, dış basınç, EN yok. Kıyas elle koşuluyor.
**Nasıl:**
1. Nozul takviyesi (UG-37), koni (UG-32(g)), dış basınç (kullanıcı A/B ile) ekle.
2. `kiyas.js`'i tek komutla regresyon olarak koş (CI yoksa yerel script; D3 sonrası CI'a).
3. Motor suite kodunu okumadan yazılmaya devam etsin.
**Bitti ölçütü:** Kıyas raporunda ❌ yok, ⚠️ gerekçeli.
**Kim:** Kod işi.

### B4 — Süreç kuralı: formül birleştirme kapısı
**Sorun:** Formülleri farklı modeller (Codex, Gemini, Sonnet) bellekten yazıyor; E06 bu yoldan geldi.
**Nasıl:** `.project-ai/DECISIONS.md`'ye karar olarak yaz. Hesap formülü içeren hiçbir paket şu üçü olmadan main'e girmez: (a) madde/denklem numarası ve kaynağın nereden okunduğu, (b) API'den önce yazılmış bağımsız sayısal vaka, (c) code-reviewer geçişi. Kaynak yoksa `verified=False` + REVIEW_REQUIRED.
**Bitti ölçütü:** Karar DECISIONS.md'de; paket şablonuna (`paketler/`) üç madde eklendi.
**Kim:** Yusuf kararı (karar numarasını Yusuf/şef verir; burada yalnız öneri).

### B5 — Nitelikli mühendis incelemesi
**Sorun:** PV Elite/COMPRESS raporlarını muayene kuruluşları tanıyor; buradaki doğrulama ajanların web'de bulduğu örneklere dayanıyor, imzalı inceleme yok.
**Nasıl:**
1. ASME/PED deneyimli bir basınçlı kap mühendisine çekirdek ASME modüllerini (gövde, bombeler, MAWP, hidrotest, nozul takviyesi) inceletme.
2. Bulgular `docs/validation/` altına tarihli kayıt.
3. Sitede "kim, ne zaman, neyi inceledi" açıkça.
**Bitti ölçütü:** İmzalı/tarihli inceleme kaydı repoda; landing buna atıf yapıyor.
**Kim:** Yusuf.

### B6 — Lisanslı veri bekleyen bloklu modüller
**Sorun:** Tablo verisi gelmeden bloklu kalan modüller; bunlar "var" gibi sunulmamalı.
**Nasıl:**
1. Zick K katsayıları: tablo beklemek yerine Zick (1951) kapalı-form ifadelerinden eyer açısına göre hesapla; bilinen tablo değerleriyle (120°/150°) karşılaştırarak doğrula. Kaynak ifadeler doğrulanmadan PASS yok.
2. Dış basınç A/B (ASME II-D Subpart 3), ASME Tablo 1-5.2 (Δ), UCS-66 eğrileri, B16.5 basınç-sıcaklık sınıfları: B1'deki veri paketi mekanizmasıyla aynı kanaldan (kullanıcı içe aktarır / lisanslı özel set).
3. WRC 537: veri gelene kadar arayüzde "veri gerekli" olarak kalsın; özellik listesinde "var" diye sunulmasın.
**Bitti ölçütü:** Her bloklu modül ya veriyle çalışıyor ya arayüzde "veri gerekli" diyor; Zick K kapalı-form kaynağıyla doğrulanmış.
**Kim:** Zick: kod işi (kaynak okuma); diğerleri Yusuf verisi (B1 kararına bağlı).

### B7 — Doğrulanmamış katalog verileri
**Sorun:** `apps/web-ui/src/data/` içinde üç dosya, üçü de `"verified": false` (doğrulandı): `upn-catalog.json` (elle girilmiş, çapraz doğrulanmamış), `coupling-catalog.json` (diş açılmış manşon iç çapı ↔ SCH160/XXS eşlemesi ajan hafızasından; kaynak wermac.org/hardhatengineer.com), `nozzle-catalog.json` ("SCH10" NPS 1/2–12'de aslında 10S; kullanıcı girişi).
**Nasıl:**
1. ASME B36.10M/B36.19M, B16.11 ve DIN 1026-1 ile satır satır karşılaştır.
2. Kaynağı dosyaya yaz; doğrulanan satırda `verified: true`.
3. Doğrulanana kadar arayüzde "katalog değeri doğrulanmadı" notu.
**Bitti ölçütü:** Her katalog ya `verified: true` + kaynak, ya arayüzde uyarı.
**Kim:** Kod/veri işi; standart tabloları Yusuf'un erişimine bağlı olabilir.

---

## 🟡 P2 — Vitrin ve konumlandırma (1–2 gün; ucuz olduğu için erken yap)

### C1 — Landing ürünle uyuşmuyor
**Sorun:** `apps/landing/index.html` (uzun tek satırlık HTML; 2026-10-11'den kalma). Doğrulandı: "FEA is not available." (SCOPE/LIMITATIONS bölümü), "HTML calculation report", "CadQuery/OpenCascade model with a live in-browser 3D preview", "900+ AUTOMATED TESTS" (proofbar ve metin), "Independent verification against published worked examples produced by commercial pressure-vessel software", "draft Declaration of Conformity and nameplate", sayfa dili `lang="en"`.
**Nasıl:**
1. "FEA is not available" → eksenel simetrik FEA var, sınırıyla yaz (eksen dışı nozul, destek, dış yük yok).
2. "HTML calculation report" → A4 baskı + PDF de var.
3. "CadQuery/OpenCascade" → tarayıcıda replicad/OCCT.
4. "900+ automated tests" → güncel sayı (STATE: pytest 1202 + vitest 164 + e2e 3).
5. "Independent verification…" iddiası A7 bitene kadar yumuşatılsın.
6. Dil: landing İngilizce, uygulama yalnız Türkçe → ya landing'e Türkçe sürüm ya uygulamaya İngilizce. Öneri: önce Türkçe landing (hedef kitle Türk imalatçı).
7. Konum cümlesi: "ön boyutlandırma + imalatçı çıktıları (STEP, DXF, açınım, BOM) + PED ön hazırlık; PV Elite/COMPRESS'in yerine geçmez."
8. EN "deneysel" (A4).
9. "Draft Declaration of Conformity and nameplate" iddiası → C3 sonucuna göre.
10. "calculated in the open" ifadesi → C2.
**Bitti ölçütü:** Landing'deki her iddia ürün ekranında gösterilebiliyor; yukarıdaki ifadeler grep'te yok/düzeltilmiş.
**Kim:** Kod işi; dil kararı Yusuf.

### C2 — "Calculated in the open" ↔ repo private
**Sorun:** Landing başlığı/meta ("calculated in the open") açıklık çağrıştırıyor; repo private. "open-source" ifadesi landing'de geçmiyor (grep boş); başvuru metinlerinde olabilir (doğrulanmadı). `.env`: `pressure-vessel-suite/.env` diskte var ama git'te izlenmiyor (`.gitignore:16`), yalnız `.env.example` izleniyor — acil değil.
**Nasıl:**
1. Karar: repo public mi? Evet ise önce `.env`, anahtar geçmişi (git log taraması), lisanslı veri taraması.
2. Hayır ise başlık/meta ifadesi değişir ("hesap adımları açık gösterilir" gibi).
**Bitti ölçütü:** Landing ve başvuru metinleri reponun gerçek durumuyla uyumlu.
**Kim:** Yusuf kararı.

### C3 — PED çıktıları (DoC taslağı, isim plakası, ESR listesi) landing'de vaat ediliyor
**Sorun (kodla doğrulandı):**
- ESR matrisi bağlı: `apps/api/services.py:21,247` `ESRMatrix` ve `ped_2014_68_eu` kullanılıyor.
- İsim plakası kısmen: raporda `packages/report-engine/src/report_engine/generator.py:693` "18. İsim Plakası Bilgileri" tablosu var (PS, tasarım basıncı/sıcaklığı, standart). `compliance.NameplateInfo` bağlı değil.
- DoC taslağı BAĞLI DEĞİL: `packages/compliance/src/compliance/declaration.py` `DeclarationOfConformity` sınıfı yalnız paket içinde ve testlerde; API, rapor ve arayüzde kullanılmıyor.
**Nasıl:**
1. Karar: DoC taslağını bağla (rakiplerin yapmadığı gerçek farklılaştırıcı — öncelik ver) ya da landing'den çıkar.
2. Bağlanırsa: `DeclarationOfConformity` + `NameplateInfo` → API uç noktası + rapor bölümü + arayüz düğmesi; her alan revizyona bağlı (`CalculationRevisionBinding`).
3. Bağlanmayacaksa landing'deki cümle "ESR matrisi ve isim plakası bilgileri" olarak daralsın.
**Bitti ölçütü:** Landing'de vaat edilen her PED çıktısı arayüzden indirilebiliyor.
**Kim:** Kararı Yusuf; kod işi.

### C4 — Marka ve iletişim dağınık
**Sorun:** "Pressure Vessel Suite" / "PV Suite" / "Vessela" / "Basınçlı Kap Tasarım Suite". İletişim: landing/privacy/terms `contact@zeyslabs.com`; `info@zeyslab.com` yalnız `.project-ai/STATE.md`'de (Console org kaydı, 2026-10-09 notu) — kodda geçmiyor. Yani sitede iki adres çakışması yok; kayıtlı org adresi ile site adresi farklı.
**Nasıl:** Tek ad, tek adres seç; landing (`index.html`, `404.html`, `privacy.html`, `terms.html`), uygulama başlığı, kılavuz kapağı aynı olsun.
**Bitti ölçütü:** Repo genelinde grep'te tek marka adı ve tek e-posta.
**Kim:** Yusuf kararı (ad/adres); kod işi.

### C5 — Sonuç ekranında doğrulama seviyesi görünmüyor
**Sorun:** `docs/calculation-coverage.md`'de dört etiket var (doğrulandı / ön kontrol / bloklu / yok) ama sonuç satırında yok. `apps/web-ui/src/types.ts:476` `notices` alanı tanımlı, `pages.tsx` onu göstermiyor; `calc.verification` (pages.tsx:1273) başka şey: kontrol kümesi sonucu.
**Nasıl:**
1. Her `calculation_type` için doğrulama seviyesi eşlemesini API yanıtına koy (coverage dosyasından türet).
2. Her sonuç satırında rozet.
3. EN satırları A4 gereği "deneysel".
**Bitti ölçütü:** Kullanıcı her satırda hangi sayıya güvenebileceğini görüyor.
**Kim:** Kod işi.

---

## 🟡 P3 — Altyapı ve güvenlik

### D1 — Kalıcılık ve kimlik
**Sorun:** `X-Client-Id` sır değil; API'de hız sınırı yok (grep boş). Depo seçimi `apps/api/main.py:32`: SUPABASE_URL + SERVICE_ROLE_KEY yoksa bellek içi → veri kaybı.
**Nasıl:**
1. Üretimde Supabase deposunun gerçekten etkin olduğunu doğrula (env yoksa bellek içi).
2. "Projeyi dosya olarak indir / yükle (JSON)": hesapsız kullanımda en sağlam kalıcılık.
3. API'ye basit hız sınırı.
4. Giriş (AUTH_ENABLED) yalnız kalıcı proje/paylaşım isteyen kullanıcı için, zorunlu değil.
**Bitti ölçütü:** Üretimde kalıcılık kanıtlı; JSON indir/yükle çalışıyor; hız sınırı testli.
**Kim:** Kod işi; canlı env kontrolü Yusuf.

### D2 — Güvenlik başlıkları ve küçük açıklar (kaynak: kök `bulgular.md`, 2026-10-25)
Durum (2026-11-10 kodda):
- CSP hâlâ yalnız `frame-ancestors 'none'` (`vercel.json`, kökte) → tam politika (wasm ve worker/blob istisnalarıyla). AÇIK.
- `apps/web-ui/src/api.ts` encode tutarsızlığı SÜRÜYOR: satır 124/128/132 `encodeURIComponent(id)` kullanıyor; 153 (PUT), 179, 188, 192, 196 kullanmıyor. AÇIK.
- CORS `*` → KAPANDI: `apps/api/main.py:56` ortam değişkeninden köken listesi (varsayılan localhost). Üretimde `CORS_ORIGINS` ayarlı mı, doğrulanmadı.
- "uvicorn --reload" → KAPANDI: kök `Dockerfile:26` `--reload` yok.
- HSTS includeSubDomains: `vercel.json`'da başlık yok; canlıda doğrulanmadı.
- Rapor HTML kaçışı XSS regresyon testi, ölü DNS kaydı api.zeyslabs-vessela.com: doğrulanmadı.
**Nasıl:** Açık olanları paket yap: CSP, api.ts encode (tek yardımcı fonksiyon), HSTS, XSS testi, DNS temizliği.
**Bitti ölçütü:** Açık satırlar kapandı, `bulgular.md`'de işaretli.
**Kim:** Kod işi; DNS Yusuf.

### D3 — CI yok / bundle
**Sorun:** `.github/workflows` yok (doğrulandı; ne kökte ne `pressure-vessel-suite/`te, `git ls-files`'ta da yok). Ana bundle ~1,4–1,5 MB (bu turda ölçülmedi).
**Nasıl:**
1. Push'ta pytest + vitest + build + `kiyas.js` (B3).
2. Kod bölme: katalog JSON'ları, three.js, FEA tembel yükleme.
**Bitti ölçütü:** Push'ta otomatik koşu yeşil; ana bundle küçüldü (ölç, rakamı nota yaz).
**Kim:** Kod işi.

### D4 — Girdi doğrulama
**Sorun:** Geometri alanlarında üst sınır/NaN/inf yok (G-03'ün açık kalan kısmı).
**Nasıl:** API şemasında (pydantic) sonlu-sayı ve makul üst sınır kontrolü; arayüzde aynı sınırlar; negatif/sıfır/aşırı değer testleri.
**Bitti ölçütü:** NaN/inf/aşırı değer 422 dönüyor; test var.
**Kim:** Kod işi.

### D5 — Eski ajan API anahtarının sağlayıcıda iptali
**Sorun:** STATE 2026-10-09'da Yusuf'ta bekliyor. Anahtar değeri bu notta yok.
**Nasıl:** Yusuf sağlayıcı panelinden eski anahtarı iptal eder; yenisi `.env`'de.
**Bitti ölçütü:** Eski anahtar sağlayıcıda "revoked".
**Kim:** Yusuf.

---

## ⚪ P4 — Kapsam (yalnız P0–P1 bittikten sonra, bu sırayla)
Kural: P0–P1 bitene kadar yeni özellik yok (3D CalculiX, CFD, yeni çıktı türleri dondu).
1. **Flanş (App. 2):** conta m/y → Wm1/Wm2, cıvata alanı, moment türetimi, rijitlik; B16.5 sınıf kontrolü (veri B6). Bitti: yayınlanmış vakalarla ±%1.
2. **Nozul:** UG-45 tam, kaynak dayanımı (UG-41/UW-16), büyük açıklık, bombe/eğik nozul.
3. **Dış basınç:** A/B verisiyle iteratif kalınlık, rijitleştirici halka, koni.
4. **Rüzgâr/deprem:** tek kod seç (öneri: Türkiye pazarı için TS EN 1991-1-4 + TBDY 2018); `domain/global_loads.py`'yi hesap hattına ve destek kontrolüne bağla. Yusuf kararı: kod seçimi.
5. **MDMT:** UCS-66 eğrileri + coincident ratio (B-04). Veri B6.
6. **Destekler:** 3+ eyer, taban halkası (Δ), eyer Zick tamamı.
7. **Hidrotest gerilme sınırı:** σ ≤ Sy mi 0,9·Sy mi (Yusuf kararı), Sy(T).
8. **EN flanş / yorulma / yük kombinasyonu:** FUTURE'da kalır.

## Yusuf'un kararı / verisi gerekenler
| Konu | Ne gerekiyor | Madde |
|---|---|---|
| Malzeme verisi kanalı | Lisans/hukuki durum; kullanıcı içe aktarımı mı, özel depo mu; 10–15 malzemelik başlangıç seti | B1 |
| EN 13445-3 metni | TSE'den temin ya da çözümlü örnek | B2 |
| Formül birleştirme kuralı | Karar numarası + onay | B4 |
| Mühendis incelemesi | Kim inceleyecek, bütçe | B5 |
| Lisanslı tablolar | ASME II-D Subpart 3, Tablo 1-5.2, UCS-66, B16.5 P-T, WRC 537 | B6 |
| Landing dili | Türkçe landing mi, İngilizce uygulama mı | C1 |
| Repo public mi | Evet/hayır; hayırsa "open" ifadesi değişir | C2 |
| DoC taslağı | Bağla mı, landing'den çıkar mı | C3 |
| Marka adı + tek e-posta | Ad ve adres seçimi | C4 |
| Üretim env kontrolü | Supabase etkin mi, CORS_ORIGINS ayarlı mı | D1, D2 |
| DNS | Ölü kayıt api.zeyslabs-vessela.com | D2 |
| Eski API anahtarı | Sağlayıcıda iptal | D5 |
| Hidrotest sınırı | σ ≤ Sy mi 0,9·Sy mi | P4-7 |
| Rüzgâr/deprem kodu | TS EN 1991-1-4 + TBDY 2018 öneri | P4-4 |
| Canlıya alma | A5 sonrası onay | A5 |
| Torisferik tanım teyidi | UG-32(e) L/r ölçüsü | A3 |

## Bilerek yapılmayacaklar (landing'de açıkça yazılsın)
Eşanjör (UHX/TEMA) · ASME VIII-2 / tam DBA · çok odalı ve ceketli kap · sünme · kapsamlı yorulma · 3D FEA sunucusu · CFD.
