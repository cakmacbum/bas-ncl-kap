# Vercel dağıtımı (arayüz + FastAPI aynı projede)

`pv-suite-app` projesi artık hem `apps/web-ui` statik çıktısını hem de `api/index.py`
Python sunucusuz fonksiyonunu (FastAPI) yayınlar. Arayüz `/api/*` çağrılarını aynı
origin'den yapar (`VITE_API_URL` boş bırakılır).

## Dosyalar
- `vercel.json`: build/çıktı, `api/index.py` (maxDuration 60, includeFiles/excludeFiles), rewrites.
  `"framework": null` bilinçli: FastAPI preset'i tüm istekleri yutmasın, statik arayüz + `/api` birlikte çalışsın.
- `api/index.py`: ASGI girişi (`apps.api.main:app`).
- `requirements.txt`: Vercel'in okuduğu bağımlılıklar (fastapi, pydantic, numpy, pyjwt). `requirements-api.txt` Render/Docker içindir.
- `.python-version`: 3.12 (pyproject `requires-python >=3.11` ile uyumlu).

## Adımlar (PowerShell)
1. Vercel panelinde `pv-suite-app` > Settings > General > **Root Directory** = `pressure-vessel-suite`
   (eskiden `apps/web-ui/dist` yayınlanıyorsa bu ayarı değiştir; Build & Output ayarlarını boş/varsayılan bırak, `vercel.json` geçerli olur).
2. Bağlama (bir kez):
   ```powershell
   cd pressure-vessel-suite
   vercel link
   ```
   Mevcut `pv-suite-app` projesini seç. Ortam değişkenlerini indirmeyi (`.env.local`) sorarsa **hayır** de.
   `.vercelignore` `.env*` ve `Dockerfile`'ı yüklemeden hariç tutar.
3. Ortam değişkenleri (Settings > Environment Variables, değerleri panelde gir):
   `AUTH_MODE`, `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `CORS_ORIGINS` (aynı origin ise gerekmez), `AUTH_DISABLED` (yalnız test).
   `VITE_API_URL` tanımlama (boş kalsın).
4. Önizleme ve üretim:
   ```powershell
   vercel deploy
   vercel deploy --prod
   ```

## Notlar
- Sunucuda **CadQuery yok** (boyut ve soğuk başlangıç). CAD uç noktaları `services.py` içinde opsiyonel
  olarak devre dışı döner (503); STEP/STL tarayıcıda üretilir (Kap Geometrisi → Dışa aktar).
- WeasyPrint de yüklü değildir: raporlar HTML üretir, PDF üretimi kapalıdır.
- Fonksiyon dosya sistemi salt okunurdur (yalnız `/tmp` yazılabilir); bellek içi `store` örnekler arası kalıcı değildir.
- Paket boyutu sınırı: Python için 500 MB sıkıştırılmamış (Vercel dokümanı).
