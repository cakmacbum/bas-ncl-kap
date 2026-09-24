# Kullanılmayan Kod ve Eksik Bağlantılar İncelemesi

İnceleme tarihi: 2026-09-24  
Kapsam: `pressure-vessel-suite` kaynak kodu, arayüz, testler ve ilgili kapsam dokümanları.

Bu not, kesin kullanılmayan yerel öğeleri, uygulama akışına bağlanmamış yardımcıları ve kasıtlı iskeletleri ayrı tutar. Burada listelenen her kod otomatik olarak silinmemelidir; özellikle hesap güvenliğiyle ilgili yardımcıların kaldırılması yerine üretim akışına bağlanması gerekebilir.

## Kesin kullanılmayan arayüz öğeleri

Web UI TypeScript derleyicisi `--noUnusedLocals --noUnusedParameters` seçenekleriyle çalıştırıldı. Toplam 12 kullanılmayan öğe raporlandı:

| Dosya | Bildirilen öğeler |
|---|---|
| `pressure-vessel-suite/apps/web-ui/src/livePreview.tsx` | `React` içe aktarımı (satır 8) |
| `pressure-vessel-suite/apps/web-ui/src/pages.tsx` | `StatusBadge`, `CALC_TYPE_TR`, `tr` içe aktarımları (satır 9, 14); kullanılmayan `index`/`i` callback parametreleri (satır 298, 312, 319, 434) |
| `pressure-vessel-suite/apps/web-ui/src/schematic.tsx` | `React` ve `NOZZLE_TYPE_TR` içe aktarımları (satır 1–2); `maxHD` ve `cX` yerel değişkenleri (satır 203, 217) |

Bunlar arayüzün derleme uyarılarını temizlemek için düşük riskli adaylardır. Silme/değişiklik yapılmadı.

## Üretim akışında çağrılmayan doğrulama yardımcısı

- `pressure-vessel-suite/packages/calc-core/src/calc_core/verification.py` içindeki `validate_suite()` hesap sonuçlarını bir bütün olarak doğruluyor ve `calc_core` paketinden dışa aktarılıyor.
- Depo aramasında uygulama akışında veya testlerde bir çağrısı bulunmadı; yalnızca tanımı, kendi içindeki `validate_result()` çağrısı ve dışa aktarımları var.
- Bu yardımcı boş kod değildir. Hesap sonuçlarını yayımlama/raporlama öncesinde doğrulama amacı varsa üretim hattına bağlanması değerlendirilmeli; kullanılmayacaksa API'den çıkarılması ayrıca kararlaştırılmalı.

## Kasıtlı iskeletler ve yedek yollar

- FEA adaptörü (`packages/fea/src/fea/fea_adapter.py`) gerçek bir sonlu eleman çözücü sonucu üretmiyor. Çözücü kurulu olsa bile `REVIEW_REQUIRED` veriyor; iskelet gerilme değerlerinin sıfır olması hesap sonucu olarak kullanılmamalı. Bu davranış dosyada açıkça belirtilmiş.
- EN 13445 nozul takviye metodu `NOT_CALCULATED` döndürüyor. Metot boş bırakılmış değil; kapsam eksiğini açıkça bildiriyor.
- CAD doğrulama kodundaki `pass` ifadeleri alternatif CadQuery/OCC nesne metotları denenirken hata yutma/yedekleme yolu olarak kullanılıyor. Revizyon servisindeki `pass`, isteğe bağlı CadQuery bağımlılığı yokken STEP üretimini atlıyor. Bunlar tek başına gereksiz kod sayılmadı.

## U profilden ayak ve ayak plakaları: mevcut durum

### U profilli ayak

- `packages/supports/src/supports/sections.py` içinde `channel_section(h, b, s, t)` U profil kesit özelliklerini hesaplıyor; kesit özelliği testleri de var.
- Buna karşın üretim destek hesaplayıcısında bu fonksiyona çağrı bulunamadı. Mevcut domain/UI alanları ayak dış çapı ve et kalınlığını alıyor; ayak hesabı boru/halka kesit alanı (`leg_pipe_section_area`) varsayıyor.
- UI'da U profil yüksekliği, flanş genişliği, gövde kalınlığı ve flanş kalınlığı gibi geometri girdileri bulunmuyor.
- Sonuç: U profil hesabı yardımcı bir matematik fonksiyonu olarak mevcut, ancak kullanıcı tarafından seçilebilir ve üretim hesabında kullanılabilir U profilli ayak özelliği eklenmiş değil.

### Ayak taban plakası ve kaba bağlantı pedi

- UI ve `Support` domain modeli ayak başına yalnızca `base_plate_area_mm2` alanını alıyor. Üretim destek hesabı bu alanı taban basıncında kullanabiliyor; alan verilmezse boru ayağının kesit alanına geri dönüyor.
- `base_plate_bearing_pressure`, `base_plate_cantilevers` ve `base_plate_required_thickness` yardımcıları `supports/formulas.py` içinde mevcut ve birim testleri var. Arama sonuçlarında bu üç fonksiyonun üretim destek hesaplayıcısından çağrısı görünmedi.
- Plaka boyu/en, ankrajların plaka üzerindeki konumu ve plaka kalınlığı üzerinden tamamlanmış taban plakası boyutlandırma akışı bulunamadı.
- Ayak ile basınçlı kap kabuğu arasındaki takviye/bağlantı pedine ait ayrı domain girdisi veya tamamlanmış hesap akışı bulunamadı. Kaynakta U profil flanş uçlarının pede kaynağından söz eden tekil bir açıklama, bu özelliğin uygulandığını göstermiyor.
- Sonuç: basınçlı kap ayağı için tam bağlantı pedi/ayak pabucu tasarımı eklenmiş değil. Mevcut taban plaka desteği alan girdisi ve basınç kontrolü seviyesinde sınırlı.

## Dokümantasyon tutarlılığı

- `docs/limitations.md` ve `docs/audit-verification-2026-09-20.md` içindeki destek hesap hattı/alan eşleşmesiyle ilgili bazı notlar farklı tarihlerdeki durumları anlatıyor. Bunlar kaynak kodda kullanılmayan öğe değildir; güncel kodla karşılaştırılıp dokümanların tek bir güncel duruma getirilmesi gerekir.

## Denetim sınırları

- Python, Ruff, Vulture ve Pyflakes bu ortamda kullanılabilir olmadığından Python sembolleri için otomatik ölü kod taraması yapılamadı. Python bulguları depo çapında metin araması ve kaynak incelemesiyle sınırlıdır; dinamik içe aktarma/yansıma ihtimali nedeniyle referanssız her Python sembolü kesin ölü kod sayılmamalıdır.
- TypeScript denetimi kaynak dosyaları değiştirmeden yapıldı. Bu not eklenirken kod değişikliği veya test çalıştırması yapılmadı.
