# X01 — Tarayıcı uçtan uca testi (Playwright) — 3 temel tank
Kendi başına yeterli paket. Yollar `pressure-vessel-suite/` köküne göre. Gizli bilgi yok. UYGULAMA KODUNU DEĞİŞTİRME
(yalnız yeni test dosyaları + config + package.json script/devDependency).

## Bağlam
Web arayüzü: `apps/web-ui` (React + Vite, `npm run dev` → http://localhost:5173). Hesap API'si: FastAPI, repo
`pressure-vessel-suite` kökünden `python -m uvicorn apps.api.main:app --port 8000` (web-ui istekleri Vite proxy ile /api'ye gider;
`apps/web-ui/vite.config.ts`'e bak). Üç temel tank tanımı Python'da: `tools/campaign/bases.py` (vertical_leg_tank,
horizontal_saddle_tank, skirt_column). Arayüzde proje JSON içe aktarma yolu var mı bak (ör. "Modelden içe aktar"/proje aç;
yoksa API'ye POST /api/projects ile proje oluşturup UI'da açmak da kabul).

## İstenen
1. `@playwright/test` devDependency + `apps/web-ui/playwright.config.ts`: tarayıcı İNDİRME YOK — `use: { channel: 'msedge' }`
   (Windows'ta kurulu Edge). `webServer` ile Vite dev server'ı (ve mümkünse uvicorn'u) başlat; API başlatılamıyorsa test açık mesajla skip.
2. `apps/web-ui/e2e/basic-tanks.spec.ts`: 3 tank için: projeyi yükle → Kap Geometrisi'nde 3D önizleme çiziliyor (canvas var) →
   Hesap Sonuçları'na git → hesap çalışsın → sonuç tablosu/kartı en az bir kontrol satırı gösteriyor, sayfada "Error"/beyaz ekran yok →
   ekran görüntüsü `apps/web-ui/e2e/__screenshots__/<tank>.png` (git'e ekleme; .gitignore).
3. Tank JSON'ları: `tools/campaign/bases.py`'den üretmek için küçük Python betiği `apps/web-ui/e2e/fixtures/make_fixtures.py` →
   `fixtures/*.json` (üretilmiş JSON'ları commit et).
4. `package.json` script: `"e2e": "playwright test"`. Mevcut `npm test` (vitest) e2e dosyalarını toplamasın (vitest config'de exclude).

## Kabul
- `cd apps/web-ui && npm test && npm run build` yeşil (vitest e2e'yi çalıştırmamalı).
- `npm run e2e` yerelde 3/3 geçer (geçemiyorsa hangi adımda ve neden — rapora yaz; sahte geçme yok).
- tsconfig.tsbuildinfo commit etme. Commit mesajı sonu: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- Kısa Türkçe rapor: dosyalar, nasıl çalıştırılır, 3 tankın sonucu.
