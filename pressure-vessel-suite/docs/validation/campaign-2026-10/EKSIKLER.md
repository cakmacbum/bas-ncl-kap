# M2 kampanyası — açık eksikler (2026-10-17)

Bu dosya, hedefin kapanmasını engelleyen tüm açık maddeleri toplar. Her madde kapandığında
"Durum" sütunu güncellenir.

## A. Ürün / hesap bulguları

| ID | Önem | Eksik | Durum |
|---|---|---|---|
| B-01 | YÜKSEK, emniyetsiz | Gövde MAWP'de dış korozyon payı (CA_o) düşülmüyor (1000 vakada 641'i etkilenmiş) | DÜZELTİLDİ (A1+şef); 1000/1000 uyuşuyor, 938 test geçti |
| B-02 | YÜKSEK, emniyetsiz | Gövde/bombe/koni gerekli nominal kalınlık CA_o'yu kullanmıyordu | DÜZELTİLDİ (shell, head, koni); nozul/EN ayrı kontrol edilecek |
| B-03 | UYARILI VARSAYILAN | Boş knuckle için 0.06·L varsayılıyor; K4 uyarısı var | Sorun değil (A4, güven yüksek) |
| B-07 | YANLIŞ ALARM (A2+A4, güven orta-yüksek; birincil metin erişilemedi) | Nozul takviyesinde ev sahibi t_r E = 1 ile hesaplanıyor. UG-37(a) t_r'yi dikişsiz kabuk için tanımlıyorsa bu doğrudur; bağımsız doğrulama bir ajana atandı | Düzeltme uygulanmaz; doğrulama sonucu bekleniyor |
| B-04 | ORTA | MDMT coincident ratio alanı hesaba bağlı değil | Kod incelemesi; test yok |
| B-05 | DÜŞÜK | Vakum sonucu `external_pressure` adıyla dönüyor | Kod incelemesi |
| B-06 | ORTA | EN 13445 flanş, yük kombinasyonu, yorulma tetiklenemiyor | Kod incelemesi |
| B-08 | ORTA | Nozul yerleşim kontrolü sayısal çıktı vermiyor | Kod incelemesi |
| B-09 | ORTA | MDMT için bağımsız sayısal kıyas yok (UCS-66 telifli, K6) | Açık |
| G-01 | YANLIŞ ALARM | 0.8D, UG-37(a)'da t_r seçim dairesi; yerleşim yasağı değil | Kapandı (A4, güven orta) |
| B-10 | YÜKSEK, emniyetsiz | Statik kafa düzeltmesi ölü kod: `reference_elevation_mm` hiç atanmıyor; hidrotestte statik kafa yok | DÜZELTİLDİ (A5+A9): `liquid_level_mm` + geometriden kot; uçtan uca doğrulandı. Açık: arayüz alanı yok, dikeyde `component_sequence` gerekli, hidrotest statik kafası yok |
| G-03 | ORTA | Anlamsız girdi (ör. basınç 1e9) HTTP 200 PASS/FAIL dönüyor; bazı NaN'lar 500 veriyor | DÜZELTİLDİ: şemaya akıl sağlığı üst sınırları + inf/NaN reddi (422); `tests/regression/test_girdi_sinirlari_g03.py`. inf/NaN 500'ü yalnız test istemcisi JSON kodlayıcısından |
| G-04 | DÜŞÜK | Büyük harfli UUID kabul ediliyor (aynı sahibe normalleşiyor; sızıntı yok) | Bilgi |
| G-05 | ORTA | Etekli kolonda taban halkası sonucu API'de yok (T14) | Açık |
| G-06 | ORTA | Yatay tankta 216 saddle sonucu OUT OF SCOPE; kapsam belgelenmedi | Açık |
| B-11 | ORTA | HTML rapor koni bileşenini içermiyor | DÜZELTİLDİ (A6, `6611dc3`) |
| B-12 | ORTA-DÜŞÜK, güvenlik | Rapor HTML'i kullanıcı metinlerini kaçışsız yazıyordu | DÜZELTİLDİ (A7); uçtan uca doğrulandı. B-12b (`compliance.to_html`) DÜZELTİLDİ (A8) |
| D-03 | ORTA (altyapı) | Sahip başına 50 proje tavanı kampanyayı sessizce 429'a sokuyordu | Düzeltildi (harness uuid4 sahip) |
| D-04 | ORTA (altyapı) | T32 satır durumu hatalı birleştirilmişti | Düzeltildi (kontrollerden türetme) |

## B. Test ve sınıflandırma eksikleri

