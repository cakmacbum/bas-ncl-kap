# app.zeyslabs-vessela.com — Keşif Notları

Tarih: 2026-10-25 · Kapsam: pasif keşif + client-side analiz + canlı probe (yetkisiz/anonim)
Hedef: https://app.zeyslabs-vessela.com/ ("Basınçlı Kap Tasarım Suite", ASME VIII-1 hesap aracı)

> Not: Backend ayakta olmadığı için dinamik doğrulama yapılamadı. Aşağıdaki maddelerin
> çoğu "kod kanıtı" (bundle) temelli; canlı doğrulanmış olanlar [CANLI] ile işaretli.

---

## 0. Özet (en kritik → en az)

| # | Bulgu | Önem | Durum |
|---|-------|------|-------|
| 1 | Backend/API tamamen erişilemez — uygulama işlevsiz | Kritik (fonksiyonel) | [CANLI] |
| 2 | Sıfır kimlik doğrulama; yetki = tahmin edilebilir proje no + uydurma UUID | Kritik | Kod kanıtı |
| 3 | Supabase entegrasyonu ölü kod (client hiç oluşturulmuyor) | Yüksek | Kod kanıtı |
| 4 | CSP yalnızca `frame-ancestors 'none'` (default-src/script-src yok) | Yüksek | [CANLI] |
| 5 | Path param'ları `encodeURIComponent` olmadan URL'e giriyor | Orta | Kod kanıtı |
| 6 | report.html sunucu-render HTML → blob: olarak açılıyor (stored XSS yüzeyi) | Orta | Kod kanıtı |
| 7 | `Access-Control-Allow-Origin: *` (tüm yanıtlarda) | Düşük/Orta | [CANLI] |
| 8 | Dev hata mesajı prod'a sızmış (`uvicorn apps.api.main:app --reload`) | Bilgi | Kod kanıtı |
| 9 | Eksik güvenlik başlıkları: Permissions-Policy, COOP/COEP, HSTS'te includeSubDomains/preload yok | Düşük | [CANLI] |
| 10 | Ölü DNS kaydı: api.zeyslabs-vessela.com (TLS handshake fail / DEPLOYMENT_NOT_FOUND) | Düşük | [CANLI] |
| 11 | Tek 1.37 MB chunk, kaynak haritası yok, three.js+supabase peşin yükleniyor | Düşük (perf) | [CANLI] |

---

## 1. [CANLI] Backend erişilemez — uygulama çalışmıyor

* `GET /api/health`, `GET /api/projects`, `POST /api/projects`, `/api/projects/PRJ-001`,
  `/api/config`, `/api/docs`, `/api/parse`, `/api/ai`, `/api/chat` … hepsi **200 + `text/html`**
  dönüyor ve gövde `index.html`.
* Yani Vercel'de catch-all SPA rewrite var, `/api/*` route'u **yok**.
* `POST /api/projects` → **405** + yine `Content-Type: text/html` (SPA fallback).
* Tarayıcıda "Projeleri Yenile" → console: `Unexpected token '<', "<!doctype "... is not valid JSON`.
* `GET /api/openapi.json` → 404 (FastAPI olsaydı varsayılan olarak açık olurdu).
* `/api/projects/PRJ-001/report.html` ve `/model.stl` → 404.

Etki: kayıtlı proje listeleme, hesaplama, 3D/rapor/STEP çıktısı tamamen devre dışı.
Deploy/route yapılandırması bozuk veya backend servisi düşük.

## 2. Kimlik doğrulama / yetkilendirme yok

Bundle'daki API istemcisi:

```js
async function Uz(){ if(!Ad) return null; ... }        // Ad = supabase client
const XR=void 0, Dz=void 0, Oz=!!XR, Ad=Oz?Nz(XR,Dz):null;
const GM="pvs.clientId";
function Bz(){ /* localStorage'dan UUID oku, yoksa crypto.randomUUID() üret ve yaz */ }
```

* `XR`/`Dz` (Supabase URL + anon key) **tanımsız** → `Ad` daima `null` → `Uz()` daima `null`.
* Dolayısıyla her istek yalnızca `X-Client-Id: <v4 UUID>` başlığı ile gidiyor; `Authorization`
  hiçbir zaman eklenmiyor.
* `r.status===401 && t && zz()` var ama `t` hep null olduğu için 401 kurtarma da çalışmaz.
  `zz()` → `Ad?.auth.signOut()` → no-op.
* Client tarafında UUID okunurken regex ile doğrulanıyor (`Fz`), **yazılırken doğrulanmıyor**;
  herhangi bir UUID elle localStorage'a konabilir. Sunucu tarafında bağlama olup olmadığı
  backend gelmeden doğrulanamaz.
* Projeler insan-okur numara ile adresleniyor (`/api/projects/PRJ-001`) → IDOR/numaralandırma
  yüzeyi çok geniş. Kullanıcı izolasyonu yoksa herkes her projeyi okur/yazar/siler.

## 3. Supabase ölü kod — ve iyi haber: sır sızıntısı yok

* `supabase-js@2.117.3` bundle içinde tam olarak mevcut (auth-js, realtime-js, storage-js,
  postgrest).
* Ama client hiç kurulmadığı için auth/realtime/storage/postgrest çağrılarının hiçbiri kullanılmıyor.
* `/assets/index-CUoz1SHY.js.map`, `/.env`, `/config.json`, `/package.json`, `/vercel.json`,
  `/robots.txt`, `/sitemap.xml` → **hepsi 404**. Bundle'da `eyJ...` formatında JWT **yok**.
* Sonuç: statik asset üzerinden anahtar sızıntısı bulunmadı (anon key de yok).

