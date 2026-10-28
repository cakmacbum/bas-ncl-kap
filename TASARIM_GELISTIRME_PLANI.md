# Vessela — Adım Adım Kap Tasarım Sihirbazı ve Gerçekçi 3D Parça Kütüphanesi Planı

## Amaç
1. **AI Ajanını tamamen kaldırmak:** Backend uç noktası, OpenRouter bağlantısı, ön yüz çekmecesi ve testleri kod tabanından temizlenecek.
2. **Adım adım (Guided Step-by-Step) Tasarım Akışı:** Karmaşık tek sayfalık akordeon yığını yerine, gerçek bir basınçlı kap imalat sırasını izleyen **5 aşamalı görsel tasarım sihirbazı** kurulacak:
   - **Aşama 3.1 — Gövde & Uzatma/Daraltma:** İlk silindiri seç (çap, kalınlık, boy) → uçlarına "+" ile daralan/genişleyen koni veya yeni silindir halkaları ekleyerek gövdeyi istediğin (hatta asimetrik/kademeli) şekilde uzat.
   - **Aşama 3.2 — Bombeler (Uç Kapama):** Oluşan gövdenin sol/alt ve sağ/üst açık uçlarının çaplarını otomatik algıla, bombe şekillerini (2:1 eliptik, torisferik, yarım küre, düz kapak) seç.
   - **Aşama 3.3 — Boru & Flanşlı Nozullar:** Gövde veya bombe üzerinde hangi parçaya, hangi mesafeye/açıya boru + flanş (veya manway) geleceğini seç.
   - **Aşama 3.4 — Manşonlar (Coupling / Soket):** Nereye manşon (dişli/soketli dövme bağlantı) geleceğini borulardan ayrı bir adımda seç.
   - **Aşama 3.5 — Ayaklar & Mesnetler:** Kabın yönüne göre eyer (saddle), etek (skirt) veya boru/profil ayakları yerleştir.
3. **Gerçekçi 3D Parça Kütüphanesi (Three.js + CadQuery):** Şu an manşon bile 150 mm boru ucuna takılmış düz bir silindir gibi çiziliyor. Bunun yerine gerçek geometri üreten parametrik parça kütüphanesi yazılacak (pahlı/kademeli gerçek dövme manşon, konik boyunlu ve cıvata delikli WN flanş, cıvatalı/mapalı manway kapağı, kaburgalı eyer ve taban plakalı ayaklar).

---

## Mevcut Kodda Neden "Manşon Manşona Benzemiyor" ve "Gövde Uzatılamıyor"?

1. **Manşon (`coupling`) şu an boru gibi çiziliyor:**
   - `apps/web-ui/src/livePreview.tsx` (satır 87-115) ve `packages/cad-engine/src/cad_engine/vessel_builder.py` (satır 428-435) her nozul için önce `outside_projection` (varsayılan 150 mm) boyunda ince bir boru çiziyor, üstüne bir silindir ekliyor. Oysa gerçek manşon (ASME B16.11 Full/Half Coupling veya Weldolet) **boru boynu olmadan doğrudan gövde sacına kaynaklanan**, dışta pahlı (chamfered), içte soket kademeli veya dişli kalın bir dövme parçadır.
2. **Flanşlarda boyun (hub), sızdırmazlık yüzeyi (RF) ve cıvata delikleri yok:**
   - Sadece tek bir düz disk (`CylinderGeometry`) çiziliyor; cıvata çemberi, konik kaynak boynu (weld neck hub) ve kör flanş cıvataları yok.
3. **Kademeli/daralan gövde (Silindir + Koni + Silindir) 3D'de ve CAD'de kırılıyor:**
   - Koni eklediğinde `addCone` koni çapını yeni silindire bağlamıyor.
   - İkinci silindire veya koniye koyduğun nozul/manşon `apps/web-ui/src/vesselModel.ts` (satır 227) içinde yalnızca `activeShellId` ile eşleştiği için 3D sahnede kayboluyor.
   - CadQuery (`vessel_builder.py` satır 490) tek silindir dışındaki her şeye `OUT_OF_SCOPE` hatası veriyor.
4. **Ayaklar 3D sahnede hiç yok:**
   - Eyer, etek ve ayaklar ne Three.js önizlemesinde ne de CadQuery STEP/STL modelinde üretiliyor.

---

## Kurallarla Uyum (K1, K2, K6)

