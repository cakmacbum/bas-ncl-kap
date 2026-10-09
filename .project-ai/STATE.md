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
W04 (41e84a3): sahip bazlı depo — AUTH_MODE=anonymous, X-Client-Id; 404-only, 50/sahip, 5000 LRU; 65/65 test.
Giriş kapalı (AUTH_ENABLED=false, Yusuf 2026-10-09). render.yaml kökte (71d9d6d), Render hesabı bekleniyor.
Açık risk: X-Client-Id sır değil; depo bellek içi (restart = veri kaybı); rate limit yok; free plan 512 MB bellek CadQuery için riskli
Bilinmeyen: Dockerfile derlenmedi (Docker daemon kapalı); cadquery pip wheel slim imajda doğrulanmadı
Sıradaki: kullanıcı-bazlı proje izolasyonu (W04) · Vercel deploy (landing + pv-suite-app) · Render
