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

## 2026-10-18 — M2 doğrulama kampanyası: kaldığımız yer
M2 askıda değil, bu turda büyük ölçüde kapandı. Tam paket **959 geçti / 1 atlandı** (M1: 902, kampanya başı 934).
Kayıt dosyaları (tek doğruluk kaynağı): `pressure-vessel-suite/docs/validation/campaign-2026-10/`
  `BULGULAR.md` (bölüm A…Y, tüm bulgular + hükümler) · `EKSIKLER.md` (açık madde tablosu) · `OZET.md` · `F01…F21-*.md` · `tur7/A2,A3,A4.md`
Kampanya: 21 aile (F01–F21), 2.000+ doğrulanmış vaka (1000 gövde kütle koşusu, 440 Tur 3, 300 bombe, 300 A2 bağımsız, 300 T04 …).
**Düzeltilen (main):** B-01 dış korozyon payı MAWP (`085e799`) · B-02 nominal gereksinim CA_o (aynı) · B-10 statik kafa
  (`8dd3270` uyarı + `5b339ff` `liquid_level_mm` + geometriden kot) · B-11 raporda koni (`6611dc3`) · B-12 rapor HTML kaçışı
  (`de9456d`) · B-12b uyumluluk HTML kaçışı + `_esc` str-Enum (`880ebdd`).
**Yanlış alarm (kapandı):** B-07 (nozul t_r E=1: UG-37(a) dikişsiz kabuk; birincil metne erişilemedi, güven orta-yüksek) · G-01 (0.8D = t_r seçim dairesi) · B-03 (uyarılı varsayılan).
**Açık / sıradaki:**
  1. Arayüze `liquid_level_mm` alanı (apps/web-ui; şu an yalnız API/JSON; `test_ui_parity` ARAYUZDE_YOK kaydı var)
  2. Dikey kapta `component_sequence` boşsa statik kafa kotu hesaplanmaz (kampanya taban tankı sırasız) · hidrotest (UG-99) statik kafası yok
  3. Koni modelinde `external_corrosion_allowance` alanı yok (CA_o koni için 0 kabul)
  4. Kapsam boşlukları: EN 13445 flanş/yük kombinasyonu/yorulma tetiklenemiyor (B-06) · MDMT coincident ratio bağlı değil (B-04) ·
     taban halkası sonucu yok (G-05) · yatay tankta 216 saddle sonucu OUT OF SCOPE (G-06) · nozulda E1<1 (Kategori B dışı dikiş) uygulanmıyor (`reinforcement.py:265`)
  5. Girdi doğrulama: basınç 1e9 / NaN → HTTP 200 PASS/FAIL ya da 500 (G-03; şemada üst sınır yok)
  6. Test boşlukları: düz kapak/torisferik/yarım küre/koni MAWP'de CA_o>0 bağımsız test yok · T01 nozul E/nominal ilişkileri etkisiz (boş doğrulama)
  7. Luna paketleri: yol kuralı eklenince çalıştı; T42/T50 T11 çıktıları birleştirilmedi (tek kaynak: `t11_*/results_v2.json`)
**Push yapılmadı:** main origin'in **116 commit** ilerisinde (yerel commit'ler); `git push` kararı Yusuf'ta. Çalışma ağacında commit'lenmemiş: `.claude/launch.json`, `tsbuildinfo`, `.claude/worktrees/`, `W01-landing.RAPOR.md`.
**Araç durumu:** OpenCode 1.14.28 kurulu ama API anahtarı süresi dolmuş (OpenCode Console'dan yenilenmeli; ücretsiz katman 1.18.0+ ister).
  Gemini CLI kişisel hesapla kapalı (Antigravity'ye taşınmış, dışarıdan iş verilemez).
**Yürütücüler:** Codex luna (paket yazar → worktree) · Sonnet ajanları (izole worktree, şef diff'i okur, yalnız ilgili dosyaları ana ağaca kopyalar) · Haiku (örnek doğrulama; **`t_hesap` sütunları API kopyası çıktı → bağımsız kanıt sayılmaz**).
**Kaldığım yerden devam:** önce `EKSIKLER.md` oku; açık madde yoksa M3 (Render backend, repo public kararı, iletişim e-postası) ya da arayüz `liquid_level_mm`.

## 2026-10-18 (akşam) — M2 kapanış turu, push ve deploy
K2/K3/K4/C1 birleştirildi; tam paket 983 geçti / 1 atlandı. GitHub'a push edildi (`ee35425`, origin/main). Web arayüzü Vercel'e (pv-suite-app → https://app.zeyslabs-vessela.com, 200; dist hash canlıda eşleşti) CLI ile yüklendi.
Backend (Render) hâlâ yok → canlı arayüz hesap API'sine ulaşamaz. Açık: B-06 EN 13445, B-09, hidrotest bileşen-bazlı kontrol, E1 domain çıkarımı, Browser e2e görsel kanıt, ajan worktree temizliği.
