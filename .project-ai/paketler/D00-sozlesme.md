# D00 — Step 03 arayüz sözleşmesi (architect, 2026-10-28; şef onaylı)

Tüm yollar `pressure-vessel-suite/apps/web-ui/src/` altında (aksi belirtilmedikçe). Birim mm.

## Kodda doğrulanan gerçekler
- Domain Pydantic modelleri `extra="ignore"` → bilinmeyen alan PUT'ta sessizce silinir. Kalıcı her yeni alan Pydantic'e de eklenir.
- `NozzleType` (packages/domain/src/domain/enums.py:62): `slip_on | socket_welded | coupling | manway | flanged | pad_reinforced`. Yeni enum değeri YOK.
- `VesselProject` doğrulayıcısı (project.py:147): sequence ilk ve son eleman head; id yinelenmez → zincire ekleme hep iki bombe arasına.
- `Support.location_mm` küresel konum (support_calc.py:43, Zick teğet-teğet).
- Yeni opsiyonel alanlar eski dosyaları bozmaz; testlerde sabit hash yok.
- web-ui'de vitest / replicad / opencascade bağımlılığı yok (şef checkpoint'i ekler).

## 1. vesselModel.ts
**Eksen:** kap ekseni +Z; z=0 sol (ilk) bombenin kutbu; bileşenler sequence sırasıyla arka arkaya. Head frame boyu
`headDepth = kubbe + sf`. θ +X'ten ölçülür (görüntüde yatay kapta θ=0 üst). Model çerçevesinde "aşağı": yatay −X, dikey −Z.
Worker ve STEP bu çerçeveyi kullanır (CadQuery "gövde başlangıcı=0" kuralı donduruldu).

```ts
export type FrameKind = "head" | "shell" | "cone";
export interface ComponentFrame {
  kind: FrameKind; id: string; index: number;          // sequence indeksi
  zStart: number; zEnd: number;                        // global, zEnd(i) === zStart(i+1)
  rInStart: number; rInEnd: number; rOutStart: number; rOutEnd: number;
  thickness: number;                                   // nominal_thickness (rOut = rIn + t)
  head?: { side: "left" | "right" | "internal"; type: HeadTypeT; domeHeight: number; sf: number; equatorZ: number };
  cone?: { largeAtStart: boolean };
}
export function componentFrames(p: VesselProject): ComponentFrame[];
export function chainIssues(p: VesselProject, f: ComponentFrame[]): { code: "DIAMETER_MISMATCH"|"INTERNAL_HEAD"|"MISSING_REF"; id: string; message: string }[];
export function tangentDatum(f: ComponentFrame[]): { left: number; right: number }; // sol bombe zEnd, sağ bombe zStart
```

