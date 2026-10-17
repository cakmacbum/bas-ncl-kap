# M2 kampanyası — bulgu kaydı

> Canlı kayıt. Her bulgu kod veya el hesabıyla şef (Claude) tarafından kontrol edildikten sonra
> "Teyitli" olur. Düzeltmeler **yalnız Yusuf onayından sonra** yapılır (DEC-005).
> Son güncelleme: 2026-10-17

Önem: KRİTİK (emniyetsiz, yaygın) · YÜKSEK (emniyetsiz, sınırlı) · ORTA (yanlış durum/eksik hesap) ·
DÜŞÜK (emniyetli yönde, kozmetik, altyapı).

## A. Teyitli suite hataları (düzeltme onay bekliyor)

| ID | Önem | Yön | Bileşen | Bulgu | Kanıt | Kaynak |
|---|---|---|---|---|---|---|
| B-01 | YÜKSEK | EMNİYETSİZ | Gövde MAWP (UG-27) | MAWP net cidarından yalnız iç korozyon payı (CAi) düşülüyor, **dış korozyon payı (CAo) düşülmüyor**. MAWP 9 vakada +%6.3 … +%41.7 fazla. | `code-asme-viii-1/design_code.py:692` (`C = internal_corrosion_allowance`), `:724` → `formulas.py:356-360` (`t_actual − C`) | F01, V01 teyidi, şef kod kontrolü |
| B-02 | YÜKSEK | EMNİYETSİZ | Gövde/bombe/koni gerekli nominal kalınlık, nozul, EN 13445 | Basınç hesaplarının hiçbiri **dış korozyon payını (CAo)** kullanmıyor; nominal gereksinim yalnız CAi ile kuruluyor. CAo > 0 girilen her tankta seçilen sac yetersizken PASS dönebilir. B-01 ile aynı kök neden; aynı turda düzeltilmeli. | `external_corrosion_allowance` tüm `packages/` içinde yalnız `supports/leg_detail.py:640`, `supports/support_calc.py:154`, `code-asme-viii-1/design_code.py:1920` satırlarında okunuyor; `design_code.py:337, 486, 2178` yalnız CAi alıyor; `code-en-13445` hiç okumuyor | Şef kod taraması |
| B-03 | ORTA | EMNİYETSİZ olabilir | Torisferik bombe UG-32(e) | `knuckle_radius` boş bırakılınca BLOCKED yerine varsayılan standart yarıçap kabul edilip **PASS** dönüyor. Eksik girdi bloke edilmeli (K4: sessiz varsayım yok) ya da en azından açık varsayım uyarısı verilmeli. | F03 vakası BAD-MISSING-R | F03 raporu |

## B. Bağlanmamış / tetiklenemeyen hesap yolları (ORTA — eksik kapsam)

| ID | Bulgu | Kanıt |
|---|---|---|
| B-04 | MDMT coincident ratio alanı solver girişine bağlı değil; UCS-66.1 indirimi hesaplanamıyor. | `code-asme-viii-1/design_code.py:1320-1340` |
| B-05 | `external_pressure_check` normal akışta üretilmiyor; vakum stabilitesi `external_pressure` adıyla dönüyor (sonuç adı karışıklığı). | `design_code.py:2029-2041`, `external_pressure/ext_pressure.py:325-358` |
| B-06 | EN 13445: flanş, yük kombinasyonu ve yorulma hesapları tetiklenemiyor (desteklenmiyor). | `code-en-13445/design_code.py:709-769` |
| B-07 | `material_check` yalnız malzeme eksikken `NOT CALCULATED` üretiyor; normal durumda kontrol satırı yok. | `calc-core/orchestrator.py:490-507` |
| B-08 | Nozul çakışma/yerleşim kontrolü (F10) yalnız kategorik sonuç veriyor; sayısal mesafe/marj çıktısı yok. | F10 raporu (30 vaka KAPSAM_DIŞI) |
| B-09 | MDMT (F12) için bağımsız sayısal kıyas yapılamadı (136 vaka KAYNAK_BEKLİYOR); UCS-66 eğri değerleri telifli (K6). | F12 raporu |

## C. Aday bulgular (teyit edilmedi)

| ID | Bulgu | Durum |
|---|---|---|
| C-01 | Flanş K2-13 (PVEng örneği) kıyasında Bsc=1.1893 cıvata aralığı düzeltme katsayısının uygulanışı şüpheli. | F21 16 satırı KAYNAK_BEKLİYOR; App 2 bağımsız oracle yok. Teyit paketi gerekli. |

## D. Altyapı bulguları

| ID | Önem | Bulgu | Durum |
|---|---|---|---|
| D-01 | DÜŞÜK | W04 (`869e874`, sahip izolasyonu) sonrası her API isteği `X-Client-Id` istiyor; kampanya harness'i 400 alıyordu. | **Düzeltildi**: P11 (`63434ed`), 934 test geçti |
| D-02 | DÜŞÜK | Bazı `results.json` dosyalarında etiketler bozuk kodlanmış (mojibake, ör. f06). | **Düzeltildi**: aggregate normalizasyonu (P10/P11) |

## E. Reddedilen iddialar (suite doğru — kayıt için)