## 4. [CANLI] Güvenlik başlıkları

Mevcut: `Strict-Transport-Security: max-age=63072000` · `X-Content-Type-Options: nosniff` ·
`Referrer-Policy: strict-origin-when-cross-origin` · `CSP: frame-ancestors 'none'`

* **CSP yalnızca frame-ancestors'tan oluşuyor** → `default-src`, `script-src`, `object-src`,
  `base-uri`, `form-action` yok. XSS'e karşı gerçek koruma sağlamıyor.
* `frame-ancestors 'none'` sayesinde clickjacking kapalı; `X-Frame-Options` gereksiz ama yok.
* `Permissions-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`,
  `Cross-Origin-Resource-Policy` yok.
* HSTS'te `includeSubDomains` ve `preload` yok.
* `Access-Control-Allow-Origin: *` tüm yanıtlarda (statik asset'ler için normal, fakat custom
  header + ileride cookie/token gelirse `*` yetmez).
* `Server: Vercel` + `X-Vercel-Id` + `X-Vercel-Cache` fingerprint'leri açık;
  `POST` → `X-Vercel-Cache: BYPASS`.

## 5. URL / path işleme

```js
getProject(n)      -> `${er}/projects/${encodeURIComponent(n)}`   // encode VAR
updateProject(n,e) -> `${er}/projects/${n}`                       // encode YOK
calculate(n)       -> `${er}/projects/${n}/calculate`             // encode YOK
```

Aynı parametre için üç farklı davranış. Proje no'ya `/`, `?`, `#`, `%`, `..` konursa
`PUT`/`calculate` bozulur veya farklı path'e gider. Üstüne `reportBlobUrl/stepUrl/stlUrl`
de encode etmiyor.

## 6. HTML/çıktı enjeksiyonu yüzeyi

* `reportBlobUrl()` → `URL.createObjectURL(await blob)` ile sunucunun ürettiği `report.html`
  `blob:` URL üzerinden açılıyor. `blob:` **uygulamanın origin'ini** taşır (opaque değil).
* Proje adı / müşteri / notlar serbest metin ve doğrudan rapora giriyor (preview'da `<h2>{proje adı}</h2>`).
  Sunucu şablonu kaçışlamıyorsa **stored XSS** → açan mühendisin origin'inde kod → `localStorage`
  `pvs.clientId` okunur, kullanıcı adına `PUT /api/projects/...` çağrılabilir.
* Client'ta `dangerouslySetInnerHTML` 4 yerde var; biri ReactDOM iç kullanımı, diğerleri
  şablon render'ı. `importStep` binary dosyanın `X-Filename` başlığını `encodeURIComponent`
  ile veriyor (iyi) ama boyut/tip limiti client'ta yok.

## 7. Keşfedilen tam API yüzeyi (bundle'dan)

```
GET  /api/health
GET  /api/projects
POST /api/projects
GET  /api/projects/{n}
PUT  /api/projects/{n}
POST /api/projects/{n}/calculate
GET  /api/projects/{n}/report.html
GET  /api/projects/{n}/model.step
GET  /api/projects/{n}/model.stl
POST /api/import/step      (octet-stream + X-Filename)
POST /api/agent/geometry/interpret
```

+ Supabase alt yolları (`auth/v1`, `rest/v1`, `functions/v1`, `storage/v1`) yalnızca kütüphane
  varsayılanı; host tanımsız olduğu için hepsi ölü.
* Backend stack: **Python / uvicorn / FastAPI** — koddaki hata metni:
  `"... Backend çalışıyor mu? (pressure-vessel-suite kökünden: uvicorn apps.api.main:app --reload)"`
  → prod'da `--reload` (dev) komutu gösteriliyor, iç path yapısı (`apps/api/main.py`) sızıyor.

## 8. Altyapı / parmak izi

* Hosting: Vercel (edge `fra1`), IPv4 `64.29.17.1` / `216.198.79.1`, `ns1.vercel-dns.com`.
* Kök alan `zeyslabs-vessela.com` ayrı statik site (privacy.html + terms.html + mailto
  contact@zeyslabs.com) — `app` ile ilişkisiz deploy.
* `api.zeyslabs-vessela.com` DNS'te var (64.29.17.65) ama HTTPS handshake başarısız,
  HTTP'de `DEPLOYMENT_NOT_FOUND` → bayat kayıt.
* Frontend: React + Vite + three.js / react-three-fiber + zustand. Tek chunk 1.374.540 bayt,
  code-splitting yok.
* Tek localStorage anahtarı: `pvs.clientId`. Cookie yok, sessionStorage yok, consent banner yok.

## 9. Sonraki adımlar (backend ayağa kalkınca / yetki varsa)

1. `X-Client-Id` gerçekten sunucuda doğrulanıyor mu? Aynı projeyi iki farklı UUID ile
   `GET`/`PUT` dene (IDOR testi).
2. `POST /api/projects` ile proje aç, alanlara `<img src=x onerror=...>` koy, `report.html`'i
   `blob:` olarak aç → stored XSS doğrula.
3. `PUT /api/projects/../..%2f...` ve `PRJ-001%00` ile path traversal / encode testi.
4. `POST /api/import/step` → 50 MB dosya, boş dosya, `.step` olmayan dosya, dev boyutlu
   `X-Filename` (header injection / DoS).
5. `POST /api/agent/geometry/interpret` → prompt injection / model maliyeti testi.
6. `calculate` üzerinde büyük değerler (1e309, negatif, 0) → çökme / NaN yayılımı.
7. Rate limit ve `X-Vercel-Cache` davranışı: aynı projeyi tekrar tekrar çekip cache HIT ile
   başka kullanıcının verisini görme ihtimali.