- **Gerçekçi 3D Şekil vs. Standart Tablo Kuralı (K6):** Parçaların (manşon, kaynak boyunlu flanş, manway, eyer, ayak) **3D şekilleri** gerçek mühendislik geometrisinde (konik boyun, yükseltilmiş yüzey RF, cıvata delikleri, pahlı manşon gövdesi, iç soket kademesi, eyer kaburgaları) üretilecek. Ölçüler ise `src/data/` altındaki açık/düzenlenebilir JSON kataloglarından (`nozzle-catalog.json`, yeni `coupling-catalog.json` ve `flange-visual-catalog.json` — `verified: false` uyarısıyla kullanıcı tarafından doğrulanabilir ticari ölçüler) ve kullanıcının formdan girdiği değerlerden beslenecek.
- **AI Ajanının Silinmesi:** `apps/api/geometry_agent.py`, `apps/web-ui/src/GeometryAgentDrawer.tsx`, `apps/web-ui/src/geometryAgent.ts` ve `tests/api/test_geometry_agent.py` dosyaları tamamen silinecek; `/api/agent/geometry/interpret` uç noktası kaldırılacak.

---

## Yeni Tasarım Akışı (Adım 03 İçindeki 5 Alt Adım)

```
[3.1 Gövde & Uzatma] ──► [3.2 Bombeler] ──► [3.3 Boru & Flanşlar] ──► [3.4 Manşonlar] ──► [3.5 Ayaklar & Mesnet]
```

Sağ tarafta **3D Canlı Sahne + 2D Ölçülü Kesit** sabit durur; sol tarafta ise kullanıcı yukarıdaki 5 alt adımda sırayla ilerler (istediği adıma üstteki çubuktan geri dönebilir):

### Aşama 3.1 — Gövdeyi Kur ve Uzat (`Step1BodyChain.tsx`)
- Başlangıçta `SHELL-01` (İç Çap, Kalınlık, Uzunluk, Malzeme) seçilir.
- Altında görsel **"Gövde Zinciri Şeridi"** bulunur:
  `[ + Sol Uca Ekle ]  ── [ SHELL-01 (Ø1000 × 2000) ] ── [ + Sağ Uca Uzat / Daralt ]`
- **"+ Sağ Uca Uzat / Daralt"** butonuna basınca 3 net seçenek çıkar:
  1. **Yeni Silindir Virol Ekle:** Aynı çapta veya farklı kalınlıkta uzatır.
  2. **Daralan / Genişleyen Koni Ekle:** Başlangıç çapı otomatik olarak önceki parçanın çapından gelir; kullanıcı yalnız **Uç Çapı** ve **Koni Boyunu** yazar, yarı tepe açısı ($\alpha$) anında hesaplanıp gösterilir.
  3. **Daralt ve Silindirle Devam Et:** Koni + yeni çapta Silindiri tek seferde ekler ("garip" kademeli kapları saniyeler içinde kurdurur).
- Zincirdeki herhangi bir halkaya (veya 3D modeldeki parçaya) tıklayınca hemen altında o halkanın ölçüleri düzenlenir; silme, sıralama ve kopyalama anında 3D sahneye yansır.

### Aşama 3.2 — Bombeleri Seç (`Step2Heads.tsx`)
- Gövde zincirinin **sol uç çapı** (ör. Ø1000) ve **sağ uç çapı** (ör. koniden sonra Ø600) otomatik okunur.
- Yan yana iki görsel kart: **Sol/Alt Bombe** ve **Sağ/Üst Bombe**.
- Her kartta bombe şekli (2:1 Eliptik, Torisferik, Yarım Küresel, Düz Kapak) SVG ikonlarıyla seçilir; et kalınlığı ve düz flanş (etek) boyu girilir.

### Aşama 3.3 — Boru ve Flanşlı Nozullar (`Step3FlangedNozzles.tsx`)
- Yalnızca borulu/flanşlı bağlantılar (`flanged`, `slip_on`, `pad_reinforced`, `manway`) bu adımda yönetilir.
- **Adım adım ekleme:**
  1. **Nereye gelecek?** (`SHELL-01`, `CONE-01`, `SHELL-02` veya `HEAD-L` / `HEAD-R` — 3D modelden tıklayarak da seçilebilir)
  2. **Ne tip?** (Kaynak Boyunlu Flanşlı Boru, Slip-On Flanşlı Boru, Adam Deliği / Manway)
  3. **Standart Ölçü:** DN / NPS + Schedule seçici (`DN100 / 4" SCH40`) + Flanş Sınıfı (`PN16` / `Class 150`).
  4. **Konum:** Seçilen gövde/koni halkası üzerindeki mesafe ($z$, kaydırma çubuğu + sayı kutusu) ve saat yönü açısı ($\theta$: `0° Üst`, `90° Sağ`, `180° Alt`, `270° Sol` hızlı butonları + serbest açı).
  5. **Takviye Pedi:** Açılır/kapanır anahtar + ped çapı ve kalınlığı (3D modelde gövde eğrisine sarılmış gerçek halka olarak görünür).