| İddia | Kaynak | Neden reddedildi |
|---|---|---|
| F05 düz kapak: suite CA eklemiyor, emniyetsiz | V05 | Suite `t_required`'a CA eklemez, nominal adımda bir kez ekler (`design_code.py:547-587`). Oracle tanım farkı. `d+2CA` kullanımı emniyetli yönde formülasyon farkı. |
| F04 yarım küre: suite E=0.875 kullanıyor | V04 | Fark her vakada tam 1/0.875: varsayılan %12.5 sac toleransı (K4) ile kıyaslanan alan uyuşmuyor. Suite UG-32(f) doğru (`design_code.py:533`). |
| F01 OD dalında CAi yerine CAo kullanılmalı | V01 | OD verildiğinde korozyonlu iç yarıçap `Do/2 − t + CAi`'dir; suite doğru (`design_code.py:720-722`). |
| F02 eliptik sapmaları | V02 | Oracle korozyonlu çapı kullanmıyor; suite emniyetli. |
| F09 nozul 30 sapma | V09 | Oracle gövde t_r'yi UG-27 dışı formülle hesaplıyor; suite doğru. |

| D-03 | ORTA (test altyapısı) | **DÜZELTİLDİ** (harness) | Kampanya tüm vakaları tek sahip kimliğiyle gönderiyordu; sahip başına proje tavanı 50 (`apps/api/store.py:18`). Tavan aşılınca 429 "Project limit reached" sessizce dönüyordu. Sonuç: T01 160/240, T04 250/300, T11 94/144, T30 60/110, T31 85/110 satır bu hatayla "KAPSAM_DIŞI" ya da "BLOCKED" sayılmıştı. | Harness her vakaya `uuid4` sahip veriyor (`tools/campaign/harness.py`). Bu, Tur 2'deki kapsam dışı sayılarının büyük kısmının sebebiydi; yeniden koşu gerekiyor. Aile sonuçları (F01–F21) etkilenmemiş (0 hata). |
| D-04 | ORTA | **DÜZELTİLDİ** (paket) | T32 satır durumu hatalı birleştirilmiş: 110/110 BULGU, oysa alt kontroller GEÇTİ. | Satır durumu kontroller üzerinden yeniden hesaplanacak (T40). |
| D-05 | — | **HAİKU DOĞRULAMASI** | T30 gövde sonuçlarından 30 rastgele vakanın bağımsız t_req hesabı: 12 UYUŞUR, 0 UYUŞMUYOR, 18 VERİ_YOK (VERİ_YOK hepsi D-03 kaynaklı). | Sonuç payload'ıyla çelişki yok. Yeniden koşudan sonra VERİ_YOK sıfırlanmalı; yeniden doğrulama yapılacak. |

## F. Tur 2 sonuçları (2026-10-17) — kısmen teyitli

