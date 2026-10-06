# PAKET P03 — STEP içe aktarma arayüzü + STL görüntüleme

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 1 · Yürütücü: codex:yaz
> Mod: yaz → worktree'de yazarsın, dönüş = ≤15 satır rapor
> Codex yoksa: bu paket Claude Sonnet'e brief'lenir.
> Oluşturan: Orkestra şefi (Opus) · Tarih: 2026-10-06

## Sen kimsin, ne yapıyorsun
Büyük bir işin **tek parçasını** yapıyorsun. Backend ucu (P02) ve STEP tanıyıcı (P01)
paralel yazılıyor; sen yalnız ön yüzü yazıyorsun. Sözleşmeye birebir uy, kapsam dışına çıkma.
Emin olmadığın şeyi uydurma — rapora "Açık soru" olarak yaz.

## Amaç
Kullanıcı Geometri adımında bir STEP dosyası yükler. Backend'in tanıdığı ölçüler bir onay
çekmecesinde **öneri** olarak listelenir, kullanıcı satır satır onaylar ve yalnız onaylananlar
forma yazılır. STL dosyası yüklenirse yalnız 3D görüntü olarak gösterilir, hiçbir form alanı
değişmez.

## Bağlam
- Proje: basınçlı kap tasarım suite'i (ASME VIII-1 / EN 13445). React + TypeScript + Vite +
  zustand + three.js. Arayüz metinleri **Türkçe**.
- Stil: mevcut dosyalara uy (isimlendirme, CSS sınıf adları, yorum yoğunluğu az). Renkler
  yalnız `theme.css` tokenlarından gelir — sabit hex/rgba yazma.
- Önce oku:
  - `pressure-vessel-suite/apps/web-ui/src/GeometryAgentDrawer.tsx` → **aynı onay-sonra-uygula
    çekmece deseni**. Yeni çekmece bunun görsel/yapısal kardeşi olmalı (aynı CSS sınıfları
    kullanılabilir).
  - `pressure-vessel-suite/apps/web-ui/src/store.ts` → `updateShell(sectionId, patch)`,
    `updateHead(headId, patch)`, `addNozzle`, `updateNozzle(index, patch)`, `setDirty`.
    Aktif gövde `project.shell_sections[0]`. Sol/sağ bombe: `project.heads`
    (`component_sequence` sırası: ilk bombe = sol, son bombe = sağ).
  - `pressure-vessel-suite/apps/web-ui/src/api.ts` → `fetchJson`/`jsonOrThrow` deseni ve hata mesajları.
  - `pressure-vessel-suite/apps/web-ui/src/pages.tsx` → `GeometryPage` (yaklaşık satır 451) ve
    3D sekmeleri; `VesselViewer` kullanımı.
  - `pressure-vessel-suite/apps/web-ui/src/viewer.tsx` → `VesselViewer({url, ...})` STL'yi URL'den
    `STLLoader` ile yükler. Blob URL (`URL.createObjectURL(file)`) verilerek kullanılabilir.
  - `pressure-vessel-suite/apps/web-ui/src/types.ts` → `ShellSection`, `Head`, `HeadTypeT`, `Nozzle`.

## Arayüz sözleşmesi (değiştirme)
Tam şema: `.project-ai/ORKESTRA.md` → "Sözleşmeler" S-2 ve S-3. Özet:

```ts
// types.ts'e ekle
export type RecognitionConfidence = "high" | "medium" | "low";
export interface RecognizedField<T = number> { value: T; confidence: RecognitionConfidence; note: string | null; }
export interface StepRecognition {
  status: "RECOGNIZED" | "PARTIAL" | "REJECTED" | "BLOCKED";
  source: { filename: string; unit: string; unit_scale: number; solid_count: number };
  shell: null | { inside_diameter: RecognizedField; nominal_thickness: RecognizedField; tangent_length: RecognizedField };
  heads: Array<{ side: "left" | "right"; type: RecognizedField<HeadTypeT>;
    inside_diameter: RecognizedField; nominal_thickness: RecognizedField; straight_flange_length: RecognizedField;
    crown_radius: RecognizedField | null; knuckle_radius: RecognizedField | null }>;
  nozzles: Array<{ tag: string; outside_diameter: RecognizedField; inside_diameter: RecognizedField;
    neck_thickness: RecognizedField; axial_position: RecognizedField; circumferential_angle: RecognizedField;
    outside_projection: RecognizedField }>;
  unrecognized: Array<{ feature: string; reason: string }>;
  warnings: string[];
  not_in_file: string[];
}

// api.ts'e ekle — multipart DEĞİL, ham gövde:
async importStep(file: File): Promise<StepRecognition>
//   fetch(`${BASE}/import/step`, { method: "POST",
//     headers: { "Content-Type": "application/octet-stream", "X-Filename": encodeURIComponent(file.name) },
//     body: file })  → fetchJson ile aynı hata yönetimi.
//   413 → "Dosya 20 MB sınırını aşıyor.", 415 → "Dosya STEP (ISO-10303-21) değil.", 503 → "CAD motoru kurulu değil."
```