### Aşama 3.4 — Manşonlar ve Soket Ağızlar (`Step4Couplings.tsx`)
- Borulu nozullardan tamamen ayrı bir adımdır (`nozzle_type` değeri `"coupling"` veya `"socket_welded"` olan kayıtları filtreler ve yönetir).
- **Manşon Kataloğu (`coupling-catalog.json`):** `1/2" (DN15)` — `4" (DN100)` arası `3000#` / `6000#` dövme manşon dış çapları, boyları ve iç soket/diş çapları hazır gelir.
- Kullanıcı:
  1. Hangi gövde/koni/bombe parçasına geleceğini seçer,
  2. Manşon alt tipini (Tam Manşon, Yarım Manşon, Weldolet), anma çapını (`1/2"`, `3/4"`, `1"`, `1½"`, `2"`) ve sınıfını (`3000#` / `6000#`) seçer,
  3. Mesafe ($z$) ve açıyı ($\theta$) girer.
- Manşon seçildiğinde `outside_projection` otomatik olarak manşon boyuna (ör. 35–65 mm) ayarlanır; 150 mm boru çizilmez.

### Aşama 3.5 — Ayaklar ve Mesnetler (`Step5Supports.tsx`)
- Yatay kapta varsayılan olarak **2 adet Eyer (Saddle)**, dikey kapta **Etek (Skirt)** veya **3/4 adet Ayak (Leg)** önerilir.
- Hangi gövde halkasına bastığı, eksenel konumu, yüksekliği ve genişliği seçilir; 3D sahnede anında kabın altına oturur.

---

## Gerçekçi 3D Parça Kütüphanesi Mimarisi

Hem tarayıcıdaki Three.js (`livePreview.tsx`) hem de Python CadQuery (`vessel_builder.py`) aynı parametrik parça geometrilerini üretecek:

| Parça | Şu Anki Görünüm | Yeni Gerçekçi Kütüphane Görünümü |
|---|---|---|
| **Manşon (`coupling`, `socket_welded`)** | 150 mm boru + ucunda düz silindir | Boru yok; doğrudan gövde/bombe eğrisine oturan (saddle-cut) kalın dövme bilezik, üst ve alt dış kenarda **45° pah (chamfer)**, içerde **soket oturma kademesi (shoulder)** + kaynak köşesi (fillet/weldolet konisi) |
| **Flanşlı Boru (`flanged`, `slip_on`)** | Düz boru + tek disk | Boru boynu + **konik kaynak boynu (weld-neck tapered hub)** + flanş diski + **yükseltilmiş sızdırmazlık yüzeyi (Raised Face - RF)** + çevresel **cıvata delikleri dizisi (bolt circle)** |
| **Takviye Pedi (`reinforcement_pad`)** | 3D önizlemede hiç yok | Gövde/koni dış yüzey eğrisine tam sarılmış (curved saddle ring) ikinci katman plaka |
| **Manway (`manway`)** | Kalın kapalı silindir | Boyun + cıvata delikli ağır flanş + **cıvata/somun dizili kör kapak** + üstte **tutma kolu / davit menteşe kolu** |
| **Eyer (`saddle`)** | Yok | Gövde alt yayını ($120^\circ$) saran **aşınma plakası (wear plate)** + dikey gövde sacı + yan **destek kaburgaları (stiffener ribs)** + ankraj delikli **taban plakası** |
| **Etek (`skirt`)** | Yok | Alt bombeye/gövdeye teğet silindirik etek + **taban flanş halkası (base ring)** + ankraj sandalyeleri ve menhol deliği |
| **Ayaklar (`leg`)** | Yok | $\theta$ açılarıyla dizilmiş $N$ adet boru veya profil bacak + gövdeye oturan **takviye pedleri** + **taban plakaları** |

---

## Değişecek ve Eklenecek Dosyalar

