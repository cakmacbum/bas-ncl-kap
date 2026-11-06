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

## 2026-10-28 — M4 başladı: Step 03 yeniden yazımı
Orkestra: şef kod yazmaz; D00–D08 paketleri ayrı alt-ajan context'lerinde (worktree). W1 koşuyor. Plan: `paketler/D-PLAN-step03-yeniden.md`.
2026-10-28 akşam: M4 Step 03 yeniden yazımı — D00–D09 ana dalda. Tarayıcıda replicad OCCT worker (wasm 23 MB ayrı asset), 5 adımlı sihirbaz, gerçekçi nozul/manşon/manway/mesnet katıları, tarayıcıdan STEP/STL. AI ajanı silindi. Backend'e geometri isteği yok.
Kanıt: W4 test-verifier tarayıcı senaryosu 7/9 → 2 hata düzeltildi (bombe STEP geçersizliği, STEP düğmesi örtülmesi); son doğrulama turu koşuyor.
Push yapılmadı.
Son doğrulama (6224e45): gerçek tıklamayla STEP indi; CadQuery 11/11 katı geçerli, bombeler duvarlı (HEAD-L 14.5e6 mm³). M4 tamam.

## 2026-10-29 orkestra | Dikey kap U-profil ayak (E01 CAD Opus ∥ E02 UI Sonnet)
- legs.ts yeniden: U yönü web/flanges, ayak pede oturur (rs=R+padT+b/2), height_mm=profil boyu, ped üst taşma, ilk ayak açısı, taban sacı + ankraj.
- Step 3.5 ayak editörü 4 grup (Profil/Ayak/Ped/Taban sacı), UPN 80–300 katalog (verified:false), "Kabı dikey yap", LEG_TOO_SHORT/LEG_PAD_OFF_SHELL/LEG_PROFILE_INVALID.
- vitest 78/78, build yeşil, tarayıcıda doğrulandı. Açık: flanges yönünde düz kanat ucu–eğri ped arası ~2 mm boşluk; padL ≤ ext uyarısı yok; UPN değerleri doğrulanmadı.

## 2026-10-29 orkestra | Adım 03 arayüz yeniden düzeni (U01 REA Sonnet · U02 Codex→Sonnet · U03 Haiku)
- Geri dönüş etiketi: ui-oncesi-2026-10-29. Spec: docs/rea/configurator-layout.md (MyTank yerleşimi ölçüldü).
- Tam yükseklik iki sütun (480/420/360), Geometri|Hesap girdileri sekmeleri, rozetli 3.1–3.5 şeridi, Ana ölçüler/Ayrıntılar grupları, yapışkan Önceki/Sonraki, yüzen görünüm/kamera çubukları, Dışa aktar menüsü, tek uyarı rozeti.
- Düzeltilen: çift useCadBuild (yükleniyor takılması), Bounds–fit çakışması, aspect’li fit, LivePreview hook sırası. E03 bombe kubbe derinliği h + HEAD_DEPTH_RANGE.
- vitest 92/92, build yeşil. Açık: otomatik ilk sığdırma Claude gizli tarayıcı panelinde tetiklenmedi (Playwright’ta çalışıyor) — Yusuf’un tarayıcısında kontrol edilecek.

## 2026-10-30 orkestra | Canlıda hesap sunucusu (V01 Sonnet · V02 Sonnet · V03 Sonnet)
- Durumsuz /api/calculate + /api/report.html; arayüz gövdeli çağrı, canlı hata mesajı + Tekrar dene, 30 sn zaman aşımı, uyanıyor durumu.
- Vercel pv-suite-app: api/index.py Python fonksiyonu (CadQuery yok), vercel.json, requirements.txt, .vercelignore (.env, Dockerfile, pyproject.toml hariç).
- Deploy git-archive temiz kopyadan (.test-tmp EPERM). Canlı doğrulandı: /api/health ok, Hesapla MAWP 2,31 MPa.

