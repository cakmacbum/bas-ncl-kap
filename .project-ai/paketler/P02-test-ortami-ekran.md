# P02 test-ortami ekran + kıyas

Mod: yaz
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

## Amaç
Sitenin basınçlı kap hesaplarını doğrulamak için **siteden bağımsız**, yerelde açılan tek sayfalık test
ekranı. Ekran bağımsız motoru (`hesap.js`, başka paket yazıyor) çağırıp hesabı adım adım gösterir, aynı
proje JSON'unu yerel API'ye gönderip sonuçları yan yana kıyaslar.

## Kapsam — yalnız bu dosyaları yaz
- `pressure-vessel-suite/tools/test-ortami/index.html`
- `pressure-vessel-suite/tools/test-ortami/kiyas.js`
- `pressure-vessel-suite/tools/test-ortami/stil.css`
- `pressure-vessel-suite/tools/test-ortami/ornekler/` (4 JSON: `elips.json`, `torisferik.json`, `yarim-kure.json`, `duz-kapak.json`)
- `pressure-vessel-suite/tools/test-ortami/README.md`
- `.claude/launch.json` (BASINCLI-KAP kökünde) — yalnız ekleme/env, mevcut girdileri bozma

**Dokunma:** `hesap.js`, `hesap.test.mjs` (başka paket), `packages/`, `apps/`, `.env`.
Geliştirirken `hesap.js` yoksa aynı imzalı geçici `hesap.stub.js` yazabilirsin; `index.html` önce
`./hesap.js`'i dener, yüklenemezse stub'a düşer ve ekranda "MOTOR STUB" uyarısı gösterir.

## Sözleşme (değiştirme)
```js
// hesap.js (başka paket) — index.html bunu import eder
export function hesaplaProje(project) → {
  bilesenler: [{ id, tip:'shell'|'head', alt_tip, adimlar: Adim[], t_gerekli_mm, t_nominal_gerekli_mm,
                 mawp_mpa, durum:'PASS'|'FAIL'|'HESAPLANMADI', notlar:string[] }],
  global_mawp: { deger_mpa, yoneten_id, adimlar: Adim[] },
  hidrotest:  { deger_mpa, adimlar: Adim[] },
  pnomatik:   { deger_mpa, adimlar: Adim[] },
  varsayimlar: string[]
}
// Adim = { ad, madde, formul, yerine, deger, birim }

// kiyas.js (SEN yazıyorsun)
export async function siteSonucu(project, apiUrl='http://127.0.0.1:8000') → payload
//   POST {apiUrl}/api/calculate, body = project JSON, header Content-Type: application/json ve
//   X-Client-Id: localStorage'da tutulan rastgele uuid (try/catch; yoksa her seferinde yeni).
//   Hata/ağ yoksa anlaşılır Türkçe mesajlı Error fırlat ("API çalışmıyor: localhost:8000 açık mı?").
export function karsilastir(bagimsiz, payload, tol={ok:0.5, uyari:2}) → Satir[]
// Satir = { bilesen, buyukluk, bagimsiz, site, fark_yuzde, isaret:'✅'|'⚠️'|'❌'|'—', site_madde }
```
Site payload şekli: `{ global_mawp_mpa, results: [{ component_id, component_type, calculation_type,
clause_reference, intermediate_values:[{name,value,unit}], final_result:{...}, status }], errors, ... }`.
Gerçek alan adlarını öğrenmek için yerel API'yi bir örnekle çalıştır ya da `tools/campaign/harness.py`
`find_results`/`value_of` ile `tests/fixtures/vessel_project_five_component.json`'a bak.
Eşlenecek büyüklükler (bileşen başına): gerekli kalınlık, nominal gerekli kalınlık, MAWP; ayrıca global
MAWP, hidrotest basıncı (`calculation_type` `hydrotest`), pnömatik (`pneumatic_test`).
`|fark| ≤ ok` → ✅, `≤ uyari` → ⚠️, büyükse ❌; iki taraftan biri yoksa `—` (satır yine listelenir,
sessiz atlama yok). Eşleme kurallarını `kiyas.js` içinde tek bir tabloda topla ki kolay düzeltilsin.

## Ekran
- Üç sütun (dar ekranda alt alta): **Girdi** (örnek seçici + JSON textarea + dosya yükle, geçersiz JSON
  hatası) · **Bağımsız hesap** (bileşen kartları; her kartta adımlar tablosu: Madde | Ad | Formül |
  Yerine konmuş | Sonuç+birim; altta varsayımlar listesi) · **Kıyas** ("Siteye sor" düğmesi, API adresi
  alanı, tablo: Bileşen | Büyüklük | Bağımsız | Site | Fark % | İşaret | Site maddesi; özet sayaçları).
- "Hesapla" tek tık: bağımsız hesap anında, siteye sorma ayrı düğme.
- Sade mühendislik görünümü, açık/koyu tema `:root` token'ları, CDN yok, harici font yok, monospace sayılar.
- Hiçbir hesap formülü `kiyas.js`/`index.html` içine yazılmaz — yalnız `hesap.js` çağrılır.

## Örnekler
`tests/fixtures/vessel_project_five_component.json`'dan türet (tek gövde kesiti, `component_sequence`
boş, koni/junction yok — `tools/campaign/bases.py` `_base` mantığı). Dört varyant: bombe tipi
ellipsoidal 2:1 / torispherical / hemispherical / flat. Her biri API'de 200 dönmeli (dene).

## launch.json
`test-ortami` girdisi: `python -m http.server 4322 --bind 127.0.0.1`, cwd `pressure-vessel-suite/tools/test-ortami`.
`api` girdisine `"env": {"CORS_ORIGINS": "http://127.0.0.1:4322,http://localhost:4322"}` ekle (mevcut
env varsa birleştir). `.env` dosyasına dokunma.

## Kabul
- `python -m http.server` ile açılınca konsolda hata yok; stub veya gerçek motorla kartlar dolar.
- API açıkken 4 örnekte kıyas tablosu dolar; API kapalıyken açık hata mesajı.
- README: iki komutla çalıştırma (API + ekran), tolerans anlamı, ekranın neyi kapsamadığı (nozul, EN 13445).

## Rapor
≤15 satır: dosyalar, commit, nasıl denendi, eşleme tablosunda emin olunmayan alanlar.
