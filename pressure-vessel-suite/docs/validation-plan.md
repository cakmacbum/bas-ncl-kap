# Validation Plan

> Bu doküman, yazılımın doğrulama stratejisini tanımlar. Her faz kendi test katmanını ekler.

## Genel prensip

Kaynak §17: **"Bu yazılımın en önemli kısmı kod değil, doğrulamadır."**

## Test katmanları

### 1. Birim testleri (Unit)

Her paket kendi birim testlerini içerir (`tests/unit/`):

| Alan | Kapsam |
|---|---|
| Basınç birimi dönüşümleri | bar ↔ MPa ↔ psi, tolerans |
| Sıcaklık dönüşümleri | °C ↔ K ↔ °F |
| Uzunluk dönüşümleri | mm ↔ in |
| Geometrik alan/hacim | Silindir, bombe hacimleri |
| İnterpolasyon | Malzeme gerilmesi sıcaklık interpolasyonu |
| Yuvarlama | Standart kuralına göre yuvarlama |

### 2. Golden-case testleri

Her standart maddesi için:

- Known input
- Expected intermediate values
- Expected final result
- Allowed numerical tolerance (±)
- Source and edition
- Independent reviewer (varsa)

Konum: `tests/golden-cases/`

### 3. Regresyon testleri

Yeni kod değişikliğinden sonra eski onaylı projelerin sonuçları değişiyor mu?

Konum: `tests/regression/`

### 4. Geometrik testler (Faz 2+)

- STEP açılıyor mu?
- Solid geçerli mi?
- Hacim doğru mu?
- Nozul konumu doğru mu?
- Nozul deliği açılmış mı?
- Modelde çakışma var mı?

Konum: `tests/cad-validation/`

### 5. Rapor snapshot testleri (Faz 2+)

PDF/HTML raporun beklenen yapısıyla uyumu.

Konum: `tests/report-snapshots/`

## Bağımsız hesap doğrulaması

En kritik hesaplar iki farklı şekilde doğrulanmalıdır:

1. Python hesap motoru
2. Bağımsız Excel/Mathcad veya el hesabı

Her ikisinin aynı kodu paylaşmaması gerekir.

## Uzman incelemesi

Üretimde kullanılmadan önce:

- Basınçlı kap tasarım mühendisi
- Kaynak mühendisi
- NDT uzmanı
- PED/CE uzmanı
- Gerekiyorsa onaylanmış kuruluş

tarafından kapsam ve örnek hesaplar incelenmelidir.

## Formül Doğrulama Kayıtları

Aşağıdaki formüller ASME BPVC Section VIII Division 1 (2025 Edition) ile karşılaştırılarak doğrulanmıştır.

| Formül | Madde | Durum | Tarih | Kaynak |
|---|---|---|---|---|
| Çevresel gerilme: t = PR/(SE - 0.6P) | UG-27(c)(1) Eq. (1) | Doğrulandı | 2026-07-23 | ASME BPVC VIII-1 (2025) |
| Boyuna gerilme: t = PR/(2SE + 0.4P) | UG-27(c)(1) Eq. (2) | Doğrulandı | 2026-07-23 | ASME BPVC VIII-1 (2025) |
| 2:1 Elipsoidal: t = PD/(2SE - 0.2P) | UG-32(d) | Doğrulandı | 2026-07-23 | ASME BPVC VIII-1 (2025) |
| Torisferik: M = (3+sqrt(L/r))/4, t = PLM/(2SE - 0.2P) | UG-32(e) | Doğrulandı | 2026-07-23 | ASME BPVC VIII-1 (2025) |
| Yarım küresel: t = PR/(2SE - 0.2P) | UG-32(f) | Doğrulandı | 2026-07-23 | ASME BPVC VIII-1 (2025) |
| Hidrotest: P_test = 1.3 × P_design × (S_test/S_design) | UG-99(b) | Doğrulandı | 2026-07-23 | ASME BPVC VIII-1 (2025) |

Doğrulama yöntemi: Her formülün matematiksel ifadesi ASME metniyle birebir karşılaştırılmış, ardından bağımsız web kaynaklarıyla teyit edilmiştir. Golden-case testleri (`tests/golden_cases/test_asme_golden.py`) her formül için sayısal sonuç doğrulaması içerir.

Bağımsız gözden geçiren: Henüz atanmadı — üretim öncesi uzman incelemesi gerekir.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 1.1 (formül doğrulama kayıtları eklendi: 2026-07-23)*