## 2026-10-30 — Dalga 1 (araştırma sonrası yol haritası)
- P01 kalıcı depo (Supabase PostgREST, revizyon uçları; env yoksa bellek içi) · P02 A4 baskı + PDF indir + U-1A biçiminde özet
- P03 analitik gerilme alanı (`web-ui/src/stress/analyticField.ts`, 14 test) · P04 "Gerilme" görünümü (vertex renk, skala, bilgi kartı)
- P05 Zick K arama altyapısı — `ZICK_TABLES` BOŞ (doğrulanmış Moss/Zick değerleri gerekli; K girilmezse BLOCKED kalır)
- main 115 web testi + 287 pytest yeşil; önizleme deploy READY; üretim deploy Yusuf onayı bekliyor
- Sıradaki: Dalga 2 (P06 lifting lug, P07 WRC 537, P08 koni/taban halkası, P09 BOM/maliyet). Plan: ~/.claude/plans/bu-yoldaki-plan-oku-peaceful-gem.md

## 2026-10-30 — Dalga 2 canlıda
- P06 kaldırma kulağı (5 kontrol, REVIEW_REQUIRED; BTH-1 Nd yok) · P07 WRC 537 altyapısı (WRC537/297 eğri katsayıları BOŞ → BLOCKED; kullanıcı katsayı girerse 537 hesaplanır)
- P08 koni App. 1-5 + taban halkası/ankraj (Δ tablosu yok, boşsa Δ=0 güvenli taraf) · P09 BOM + maliyet (fiyatlar kullanıcıdan, CSV)
- Bulgu (açık): `supports/wrc.py` ayak WRC'si moment normalizasyonunda β kullanmıyor — kontrol edilmeli.
- main 120 web + 633 pytest yeşil; app.zeyslabs-vessela.com üretimde.

