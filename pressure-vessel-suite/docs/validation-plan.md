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

**Doğrulama tipi** sütununun anlamı:

- `sembolik` — formülün matematiksel ifadesi ASME metniyle karşılaştırıldı. Beklenen sayısal
  değerleri suite'i yazan kişi üretti; formül baştan yanlışsa testler yine yeşil kalır.
- `sayısal-bağımsız` — sonuç, **başkasının yayımladığı** hesapla karşılaştırıldı. Ayrıntı:
  [`validation/asme-worked-examples.md`](validation/asme-worked-examples.md).

| Formül | Madde | Doğrulama tipi | Kaynak | Durum | Tarih |
|---|---|---|---|---|---|
| Çevresel gerilme: t = PR/(SE - 0.6P) | UG-27(c)(1) Eq. (1) | **sayısal-bağımsız** | 2 | Doğrulandı | 2026-07-26 |
| Boyuna gerilme: t = PR/(2SE + 0.4P) | UG-27(c)(1) Eq. (2) | **sayısal-bağımsız** | 2 | Doğrulandı | 2026-07-26 |
| 2:1 Elipsoidal: t = PD/(2SE - 0.2P) | UG-32(d) | **sayısal-bağımsız** | 3 | Doğrulandı — iç çap formunu kullanan kaynakla birebir (%0.03); dış çap alternatifini kullanan kaynaklardan %0.4-0.9 ince (limitations B-03) | 2026-07-26 |
| MAWP, silindirik gövde | UG-27 | **sayısal-bağımsız** | 1 | Doğrulandı | 2026-07-26 |
| MAWP, 2:1 elipsoidal bombe | UG-32(d) | **sayısal-bağımsız** | 1 | Doğrulandı | 2026-07-26 |
| Hidrotest: P_test = 1.3 × **MAWP** × (S_test/S_design) | UG-99(b) | **sayısal-bağımsız** | 2 | 🔴 **SAPMA bulundu ve düzeltildi** — taban tasarım basıncıydı, %42.9 düşük test basıncı üretiyordu | 2026-07-26 |
| Pnömatik: P_test = 1.1 × **MAWP** × (S_test/S_design) | UG-100 | **sayısal-bağımsız** | 1 | 🔴 Aynı sapma, aynı düzeltme | 2026-07-26 |
| Torisferik: M = (3+sqrt(L/r))/4, t = PLM/(2SE - 0.2P) | UG-32(e) | **sayısal-bağımsız** | 1 (90 nokta) | Doğrulandı — anma tablosunun tamamı, tipik %0.03-0.05 | 2026-07-26 |
| Torisferik varsayılan büküm yarıçapı | UG-32(e) | **sayısal-bağımsız** | 1 | 🔴 **SAPMA bulundu ve düzeltildi** — varsayılan D/10 idi, standart ASME F&D %6; %13 ince bombe üretiyordu | 2026-07-26 |
| Yarım küresel: t = PR/(2SE - 0.2P) | UG-32(f) | **sayısal-bağımsız** | 1 | Doğrulandı | 2026-07-26 |
| Nozul takviye alanları A1-A5 + UG-40 sınırları | UG-37(c) / UG-40 | **sayısal-bağımsız** | 1 (5 ara değer) | 🔴 **5 SAPMA bulundu ve düzeltildi** — toplam alan %85 eksikti, karar ters çıkıyordu; ped UG-40 sınırıyla kırpılmıyordu (emniyetsiz) | 2026-07-26 |
| Korozyonlu iç ölçü (gövde/bombe/koni, ASME+EN) | UG-27 / UG-32 | **sayısal-bağımsız + iç tutarlılık** | 1 | 🔴 **SAPMA — yön tersti** (`R−C` yerine `R+C`); üretilen kalınlık kendi MAWP'sini karşılamıyordu | 2026-07-26 |
| Düz kapak korozyon payı | UG-34(c)(2) | iç tutarlılık | — | 🔴 SAPMA — çifte sayım (%5-25 fazla kalınlık, emniyetli yön) | 2026-07-26 |
| Bombe dış basınç çapı | UG-33 | iç tutarlılık | — | 🔴 SAPMA — iç çap kullanılıyordu (%2-30 şişme, emniyetsiz) | 2026-07-26 |
| Koni MAWP | UG-32(g) | uçtan uca test | — | 🔴 SAPMA — hiç hesaplanmıyordu, global MAWP'e katılmıyordu | 2026-07-26 |

**Sayısal-bağımsız yöntem:** İki ayrı ticari yazılımın (PV Elite 2017 · Advanced Pressure
Vessel 10.1.5) yayımlanmış hesap setlerinden girdi ve sonuçlar alındı, suite aynı girdilerle
çalıştırıldı, %1 toleransla karşılaştırıldı. Çalıştırılabilir hâli:
`tests/golden_cases/test_published_examples.py`.

**Sembolik yöntem:** Formülün matematiksel ifadesi ASME metniyle birebir karşılaştırılmış,
bağımsız web kaynaklarıyla teyit edilmiştir. `tests/golden_cases/test_asme_golden.py` sayısal
sonuç içerir ama beklenen değerler suite yazarına aittir.

Bağımsız gözden geçiren: Henüz atanmadı — üretim öncesi uzman incelemesi gerekir.
Sayısal-bağımsız doğrulama bunun **yerine geçmez**, hazırlar.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 1.2 (sayısal-bağımsız doğrulama, tur 1: 2026-07-26)*