| ID | Eksik | Durum |
|---|---|---|
| T-01 | T01 120 KAPSAM_DIŞI (düz kapak, koni, nozul, dış basınç; 4 ayrı test hatası) | KAPANDI (A3): 240 GEÇTİ. Not: nozul E/nominal ilişkileri etkisiz (boş doğrulama) |
| T-02 | T11 saddle REVIEW/FAIL sonuçlarının sınıflandırma kuralı | Karar verildi (SAYISAL_İNCELEME / TASARIM_FAIL); benim sonuç dosyası tek kaynak |
| T-03 | T42 ve T50 (Luna) T11 sınıflandırmaları ana dala girmedi (çakışıyor, uyuşmuyor) | Karar: birleştirilmedi |
| T-04 | T04 fuzz: kontrol kuralları düzeltildi; nozul oranı ≥1 PASS | Düzeltildi; Haiku doğrulaması kopya çıktı (bağımsız değil) |
| T-05 | T40 (agregasyon), T45 (T09 torisferik) Luna çıktısı yok / boş | Açık |
| T-06 | R04 (yarım küre oracle'ı suite'e hizalandı) birleştirilmedi | Karar: kanıt sayılmaz |
| T-07 | T63 nozul kontrolü bağımsız değer yok ("UYUŞUR" boş geçiş) | Açık: Luna yeniden yazmalı |
| T-08 | T63 eliptik: 9 "uyuşmazlık" test tanımı hatası (crown_depth) | Açık: Luna yeniden yazmalı |
| T-09 | T05 determinizm ve T07 rapor: 20/20 BULGU | KAPANDI (A3): T05 20 GEÇTİ, T07 18 GEÇTİ + 2 gerçek bulgu (B-11) |
| T-10 | T09 torisferik ve T14 halka kapsamı | T09 KAPANDI (60 GEÇTİ). T14 halka sonucu API'de yok: kapsam boşluğu G-05 |

## C. Süreç (hedef kriterleri) eksikleri

| ID | Gereklilik | Durum |
|---|---|---|
| P-01 | Haiku'nun bağımsız doğrulaması | Kanıtlanmadı: t_hesap sütunları API değerinin kopyası (300 eliptik, 300 T04/üretim; 1000 gövde için şef yeniden hesabı var). Haiku'ya "API değerine bakmadan" kuralıyla yeniden iş verilmeli |
| P-02 | Luna'nın tam döngüsü (plan, yaz, koş, kendi kontrol) | T63 kendi kontrolünde hatalı; kabul edilmedi |
| P-03 | Opus'un yönetici rolü | Büyük ölçüde şef tarafından doğrudan yapıldı; kanıtlanmadı |
| P-04 | "Yüzlerce test": Luna + Haiku birlikte | Kısmen: 1000 gövde (Haiku doğrulama), 300 bombe (Luna), 300 üretim (Haiku), 300 T04 (Luna), 440 Tur 3, 240 T63, 240 T01; fakat tek bir birleşik Luna+Haiku döngüsü yok |
| P-05 | Hedef kararı | Kullanıcı kararı bekleniyor: B-07 onayı / bu haliyle kapat / yeni tur |

## D. Kullanıcı kararı bekleyenler

1. B-01/B-02/B-07 düzeltmelerinin onayı (kalkülasyon çekirdeği; DEC-005 gereği onaysız değişmez).
2. Hedefin kapatılması ya da yeni tur.

## E. Kapanış turu (2026-10-18, ikinci oturum)
- G-03 girdi üst sınırları: KAPANDI (`55df09b`).
- T-2.10 CA_o>0 bağımsız MAWP testleri (yarım küre, torisferik, düz kapak, koni): KAPANDI.
- Koni `external_corrosion_allowance` alanı eklendi (T-2.8 yarısı); hidrotest statik kafası hâlâ açık.
- T-07/T-08/P-02 (C1, Codex luna, `ork/C1`, birleştirildi): T63 yeniden yazıldı, referans API'den önce `ref.csv`'ye yazıldı. Eliptik 120/120 ve torisferik (T45) 60/60 UYUŞUR.
  Nozul 48/120 "UYUŞUR", 72 "UYUŞMUYOR" — **şef incelemesi:** 70'i oranı <1 olan gerçek TASARIM_FAIL'dir (uyuşmazlık değil; DEC-008 sınıflandırma hatası C1'de tekrarlandı),
  2'si (T63-A-027, A-104) referansın R'yi korozyonsuz alması: API/referans oranı tam (R+CA_i)/R (1.01163, 1.01747) → FORMÜLASYON_FARKI, suite doğru. Ürün hatası yok.
- B-04: `coincident_stress_ratio` girdisi bağlandı; UCS-66 azaltma eğrisi telifli (K6) olduğundan limite UYGULANMIYOR — açık uyarı verir. Otomatik oran hesabı yok.
- T-2.14: nozulda `opening_weld_joint_efficiency` alanı var (A1 = d·(E1·t − F·tr)); varsayılan E1=1 K4 uyarılı; domain'den dikiş-geçişi çıkarımı yok → kısmen açık.
