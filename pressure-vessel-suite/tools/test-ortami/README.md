# Test ortamı — bağımsız hesap + site kıyası

Siteden bağımsız, tek sayfalık statik ekran. Proje JSON'unu (1) bağımsız motorla (`hesap.js`) adım adım
hesaplar, (2) aynı JSON'u yerel API'ye (`POST /api/calculate`) gönderip sonuçları yan yana kıyaslar.
Derleme yok, CDN yok, harici font yok.

## Çalıştırma (iki komut, `pressure-vessel-suite/` içinden)

```bash
# 1) API — ekranın origin'ine CORS izni ver (.env dosyasına dokunulmaz)
CORS_ORIGINS=http://127.0.0.1:4322,http://localhost:4322 python -m uvicorn apps.api.main:app --port 8000

# 2) Ekran
cd tools/test-ortami && python -m http.server 4322 --bind 127.0.0.1
```

Sonra <http://127.0.0.1:4322>. (`file://` ile açılmaz: ES modülleri HTTP ister.)
`.claude/launch.json` içinde `api` ve `test-ortami` girdileri bu iki işin karşılığıdır.

PowerShell'de env için: `$env:CORS_ORIGINS="http://127.0.0.1:4322,http://localhost:4322"`.
Not: `CORS_ORIGINS` verildiğinde API varsayılan 5173 (web-ui) izinlerini kullanmaz; web-ui ile birlikte
çalışacaksanız listeye `http://localhost:5173` de ekleyin (launch.json'daki değer ekler).

## Kullanım

- **Girdi:** örnek seç (`ornekler/`), JSON yapıştır ya da dosya yükle. Örnek seçince hesap hemen çalışır.
- **Hesapla:** bağımsız hesap anında; bileşen kartlarında Madde | Ad | Formül | Yerine konmuş | Sonuç.
- **Siteye sor:** aynı JSON'u API'ye yollar, tabloyu doldurur. API kapalıysa Türkçe hata mesajı çıkar.
- `hesap.js` yoksa ekran `hesap.stub.js`'e düşer ve üstte **MOTOR STUB** uyarısı çıkar (sonuçlar boş, kıyas `—`).

## Tolerans anlamı

`fark % = (bağımsız − site) / |site| × 100`. `|fark| ≤ ✅ eşiği` (varsayılan 0.5) → ✅,
`≤ ⚠️ eşiği` (varsayılan 2) → ⚠️, büyükse ❌. İki taraftan biri yoksa/hesaplanamadıysa `—`
(satır yine listelenir; sitenin `BLOCKED…` durumu "Site maddesi" sütununda görünür).

## Eşleme (düzeltme için `kiyas.js` başındaki tablolar)

| Büyüklük | Site payload'ı |
|---|---|
| t_gerekli | `calculation_type=thickness`, ara değer `t_required` |
| t_nominal_gerekli | `thickness`, ara değer `t_nominal_required` |
| MAWP (bileşen) | `mawp`, ara değer `MAWP` |
| Global MAWP | `global_mawp_mpa` |
| Hidrotest | `hydrotest` (bileşensiz satır), ara değer `P_test` |
| Pnömatik | `pneumatic_test`, ara değer `P_test` |

## Kapsam dışı

Nozul/açıklık takviyesi, destekler, MDMT, kaynak doğrulama, EN 13445 ve rapor çıktıları bu ekranda
**yoktur**; yalnız gövde + bombe kalınlık/MAWP ve test basınçları (ASME VIII-1) kıyaslanır.
`ornekler/duz-kapak.json` `flat_attachment_factor: 0.33` taşır (yoksa site `BLOCKED MISSING INPUT` verir).
