# TASKS — M2 Tank doğrulama kampanyası (M1: arsiv/TASKS-M1.md)

## DONE (2026-10-18)
- T-2.0 harness · T-2.1 kaynak avı K1–K4 · T-2.2 F01–F21 aileleri · T-2.3 aggregate (OZET.md) · T-2.4 SAPMA teyidi (V*/A2/A4)
- T-2.6 bulgu listesi (BULGULAR.md) → Yusuf onayı alındı → B-01/B-02/B-10/B-11/B-12/B-12b düzeltildi (959 test)

## BACKLOG (açık, öncelik sırasıyla — ayrıntı `campaign-2026-10/EKSIKLER.md`)
- T-2.7 Arayüze `liquid_level_mm` alanı (web-ui) + `component_sequence` yoksa kullanıcıya açık uyarı
- T-2.8 Hidrotest (UG-99) statik kafası (koni CA_o alanı KAPANDI)
- ~~T-2.9 Girdi doğrulama üst sınırları~~ KAPANDI (tasarım koşulları; geometri sınırları açık)
- ~~T-2.10 CA_o>0 bağımsız testleri~~ KAPANDI
- T-2.11 Kapsam boşlukları: EN 13445 flanş/yük/yorulma · MDMT coincident ratio · taban halkası · yatay saddle OUT OF SCOPE
- T-2.12 Browser e2e: 3 temel tank UI'dan (görsel kanıt) — yapılmadı
- T-2.13 Luna'nın kendi kontrolünü bağımsız kılmak (T63 dersi) · Haiku doğrulamasında referans/API ayrımı
- T-2.14 Nozulda E1 < 1 (açıklık Kategori B dışı dikişten geçerse) — uygulanmıyor, ayrı inceleme

## 2026-10-24 — Teknik işler (Render hariç): ayrıntı `paketler/G-PLAN-teknik-isler.md` (G01–G12; Gemini yazar, Claude şef; Gemini CLI kapalı → dış paket akışı)

## 2026-10-28 — M4 Step 03 yeniden yazımı (plan: `paketler/D-PLAN-step03-yeniden.md`)
Karar: backend yok → geometri tarayıcıda replicad+opencascade.js (Worker); REA hedefi MyTank Configurator.
- W1 (başladı): D00 sözleşme (architect) · D01 REA spec · D02 AI ajanı silme · D03 kataloglar
- W2: D04 componentFrames+store · D06 CAD worker+gövde zinciri
- W3: D05 sihirbaz 5 adım · D07 nozul/manşon/ped/manway · D08 destekler+STEP/STL
- W4: entegrasyon, code-reviewer + test-verifier
- 2026-10-28: W1 (D00, D00b, D01, D02, D03) ve W2 (D04, D06) birleşti — build temiz, vitest 31/31, pytest 332/332. W3 (D05, D07, D08) başladı.
- AÇIK: diş açılmış manşon iç çapı ↔ SCH160/XXS eşlemesi (catalogAdapter couplingNozzleDims) ajanın hafızasından; kaynakla doğrulanacak. Half SW boy null. Weldolet katalogda yok.
- AÇIK: nozzle-catalog.json "SCH10" değerleri NPS 1/2–12'de aslında 10S (D03 bulgusu).
- 2026-10-28: D07, D08 birleşti. D05 (sihirbaz) hâlâ koşuyordu — worktree-agent-aff28588d8cc8ccd0; pages.tsx'te D08'in 3 düzenlemesiyle çakışma olabilir. Kalan: D05 merge, W4 code-reviewer + test-verifier, tarayıcı görsel doğrulaması (D08 yapamadı).
- 2026-10-28: D05, D07, D08, D09 (W4 inceleme düzeltmeleri), D06 bombe katısı düzeltmesi, D08 yerleşim/3D yönü düzeltmesi birleşti. vitest 63/63, build temiz, pytest 332/332 (D09 öncesi ana dal).
- AÇIK (Yusuf kararı): position.py bombe nozulunda sessiz kırpma yapıyor (axial > head_height → tepe, negatif axial kontrolsüz); TS artık OUT_OF_HOST veriyor → UI/backend uyumsuz.
- AÇIK: ana bundle 1.49 MB (500 kB uyarısı; katalog JSON'ları + sihirbaz) — kod bölme ayrı iş.
- 2026-10-28: D10 position.py sessiz kırpma kaldırıldı (OUT_OF_HOST ValueError; CAD uyarıya çeviriyor). pytest 341/341. AÇIK: torisferik bombe yüksekliği backend R*0.25 vs frontend headDomeHeight — sınır farklı olabilir.