## 2026-10-30 — Dalga 2 düzeltmeleri + Dalga 3 (main'de, üretime alınmadı)
- F1: ayak WRC moment normalizasyonuna eğri β'sı (N=K·M/(Rm²β)); Support.wrc_beta_ML/MC kullanıcı girer, yoksa BLOCKED_MISSING_INPUT
- F2: BOM profil ayak kütlesi (sections A×boy×ρ). Eyer kütlesi YOK — Support'ta eyer plaka alanları yok (sıradaki iş)
- P10 2D imalat resmi (`web-ui/src/drawing/`, A3, SVG+DXF R12; nozul deliği/tarama/etek yok) · P11 sac açınımı (`web-ui/src/flat/`, Rapor kartı)
- Temizlik: 70 worktree + 40 ork/* dalı silindi; birleşmemiş 7 dal ucu `refs/arsiv/ork/*`'ta, listesi `.project-ai/arsiv/ork-dallari/`
- main 130 web + 644 pytest yeşil
- F3 eyer plaka alanları (saddle_web_thickness_mm, saddle_rib_count/thickness; taban=base_plate_*, aşınma=thickness_mm/width_mm/contact_angle_deg) + BOM eyer kütlesi
- Dalga 3 + F1–F3 üretimde (app.zeyslabs-vessela.com); main 130 web + 646 pytest

## 2026-10-31 — Dalga 4 (P12+P13) main'de, üretime alınmadı
- P12 eksenel simetrik FEM (`web-ui/src/fea/`, saf TS Q8 + bant Cholesky, worker; ~1200 eleman 30–110 ms). Lamé/PR/t/yarımküre <%1, birleşim analitikle %5–9
- P13 SCL linearizasyonu (Pm/PL/PL+Pb+Q, von Mises/Tresca, S/1,5S/3S) + Gerilme sekmesinde Analitik/FEA anahtarı + hamut uyarısı
- Açık: P03 analitik torisferik hamut ~3× FEA (715 vs 237 MPa) — bağımsız doğrulama gerekli; E/ν malzemede yok (200 GPa/0,3)
- P14 (3D CalculiX sunucusu) Yusuf kararı bekliyor
- 2026-10-31: Dalga 4 üretimde. P14 Yusuf kararıyla ERTELENDİ (şimdilik yapılmayacak).

## 2026-10-31 — F4 + V1 main'de (üretime alınmadı)
- F4: TS MaterialProperty'ye elastic_modulus/poisson_ratio (Python'da zaten vardı); FEA eleman bazlı E/ν, varsayılan 200 GPa/0,3 + bileşen uyarısı
- V1: torisferik hamut — bağımsız kabuk çözümü (tools/verification/torispherical_shell.py) FEA ile %2–4 tutarlı; P03 analitik hamutta +%92…214 (hatalı), tacda güvensiz. P03 hamut+taç birleşim bandı artık NaN/"düşük güven — FEA kullanın" (gri). Yayımlanmış referans (A) künyeli doğrulanamadı. Rapor: docs/validation/torispherical-knuckle.md
- main 164 web + 653 pytest yeşil
- 2026-10-31: F4 + V1 üretimde.

## ➜ Güncel durum notu: `.project-ai/durum-notlari/2026-11-06/` (KALDIGIMIZ-YER.md + EKSIKLER.md)

## 2026-11-06 — DURAKLATILDI (Yusuf: "durdur, devam edeceğiz") — D5 Dalga A
Plan: `.project-ai/paketler/D5-PLAN-en13445-eski-isler.md` · Kadro: `.project-ai/KADRO.json` (kodlayıcı Sonnet · ağır Codex Luna · test/tarama agy Flash)
- BİTTİ, main'de: E01 EN sessiz boşluklar (5d1dcbe) · N01 nozul E1 alanı (5b795a8) · H01 hidrotest statik basınç ρ·g·h (0baf19a, merge 81c600d) ·
  supportParts testine 30 s zaman aşımı (e6874f7). T-2.7 kapandı (zaten vardı).
- **AÇIK — main şu an KIRMIZI (push edilmedi):** H01 + E01 birleşince pytest tüm `tests/`: 2 test düşüyor:
  `tests/faz4/test_faz4_en13445_gaps.py::test_asme_headings_covered_by_en` (H01 ASME'ye yeni hidrotest bileşen başlığı ekledi, EN'de karşılığı yok →
  E01 deseniyle EN'e NOT_CALCULATED override eklenmeli) ve `tests/wiring/test_no_ghost_features.py::test_uretilen_her_tip_ya_gosteriliyor_ya_kayitli`
  (yeni sonuç tipi arayüzde/kayıtta eksik — H01'in pages.tsx/i18n ResultGroup eklemesi ile birlikte kontrol). web 164/164 + build yeşil.
- **X01 e2e YARIM:** Codex kodu yazdı (ork/X01, ağ yok → kuramadı); Sonnet devraldı, durduruldu. WIP: dal `worktree-agent-a23cc1cdf8fc49f61`
  (worktree `.claude/worktrees/agent-a23cc1cdf8fc49f61`). Son durum: Playwright kuruldu, test akışında "Hesapla" butonu bulunamadı → Hesap Sonuçları sayfası akışı ayarlanıyordu.
- Bulgular: EN projelerinde check_pressure_relief ASME UG-125 etiketiyle çalışıyor (Dalga B'ye). H01 açıkları: σ≤Sy ölçütü normatif değil (0,9·Sy Yusuf kararı), Sy sıcaklıktan bağımsız;
  dikey kapta component_sequence boşsa hidrotest satırları REVIEW_REQUIRED.
- agy headless komut iznini reddediyor (settings.json allow kuralı Yusuf'ta) → test/tarama şimdilik Claude. Codex sandbox'ında npm ağı yok → kurulum isteyen paket Claude'a.
- SIRADAKİ: (1) 2 kırmızı testi düzelt → main yeşil → push · (2) X01'i WIP dalından tamamla · (3) Dalga B: E02 koni+düz kapak · E03 torisferik tam · E04 fa/ft/z/pnömatik (+ EN emniyet ventili etiketi) · E05 dış basınç + nozul takviyesi (hepsi Opus, sıralı) · (4) canlıya alma Yusuf onayıyla.
