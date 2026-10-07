# F04 — Yarım küre bombe, ASME VIII-1 UG-32(f)

## 1. Özet

35 varyant çalıştırıldı; `results.json`'da kalınlık ve MAWP için ayrı 70 satır var. Etiket dağılımı: DOĞRULANDI 34, SAPMA 34, KAPSAM_DIŞI 2. Bütün geçerli kalınlık satırları SAPMA; MAWP satırları bağımsız ters çözümle uyuştu. Geçersiz sıfır tasarım basıncı API tarafından reddedildi. FORMÜLASYON_FARKI, TEK_KAYNAK ve KAYNAK_BEKLİYOR satırı yok.

## 2. Oracle formülleri

- ASME VIII-1 UG-32(f), iç basınç altındaki hemisferik bombe: `t = P L / (2 S E − 0.2 P)`, `L=Di/2`; gerekli imalat kalınlığına iç korozyon payı eklenir. Buradaki yeniden hesapta etkin yarıçap `Di/2 + CA` kullanıldı.
- Aynı basınç bağıntısının cebirsel ters çözümü: `P = 2 S E (tnom−CA) / (L + 0.2 (tnom−CA))` (MAWP). Oracle kodu aile klasöründeki `oracle.py` içindedir.
- Bu denklem ince cidar biçimidir. `t > L/2` kalın cidar durumlarında UG-32(f) bu bağıntıyı geçerli kılmaz; App. 1-3 ayrıca incelenmelidir. Bu paket için kalın cidar vakası sayısal hükme dahil edilse de oracle SAPMA gösterebilir.

## 3. SAPMA tablosu

Kalınlık sonuçlarının tamamında suite değeri oracle'dan yüksek (gerekli kalınlık bakımından daha emniyetli yönde); farklar %14.29. MAWP sonuçlarında sapma yok. Ham değerler, girişler ve farklar `../../../tools/campaign/families/f04_bombe_yarimkure/results.json` içindedir. Gözlenen farkın olası nedeni: tahmin — kalınlık hesabının MAWP'den farklı etkin kaynak verimi kullanması; MAWP uyuştuğundan bu ayrım dikkat çekicidir. Kod implementasyonu temiz oda nedeniyle incelenmedi.

| Örnek case | Girdiler | Suite t | Oracle t | Fark | Yön |
|---|---|---:|---:|---:|---|
| grid-D300-P0.1 | D=300 mm, P=0.1 MPa, CA=0 | 0.062116 mm | 0.054352 mm | +14.29% | Daha kalın / emniyetli |
| grid-D300-P20 | D=300 mm, P=20 MPa, CA=0 | 12.604 mm | 11.029 mm | +14.29% | Daha kalın / emniyetli |
| pressure-10 | D=1500 mm, P=10 MPa, CA=0 | 31.283 mm | 27.372 mm | +14.29% | Daha kalın / emniyetli |

Not: Paket kapsamı App. 1-3'ü işaret ediyor fakat App. 1-3 bağımsız kalın cidar denklemi için doğrulanmış kaynak/uygulama verilmedi. Kalın cidar case'i bu nedenle kesin kod doğrulaması sayılmaz; ince cidar eşitlikleriyle kıyaslama sınırlıdır.

## 4. Yayınlanmış vakalar

K1-12 ve K1-13 (Pressure Vessel Engineering Ltd., *Propane/Butane Sphere*, PVEcalc-4225-0-1 Rev 0, 6 Ağu 2010, s. 4 ve 8) küresel segmentleri kapsar; tam yarım küre bombeye ait yayınlanmış vaka değildir. K1-12: `P=157.165 psi`, `L=360.03 in`, `S=21,400 psi`, `E=1`, `CA=0.03 in`, yayımlanan `t=1.353 in`, `Pmax=172.2 psi`. K1-13: `P=169.578 psi`, aynı küre/malzeme, yayımlanan `t=1.458 in`, `Pmax=169.9 psi`. Kaynak vakalar, küre segmentlerini temsil ettikleri açık notuyla `K1-12-spherical-segment` ve `K1-13-spherical-segment` case_id'leriyle sonuç dosyasına eklendi; ref_source alanı PVEcalc raporuna atıf yapar. Kaynakta belirtilen bağıntı aynı UG-32(f) basınç yasasıdır. Aile için bağımsız yayınlanmış tam yarım küre örneği yok (K1 kaynak taraması).

## 5. Kapsam dışı ve bloklanan vakalar

`invalid-zero-pressure`: API HTTP isteğini `design_pressure > 0` doğrulamasında reddetti; suite hesabı oluşmadı ve iki büyüklük KAPSAM_DIŞI olarak kaydedildi. Sapma değerlendirmesinde kalın cidar case'leri UG-32(f) formülünün geçerlilik aralığı dışındadır; App. 1-3 için bağımsız sayısal oracle bulunmadığı için bu vakaların yorumu açık kalır.

## 6. Temiz oda beyanı

Yasaklı kod/standart paketleri okunmadı. Suite sonucu yalnızca harness'in API yanıtından alındı. Oracle sıfırdan yazılmış UG-32(f) eşitliği ve cebirsel ters çözümüdür. Domain modelleri, kampanya harness'i ve izin verilen yayınlanmış kaynak dokümanı okundu.
