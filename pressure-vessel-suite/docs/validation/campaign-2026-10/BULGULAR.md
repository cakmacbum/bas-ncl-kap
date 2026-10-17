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
