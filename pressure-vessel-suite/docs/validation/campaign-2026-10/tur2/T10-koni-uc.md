# T10 — Koni bağlantıları uç değerler

## Kapsam ve yöntem

35 public API vakası çalıştırıldı: α=5°–75° aralığı 5° adımlı, knuckle yarıçapı var/yok çiftleri; 30° eşiği; büyük/küçük uç beyanı ve uyumsuz uç çapı. Bağımsız beklenti yalnız girdi/topoloji zarfı içindir. Bu kampanyada App 1-5/1-8 sayısal takviye gereksinimi oracle'ı kurulmamıştır; böyle bir yeterlilik karşılaştırması kapsam dışıdır.

## Dağılım

- Toplam: 35
- GEÇTİ: 35 (23 OUT OF SCOPE, 12 BLOCKED MISSING INPUT)
- BULGU: 0
- KAPSAM_DIŞI: 0 (vakaların girdileri kapsam içidir; numeric Appendix 1-5/1-8 iddiası kapsam dışıdır.)

## Bulgu tablosu

Bulgu yok.

## Gözlemler

- α≤30° ve tutarlı büyük uç bağlantısı: geometri/topoloji kaydı oluşuyor, sayısal koni ucu yeterliliği OUT OF SCOPE.
- α>30° ve knuckle yok: BLOCKED uyarısı/girdisi beklenen davranışla tutarlı.
- α>30° ve knuckle_radius_mm mevcut: vaka engelden çıkıyor, ancak sonuç sayısal yeterlilik değil OUT OF SCOPE; yarıçapın tasarım yeterliliği doğrulanmıyor.
- Küçük uç bu projede 800 mm başlığa bağlanmadığı için BLOCKED; büyük uca ait hatalı çap beyanı da BLOCKED.
- Büyük/küçük uç takviye ihtiyacı ve App 1-8 koşulları sayısal olarak değerlendirilemedi.

## Kapsam dışı listesi

- App 1-5/1-8 gereği küçük ve büyük uç takviye alanı/kalınlığı gereksinimleri: API sonucu sayısal yeterlilik üretmediğinden kıyaslanamadı.
- Küçük uca geçerli bağlantı varyantı: fixture geometrisi yalnız büyük uçtaki kabuğa tutarlı bağlanıyor.
- Knuckle yarıçapının standarda göre kabul edilebilirliği: yalnız giriş alanı mevcutluğu gözlendi.

SONUÇ: vaka=35 · geçti=35 · bulgu=0 (kritik=0, emniyetsiz=0) · kapsam_dışı=0