## Kapsam
- Yazacağın dosyalar (hepsi `pressure-vessel-suite/apps/web-ui/src/` altında):
  - `StepImportDrawer.tsx` (yeni)
  - `types.ts` (yalnız ekleme)
  - `api.ts` (yalnız `importStep` ekleme)
  - `pages.tsx` (GeometryPage'e düğme + çekmece bağlama, 3D alanına "Yüklenen model" sekmesi)
  - `workspace.css` (gerekirse, token kullanarak)
- **Dokunma:** `apps/api/**`, `packages/**`, `tests/**`, `store.ts` (mevcut aksiyonlar yeterli), `theme.css`.
- Yapılmayacaklar: STL'den ölçü çıkarma, model üst üste karşılaştırma, backend kodu, yeni npm paketi.

## Davranış ayrıntısı
1. GeometryPage'de "Modelden içe aktar" düğmesi olur; `accept=".step,.stp,.stl"`.
2. `.step/.stp` seçilirse `api.importStep` çağrılır, beklerken "Model tanınıyor…" yazar.
   Sonuç çekmecede gösterilir:
   - Başlıkta durum rozeti (Tanındı / Kısmen tanındı / Reddedildi / CAD yok) ve dosya adı.
   - Her önerilen alan için bir satır: etiket · önerilen değer + birim · mevcut değer · güven
     rozeti (low ise uyarı rengi) · onay kutusu. Kutular varsayılan **işaretli**, ama
     `confidence === "low"` olan satırlar varsayılan **işaretsiz**.
   - `unrecognized` ve `warnings` ayrı bir uyarı listesinde.
   - `not_in_file` alanları "Dosyada yok — elle girin" rozetiyle listelenir. Bunlar için onay
     kutusu olmaz. Etiketler: material→Malzeme, design_pressure→Tasarım basıncı,
     design_temperature→Tasarım sıcaklığı, joint_efficiency→Kaynak verimi,
     corrosion_allowance→Korozyon payı.
   - "Seçilenleri uygula" yalnızca işaretli alanları store'a yazar: gövde →
     `updateShell(shell_sections[0].section_id, …)`, bombeler → sol/sağ eşleşmesiyle
     `updateHead(headId, …)`, nozullar → `addNozzle` + `updateNozzle` (malzeme/korozyon
     alanlarına dokunma, mevcut varsayılanlar kalır). Ardından `setDirty(true)`.
   - status `REJECTED` veya `BLOCKED` ise "uygula" düğmesi devre dışıdır ve form değişmez.
3. `.stl` seçilirse API çağrılmaz. Blob URL üretilir ve 3D alanında "Yüklenen model (yalnız
   görüntü — hesaba girmez)" sekmesi açılır, içinde `VesselViewer` bu URL ile çalışır. Yeni
   yüklemede eski blob URL `revokeObjectURL` ile serbest bırakılır.
4. Erişilebilirlik: çekmece `role="dialog"`, `aria-label`; hata `role="alert"`; Esc kapatır.

## Kabul kriterleri
1. `npm run build` (apps/web-ui) → TypeScript ve Vite hatasız.
2. RECOGNIZED yanıtla çekmece açılır. İşaretli satırlar uygulanınca form değerleri önerilenle aynı olur.
3. REJECTED yanıtla uygula düğmesi devre dışıdır, `unrecognized` sebebi görünür.
4. STL seçilince form değişmez, sekmede model görünür.
5. Sabit renk kodu eklenmemiştir (yalnız `var(--…)` kullanılır).

`node_modules` worktree'de yoksa `npm run build` koşamayabilirsin. Bu durumda rapora
"build koşulamadı" yaz; şef ana ağaçta koşturacak.
