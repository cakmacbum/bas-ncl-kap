# Bağımsız Doğrulama — Kaynak Politikası

Bu klasör, suite'in hesap sonuçlarının **başkaları tarafından yayımlanmış** sonuçlarla
karşılaştırmasını tutar.

## Neden var

`tests/golden_cases/test_asme_golden.py` içindeki beklenen değerlerin tamamı suite'i yazan
kişi tarafından üretildi. Bir formül baştan yanlış yazıldıysa o testlerin hepsi yeşil kalır —
hata ancak imal edilmiş bir kapta ortaya çıkar. Bu klasör o döngüyü kırar: sayılar dışarıdan
gelir.

Bu, `docs/validation-plan.md`'deki "Bağımsız hesap doğrulaması" katmanının uygulamasıdır ve
oradaki uzman incelemesinin **yerine geçmez** — onu hazırlar.

## Kaynak kademeleri

| Kademe | Tanım | Bağımsızlık gerekçesi |
|---|---|---|
| **K-A** | Gerçek projede kullanılmış, yayımlanmış hesap seti (ticari yazılım çıktısı, mühendis imzalı) | Farklı ekip, farklı yazılım, ticari sonuç sorumluluğu altında üretilmiş |
| **K-B** | Bağımsız üçüncü taraf hesaplayıcı | Ayrı bir implementasyon; ama yine "birinin kodu" |
| **K-C** | Ders kitabı / hakemli yayın çözümlü örneği | Editoryal inceleme geçmiş |

## Kabul kuralı

Bir **formül** doğrulanmış sayılmak için:

1. Suite'in sonucu, yayınlanmış sonuçtan **±%1** içinde olmalı, **ve**
2. Aynı formül **en az iki bağımsız uygulamadan** ya da **en az iki ayrı sayısal vakadan**
   teyit edilmeli.

Tek kaynak/tek vaka varsa satır `TEK_KAYNAK` etiketlenir ve **doğrulanmış sayılmaz** —
K4: eksiklik gizlenmez.

Sonuç etiketleri:

| Etiket | Anlamı |
|---|---|
| `DOĞRULANDI` | ±%1 içinde, ≥2 bağımsız teyit |
| `FORMÜLASYON_FARKI` | Kaynak, Kod'un **başka bir geçerli alternatifini** kullanmış (ör. dış çap formu). Hata değil; fark ve sebebi kayıtlı |
| `SAPMA` | Gerçek uyuşmazlık → kök neden bulunur, düzeltilir, ayrı commit |
| `TEK_KAYNAK` | Tek teyit var, kural sağlanmadı |
| `KAYNAK_BEKLİYOR` | Uygun yayınlanmış vaka henüz bulunamadı |

## Telif (K6)

Kaynak dosyaları `docs/validation/sources/` altına iner ve **`.gitignore`'dadır**. Depoya
yalnızca şunlar girer: yayın künyesi, URL, erişim tarihi, girdi değerleri ve **sayısal sonuç**.
Standart metni, tablo veya sayfa görüntüsü kopyalanmaz.

## İçerik

- [`asme-worked-examples.md`](asme-worked-examples.md) — ASME VIII-1 karşılaştırma kayıtları
- `tests/golden_cases/test_published_examples.py` — aynı vakaların çalıştırılabilir hâli
