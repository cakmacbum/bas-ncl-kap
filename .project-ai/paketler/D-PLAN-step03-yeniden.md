# Vessela Step 03 Yeniden Yazımı — Tarayıcıda OCCT + REA Referanslı Sihirbaz

## Context
`TASARIM_GELISTIRME_PLANI.md` Step 03'ün (geometri) baştan yazılmasını istiyor: 5 alt adımlı sihirbaz,
gerçekçi parça kütüphanesi (manşon, WN flanş, manway, eyer/etek/ayak), çoklu gövde+koni zinciri, AI ajanının silinmesi.
Bugünkü durum (keşif): `GeometryPage` pages.tsx:468–1418 arasında ~900 satırlık tek fonksiyon; 3D önizleme
(livePreview.tsx, R3F 8 + three 0.169) ile CadQuery (vessel_builder.py) aynı parçaları **ayrı ayrı** çiziyor;
vesselModel.ts:227 yalnız aktif gövdeyle eşleşip zincir ofseti eklemiyor → koni/2. gövdedeki nozullar kayboluyor;
vessel_builder.py:496–509 tek gövde dışında OUT_OF_SCOPE; destekler hiç çizilmiyor; flanş boyut tablosu yok.

**Yusuf'un kararları:** Render/backend'e bağlı olmayacak · REA hedefi MyTank Configurator (web) ·
kapsam Step 03 + 3D + CAD (VesselProject şeması korunur, yalnız genişletilir).

→ Sonuç: **tek geometri kaynağı tarayıcıda OpenCascade (replicad + opencascade.js, Web Worker)**.
Aynı B-rep hem Three.js'te gösterilir hem STEP/STL olarak tarayıcıdan indirilir. CadQuery yolu UI'dan çıkar,
Python tarafında testler/ofline için kalır (silinmez, bu turda yalnız dondurulur).

## GitHub'dan kullanılacak repolar
| Repo | Ne için | Nasıl |
|---|---|---|
| `sgenoud/replicad` (+ `donalffons/opencascade.js`) | Tarayıcıda B-rep, boolean, fillet/chamfer, STEP/STL export | npm bağımlılığı, Worker'da |
| `gumyr/bd_warehouse` → `flange.py`, `pipe.py` | ASME B16.5 WN/SO/SW/Blind flanş, NPS×Schedule boru ölçüleri ve profil mantığı | Ölçü tabloları JSON'a dönüştürülür (lisans teyidi şart, atıf `verified:false`); geometri mantığı replicad'de **sıfırdan** yazılır |
| `oddtopus/dodo`, `rkrenzler/ose-piping-workbench` | FreeCAD boru/fitting (coupling, socket) parametre setleri | Yalnız referans: manşon ölçü alanları ve parça ayrıştırması |
| `Irev-Dev/CascadeStudio` | opencascade.js + Worker + three entegrasyon deseni | Mimari referans (mesh aktarımı, iptal) |

