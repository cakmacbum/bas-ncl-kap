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

## 2026-10-11 — Domain canlı
zeyslabs-vessela.com (+www) → pv-suite-landing · app.zeyslabs-vessela.com → pv-suite-app.
Kayıt: turkticaret.net, nameserver → ns1/ns2.vercel-dns.com; SSL Vercel, tüm adresler 200.
Açık: Render deploy (root Dockerfile d9a6dd9 sonrası sonuç bekleniyor) → VITE_API_URL ile app yeniden build.
Açık: ICANN RAA e-posta onayı (turkticaret panelinde uyarı) — yapılmazsa domain askıya alınır.

## 2026-10-11 — Claude Startups başvurusu gönderildi
Console org: ZeysLAB (info@zeyslab.com). Kredi alınmadı (Skip). Ürün: Pressure Vessel Suite, site zeyslabs-vessela.com.
Metin "open-source" diyor → repo cakmacbum/bas-ncl-kap hâlâ private: public kararı Yusuf'ta.
Sitedeki iletişim adresi contact@zeyslabs.com ≠ info@zeyslab.com → düzeltilmeli.
İnceleme öncesi öncelik: Render backend (hesaplama canlı değil).
