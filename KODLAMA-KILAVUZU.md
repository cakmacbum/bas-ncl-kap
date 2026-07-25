# Basınçlı Kap Suite — Başka Bir YZ'ye Verilecek Adım-Adım Kodlama Kılavuzu

> **Bu dosya bir uygulama komut setidir.** Kodlamayı yapacak yapay zekaya (veya kodlama
> aracına) **bütün olarak** verilir. Her adım: hangi dosya, ne eklenir, hangi imza/formül,
> hangi ASME referansı, hangi test, hangi kabul kriteri — tek tek yazılıdır. Kaynak gereksinim
> dokümanı `Basincli_Kap_Sitesi_Cok_Detayli_Ana_Prompt.md`'dir (buna "Ana_Prompt" denir; §
> atıfları oraya). Ana konsept: `GELISTIRME-ADIMLARI.md`.

---

## 0. Uygulayıcı YZ'nin uyacağı kurallar (ÖNCE OKU)

### 0.1 Proje yapısı ve çalıştırma
- Kök: `pressure-vessel-suite/`. Python monorepo (paketler `packages/*/src/<pkg>/`), FastAPI
  (`apps/api`), React+TS+Vite (`apps/web-ui`).
- Python 3.14, CadQuery 2.8, FastAPI, uvicorn, pytest kurulu.
- **Testleri çalıştır:** `cd pressure-vessel-suite; python -m pytest -q` (mevcut ~473 test).
- **Backend:** `python -m uvicorn apps.api.main:app --reload` (pressure-vessel-suite kökünden).
- **Frontend:** `cd apps/web-ui; npm run dev` (Vite `/api` → localhost:8000 proxy).