## Faz 0 — REA: MyTank Configurator davranış spesifikasyonu
`/rea` skill'i ile (kod kopyalanmaz, yalnız gözlem): `capture_browser_scenario` / `observe_web_session` /
`inspect_web_network_capture` / `analyze_web_bundle`.
Çıkarılacaklar → `docs/rea/mytank-spec.md`: adım sırası ve geri dönüş, parça ekleme etkileşimi (konum/açı
girişi, 3D'den seçim), parametre→3D güncelleme gecikmesi ve yöntemi (istemci mi sunucu mu), veri modeli
(request/response şekli), doğrulama/uyarı biçimi. Hedef içeriği veri sayılır; çerez bandında en az izin.
Çıktı yalnız Faz 3 UX kararlarını besler; diğer fazları bloklamaz.

## Faz 1 — Temizlik (AI ajanı)
Sil: `apps/api/geometry_agent.py`, `tests/api/test_geometry_agent.py`, `tests/wiring/test_geometry_agent_ui.py`,
`apps/web-ui/src/GeometryAgentDrawer.tsx`, `geometryAgent.ts`. Düzenle: main.py:28,78–81, api.ts:7,122,
App.tsx:12,86,131, types.ts:256–285, features.ts, `.env.example`.

## Faz 2 — Model katmanı (sözleşme, Opus yazar)
- `vesselModel.ts`: `componentFrames(project)` → her head/shell/cone için `zStart,zEnd,rStart,rEnd` (sequence'tan).
  `nozzlePlacement` host'u frames'ten bulur (konide yüzey normali dahil); vesselModel.ts:227 ve livePreview.tsx:215 hatası kapanır.
- `store.ts`: `geoSubStep 0..4`, `selection {kind,id}|null`, `appendShell/appendCone/appendStepped(left|right)`,
  `addPipeNozzle` / `addCoupling` ayrımı; koni başlangıç çapı komşudan otomatik.
- Kataloglar (`src/data/`): `flange-b165.json` (bd_warehouse'tan), `pipe-nps.json` (mevcut nozzle-catalog genişler),
  `coupling-catalog.json` (B16.11 3000#/6000#, 1/2"–4"), hepsi `verified:false` + kaynak alanı.

## Faz 3 — Sihirbaz UI (`src/geometrySteps/`)
`GeometryWizard.tsx` + `Step1BodyChain`, `Step2Heads`, `Step3FlangedNozzles`, `Step4Couplings`, `Step5Supports`
(içerik TASARIM_GELISTIRME_PLANI.md'deki gibi; REA spec'inden gelen etkileşim düzeltmeleriyle).
pages.tsx'teki `GeometryPage` bu wizard'ı çağıran ince kabuğa iner. Sağda 3D + 2D kesit (schematic.tsx `ChainSchematic` korunur).

## Faz 4 — Tarayıcı CAD motoru (`src/cad/`)
- `cad.worker.ts` (replicad + opencascade.js, lazy-load; ilk açılışta yükleniyor göstergesi).
- `parts/`: `shellChain` (silindir+koni revolve, bombeler: 2:1 eliptik, torisferik, yarım küre, düz),
  `flangedNozzle` (boru + konik hub + disk + RF + cıvata delikleri), `coupling` (pahlı dövme gövde, iç soket kademesi,
  gövdeye saddle-cut), `manway` (boyun+flanş+kör kapak+cıvatalar+davit), `pad` (gövde eğrisine sarılı halka),
  `saddle` (aşınma plakası 120°, web, kaburgalar, taban), `skirt` (etek+taban halkası), `legs`.
- Çıktı iki seviye: hızlı mesh (her değişiklikte, debounce ~150 ms) ve tam boolean model (delik kesme, STEP).
- `exportStep()/exportStl()` → tarayıcıdan indirme; mevcut "exact" sekmesi (VesselViewer) bu kaynağa bağlanır.
- livePreview.tsx: LatheGeometry yerine worker mesh'i; worker hazır değilken mevcut lathe yer tutucu kalır.

## Faz 5 — Python CAD
vessel_builder.py dokunulmaz (OUT_OF_SCOPE testleri geçerli kalır); UI artık ona istek atmaz.
FUTURE.md'ye "Python CAD'i ya JS motoruna eşle ya emekliye ayır" kaydı.

## Yürütme (orkestra — şef kod yazmaz, her paket ayrı alt-ajan context'inde)
Şef (ben): paketleri `.project-ai/paketler/D<NN>-*.md` olarak yazar (amaç, dosyalar, arayüz sözleşmesi, kabul
kriteri, doğrulama komutu), ajanı `isolation: worktree` ile arka planda başlatır, ≤15 satır raporu + diff'i okur,
kabul kriterine göre onaylar ya da düzeltme mesajıyla aynı ajana geri yollar (SendMessage), sonra ana dala alır.
Her dalga öncesi checkpoint commit.

| Paket | Ajan (mevcut tipler) | Model |
|---|---|---|
| D00 Faz 2 arayüz sözleşmesi (`componentFrames`, store aksiyon imzaları, `cad` worker mesaj tipleri) | `architect` | Opus |
| D01 REA MyTank spec (Faz 0) | `general-purpose` (rea skill'iyle) | Sonnet |
| D02 AI ajanı temizliği (Faz 1) | `backend-builder` (API+test) | Haiku |
| D03 Kataloglar JSON (B16.5 flanş, NPS boru, B16.11 manşon) | `general-purpose` | Sonnet |
| D04 vesselModel `componentFrames` + store (Faz 2 uygulama) | `frontend-builder` | Opus (çekirdek) |
| D05 Sihirbaz 5 adım (Faz 3) | `frontend-builder` | Sonnet |
| D06 CAD worker + shellChain/bombeler | `frontend-builder` | Opus |
| D07 flangedNozzle + coupling + pad + manway | `frontend-builder` | Sonnet |
| D08 saddle/skirt/legs + STEP/STL export | `frontend-builder` | Sonnet |
| Her paket sonrası | `code-reviewer` (diff) → `test-verifier` (pytest/build/preview) | Sonnet |

Dalgalar: **W1** D00 ∥ D01 ∥ D02 ∥ D03 → **W2** D04 ∥ D06 → **W3** D05 ∥ D07 ∥ D08 → **W4** entegrasyon,
code-reviewer + test-verifier tam tur. Paralel paketler farklı dosyalara dokunur (D05 `geometrySteps/`, D06–D08 `cad/`).
Kayıt: `.project-ai/STATE.md`, `TASKS.md`, `ORKESTRA.md`, vault log.

## Doğrulama
- `python -m pytest tests/unit tests/api tests/wiring tests/cad-validation -q` (ajan testleri silinmiş halde yeşil).
- `cd apps/web-ui && npm run build` + yeni birim testleri: `componentFrames` (SHELL→CONE→SHELL ofset/çap), nozzlePlacement konide.
- Preview (launch.json) ile tarayıcıda: SHELL-01→CONE-01→SHELL-02 zinciri; bombe çapları otomatik; konideki nozul görünür;
  WN flanşta hub/RF/cıvata delikleri; manşon borusuz ve pahlı; eyer/etek/ayak; STEP indir → dosya geçerli
  (CadQuery `importStep` ile pytest'te açılabilirliği test edilir). Ekran görüntüsü kanıtı.
- Build boyutu: OCCT WASM ayrı chunk, ilk sayfa yükünü artırmamalı.