| ID | Önem | Durum | Bulgu | Kanıt / karar |
|---|---|---|---|---|
| G-01 | YÜKSEK (aday) | **KAYNAK_BEKLİYOR** | Nozul merkezi 801 mm (>0.8D) PASS dönüyor, uyarı yok (T13). | Kodda 0.8D merkez sınırı yok (`nozzles/` ve `code-asme-viii-1/` tarandı). Ama bu sınırın normatif dayanağı teyit edilmedi; kaynak olmadan bulgu sayılmaz. |
| G-02 | — | **TEYİT EDİLMEDİ** | Statik kafa MAWP'den eksik düşülüyor (T16, 18 vaka). | Düzeltme kodu var (`calc-core/orchestrator.py:405-460`). Sapma ~0.0123 MPa, ρgh ile tam örtüşmüyor; referans kota konvansiyonu farkı olabilir. Vaka bazında yeniden kontrol gerek. |
| G-03 | ORTA | **TEYİTLİ (gözlem)** | Anlamsız girdiler (ör. basınç 1e9, NaN) HTTP 200 PASS/FAIL dönüyor; bazıları 500 veriyor (T03, 25 vaka). | Şema `conditions.py:24-29` yalnız `gt=0` koyuyor; üst sınır ve sonlu sayı kontrolü yok. 500 hatası gözlemlendi. |
| G-04 | DÜŞÜK | **DÜZELTİLDİ AYRICA** | Büyük harfli UUID kabul ediliyor (T06, 10 vaka). | Aynı sahibe normalleşiyor, sızıntı yok. Sahiplik izolasyonu (B, A'nın projesine 404) geçti. |

**İyi haber:** Sahiplik izolasyonu testi (T06) sızıntı bulmadı. Bir kullanıcı başka birinin projesini okuyamıyor, güncelleyemiyor ya da hesaplatamıyor.

**Eksik / bozuk test sonuçları (test hatası, bulgu değil):**
- T01 (240 vaka) ve T11 (144 vaka) tamamen KAPSAM_DIŞI: harness/üretici eşleşmesi yanlış, yeniden yazılmalı.
- T04 fuzz: 250 vakanın 250'si KAPSAM_DIŞI; yalnız 50 vaka anlamlı.
- T05 determinizm ve T07 rapor: 20/20 BULGU, ama sebebi test hatası olabilir; kontrol edilmeli.
- T09 (torisferik) ve T14 (etekli kolon): rapor yok, T14 modül bulunamadı; yeniden paketlenmeli.
- R02, R04, R05, R09 oracle düzeltmeleri: R04 yarım küre sapmalarını 0 yaptı, ama bunu suite'in varsayılan %12.5 sac toleransına hizalayarak yaptı. Bu kontrol hesabını suite'e uydurmak olur; bağımsız kanıt sayılmaz. R09 hâlâ 2 SAPMA bırakıyor.

Tur 3 (T30–T33, toplam ~440 vaka rastgele tank taraması) koşuyor; sonuçlar gelince aynı kontrol uygulanacak.

## H. Yeniden koşu sonrası durum (2026-10-17, sahip tavanı düzeltildikten sonra)

Geçerli sayılar, yalnız düzeltilmiş harness ile koşulan ve sınıflandırması doğrulanan vakalardır.

| Koşu | Vaka | Geçerli | Sonuç | Not |
|---|---:|---:|---|---|
| T30 gövde (mega_govde) | 110 | 110 | 110 GEÇTİ | Kontroller: monotonluk, tutarlılık. Gövde bağımsız t_req karşılaştırması Haiku örnekleminde 12/12 uyuştu |
| T31 destek (mega_destek) | 110 | 110 | 110 GEÇTİ | Satır durumu kontrollerden yeniden hesaplandı (eski üretici hatalıydı) |
| T32 nozul (mega_nozul) | 110 | 110 | 89 PASS (oran≥1), 21 FAIL (oran<1) | Kullanım oranı = mevcut/gerekli alan. Test beklentisi tersti; API tutarlı, bulgu yok |
| T33 yük (mega_yuk) | 110 | 110 | 110 GEÇTİ | |
| T14 etekli kolon | 30 | 30 | 30 GEÇTİ | Taban halkası sonucu API'de yok: kapsam boşluğu (aşağıda) |
| T04 fuzz | 300 | 300 | 300 GEÇTİ | Sınıflandırma yalnız "GEÇTİ" üretiyor; bulgu kontrolü zayıf, güvenilir sayılmaz |
| T11 yatay tank | 144 | 0 | — | Sınıflandırıcı hatalı: 216 saddle sonucunun 72'si REVIEW REQUIRED, 54'ü FAIL (sayısal), 18'i BLOCKED; hepsi "kapsam dışı" sayılmış. 216 OUT OF SCOPE gerçek kapsam dışı |
| T01 metamorfik | 240 | 0 | — | Gözlenen değerler None; sınıflandırma yapılmamış. Yeniden yazılmalı |

**Toplam geçerli (doğrulanmış sınıflandırma): 110+110+110+110+30 = 470 vaka. Ayrıca T04 300 vaka ama zayıf kontrol.**

Yeni kapsam boşlukları:
- **G-05:** Taban halkası (ring) sonucu API'de yok; etekli kolonda ring gerilmesi hesaplanmıyor (T14, 30/30 vaka).
- **G-06:** Yatay tankta saddle sonuçlarının 216'sı OUT OF SCOPE. Hangi konfigürasyonların kapsam dışı kaldığı belgelenmeli.

Açık işler: T01 ve T11 sınıflandırıcılarının yeniden yazımı; T40–T43 ve T45 Codex paketleri çıkış kodu 4 ile boş döndü (üretim yok); R04 oracle düzeltmesi bağımsız kanıt olmadığı için birleştirilmedi.

## I. Kütle gövde koşusu (tur5, n=1000, tohum 20261017) — B-01 yeniden üretildi

Koşu: `tools/campaign/tur5/mass_govde.py`. Bağımsız UG-27 formülü (script içinde yazılmış) API'nin `t_required` ve MAWP değerleriyle karşılaştırıldı.

| Sonuç | Vaka | Not |
|---|---:|---|
| HTTP 200 | 1000 / 1000 | Hata yok |
| t_required uyuşuyor (±%1) | 1000 / 1000 | Gerekli kalınlık hesabı tutarlı |
| MAWP uyuşuyor, CA_o = 0 | 359 / 359 | Tam uyum |
| MAWP sapıyor, CA_o > 0 | 641 / 641 | API değeri, dış korozyon payı düşülmemiş varyantla birebir eşleşiyor (B-01) |

Sonuç: B-01 bağımsız rastgele örnekte deterministik olarak yeniden üretildi; sapma tüm CA_o > 0 vakalarında, istisnasız. Emniyetsiz yön (MAWP fazla). Kanıt: `tools/campaign/tur5/mass_govde_20261017.csv`.

**Haiku bağımsız doğrulaması (ikinci gözlemci, 60 satır, tohum 7):** t_required 60/60 uyuştu. MAWP: 25 uyuşur (CA_o=0), 35 "CA_o düşülmemiş" varyantıyla birebir eşleşti (B-01), açıklanamayan sapma 0. Bu, kütle koşusunun sonucunu bağımsız olarak doğrular.

**Açık kalan işler (bu oturumda tamamlanmadı):**
- T01 (240): üretici `observed` değerini doğru bileşenden okumuyor; yeniden yazılıp koşulmalı.
- T11 (144): sınıflandırıcı yeniden yazılmalı (216 sayısal saddle sonucu kapsam dışı sayılmış).
- T50 Codex paketi iki kez boş döndü (çıkış 4); bu iş Codex'e değil doğrudan yazılmalı.
- T04 (300): yalnızca "GEÇTİ" üretiyor; kontroller zayıf.

## J. Son tur (2026-10-17): T04 ve T01

- **T04 (300 vaka, tur2/t04_fuzz):** Gerçek kontroller eklendi (sonlu sayı, kullanım tutarlılığı, gövde bağımsız UG-27). Kullanım: 806 kontrol tutarlı, 0 BULGU. Gövde bağımsız: 300/300 uyuştu. Satır durumu: 300 GEÇTİ. Haiku bağımsız yeniden hesabı: 40/40 uyuştu.
- **Tekrarlayan kural hatası:** Nozul takviyesinde `utilization_ratio = mevcut/gerekli`, PASS ⇔ ≥1 olmalı. Üç farklı koşuda (T32, T51, T04) test beklentisi bu oranı ters okudu ve yüzlerce PASS satırını sahte BULGU saydı. Düzeltildi; API tutarlı.
- **T01 (240):** Yön ihlali yok. 120 GEÇTİ, 120 BLOCKED (düz kapak, bağlantı faktörü C test girdisinde yok; API doğru bloke ediyor).
- **T11 (144):** Ana dalda yalnızca benim sınıflandırmam (81 KAPSAM, 36 SAYISAL_İNCELEME, 27 TASARIM_FAIL). Codex T42/T50 sonuçları ayrı ve birleşmedi.

## K. Şef kararları (2026-10-17)

- **T11 sınıflandırma kuralı:** `REVIEW REQUIRED` → SAYISAL_İNCELEME (ne GEÇTİ ne BULGU). `FAIL` → TASARIM_FAIL (sayısal yetersiz tasarım). `PASS` → GEÇTİ. `OUT OF SCOPE` / `BLOCKED CODE DATA` → KAPSAM_DIŞI. Kaynak: `tools/campaign/tur2/t11_yatay_tank_tarama/results_v2.json` (81 / 36 / 27).
- **T42 ve T50 Codex dalları birleştirilmedi:** İkisi de T11 `results.json`/`run.py` ve `results_v2.json` dosyalarını benim sınıflandırmamla çakışacak şekilde değiştiriyor ve birbirleriyle uyuşmuyor (T42: "36 BULGU", T50: "63 GEÇTİ"). Tek kaynak olarak ana daldaki sınıflandırma kullanılır.
- **Nozul kullanım kuralı:** `utilization_ratio` = mevcut/gerekli. PASS ⇔ oran ≥ 1. Gövde için PASS ⇔ kullanım ≤ 1.

## L. Haiku tam doğrulaması (1000 satır, gövde kütle koşusu)

Haiku bağımsız betikle 1000 satırın tamamını yeniden hesapladı: t_required 1000/1000 uyuştu; MAWP 359 uyuşur (CA_o=0), 641 CA_o düşülmemiş varyantla eşleşti (B-01), açıklanamayan sapma 0. Bu, şef kontrolündeki 1000 satır sonucunu bağımsız olarak doğrular. Betik ve çıktı: scratchpad `haiku_mass_tam.py` / `haiku_mass_tam.csv`.

## M. Luna bombe toplu taraması (T60, 300 vaka)

Luna (`gpt-6-luna`) paketi `tools/campaign/tur5/bombe_tarama/` altına 300 rastgele vaka üretti: 150 yarım küre (UG-32(f)), 150 torisferik (UG-32(e)). Her vaka API'den t_required alıp bağımsız formülle karşılaştırıldı. Şef ayrıca 300 vakanın tamamını kendi formülüyle yeniden hesapladı: 300/300 uyuştu (±%1). Bulgu yok; sonuç tutarlı.

## N. Haiku kendi test üretimi (300 vaka, tohum 4242)

Haiku kendi senaryo üreticisini yazdı (farklı parametre aralıkları: P 0.05–20 MPa, D_i 200–6000 mm, S 60–300 MPa, CA 0–6 mm), harness üzerinden API'yi çağırdı ve bağımsız UG-27 formülüyle karşılaştırdı: 300/300 UYUŞUR, VERİ_YOK 0, HTTP 200 hepsinde. En yüksek basınç (19.95 MPa) vakası da uyuştu. Betik ve CSV: scratchpad `haiku_uretim.py` / `haiku_uretim.csv`.

## O. Haiku eliptik bombe üretimi (300) ve bağımsızlık uyarısı

Haiku 300 eliptik bombe vakası üretti (tohum 9911): 300/300 "UYUŞUR". Şef bağımsız kontrolü (UG-32(d), K=1, D_c=D_i+2CA_i) CSV'deki girdilerle yeniden uyguladı: maksimum bağıl fark 6.6·10⁻⁷ (CSV yuvarlaması). API değeri doğru.

**Uyarı:** Haiku'nun CSV'deki `t_hesap` sütunu, 300 satırın 300'ünde `t_api` ile birebir aynı string. Yani Haiku'nun "bağımsız hesap" sütunu kendi hesabı değil, API değerinin kopyası. Aynı durum T04 ve kendi üretim (N) koşularında da görüldü. Bu nedenle Haiku'nun "uyuştu" sonuçları tek başına bağımsız kanıt sayılmaz; yalnız şef yeniden hesabı bağımsızdır. Gelecekteki Haiku görevleri bağımsız hesabı ayrı bir sütunda ve API değerine bakmadan yazmalıdır.

## P. Luna tam döngüsü (T63) — kontrol sorunları

Luna plan, yazım, koşum ve kendi kontrolünü tek başına yaptı (240 vaka). Ama kendi kontrolü iki yerde hatalı:
- **A (nozul, 120):** Bağımsız değerler hesaplanmamış (`independent_value = None`); "UYUŞUR" yalnızca API durumunun PASS olmasından geliyor. **Bağımsız kontrol yok; bu sonuç geçersiz sayılmalı.**
- **B (eliptik, 120):** 111 uyuşur, 9 uyuşmuyor. Şef yeniden hesabında Luna'nın bağımsız değerleri formülüyle tutarlı; API değerleri %1.0–1.6 büyük (muhafazakâr yön). Açık aday bulgu: API'deki ek terim henüz belirlenmedi (emniyetli yön, ORTA). Kod kontrolü gerekli.

Sonuç: Luna'nın tam döngüsü mekanik olarak tamamlandı, ama kontrol kalitesi yetersiz; A kontrolü boş geçiş üretti. Bu, Luna'nın bağımsız doğrulama yeteneğinin kanıtlanmadığı anlamına gelir.

## Q. Açık maddelerin kapanışı (T63 kontrolü, kod incelemesi)

- **B-07 · YÜKSEK · EMNİYETSİZ (yeni):** Nozul takviye hesabında ev sahibi gövde/bombe gerekli kalınlığı `_host_required_thickness` ile hesaplanıyor ve `"welds": []` veriliyor (`code-asme-viii-1/design_code.py` ~1066–1088). Kaynak verimi görünmediği için E = 1 alınıyor; `t_r = P·R/(S·E − 0.6P)` E'siz kalıyor ve gerekli alan (A_required = d·t_r) olduğundan küçük çıkıyor. Kanıt: T63 nozul A-001: API A_required = 4065.14 mm²; E = 0.86196 ile bağımsız hesap 4720.43 mm² (fark %16.1 ≈ 1/E). Düşük verimli kaynaklarda (E = 0.7) fark ~%43. Varsayım: UG-37'de t_r, UG-27 formülüyle kabuğun kaynak verimini kullanır (madde numarası teyit edilmeli). Düzeltme önerisi: `_host_required_thickness` içinde ev sahibinin kaynak kayıtlarını (`materials`/`welds`) geçirmek; onay gelene kadar uygulanmadı.
- **A (nozul) boş geçiş:** Kapandı. Gerçek bağımsız kontrol yapıldı ve B-07'yi yakaladı.
- **B (eliptik 9 uyuşmazlık) · TEST TANIMI HATASI, kod hatası değil:** Üretici `crown_depth = d_i/4` (yeni çap) veriyor; kod ise korozyonlu çapla `K = (2 + (D_c/2h)²)/6` hesaplıyor. Luna'nın bağımsız formülü K = 1 (2:1) varsayıyordu. API değeri %1.0–1.6 büyük (muhafazakâr yön) ve kod, girdideki sabit `h` ile tutarlı. Test tanımı düzeltilmeli.

## R. B-07 düzeltmesi (şef notu, 2026-10-17): olası YANLIŞ ALARM

B-07 (nozul takviyesinde ev sahibi `t_r`'nin E = 1 ile hesaplanması) hata olarak kaydedilmişti. Şefin yeniden değerlendirmesi: ASME VIII-1 UG-37(a), `t_r`'yi **dikişsiz** (seamless) kabuk/bombe için tanımlar; yani E = 1 almak Kod'un öngördüğü davranış olabilir ve kaynak verimi alan denklemlerinde ayrıca (E1 faktörü) devreye girer. Bu durumda API'nin 4065 mm² değeri doğru, benim 4720 mm² "bağımsız" hesabım yanlış olur.
**Karar:** B-07 düzeltmesi uygulanmaz. Durum "KAYNAK_BEKLİYOR (olası yanlış alarm)". Bağımsız doğrulama bir ajana atandı. Kod metninden paragraf kopyalanmaz; yalnız madde numarası ve formül sembolü kullanılır (K6).

## S. Sonnet ajanları A2 ve A4 sonuçları (2026-10-17) — şef çapraz kontrolüyle

- **B-07: YANLIŞ ALARM (güven orta-yüksek).** A2: nozulda API `A_required`, t_r'yi E = 1 ile hesaplayan varyantla 100/100 birebir uyuşuyor; kabuk verimini kullanan varyantla yalnız 22/100. A4: UG-37(a) t_r'yi dikişsiz kabuk için E = 1 ile tanımlar, kaynak verimi yalnız A1'deki E1 faktörüne girer. Kısıt: A4 birincil standart metnine erişemedi; kaynak PV Elite yardım arama özeti. Kapsam notu: `reinforcement.py:265` E1 = 1.0 sabit, açıklığın Kategori B dışı dikişten geçtiği durumda E1 < 1 uygulanmıyor (ayrı inceleme konusu).
- **G-01: YANLIŞ ALARM (güven orta).** 0.8D, UG-37(a)'da t_r seçim dairesinin tanımıdır; yerleşim yasağı değil. Daire dışında tam bombe t_r kullanılır; kod hep tam bombe t_r'yi kullanıyor (muhafazakâr).
- **B-03: UYARILI VARSAYILAN (güven yüksek).** Boş knuckle yarıçapı için 0.06·L varsayılıyor; K4 varsayımı ve uyarı thickness ve mawp sonuçlarında var. Sorun değil; F03 oracle beklentisi BLOCKED ise güncellenmeli.
- **Nozul `d` ve korozyon:** Aday kapandı. Kod `d = iç çap + 2·nozul_CA` hesaplıyor (`reinforcement.py:239`); taban tankta nozul CA = 0. A2'nin `d_corr` varyantı gövde CA'sını kullanmıştı (test tanımı hatası).
- **G-02 → B-10 · YÜKSEK · EMNİYETSİZ (yeni ürün bulgusu, şef doğruladı):** Statik kafa düzeltmesi ölü kod. `reference_elevation_mm` yalnız `result.py:69` içinde `0.0` varsayılanıyla tanımlı; `orchestrator.py:441` yalnız okuyor, hiçbir yerde atanmıyor. `if ref_elev > 0` koşulu hiç sağlanmıyor; MAWP hiçbir zaman statik kafa kadar düşürülmüyor. Sıvı yoğunluğu girilince de uyarı çıkmıyor (uyarı yalnız yoğunluk = 0 iken var). Hidrotestte de statik kafa yok (A4: 4 yeniden üretimde P_test sabit 2.22276 MPa). Düzeltme onay bekliyor.
- **A2 kırmızı bayrak açıklaması:** 300 satırın 221'inde ref ve api string'i birebir aynı; A2 nedenini kanıtladı (ref.csv api.csv'den 10 sn önce yazıldı; nozul V1 78 vakada farklı; 40 haneli Decimal yeniden hesabı). Bit uyumu iki tarafın aynı formülü kullandığını gösterir; formülün doğruluğunu ayrıca kanıtlamaz.

## T. B-01 ve B-02 düzeltildi (2026-10-17)

A1 (Sonnet) izole worktree'de düzeltti, şef diff'i okudu ve ana ağaçta test etti.
- **B-01 (MAWP):** `calculate_mawp` net cidarı `C_wall = CA_i + CA_o` ile kuruyor (shell, eliptik, torisferik, yarım küre, düz kapak, koni). Yarıçap/çap yalnız CA_i ile (çift sayım yok; tüm formüller C'yi yalnız `t = t_actual − C` için kullanıyor).
- **B-02 (nominal gereksinim):** `shell_required_nominal_thickness(C = CA_i + CA_o)` (shell, head, koni). `t_required` yalnız CA_i.
- **Koni notu:** Modelde `external_corrosion_allowance` alanı yok (yalnız ShellSection ve Head); koni için `getattr(..., 0.0)` kullanıldı. Koniye CA_o alanı eklemek ayrı karar.
- **Kanıt:** tam test paketi 938 geçti / 1 atlandı (önce 934 + 4 yeni regresyon testi). 1000 vakalık kütle koşusu: önce 641 SAPMA_CAO_MAWP + 359 UYUŞUR; sonra 1000 / 1000 UYUŞUR.
- **Kalan boşluk:** Düz kapak, torisferik, yarım küre ve koni MAWP dallarında CA_o>0 için bağımsız test yok (yalnız mevcut CA_o=0 testleri).

## U. A3 (Sonnet) Tur 2 onarımları (2026-10-17) — şef çapraz kontrolüyle

| Modül | Önce | Sonra | Kök neden |
|---|---|---|---|
| T01 metamorfik (240) | 120 GEÇTİ / 120 KAPSAM_DIŞI | 240 GEÇTİ | "120 düz kapak" aslında düz kapak + koni + nozul + dış basınç (4×30): düz kapakta `flat_attachment_factor=0.33` eksik (`geometry.py:121`), konide bombe sırası geçersiz, nozulda `A_required` adı yanlış, dış basınçta `P_allow` adı yanlış |
| T05 determinizm (20) | 20 BULGU | 20 GEÇTİ | Test hatası; fark yalnız permütasyonda çıktı sırası (weld satırları, uyarıdaki malzeme listesi). Gözlem (DÜŞÜK): çıktı sırası girdi sırasına bağlı |
| T07 rapor (20) | 20 BULGU | 18 GEÇTİ / 2 BULGU | 18'i test hatası (tüm ara değerleri bekliyordu, başlık sonuçlarına bakacak şekilde düzeltildi); 2'si gerçek ürün bulgusu (B-11) |
| T09 torisferik (60) | 60 KAPSAM_DIŞI | 60 GEÇTİ | `component_sequence` yalnız `[HEAD-L]` olduğu için API 422 dönüyordu; sıra düzeltildi, oracle ile sapma 0 |
| T14 etekli kolon (30) | 30 GEÇTİ | 30 | 30/30 vakada taban halkası sonucu yok (kapsam boşluğu G-05); `skirt_stress` hepsinde REVIEW REQUIRED |

- **B-03 yeniden değerlendirme (T09):** `knuckle_radius` boş, `custom` geometri → API sonucu `NOT CALCULATED` ("knuckle_radius zorunludur"); güvenli yönde engelleniyor. Eski "varsayılanla PASS" iddiası bu girdi için doğrulanmadı. (A4: standart geometride 0.06·L uyarılı varsayılan.)
- **B-11 · ORTA (yeni, şef doğruladı):** HTML rapor koni bileşenini içermiyor. `report-engine/src/report_engine/generator.py` içinde "cone" kelimesi hiç geçmiyor; yalnız shell ve head kalınlık bölümleri var (`_section_shell_calculations`, `_section_head_calculations`). Konili bir kapta koni kalınlığı (ör. C1, 5.17 mm) raporda görünmüyor. Düzeltme onay bekliyor.
- **Gözlem (belirsiz, bulgu değil):** `skirt_stress`, `leg_stress`, `flange_stress` gibi başlık sonuçları raporda sayısal görünmüyor; eksiklik mi ürün kararı mı belirsiz.
- **T01 boş doğrulama uyarısı:** A3'ün kendi notu: nozulun E ve nominal kalınlık ilişkileri sabit kalıyor; bu ilişkilerin "GEÇTİ"si etkisiz (monotonluk kontrolü bir şey ölçmüyor). T01'in 240 GEÇTİ'sinin tamamı eşit güçte kanıt değildir.
- A3'ün yazdığı çıktılar: her modülde `results_v3.json`; T05 ve T09 raporları modül içinde `rapor_v3.md` (yazma kısıtı nedeniyle).

## V. B-10 kısmen, B-11 tamamen düzeltildi (2026-10-17)

- **B-11 (rapora koni): DÜZELTİLDİ.** A6 (Sonnet), şef diff incelemesi ve ana ağaç testi. `report-engine/generator.py`: koni varsa "Koni Bölümleri" geometri tablosu ve "10A. Koni Hesapları" (kalınlık ve MAWP); BLOCKED/NOT CALCULATED durumu gizlenmiyor, sayı yoksa "—". Konisiz raporlar birebir aynı. +2 test. Commit `6611dc3`.
- **B-10 (statik kafa): KISMEN DÜZELTİLDİ (K4 uyumu).** A5 (Sonnet): modelde bileşen kotu / bileşen dibine bağlı sıvı seviyesi alanı yok (`DesignConditions` yalnız `fluid_density_kg_m3`; `load_cases.fluid_level_mm`/`elevation_mm` yük durumuna ait), bu yüzden alan UYDURULMADI. Yoğunluk > 0 iken referans kot yoksa her MAWP sonucuna açık varsayım satırı eklendi ("Statik kafa uygulanmadı ..."); sessiz atlama kalktı. MAWP sayıları değişmedi. `ref_elev > 0` dalı ve ρgh mantığı aynı; kot modele eklenirse çalışır. +3 test.
  **Kalan boşluk (karar gerekli):** Sıvı dolu işletmede ve hidrotestte alt bileşenler MAWP'den daha yüksek basınç görür; gerçek düzeltme için `DesignConditions` veya bileşene sıvı seviyesi (üst) ve bileşen taban kotu alanları eklenip `reference_elevation_mm` atanmalı. Domain değişikliği: onay bekliyor.
- **B-12 · ORTA-DÜŞÜK · GÜVENLİK (yeni, şef doğruladı):** `report-engine/generator.py` kullanıcı metinlerini (bileşen kimlikleri, proje adı, nozul etiketleri) HTML'e kaçışsız yazıyor; dosyada hiç `escape` yok (A6'nın yeni koni kodu aynı stili sürdürüyor). Rapor yalnız proje sahibine sunulduğundan etki sınırlı (self-XSS), ama kimlik/etiket STEP veya başka içe aktarmadan geliyorsa risk artar. Düzeltme önerisi: tüm kullanıcı kaynaklı alanlarda `html.escape`. Onay bekliyor.
- **Test durumu:** tam paket 943 geçti / 1 atlandı (önce 934 → 938 → 940 → 943).

## W. B-12 düzeltildi (2026-10-17)

A7 (Sonnet) izole worktree'de uyguladı; şef diff'i okudu, ana ağaçta tam paketi çalıştırdı ve gerçek API yolundan uçtan uca doğruladı.
- **Değişiklik:** `report-engine/generator.py` içine `_esc()` yardımcısı (`html.escape`, quote=True; enum için `.value`) ve yaklaşık 87 `_esc(` çağrısı: kapak, proje bilgisi, malzeme, geometri (gövde/bombe/koni), hesap tabloları, kaynak, MAWP, hidrotest, nozul etiketleri, uyarı/varsayım, `<title>` vb. `traceability.py` `to_html` değerleri de kaçırılıyor. Sayısal alanlar ve kodun kendi HTML'i kaçırılmıyor (çifte kaçış yok).
- **Test:** +3 test (düşmanca proje/müşteri/revizyon/gövde/bombe/nozul/malzeme/kaynak alanları; `&lt;script&gt;` ve `&quot;` var, ham `<script>` yok; normal projede `&amp;` yok). Tam paket 946 geçti / 1 atlandı.
- **Uçtan uca (şef):** `POST /api/projects` ile proje adı `<script>alert(1)</script>` ve müşteri `"><img src=x onerror=alert(2)>` → `GET /api/projects/{id}/report.html` 200, 20128 bayt; ham `<script>` ve `<img` yok, kaçışlı `&lt;script&gt;` var.
- **Kalan (B-12b, DÜŞÜK):** `compliance.to_html()` çıktısı (ESR matrisi, rapor bölüm 19) kendi HTML'ini üretiyor ve kapsam dışı kaldı; o modülde de kaçış gerekebilir. PDF/WeasyPrint yolu bu ortamda test edilemedi (skip). Domain doğrulamasının bu karakterleri girdi aşamasında engelleyip engellemediğine bakılmadı.
- **Test durumu:** 934 → 938 → 940 → 943 → 946 geçti.

## X. B-12b düzeltildi; `_esc` str-Enum hatası kapatıldı (2026-10-17)

- **B-12b:** A8 (Sonnet) `compliance` paketinde yeni `_html.py` (`esc()`) ve `esr_matrix.py`, `risk_analysis.py`, `declaration.py` içindeki `to_html` çıktılarında yaklaşık 40 kullanıcı kaynaklı alanı kaçırıyor (ESR matrisi, risk analizi, isim plakası, uygunluk beyanı). +5 test. Markdown çıktıları HTML olmadığı için dokunulmadı.
- **A8'in yan bulgusu (şef doğruladı): `report_engine/generator.py:_esc` str tabanlı enum'larda `.value` almıyordu** (`_esc(SE.A)` → `'SE.A'`). Koşul `hasattr(value,'value') and not isinstance(value,(str,int,float))` str-Enum'ları dışarıda bırakıyordu. Bu hata B-12 düzeltmesiyle (A7) girmişti ve şu anki rapor çağrı noktalarında sızıntı göstermiyor (denetlendi: `Sinif.UYE` deseni yok), ama gizli bir tuzaktı. `isinstance(value, Enum)` ile düzeltildi; +1 test.
- Test durumu: tam paket 952 geçti / 1 atlandı.

## Y. B-10 gerçek düzeltmesi (2026-10-17)

A9 (Sonnet) izole worktree'de uyguladı; şef diff'i okudu, savunmacı koruma ekledi, tam paket ve uçtan uca API ile doğruladı.
- **Alan:** `DesignConditions.liquid_level_mm: Optional[float]` (ge=0; datum = kabın en alt noktası) (`domain/conditions.py:78`).
- **Kot hesabı:** `calc_core/hydrostatics.py` `component_bottom_elevations()`: DİKEY kapta `component_sequence` (alttan üste) ile kümülatif (alt bombe ucu datum 0; sonraki bileşen taban kotu = önceki bileşenlerin uzunluğu; bombe = derinlik + düz flanş); YATAY kapta gövde ve bombeler datumda. Hesaplanamayan bileşende kot uydurulmaz, "statik kafa uygulanmadı" uyarısı kalır.
- **Orkestratör:** `_apply_static_head_correction` `reference_elevation_mm = max(0, seviye − taban kotu)` atıyor ve mevcut `MAWP − ρgh` yolu çalışıyor. Seviye taban kotunun altındaysa ayrı not. Seviye girilmemiş / yoğunluk 0 ise davranış birebir aynı.
- **Şef eklemesi:** `component_bottom_elevations` çağrısı `try/except (KeyError, TypeError, AttributeError, ValueError)` ile korundu (tutarsız `component_sequence` hesabı çökertmez); +1 test.
- **Uçtan uca kanıt (şef, API):** dikey kap, sıra HEAD-L → SHELL-01 → HEAD-R, ρ = 1000 kg/m³, seviye 3000 mm: HEAD-L MAWP 2.3327 → 2.3033 (Δ 0.02942 = ρ·g·3.0·1e-6 MPa), SHELL-01 2.3132 → 2.2866 (h 2710 mm), HEAD-R 1.7098 → 1.7029 (h 710 mm). Hepsi bağımsız formülle tutarlı.
- **Test:** +6 (A9) +1 (şef) test; `tests/wiring/test_ui_parity.py` içinde yeni alan için ARAYUZDE_YOK kaydı. Tam paket 959 geçti / 1 atlandı.
- **Açık riskler:**
  1. **Arayüzde `liquid_level_mm` alanı yok;** yalnız API/JSON ile girilir (`apps/web-ui`, `apps/api` bilerek değiştirilmedi).
  2. **Dikey kapta `component_sequence` boşsa kot hesaplanmaz** (kampanya taban tankı `vertical_leg_tank()` sıra içermiyor; bu durumda eski uyarı kalır). Sıra "alttan üste" varsayılıyor; ters girilirse kotlar ters çıkar.
  3. Hidrotest (UG-99) statik kafası hâlâ uygulanmıyor (uyarı metninde belirtildi).
  4. Yatay kapta koni için kot hesaplanmıyor (eksen kayması bilinmiyor).