### 0.2 Değişmez kurallar (K1–K7 — ihlal etme)
K1 **Formülü yalnız `packages/code-*` içine yaz** (arayüze/orchestrator'a formül yazma).
K2 CAD hesabın kaynağı değildir; `project data → hesap` ve `project data → CAD` ayrı akar,
mesh ölçüp hesaba sokma. K3 standart/malzeme sürümünü koda gömme. K4 program bir varsayım
seçtiyse (E, CA, S…) sonuç nesnesine `add_assumption` ile yaz ve kullanıcı onayına sun.
K5 her sonuç denetlenebilir: ara değerler + madde referansı + malzeme + sürüm. K6 telifli
standart metnini/tablosunu gömme; yalnız madde referansı sakla, veriyi kullanıcı import eder.
K7 `packages/domain` standarttan bağımsızdır. **Ek kural:** lisanslı veri yoksa tahminle PASS
üretme; `BLOCKED_CODE_DATA` ile dur (§2.3).

### 0.3 Her hesap adımının izleyeceği iç döngü (§21)
Her modül için: **(1)** madde referansını doğrula → **(2)** saf formülü `code-*/formulas.py`'ye
yaz → **(3)** `design_code.py` metodunu ekle (CalculationResult doldur; ara değer + clause) →
**(4)** orchestrator'a bağla → **(5)** golden + boundary testi yaz → **(6)** API/UI'a bağla →
**(7)** `pytest -q` yeşil + regresyon bozulmadı. **Bir adım bitmeden diğerine geçme.**

### 0.4 Kod deseni (birebir taklit et)
Mevcut `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py` içindeki
`calculate_shell_thickness` ve `calculate_head_thickness` **referans şablondur**: malzeme bul →
E bul → girdi al → `input_snapshot` doldur → `add_assumption(K4…)` → formülü `try/except
ValueError` içinde çağır → `add_intermediate(...)` → `final_result`/`allowable_limit`/
`utilization_ratio` → `set_pass/set_fail/set_not_calculated`. Yeni her hesap **aynı iskeleti**
kullanır. `CalculationResult` API'si: `add_intermediate(name,value,unit,desc)`, `add_warning`,
`add_assumption`, `set_pass(util)`, `set_fail(util)`, `set_not_calculated(reason)`,
`set_out_of_scope(reason)`, `set_review_required(reason)`, `set_blocked_code_data(reason)`,
`set_blocked_missing_input(reason)`.

### 0.5 Mevcut durum (koddan doğrulanmış — Faz A + kısmi B/C KODLANDI, 473 test geçiyor)
**Tam VAR:** M6 gövde UG-27+MAWP · M11 kaynak/NDE · M12 nozul takviye UG-37 · **M8 düz kapak
UG-34** (thickness+MAWP) · **M20 pnömatik UG-100** · **M19 global MAWP** (statik-kafa + governing
+ eksik-bileşen blokajı) · **M7 koni UG-32(g)** · dış basınç orchestrator'a bağlı · yeni
`domain/load_cases.py`, `packages/mdmt/`, `calc-core/hydrostatics.py` · CalculationResult §12.4
alanları + `BLOCKED_*` durumları. **YOK/KISMEN:** M17 rüzgâr/deprem, M15 WRC nozul dış yükleri,
M18 yorulma, DB kalıcılığı, RBAC/audit/approval, AI katmanı, API §13 genişletme, PDF §16,
RTM/research_spec/validation-pack, **ve TÜM FRONTEND bağlama (apps/web-ui'ye Faz A hiç işlenmedi).**

---

## 1. FAZ A — Temel sözleşme + hızlı mühendislik kazanımları  ✅ KODLANDI (referans/doğrulama için)

### Adım A1 — CalculationResult §12.4 genişletme  ✅
`enums.CalculationStatus` + `BLOCKED_CODE_DATA`/`BLOCKED_MISSING_INPUT`; `result.py`'ye
`engine_version, formula_key, load_case_id, reference_elevation_mm, input_snapshot_hash,
governing, verified_by, created_at, validity_checks[]` + `set_blocked_*` + `add_validity_check`.

### Adım A2 — Düz kapak UG-34  ✅
`formulas.flat_head_thickness(P,d,S,E,C_attach,CA)` = `d·sqrt(C·P/(S·E))+CA` ve
`flat_head_mawp(d,t_corr,S,E,C_attach,CA)`; `geometry.Head.flat_attachment_factor`;
`design_code` FLAT dalı `d=inside_diameter-2·C` ile hesaplar, C yoksa `BLOCKED_MISSING_INPUT`.
`clause_reference="UG-34(c)(2)"`. golden: `test_flat_head_thickness/_mawp`.

### Adım A3 — Global MAWP: statik-kafa + governing + blokaj  ✅
`orchestrator.get_global_mawp()` BLOCKED/NOT_CALCULATED hariç; min → `governing=True`;
`_apply_static_head_correction` + yeni `calc_core/hydrostatics.static_head_pressure`.

### Adım A4 — Pnömatik test UG-100  ✅
`formulas.pneumatic_test_pressure(P_design,S_test,S_design)` = `1.1·P·(S_test/S_design)`;
`design_code.calculate_pneumatic_test_pressure`. golden var. **NOT:** MAWP değil design_pressure
tabanlı — niyet teyit edilmeli (UG-100 tipik olarak MAWP tabanlıdır).

---

## 1.5 FAZ A-UI — Arayüzü bağla (UI skill'leriyle — GENERIC "AI TASARIMI" YASAK)  ⬅ SIRADAKİ İŞ

> Faz A backend'i hazır ve testli ama `apps/web-ui`'ye HİÇ bağlanmadı → kullanıcı tarayıcıda
> göremiyor. Bu faz onu bağlar. **Kural: basit/jenerik arayüz üretme.** UI skill'lerini kullan.

### UI-0 — Önce UI skill'lerini yükle ve tasarım dilini çıkar (ZORUNLU)
- **Skill kaynakları** (Beyin-claude içinde mevcut — bu üç klasörü `BASINCLI-KAP/.claude/skills/`'e
  kopyala, sonra çalıştır; ortamında bu adlarla skill zaten varsa doğrudan invoke et):
  - `webmaker_test/.claude/skills/ui-ux-pro-max/` → tasarım-sistemi CLI'ı içerir.
  - `webmaker_test/.claude/skills/frontend-design/SKILL.md` → "generic AI slop" estetiğinden kaçın.
  - `webmaker_test/.claude/skills/ui-design-system/SKILL.md` → design token / component tutarlılığı.
- **Çalıştır** (bu bir **mühendislik/teknik SaaS** aracı — PV Elite/COMPRESS muadili, veri-yoğun,
  profesyonel; landing page DEĞİL):
  ```bash
  python .claude/skills/ui-ux-pro-max/scripts/search.py \
    "engineering technical SaaS dashboard data-dense professional" --design-system -f markdown
  python .claude/skills/ui-ux-pro-max/scripts/search.py \
    "accessibility data-table loading z-index focus" --domain ux
  ```
- **Uygula ama mevcut tasarımı YIKMA:** `apps/web-ui/src/theme.css` (1186 satır, IBM Plex Sans/Mono,
  oturmuş token seti) zaten tutarlı bir dil. Skill çıktısını bu dili **genişletmek** için kullan
  (yeni durum renkleri, governing vurgusu, form/tablo kalite kuralları) — sıfırdan tema atma
  (tutarlılık > yenilik; `ui-design-system` prensibi). Palet/tipografi/gerekçeyi
  `docs/ui-design-notes.md`'ye yaz (izlenebilirlik).
- **frontend-design yönü:** bu ürün için "refined minimalism / precision" — bilgi yoğun mühendislik
  aracı; maksimalizm değil, netlik + hiyerarşi + erişilebilirlik. Emoji ikon kullanma (SVG);
  hover'da layout kayması yok; renk tek gösterge olmasın (durum = renk + ikon + metin).

### UI-1 — TS tipleri (`apps/web-ui/src/types.ts`)
- `Head` arayüzüne: `flat_attachment_factor: number | null;`
- `CalcResult` arayüzüne: `governing?: boolean;` `reference_elevation_mm?: number;`
  `assumptions: string[];` (zaten var mı kontrol et).

### UI-2 — Bombe formu (`apps/web-ui/src/pages.tsx`, ~231–250 bölge + `store.ts` başlangıç objesi)
- `h.type === "flat"` iken **koşullu** `NumField` göster: etiket "Düz Kapak C Katsayısı (UG-34)",
  `onChange` → `setHead(i, { flat_attachment_factor: v })`, `help` = "Şekil UG-34 bağlantı tipine
  göre; ör. kaynaklı 0.33, cıvatalı ~0.20/0.13. Kullanıcı girer (K4/K6)."
- `h.type === "torispherical"` iken **crown_radius + knuckle_radius** `NumField`'larını göster
  (şu an UI'da yok → torisferik L/r girilemiyor). `elliptical/hemispherical`'de gizle.
- `store.ts` başlangıç head objelerine `flat_attachment_factor: null` ekle (yoksa runtime hata).

### UI-3 — Durum i18n (`apps/web-ui/src/i18n.ts` + `theme.css`)
- `STATUS_TR`'ye: `"BLOCKED CODE DATA": "Veri Engelli (lisans)"`, `"BLOCKED MISSING INPUT":
  "Girdi Eksik"`. `STATUS_CLASS`'a bu ikisi için ör. `badge--blocked`.
- `theme.css`'e `--blocked` token + `.badge--blocked` (mevcut `.badge--*` desenini taklit et);
  kilit/uyarı SVG ikonu (renk tek gösterge olmasın). Kontrast ≥ 4.5:1.

### UI-4 — Sonuç ekranı (`pages.tsx ResultsPage` + `components.tsx ResultRow`)
- Yeni `ResultGroup`'lar: `pneumatic_test` ("Pnömatik Test — UG-100"), `external_pressure`
  ("Dış Basınç / Vakum — UG-28"), `mdmt` ("MDMT — UCS-66"); koni "thickness" altında görünür.
  Hidrotest KPI'ının yanına **Pnömatik Test KPI** kutusu ekle.
- **Governing vurgusu:** MAWP grubunda `r.governing === true` satırına "Yöneten" rozeti + accent
  kenarlık. `ResultRow`'da genişleyen detaya **assumptions (K4)** satırlarını da ekle.
- **Erişilebilirlik (ui-ux-pro-max CRITICAL):** genişleyen satır klavye ile açılsın
  (`role="button"`, `tabIndex=0`, Enter/Space), görünür focus ring; ikon-only butonlara `aria-label`.

### UI-5 — Doğrulama (ui-ux-pro-max Pre-Delivery Checklist)
- `cd apps/web-ui; npm run dev` (backend açık).
- Düz kapak seç → **C katsayısı alanı çıkar** → gir → sonuç `BLOCKED` değil, gerçek PASS/FAIL.
- Torisferik seç → crown/knuckle alanları çıkar. Pnömatik KPI + MDMT/dış basınç grupları görünür;
  MAWP grubunda "Yöneten" rozeti doğru bileşende.
- Responsive 375/768/1440px, yatay kaydırma yok; light/dark kontrast; durum renk+ikon+metin;
  focus state'ler; emoji ikon yok. `docs/ui-design-notes.md` güncel.

---

## 2. FAZ B — Dış basınç bağlama + koni + yük durumları  (B1/B2/B3 büyük ölçüde KODLANDI)

### Adım B1 — external-pressure paketini ASME orchestrator'a bağla (Modül 9)  ✅
`orchestrator` `check_external_pressure(project)` çağırır; A/B chart yoksa `BLOCKED_CODE_DATA`
(K6). **Kalan:** stiffener ring atalet/aralık; UI'da vakum/dış-basınç sonuç grubu (UI-4'te).

### Adım B2 — Konik bölüm/reducer (Modül 7)  ✅ (formül+golden)
`formulas.cone_thickness` UG-32(g). **Kalan:** `domain.Cone` modeli + `project.cones` + orchestrator
döngüsü + UI geometri alanı (henüz varsa doğrula; yoksa ekle).

### Adım B3 — Yük durumu matrisi (Modül 4)  ✅ (domain)
`domain/load_cases.py` (`LoadCase/LoadCombination/ExternalLoad`). **Kalan:** `project` alanları +
orchestrator ön-kontrol + §7.2'deki 15 zorunlu load-case şablonu + yöneten koşul + UI ekranı.

---

## 3. FAZ C — Destekler, dış yükler, ileri hesaplar  (C1/C4 kısmi KODLANDI)

- **C1** destek reaction/leg/lug/base-plate/anchor → `packages/supports/` güncellendi; equilibrium
  + `Support/AnchorGroup` domain + `project.supports` + UI kalan.
- **C2** rüzgâr/deprem/kaldırma/taşıma (Modül 17) + `structural_design_basis` seçici (§7.10) — **YOK**.
- **C3** nozul dış yükleri WRC 537/297 (Modül 15) → `packages/nozzle-loads/`, 6-bileşen dönüşüm,
  WRC geçerlilik karar ağacı (§7.9), sınır dışıysa FEA'ya yönlendir — **YOK**.
- **C4** MDMT/UCS-66 → yeni `packages/mdmt/` **✅**; relief/Section XIII (Modül 20 kalanı) — **KISMEN**.

---

## 4. FAZ D — Kurumsal altyapı (Ana_Prompt §11–§19)  — **YOK (henüz)**

- **D1** Kalıcılık: `apps/api/store.py` (dict) → SQLAlchemy+SQLite; `Project/ProjectRevision`;
  onaylı revizyon immutability; concurrency.
- **D2** API'yi §13'e tamamla: revisions, design-basis/materials/welds PUT, nozzles/supports POST,
  load-cases, run-all-valid, mawp-envelope, compliance/ped, cad/step + reports/pdf (**job**),
  reviews, approvals. Eksik girdide **500 değil**, yapılandırılmış `BLOCKED_*`.
- **D3** RBAC/audit/approval (§19): drafter/engineer/checker/approver/admin; append-only
  `AuditEvent`; onaylı revizyon kilidi. (Güvenlik için `senior-security` skill'i.)
- **D4** AI orkestrasyon katmanı (§17): NL→taslak, eksik-girdi sorma, deterministik API çağırma;
  **yasak:** hafızadan S/chart/MAWP üretmek, FAIL→PASS, "ASME onaylı" iddiası.
- **D5** PDF §16 20-bölüm (load-case/relief/ESR-gap) + UI eksik ekranlar (dashboard/proje-listesi,
  review/approval, standards-admin) + validation pack (§18.4).

---

## 5. Belge artefaktları (kod dışı — her fazda üret)
- `docs/rtm.md` — RTM (§3.3 sütunları), 20 modül satırı, durum kolonu §0.5'ten.
- `docs/research/<modul>.md` — modül başına `research_spec` (§3.4).
- `docs/calculation-coverage.md` — her fazda gerçek koda göre güncelle.
- `docs/ui-design-notes.md` — UI skill çıktısı, seçilen palet/tipografi/gerekçe.

## 6. Doğrulama (her adımda)
1. `cd pressure-vessel-suite; python -m pytest -q` → yeşil, regresyon yok (≥473 test korunur).
2. Yeni modül için golden + boundary testi eklendi mi?
3. Backend: `uvicorn apps.api.main:app --reload`; ilgili uç 200 + doğru status.
4. UI: `npm run dev`; sonuç kartı doğru durumu (PASS/FAIL/BLOCKED/REVIEW) gösteriyor mu?
5. §22 DoD: RTM satırı + exact paragraph + validity limits + golden + API/UI aynı engine +
   PDF provenance + known limitations.

## 7. Öncelik sırası
Faz A ✅ → **Faz A-UI (SIRADAKİ — arayüzü bağla)** → Faz B kalanları (Cone domain, load-case
şablonu, UI) → C2/C3 (rüzgâr-deprem/WRC) → C4 relief → D1–D5 (DB/API/RBAC/AI/rapor). Her adım
kendi testi yeşil olmadan kapatılmaz. Kaynak/karar eksikse **açık blocker** bildir; tahminle
"tamamlandı" deme (§21).
