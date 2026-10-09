# CURRENT STATE
guncellendi: 2026-10-09

Mevcut milestone:  M3 — Yayın: İngilizce landing + ücretsiz Google üyelik + deploy hazırlığı
                   (M2 doğrulama kampanyası askıda)
Bitti (main ad18abf, GitHub'da):
  W01 landing apps/landing (Codex) · W02 web-ui Supabase Google auth + ajan kapalı · W03 API JWT
  (JWKS/HS256), CORS env, ajan 503, 500 ayrıntı gizleme, Dockerfile + render.yaml.
  Kanıt: pytest tests/api+wiring 52/52 · web-ui build temiz, dist'te service_role yok ·
  landing 375px taşma yok, konsol temiz. Yerel .env ajan anahtarı boşaltıldı.
Bloke / Yusuf'ta:
  - Vercel'e yükleme: Vercel CLI yok, Vercel'in GitHub'ı ahmetefe37 → cakmacbum/bas-ncl-kap görünmüyor
  - Supabase projesi yok (3 proje INACTIVE) + Google OAuth
  - Render hesabı (backend) · eski ajan anahtarını sağlayıcıda iptal · domain
Açık risk: API STORE bellek içi ve ortak → giriş yapan herkes tüm projeleri görür (yayın öncesi düzeltilmeli)
Bilinmeyen: Dockerfile derlenmedi (Docker daemon kapalı); cadquery pip wheel slim imajda doğrulanmadı
Sıradaki: kullanıcı-bazlı proje izolasyonu (W04) · Vercel deploy (landing + pv-suite-app) · Render