### 1. AI Ajanının Tamamen Kaldırılması
- **[SİL]** `pressure-vessel-suite/apps/api/geometry_agent.py`
- **[SİL]** `pressure-vessel-suite/tests/api/test_geometry_agent.py`
- **[SİL]** `pressure-vessel-suite/apps/web-ui/src/GeometryAgentDrawer.tsx`
- **[SİL]** `pressure-vessel-suite/apps/web-ui/src/geometryAgent.ts`
- **[DÜZENLE]** `pressure-vessel-suite/apps/api/main.py` (`POST /api/agent/geometry/interpret` ve ilgili import'ların kaldırılması)
- **[DÜZENLE]** `pressure-vessel-suite/apps/web-ui/src/App.tsx`, `api.ts`, `types.ts`, `features.ts`, `.env.example`

### 2. Çok Parçalı Gövde Zinciri & State Altyapısı
- **[DÜZENLE]** `pressure-vessel-suite/apps/web-ui/src/store.ts`
  - `geoSubStep: 0 | 1 | 2 | 3 | 4` ve `selection: { kind, id } | null`
  - `appendShell`, `appendCone`, `appendSteppedSection` zincir uzatma aksiyonları
  - `addPipeNozzle` ve `addCoupling` ayrımı
- **[DÜZENLE]** `pressure-vessel-suite/apps/web-ui/src/vesselModel.ts`
  - `componentFrames(project)`: Her `head`, `shell`, `cone` için global `zStart`, `zEnd`, `rStart`, `rEnd` hesabı
  - Çoklu silindir ve koni üzerindeki nozul/manşonların global 3D konum ve yüzey normali hesabı

### 3. Gerçekçi Parça Katalogları ve 3D Geometri Kütüphanesi
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/data/coupling-catalog.json`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/data/flange-visual-catalog.json`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/partGeometry.ts`
  - `buildCouplingGroup`, `buildFlangedNozzleGroup`, `buildManwayGroup`, `buildSupportGroup`
- **[DÜZENLE]** `pressure-vessel-suite/apps/web-ui/src/livePreview.tsx`
- **[DÜZENLE]** `pressure-vessel-suite/apps/web-ui/src/schematic.tsx`

### 4. Adım Adım Tasarım Sihirbazı (Step 03)
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/geometrySteps/GeometryWizard.tsx`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/geometrySteps/Step1BodyChain.tsx`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/geometrySteps/Step2Heads.tsx`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/geometrySteps/Step3FlangedNozzles.tsx`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/geometrySteps/Step4Couplings.tsx`
- **[YENİ]** `pressure-vessel-suite/apps/web-ui/src/geometrySteps/Step5Supports.tsx`
- **[DÜZENLE]** `pressure-vessel-suite/apps/web-ui/src/pages.tsx`

### 5. Kesin CAD Modeli (CadQuery STEP/STL)
- **[DÜZENLE]** `pressure-vessel-suite/packages/cad-engine/src/cad_engine/vessel_builder.py`
  - Çoklu gövde + koni (`_build_cone_body`) zinciri birleştirme
  - Gerçekçi pahlı/kademeli manşon katısı (`_build_coupling_feature`)
  - Konik boyunlu ve cıvata delikli flanş katısı
  - Eyer, etek ve ayak katıları (`_build_supports`)

---

## Doğrulama Planı

1. **Otomatik Testler:**
   ```powershell
   cd pressure-vessel-suite
   python -m pytest tests/unit tests/api tests/wiring tests/cad-validation -q
   cd apps/web-ui
   npm run build
   ```
2. **Manuel Kontroller:**
   - AI Ajanı buton ve uç noktalarının tamamen kalktığının kontrolü.
   - Adım 3.1'de `SHELL-01` → `CONE-01` (daralma) → `SHELL-02` zinciri kurup 3D'de anında daralan gövdenin görülmesi.
   - Adım 3.2'de sol ve sağ bombelerin daralan/genişleyen uç çaplarını otomatik alması.
   - Adım 3.3'te eklenen flanşlı borunun konik boyunlu, RF yüzeyli ve cıvata delikli görünmesi.
   - Adım 3.4'te eklenen manşonun borusuz, pahlı, iç kademeli gerçek dövme manşon olarak görünmesi.
   - Adım 3.5'te eklenen eyer/etek/ayakların hem canlı 3D'de hem de CadQuery STEP/STL çıktısında yer alması.
