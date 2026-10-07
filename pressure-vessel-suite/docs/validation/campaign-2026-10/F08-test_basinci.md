# F08 — Hidrostatik UG-99(b) ve pnömatik UG-100

## 1. Özet

33 sonuç satırı: **DOĞRULANDI 30**, **FORMÜLASYON_FARKI 0**, **SAPMA 0**, **TEK_KAYNAK 1**, **KAYNAK_BEKLİYOR 0**, **KAPSAM_DIŞI 2**. 16 normal, bir eksik test gerilmesi (REVIEW REQUIRED olarak sayı üretir) ve bir geçersiz PS girdisi; hidrostatik ve pnömatik sonuçlar ayrı satırdır.

## 2. Oracle formülleri

- ASME VIII-1 UG-99(b): hidrostatik test basıncı = `1.3 × MAWP × LSR`.
- ASME VIII-1 UG-100: pnömatik test basıncı = `1.1 × MAWP × LSR`.
- LSR, basınç taşıyan tüm bileşenler için `S_test / S_design` oranlarının en küçüğüdür.
- Statik kafa varsa ölçüm kotuna göre yerel basınç etkilenir; dikey tank test basıncı gauge satırı bu kampanyada karşılaştırılmıştır.

## 3. SAPMA tablosu

SAPMA veya FORMÜLASYON_FARKI çıkmadı. Uygun sonuçların tamamında API test basıncı, API satırındaki MAWP tabanı ve oran kullanılarak temiz odada yeniden çarpıldı; fark %0. Bu bir çarpan regresyon kontrolüdür, MAWP/LSR girdilerinin uçtan uca bağımsız doğrulaması değildir.

| Kapsam | Kontrol | Bulgular |
|---|---|---|
| R10–R16, D0/D1000 | `hydrotest` ve `pneumatic_test` | 28 satır; her iki çarpan API’nin MAWP ve oran ara değerlerine uygulandı; %0 fark |
| K1-14 | UG-99(b), MAWP 157 psig, LSR 1 | Bağımsız oracle 204.1 psig; yayımlanmış yazılım sonucu yukarı yuvarlanmış 205 psig |

Yayımlanmış vaka suite çağrısına dönüştürülmedi: kaynak, ayrı basınç kabı geometrisini/komple malzeme verisini içeriyor, yalnız test hesabı girdilerini veriyor. Bu nedenle K1-14 `TEK_KAYNAK` olarak tutuldu.

## 4. Yayınlanmış vakalar

| case_id | Kaynak | Girdiler | Yayımlanmış değer | Bağımsız hesap |
|---|---|---|---:|---:|
| K1-14 | Codeware COMPRESS Demo Vessel, 2022, s.13; `sources-K1.md` | UG-99(b), nameplate MAWP 157 psig, LSR 1.000 | 205 psig (yazılım tam sayıya yukarı yuvarlıyor) | 204.1 psig |

## 5. Kapsam dışı ve bloklanan vakalar

| case_id | Sonuç | Neden |
|---|---|---|
| INVALID-ZERO-PS/hydrotest ve pneumatic_test | KAPSAM_DIŞI | PS sıfır; domain `gt=0` doğrulaması isteği reddetti/sonuç üretmedi. |

Eksik test gerilmesi vakasının iki sonucu `REVIEW REQUIRED` durumunda sayısal üretildi ve normal kıyaslandı; bu, harness sözleşmesine uygundur.

Not: `fluid_density_kg_m3` tasarım koşulu alanı dikey tankta API gauge test basıncını değiştirmedi; yerel kafa ölçüm kotu varyantı bu giriş üzerinden temsil edilemiyor. LSR 1.0–1.6 aralığı, sıcaklık oranı alanında örneklendi. `results.json`’daki 30 doğrulama satırında oracle, suite’in `pressure_basis` ve `ratio` ara değerlerini yeniden kullanıyor; bu yüzden toplam MAWP zinciri bağımsız doğrulanmış sayılmaz. Bağımsız MAWP bileşen oracle’ı ve pnömatik yayınlanmış kaynak açık kalıyor.

## 6. Temiz oda beyanı

Oracle yalnızca UG-99(b)/UG-100 çarpımlarını ve K1-14’ün `1.3 × 157` aritmetiğini uygular. Suite sonucu yalnız harness’in API çıktısından alınmıştır. Temiz oda kuralına uyuldu: yasaklanan paketlerden hiçbir dosya okunmadı.