**componentFrames algoritması**
1. `seq = component_sequence`; boşsa `[heads[0], shell_sections[0], heads[1]]` (heads[1] yoksa atla). Bulunamayan/yinelenen → atla + MISSING_REF.
2. `z=0`, sırayla:
   - shell: `ri = ID/2`, yoksa `(OD−2t)/2`, yoksa 0.5. `L = max(tangent_length,1)`. Start=End. `z += L`.
   - cone: `prevR` = önceki frame `rInEnd`. `|prevR − small/2| < |prevR − large/2|` → genişleyen (`rInStart=small/2, rInEnd=large/2, largeAtStart=false`); aksi/önceki yoksa daralan. `z += length`. (Bugünkü vesselProfileChain'in genişleyen koni hatasını kapatır.)
   - head index 0 (left): rIn 0→Ri; `equatorZ = z+h`; kubbe [z,z+h], sf [z+h,z+h+sf].
   - head son (right): rIn Ri→0; `equatorZ = z+sf`.
   - head arada (internal): `z += depth`, çizilmez, INTERNAL_HEAD.
   - bombeler için `z += h+sf`.
3. `headDomeHeight(di, type, head?)` tek kaynak: `crown_depth` → torisferik R,r varsa `h = R − sqrt((R−r)² − (Di/2−r)²)` → oransal (Di/4, Di/6, Di/2, 0). Frames, 2D şema, CAD hep bunu kullanır.
4. `vesselProfileChain` iç hesabı frames üzerinden yeniden yazılır; imza değişmez.

**Nozul yerleşimi**
```ts
export interface NozzlePlacement { position: Vec3; normal: Vec3; axis: Vec3; hostKind: FrameKind; frame: ComponentFrame; rAtAnchor: number }
export type PlacementResult = NozzlePlacement | { error: "HOST_NOT_FOUND" | "OUT_OF_HOST" | "INTERNAL_HEAD" };
export function nozzlePlacement(p: VesselProject, nz: Nozzle, frames: ComponentFrame[]): PlacementResult;
```
- Host `frames.find(f => f.id === nz.host_component_id)` (vesselModel.ts:227 + livePreview.tsx:215 hatası kapanır). Çıpa iç yüzeyde (position.py ile aynı). `s = axial_position`, host zStart'ından.
- shell/cone: `0≤s≤L` değilse OUT_OF_HOST (kırpma yok, K4). `r = rInStart + (rInEnd−rInStart)·s/L`, `k=(rInEnd−rInStart)/L`;
  `position=[r cosθ, r sinθ, zStart+s]`, `normal=norm([cosθ, sinθ, −k])`, `t̂=norm([k cosθ, k sinθ, 1])`, `axis=norm(cosα·normal + sinα·t̂)` (shell'de eski formülle aynı).
- head: position.py formülü (a=Ri, b=domeHeight, φ iki dallı, zLocal=b cosφ, elipsoid normali). Sağda `z=equatorZ+zLocal`; solda `z=equatorZ−zLocal`, normal z ters. α mevcut koddaki gibi. Düz kapak: `r=head_position_diameter/2 ?? 0`, normal ±Z (eski b=R/2 yedeği kalkar).
- Destek: `supportZ = tangentDatum.left + location_mm` (Zick uyumlu). Etek location_mm kullanmaz.

## 2. store.ts
```ts
geoSubStep: 0|1|2|3|4; setGeoSubStep(n): void;            // loadProject → 0
selection: { kind: "shell"|"cone"|"head"|"nozzle"|"support"; id: string } | null; setSelection(sel): void;
appendShell(side: "left"|"right", params?: Partial<ShellSection>): string | null;
appendCone(side, params: { endDiameter: number; length: number; nominal_thickness?: number }): string | null;
appendStepped(side, params: { endDiameter: number; coneLength: number; shellLength: number }): [string, string] | null;
addPipeNozzle(p: { host_component_id: string; nozzle_type: "flanged"|"slip_on"|"pad_reinforced"|"manway";
  nps: string; schedule: string; rating_class: FlangeClass; axial_position: number; circumferential_angle: number;
  head_position_diameter?: number | null }): string;     // tag döner
addCoupling(p: { host_component_id: string; nozzle_type: "coupling"|"socket_welded"; nps: string;
  rating_class: "3000#"|"6000#"; coupling_form: "full"|"half"|"weldolet"; axial_position: number;
  circumferential_angle: number; head_position_diameter?: number | null }): string | null; // katalogda yoksa null
addSupport(type?: "saddle"|"skirt"|"leg", host?: string): string;  // varsayılan "saddle"
export const PIPE_NOZZLE_TYPES = ["flanged","slip_on","pad_reinforced","manway"] as const;
export const COUPLING_TYPES = ["coupling","socket_welded"] as const;
```
Kurallar:
- Ekleme yeri: right → `seq.length−1` (son bombenin önü), left → 1. `appendShell` o uçtaki komşuyu kopyalar; `inside_diameter` = o uçtaki zincir iç çapı.
- Koni: `startD = 2×(right ? frames[n−2].rInEnd : frames[1].rInStart)`; large/small = max/min; `|startD−endD|<1` → null (UI butonu pasif).
  `half_apex_angle = atan(((large−small)/2)/length)` derece. Kalınlık/malzeme/kaynak/CA komşudan.
- `appendStepped` tek `set()`: koni + yeni shell (ID=endD). `updateCone` large/small/length değişince half_apex_angle yeniden.
- Bombe çap senkronu: her zincir mutasyonundan sonra `diameter_relation==="linked"` ise `syncTerminalHeads`:
  `head[0].ID = 2·frames[1].rInStart`, `head[last].ID = 2·frames[n−2].rInEnd`.
- removeComponent: terminal bombe ve tek kalan gövde elemanı silinmez (no-op); host'u silinen nozullar silinir; seçiliyse selection=null.
- moveComponent: yalnız 1..n−2. duplicateComponent `nextId` kullanır.
- `nextId(prefix, ids) = prefix-pad2(max+1)` (SHELL, CONE, HEAD; HEAD-L/HEAD-R korunur). Nozul etiketi `nextTag`: boru N, manway M, manşon C. `removeNozzle` yeniden numaralandırmaz (etiket = kimlik).
- addPipeNozzle: OD/et pipe-nps'ten, `ID = OD−2·wall`; outside_projection boru 150, manway 200; `size_designation` örn `'4" SCH40 CL150'`; pad_reinforced → `reinforcement_pad=true`, pad od=2·OD, t=host kalınlığı.
- addCoupling: `outside_diameter=body_od`, `inside_diameter=bore`, `neck_thickness=(body_od−bore)/2`, `outside_projection=length`, `inside_projection=0`. (code-reviewer: takviye hesabında d = inside_diameter teyidi.)
- Yeni opsiyonel alanlar (TS + Pydantic `Optional, default=None`, hesaba girmez, roundtrip testi):
  `Nozzle.rating_class?: string|null` (`^(CL150|CL300|CL600|CL900|CL1500|CL2500|3000#|6000#)$`), `Nozzle.coupling_form?: "full"|"half"|"weldolet"|null`.
  Destekler için yeni alan yok (mevcut: contact_angle_deg, width/height/thickness/diameter, leg_*, base_plate_*, anchor_*, support_radius_mm). Flanş sınıfı `project.flanges`'a gitmez.

## 3. src/cad/ worker protokolü
```ts
type Level = "preview" | "exact";
type MainToWorker =
  | { type: "init" }
  | { type: "build"; reqId: number; project: VesselProject; level: Level }
  | { type: "export"; reqId: number; project: VesselProject; format: "step" | "stl" };
type WorkerToMain =
  | { type: "ready" } | { type: "loading"; progress: number }
  | { type: "result"; reqId: number; level: Level; meshes: MeshPart[]; warnings: BuildWarning[]; ms: number }
  | { type: "export-result"; reqId: number; blob: Blob; filename: string }
  | { type: "error"; reqId: number; message: string };
interface MeshPart { partId: string; kind: "shell"|"cone"|"head"|"nozzle"|"support";
  positions: Float32Array; normals: Float32Array; indices: Uint32Array; edges?: Float32Array } // transferable
interface BuildWarning { partId?: string; code: "HOST_NOT_FOUND"|"OUT_OF_HOST"|"CATALOG_MISS"|"BOOLEAN_FAILED"|"INTERNAL_HEAD"|"DIAMETER_MISMATCH"; message: string }
```
- `partId = ${kind}:${id}`; seçilebilir her varlık tek mesh (boru+flanş+ped birleşik). 3D tık → `setSelection({kind,id})`.
- preview: boolean yok, delik yok, manşon tabanı sacın içine 1·t uzar; tolerans 1.0 / açısal 0.3.
- exact: her host kendi cutter'larıyla ayrı çıkarılır, gövde fuse edilmez; saddle-cut, cıvata delikleri, pah, fillet; tolerans 0.2/0.1.
  Export = adlı compound: `exportSTEP([{shape, name: partId}])`, STL `blobSTL({binary:true})`.
- Yarış: istemci `latestReqId`, eskileri atar; worker tek bekleyen yuva, parçalar arası `pending.reqId > current` → kalanı atla. preview debounce 150 ms; exact 800 ms boşta / Kesin sekmesi / export. `terminate()` yalnız kullanıcı iptalinde. Export aynı hash'li exact cache'i kullanır.
- Cache: varlık başına `stableHash(params+frame+level)` → `Map<string, Shape3D>`.
- Yükleme: `new Worker(new URL("./cad.worker.ts", import.meta.url), {type:"module"})`; WASM `replicad-opencascadejs/src/replicad_single.wasm?url` lazy; vite `worker.format="es"`, `optimizeDeps.exclude:["replicad-opencascadejs"]`; WASM ayrı chunk.
- İstemci `cad/cadClient.ts`: `useCadBuild(project, level) → {status:"loading"|"ready"|"building"|"error", meshes, warnings}`, `exportModel(project, fmt): Promise<void>`.
```ts
export interface PartModule<P> {
  build(params: P, frame: ComponentFrame | null, ctx: PartCtx): Shape3D;
  cutter?(params: P, frame: ComponentFrame, ctx: PartCtx): Shape3D;
}
interface PartCtx { level: Level; placement?: NozzlePlacement; catalogs: Catalogs; orientation: "horizontal"|"vertical"; frames: ComponentFrame[] }
```
Parçalar global çerçevede döner; yerel +Z'de kurulanlar `cad/geom.ts` `orient(shape, placement)` ile yerleşir.

| Parça | Girdi | Katalog alanları |
|---|---|---|
| shellChain.ts (D06) | frames + head/cone; iç profil revolve, dış profil normal ofset (makeOffset; olmazsa ölçekli profil) | — |
| flangedNozzle.ts (D07) flanged/slip_on/pad_reinforced | nozzle, placement | flange: outside_diameter, thickness, raised_face_*, hub_*, length_wn/length_so, bore_so, bolt_circle_diameter, bolt_count, bolt_hole_diameter; pipe: od, walls |
| coupling.ts (D07) coupling/socket_welded | nozzle (coupling_form, rating_class) | coupling: body_od, top_od, length, socket_bore, socket_depth, bore, chamfer |
| pad.ts (D07) | `(host dış yüzey ⊕ t_pad) ∩ silindir(pad_od) − silindir(OD)` | — (yoksa varsayılan + CATALOG_MISS) |
| manway.ts (D07) | boyun + B16.5 flanş + kör kapak + saplama/somun + davit | flange + pipe |
| saddle.ts (D08) | aşınma plakası, web, 4 kaburga, taban; height_mm = kap dış altı → taban alt yüzü | width_mm, height_mm, contact_angle_deg ?? 120, thickness_mm ?? 12, base_plate_* |
| skirt.ts (D08) | üst uç sol bombe zEnd, aşağı height_mm; Ø = diameter_mm ?? host OD; taban halkası + ankraj delikleri | thickness_mm ?? 10, base_plate_*, anchor_bolt_* |
| legs.ts (D08) | θᵢ = i·360/leg_count; boru/profil; ped + taban plakası | leg_*, support_radius_mm ?? rOut + d/2, base_plate_* |

## 4. Katalog şemaları (src/data/)
Zarf: `{catalog, units:"mm", verified:false, source, license_note, revision, rows|sizes}`. `nps` ASCII: "1/2","3/4","1","1-1/4","1-1/2","2","2-1/2","3","4",…,"24"; `label` gösterim (`1½"`).
Yükleyici `src/data/catalogs.ts`: `pipe(nps)`, `flange(nps, cls)`, `coupling(nps, rating, form)` → yoksa undefined.
- pipe-nps.json: `wallSeries:["SCH5S","SCH10","SCH40","STD","SCH80","XS","SCH160","XXS"]`, `sizes:[{nps,label,dn,od,walls:{[s]:number|null}}]`. nozzle-catalog.json/nozzleCatalog.ts dokunulmaz.
- flange-b165.json: `rows:[{nps,dn,class,outside_diameter,thickness,raised_face_diameter,raised_face_height,hub_base_diameter,hub_weld_diameter,length_wn,length_so,bore_so,bolt_circle_diameter,bolt_count,bolt_hole_diameter,bolt_diameter}]`.
- coupling-catalog.json: `rows:[{nps,dn,rating:3000|6000,form:"full"|"half"|"weldolet",end:"socket"|"threaded",body_od,top_od|null,length,socket_bore|null,socket_depth|null,bore,chamfer}]`.
> Not (şef): D03 kendi şemasıyla yazdı; D03 dönüşü bu şemaya eşlenir ya da catalogs.ts adaptörü bu alan adlarını sunar.

## 5. Dosya sahipliği
| Paket | Dosyalar |
|---|---|
| D00b (şef checkpoint, W2 öncesi) | `geometryContract.ts` (yalnız tipler), package.json+lock (vitest, replicad, replicad-opencascadejs), vite.config.ts test bloğu |
| D04 (W2) | vesselModel.ts, store.ts, types.ts (Nozzle 2 alan), livePreview.tsx (yalnız nozzlePlacement çağrı yeri), packages/domain/src/domain/geometry.py (2 alan), tests/unit/test_nozzle_fields.py, src/__tests__/vesselModel.test.ts |
| D06 (W2) | src/cad/{cad.worker.ts, cadClient.ts, geom.ts, cache.ts, parts/index.ts, parts/shellChain.ts}, vite.config.ts (worker/optimizeDeps). D07/D08 parçaları için stub dosyaları açar (boş şekil + CATALOG_MISS) |
| D05 (W3) | src/geometrySteps/*, pages.tsx (GeometryPage ince kabuk), schematic.tsx, i18n.ts |
| D07 (W3) | src/cad/parts/{flangedNozzle,coupling,pad,manway}.ts |
| D08 (W3) | src/cad/parts/{saddle,skirt,legs}.ts, src/cad/export.ts, livePreview.tsx (worker mesh + lathe yer tutucu), viewer.tsx (exact sekmesi) |
W3 paketleri store.ts / vesselModel.ts'e dokunmaz; eksik aksiyon gerekirse şefe raporlar. `parts/index.ts` yalnız D06'nın.

## Doğrulama ölçütleri
- D04 vitest: SHELL-01(Ø1000,L2000) → CONE-01(1000→600,L500) → SHELL-02(Ø600): `frames[2].zStart = headDepth(L)+2000`, `frames[3].rInStart = 300`; genişleyen koni doğru yön; konide nozul normal.z > 0 (k<0); shell'de nozul sonucu eski formülle birebir (regresyon).
- pytest: yeni alanlar roundtrip'te korunur.

## Kararlar
1. Global Z sıfırı sol bombe kutbu; nozul axial_position host zStart'ından; location_mm sol teğet datumundan.
2. Koni yönü komşu çap eşleşmesinden (yeni alan yok).
3. Nozul'a `rating_class`, `coupling_form` (Pydantic dahil).
4. Etiket = kimlik; N/M/C önekleri; yeniden numaralandırma yok.
5. exact'te gövde fuse edilmez; STEP varlık başına adlı katı compound'u.
6. headDomeHeight tek kaynak.
7. PN flanşlar ve junction üretimi kapsam dışı.
