# CURRENT STATE
guncellendi: 2026-10-09

Mevcut milestone:  M3 — Yayın: İngilizce landing + ücretsiz Google üyelik + deploy hazırlığı
                   (M2 doğrulama kampanyası askıda)
Bitti (main ad18abf, GitHub'da):
  W01 landing apps/landing (Codex) · W02 web-ui Supabase Google auth + ajan kapalı · W03 API JWT
  (JWKS/HS256), CORS env, ajan 503, 500 ayrıntı gizleme, Dockerfile + render.yaml.
  Kanıt: pytest tests/api+wiring 52/52 · web-ui build temiz, dist'te service_role yok ·
  landing 375px taşma yok, konsol temiz. Yerel .env ajan anahtarı boşaltıldı.
Canlı (2026-10-09, Vercel yusufsaglamci11): landing https://pv-suite-landing.vercel.app ·
  app https://pv-suite-app.vercel.app (CLI ile dist yüklendi, giriş ekranı doğrulandı)
  Supabase: basincli-kap (kpgflhkgsgswclqizgpy, eu-central-1, $0)
Bloke / Yusuf'ta:
  - Supabase Google provider + Google Cloud OAuth client + Site URL
  - Render hesabı (backend) · eski ajan anahtarını sağlayıcıda iptal · domain
Açık risk: API STORE bellek içi ve ortak → giriş yapan herkes tüm projeleri görür (yayın öncesi düzeltilmeli)
Bilinmeyen: Dockerfile derlenmedi (Docker daemon kapalı); cadquery pip wheel slim imajda doğrulanmadı
Sıradaki: kullanıcı-bazlı proje izolasyonu (W04) · Vercel deploy (landing + pv-suite-app) · Render
