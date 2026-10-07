# F19 — EN 13445 / ASME VIII-1 çapraz kontrol

## 1. Özet

30 vaka API üzerinden çalıştırıldı. Yeni dağılım: **26 DOĞRULANDI, 0 FORMÜLASYON_FARKI, 0 SAPMA, 0 TEK_KAYNAK, 0 KAYNAK_BEKLİYOR, 4 KAPSAM_DIŞI**. Sayısal karşılaştırma 26 vakada yapılabildi; bunlar geçerli varyantların API `thickness` satırlarıdır. EN ve ASME için ayrı denklem oracle'ları, API'nin o satırda raporladığı yönetici girdilerle bağımsız hesaplandı. Bu, denklem tutarlılığı kontrolüdür; yayımlanmış kaynak doğrulaması sayılmaz.

## 2. Oracle formülleri

- EN 13445-3 7.4.2, silindirik gövde: `e = P·R/(f·z − 0.5P)` (R iç yarıçap, P/f MPa, sonuç mm).
- ASME VIII-1 UG-27(c)(1): `t = P·R/(S·E − 0.6P)`.
- ASME ve EN çıktıları kendi kodlarına ait gerekli kalınlık alanlarıyla karşılaştırıldı (`t_required` ve `e_required`). Katalog sözleşmesine göre sonuç `calculation_type=thickness`, bileşen `SHELL-01` satırından alındı.

## 3. SAPMA tablosu

SAPMA yok. Bu nedenle emniyetsiz/emniyetli yönü olan bir vaka bulunmuyor. 26 karşılaştırmanın farkları ve etiketleri `results.json` içindedir. Önceki turun büyük farkları, `e_required` alanının ASME'de aranması ve oracle'ın yanlış yarıçap/etkinlik girdisi kullanmasından kaynaklanıyordu; düzeltildi.

## 4. Yayınlanmış vakalar

Bu çalıştırmada K4-01, K4-04 veya K4-06 yayımlanmış girdi setleri API projesine aktarılmadı; kaynak tabloları bu raporda suite doğrulaması gibi sunulmuyor. K4-01/K4-04 silindirik EN karşılaştırması için, K4-06 yüksek basınç EN kalınlığı için uygun dayanaklardır. Dolayısıyla 26 DOĞRULANDI etiketi yayımlanmış vaka teyidi değil, varyantlar üzerinde bağımsız denklem/API alanı uyumunu gösterir.

## 5. Kapsam dışı / bloklanan vakalar

4 vaka `KAPSAM_DIŞI`: sıfır tasarım basınçlı iki varyant zorunlu pozitif basınç girdisini sağlamıyor; eksik akma/izin verilebilir dayanım girdili iki varyantta sayısal kıyas yok. API durum ve hata ayrıntıları vaka bazında `results.json` içinde tutulur. Geçerli sayı veren 26 vaka karşılaştırmaya dahil edildi.

## 6. Temiz oda beyanı

Oracle, yasaklı hesaplama implementasyonları okunmadan, paket kapsamındaki formül dayanaklarından bağımsız yazıldı. Sonuçlar yalnız public `run_case` API çıktısından; satırlar katalogdaki `thickness` tipi ve `e_required`/`t_required` alan adlarıyla seçildi. Katalog ve `examples.py` okundu; yasaklı paketlere dokunulmadı.
