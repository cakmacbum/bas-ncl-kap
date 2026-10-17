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

## F. Tur 2 (T01–T16, R02–R09) — koşuyor

Sonuçlar `docs/validation/campaign-2026-10/tur2/` altına gelecek; teyit edilen bulgular bu kayda eklenecek.
