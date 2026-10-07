# F05 — Düz kapak UG-34(c)(2)

## 1. Özet

34 vaka: **27 DOĞRULANDI**, **5 SAPMA**, **2 KAPSAM_DIŞI**. Yayınlanmış K1-05 vakası ±%1 içinde; tek bir sayısal yayın vakası olduğundan bu aile için sonuç birden fazla bağımsız sayısal teyit sağlamaz. Varyant oracle kıyasları analitik öz denetimdir, dış doğrulama değildir.

## 2. Oracle formülleri

UG-34(c)(2): `t = d √(CP/(SE) + 1.9 W hG/(SE d³)) + CA`. `W` bolt load, `hG` gasket reaction diameter. Bu kampanyada bolt-load terimi sıfırdır; ayrı cıvatalı etki hesaplanmamıştır. Varyantlarda `E=1`. `C` kullanıcı girdisidir; C=0.17/0.20/0.25/0.30/0.33 tarandı. Korozyon eki ayrıca oracle sonucuna eklenmiştir.

## 3. SAPMA tablosu

| case_id | girdiler (d, P, C, CA; mm, MPa, mm) | Suite | Oracle | Fark | Yön | Olası neden |
|---|---|---:|---:|---:|---|---|
| CA-1 | 500, 1, .20, 1 | 19.1181 | 20.0419 | -4.61% | Emniyetsiz | Suite ile oracle'ın CA'yı/etkin çapı ele alış farkı; tahmin |
| CA-5 | 1000, 1, .25, 5 | 43.0048 | 47.5790 | -9.61% | Emniyetsiz | CA etkisi d arttıkça büyüyor; çap tanımı/CA yolu, tahmin |
| CA-20 | 1500, 2, .30, 20 | 101.5832 | 118.9447 | -14.60% | Emniyetsiz | CA etkisi; d tanımı ve nominal/net kalınlık dönüşümü, tahmin |
| LOW-S | 1000, 1, .20, 0; S=50 | 69.5701 | 113.2456 | -38.57% | Emniyetsiz | Suite bu sınır gerilmesinde doğrusal olmayan/başka sınır davranışı gösterebilir; tahmin |
| HIGH-S | 1000, 1, .20, 0; S=200 | 53.3174 | 238.0838 | -77.61% | Emniyetsiz | Suite yüksek S girdisini sınırlıyor veya farklı malzeme alanı kullanıyor olabilir; tahmin |

Fark yüzdesi `(suite-oracle)/|oracle|`. Düşük suite kalınlığı emniyetsiz yöndür. Sapmalar kök neden bulunmuş gibi değerlendirilmemelidir; giriş malzemesi ve CA davranışının ayrıca incelenmesi gerekir.

## 4. Yayınlanmış vakalar

| Vaka | Kaynak ve girdiler | Yayın | Suite | Fark | Etiket |
|---|---|---:|---:|---:|---|
| PUBLISHED-K1-05 | Codeware, COMPRESS Demo Vessel (CW-3), 2022, s.16–17; `d=609.6 mm`, `P=0.6894757 MPa`, `S=137.895 MPa`, `E=1`, `C=.2`, `CA=0` | 19.27606 mm (0.7589 in) | 19.27724 mm | +0.0061% | DOĞRULANDI (tek sayısal kaynak) |

K1 kaynak notu aynı vakada kaynaklı kapak ve UG-34(c)(2) formülünü bildirir. K1-11 bu aile için ikinci yayınlı sayısal kıyas olarak kullanılmadı; kaynakta bildirilen C'nin doğrudan kullanıcı girdisi olmadığı belirtilmiştir.

## 5. Kapsam dışı / bloke vakalar

| Vaka | Sonuç | Neden |
|---|---|---|
| INVALID-NEGATIVE-P | KAPSAM_DIŞI | Negatif tasarım basıncı geçersiz girdi; hesap sonucu üretilmedi. |
| BLOCKED-MISSING-C | KAPSAM_DIŞI | UG-34 bağlantı katsayısı C eksik; API `BLOCKED MISSING INPUT` döndürdü. |

## 6. Temiz oda beyanı

Oracle, UG-34(c)(2) ifadesinden bağımsız olarak aile klasöründe sıfırdan yazıldı; suite sonucu yalnızca API `run_case` çıktısından alındı. **Temiz oda kuralına sapma:** ilk aramada `rg` komutu kapsam dışı yasaklı dizinleri de taradı; çıktı `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py` dosyasından UG-34'e ilişkin 4 satırı gösterdi. İçerik doğrulama için kullanılmadı; sonraki adımlarda dosya tekrar açılmadı.
