import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { useStore } from "./store";
import type { Head, Nozzle, RecognitionConfidence, RecognizedField, ShellSection, StepRecognition, VesselProject } from "./types";

const NOT_IN_FILE: Record<string, string> = {
  material: "Malzeme", design_pressure: "Tasarım basıncı", design_temperature: "Tasarım sıcaklığı",
  joint_efficiency: "Kaynak verimi", corrosion_allowance: "Korozyon payı",
};
const FIELD_LABELS: Record<string, string> = {
  inside_diameter: "İç çap", nominal_thickness: "Nominal kalınlık", tangent_length: "Tanjant boyu",
  type: "Bombe tipi", straight_flange_length: "Düz flanş boyu", crown_radius: "Taç yarıçapı",
  knuckle_radius: "Mafsal yarıçapı", outside_diameter: "Dış çap", neck_thickness: "Boyun kalınlığı",
  axial_position: "Eksenel konum", circumferential_angle: "Çevresel açı (θ)", outside_projection: "Dış çıkıntı",
};
const HEAD_TYPE_LABELS: Record<string, string> = {
  elliptical: "Eliptik 2:1", torispherical: "Torisferik", hemispherical: "Yarım küre", flat: "Düz",
};
const CONFIDENCE: Record<RecognitionConfidence, string> = { high: "Yüksek", medium: "Orta", low: "Düşük" };
const STATUS_LABELS: Record<StepRecognition["status"], string> = {
  RECOGNIZED: "Tanındı", PARTIAL: "Kısmen tanındı", BLOCKED: "CAD yok", REJECTED: "Reddedildi",
};

const SHELL_FIELDS = ["inside_diameter", "nominal_thickness", "tangent_length"] as const;
const HEAD_FIELDS = ["type", "inside_diameter", "nominal_thickness", "straight_flange_length", "crown_radius", "knuckle_radius"] as const;
const NOZZLE_FIELDS = ["outside_diameter", "inside_diameter", "neck_thickness", "axial_position", "circumferential_angle", "outside_projection"] as const;
type ShellField = (typeof SHELL_FIELDS)[number];
type HeadField = (typeof HEAD_FIELDS)[number];
type StepNozzle = StepRecognition["nozzles"][number];

// ---------------------------------------------------------------------------
// Forma yazma yolları — her yolun yazdığı alanların TAMAMI burada görünür.
// ---------------------------------------------------------------------------

/** Gövde: alanın kendisi + çap tutarlılığı. ID veya t değişirse saklı dış çap
 *  bayatlar → null yapılır (motor OD'yi ID+2t'den türetir). Gövde yalnız OD ile
 *  tanımlıysa (ID null) t değişiminde OD korunur; aksi hâlde iki çap da boş kalırdı. */
function shellPatch(shell: ShellSection, field: ShellField, value: number): Partial<ShellSection> {
  if (field === "inside_diameter") return { inside_diameter: value, outside_diameter: null };
  if (field === "nominal_thickness") {
    return shell.inside_diameter != null ? { nominal_thickness: value, outside_diameter: null } : { nominal_thickness: value };
  }
  return { tangent_length: value };
}

/** Bombe: ID/t değişirse saklı dış çap null (ID+2t'den türetilir; torisferik L'yi etkiler).
 *  ID veya tip değişirse eliptik derinlik h (crown_depth) de bayatlar → null. */
function headPatch(field: HeadField, value: number | string): Partial<Head> {
  switch (field) {
    case "type": return { type: value as Head["type"], crown_depth: null };
    case "inside_diameter": return { inside_diameter: value as number, outside_diameter: null, crown_depth: null };
    case "nominal_thickness": return { nominal_thickness: value as number, outside_diameter: null };
    case "straight_flange_length": return { straight_flange_length: value as number };
    // Rc/rk yalnız "custom" modda hesaba girer (design_code.py:35) — aksi halde sessizce yok sayılırdı.
    case "crown_radius": return { crown_radius: value as number, torispherical_geometry: "custom" };
    case "knuckle_radius": return { knuckle_radius: value as number, torispherical_geometry: "custom" };
  }
}

/** Nozul: STEP nozulu HER ZAMAN yeni nozul olarak eklenir; mevcut nozul asla ezilmez.
 *  addNozzle() varsayılanlarının üstüne yazılan alanlar yalnızca bunlardır. Geri kalanlar
 *  (tip, malzeme, korozyon payı, iç çıkıntı, takviye pedi) "Nozul ekle" varsayılanında kalır. */
function nozzlePatch(nozzle: StepNozzle, tag: string, hostId: string): Partial<Nozzle> {
  return {
    tag,
    host_component_id: hostId,
    inclination_angle: 0,
    head_position_diameter: null,
    size_designation: null, // katalog anma ölçüsü STEP'ten bilinmez (K5)
    outside_diameter: nozzle.outside_diameter.value,
    inside_diameter: nozzle.inside_diameter.value,
    neck_thickness: nozzle.neck_thickness.value,
    axial_position: nozzle.axial_position.value,
    circumferential_angle: nozzle.circumferential_angle.value,
    outside_projection: nozzle.outside_projection.value,
  };
}

// ---------------------------------------------------------------------------

type Value = number | string | null | undefined;
type Row = {
  label: string; field: string; recognized: RecognizedField<number | string>; current: Value;
  /** Uygulamanın yan etkisi (ör. türetilen alan sıfırlanır) — satırda gösterilir. */
  effect?: string;
};
/** selectKey'li satır tek tek onaylanır; nozul grubu ise tek onay kutusuyla bütün uygulanır. */
type FieldRow = Row & { selectKey: string; apply: () => void };
type Group =
  | { kind: "fields"; key: string; title: string; rows: FieldRow[] }
  | { kind: "nozzle"; key: string; title: string; selectKey: string; note: string; rows: Row[]; apply: () => void };
type Plan = { groups: Group[]; warnings: string[] };

function formatValue(field: string, value: Value): string {
  if (value == null) return "—";
  if (typeof value === "string") return HEAD_TYPE_LABELS[value] ?? value;
  const text = value.toLocaleString("tr-TR", { maximumFractionDigits: 2 });
  return `${text} ${field === "circumferential_angle" ? "°" : "mm"}`;
}

function initialSelection(plan: Plan): Record<string, boolean> {
  const initial: Record<string, boolean> = {};
  for (const group of plan.groups) {
    if (group.kind === "fields") group.rows.forEach((row) => { initial[row.selectKey] = row.recognized.confidence !== "low"; });
    else initial[group.selectKey] = group.rows.every((row) => row.recognized.confidence !== "low");
  }
  return initial;
}

export function StepImportDrawer({ file, onClose }: { file: File; onClose: () => void }) {
  const project = useStore((s) => s.project);
  const [result, setResult] = useState<StepRecognition | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  useEffect(() => {
    let cancelled = false;
    api.importStep(file).then((value) => {
      if (cancelled) return;
      setResult(value);
      setSelected(initialSelection(buildPlan(value, useStore.getState().project)));
    }).catch((caught: unknown) => {
      if (!cancelled) setError(caught instanceof Error ? caught.message : "STEP dosyası okunamadı.");
    });
    return () => { cancelled = true; };
  }, [file]);

  const plan = useMemo<Plan>(() => (result ? buildPlan(result, project) : { groups: [], warnings: [] }), [result, project]);
  const rejected = result?.status === "REJECTED" || result?.status === "BLOCKED";
  const selectKeys = plan.groups.flatMap((g) => (g.kind === "fields" ? g.rows.map((r) => r.selectKey) : [g.selectKey]));
  const anySelected = selectKeys.some((key) => selected[key]);
  const toggle = (key: string, value: boolean) => setSelected((s) => ({ ...s, [key]: value }));

  const apply = () => {
    if (!result || rejected) return;
    for (const group of plan.groups) {
      if (group.kind === "fields") group.rows.filter((row) => selected[row.selectKey]).forEach((row) => row.apply());
      else if (selected[group.selectKey]) group.apply();
    }
    useStore.getState().setDirty(true);
    onClose();
  };

  const renderValues = (row: Row) => <>
    <span className="step-row__line">
      <strong>{row.label}</strong>
      <span className={`step-badge step-badge--${row.recognized.confidence}`}>{CONFIDENCE[row.recognized.confidence]}</span>
    </span>
    <span className="step-row__values">
      <del>{formatValue(row.field, row.current)}</del>
      <span aria-hidden="true">→</span>
      <ins>{formatValue(row.field, row.recognized.value)}</ins>
    </span>
    {row.recognized.note && <small className="step-row__note">{row.recognized.note}</small>}
    {row.effect && <small className="step-row__effect">{row.effect}</small>}
  </>;

  return <>
    <button className="agent-backdrop" type="button" aria-label="Paneli kapat" onClick={onClose} />
    <aside className="agent-drawer" role="dialog" aria-modal="true" aria-label="STEP önerilerini onayla">
      <div className="agent-drawer__head">
        <div><span className="agent-drawer__eyebrow">MODEL İÇE AKTARMA</span><h2>{file.name}</h2></div>
        <button className="icon-btn" type="button" onClick={onClose} aria-label="Kapat">×</button>
      </div>
      <div className="agent-drawer__body">
        {!result && !error && <p className="agent-drawer__intro" role="status">Model tanınıyor…</p>}
        {error && <div className="agent-message agent-message--error" role="alert">{error}</div>}
        {result && <>
          <div className="agent-target"><span>Tanıma durumu</span><strong>{STATUS_LABELS[result.status]}</strong></div>
          {plan.warnings.length > 0 && <div className="agent-warnings" role="alert"><strong>Eşleme uyarıları</strong><ul>{plan.warnings.map((item, i) => <li key={i}>{item}</li>)}</ul></div>}
          {plan.groups.map((group) => <section key={group.key} className="step-group" aria-label={group.title}>
            <h3 className="step-group__title">{group.title}</h3>
            {group.kind === "fields"
              ? group.rows.map((row) => <label className="agent-change step-row" key={row.selectKey}>
                  <input type="checkbox" checked={!!selected[row.selectKey]} onChange={(e) => toggle(row.selectKey, e.target.checked)} />
                  <span className="step-row__main">{renderValues(row)}</span>
                </label>)
              : <>
                  <label className="agent-change step-row">
                    <input type="checkbox" checked={!!selected[group.selectKey]} onChange={(e) => toggle(group.selectKey, e.target.checked)} />
                    <span className="step-row__main">
                      <strong>Yeni nozul olarak eklenir</strong>
                      <small className="step-row__effect">{group.note}</small>
                    </span>
                  </label>
                  {group.rows.map((row) => <div className="agent-change step-row step-row--static" key={row.field}>
                    <span className="step-row__main">{renderValues(row)}</span>
                  </div>)}
                </>}
          </section>)}
          {(result.unrecognized.length > 0 || result.warnings.length > 0) && <div className="agent-warnings"><strong>Uyarılar</strong><ul>{result.unrecognized.map((item, i) => <li key={`u${i}`}>{item.feature}: {item.reason}</li>)}{result.warnings.map((item, i) => <li key={`w${i}`}>{item}</li>)}</ul></div>}
          {result.not_in_file.length > 0 && <div className="agent-warnings"><strong>Dosyada yok — elle girin</strong><ul>{result.not_in_file.map((field) => <li key={field}>{NOT_IN_FILE[field] ?? field}</li>)}</ul></div>}
          <div className="agent-actions">
            <button className="btn" type="button" onClick={onClose}>İptal</button>
            <button className="btn btn--primary" type="button" disabled={rejected || !anySelected} onClick={apply}>Seçilenleri uygula</button>
          </div>
        </>}
      </div>
    </aside>
  </>;
}

function buildPlan(result: StepRecognition, project: VesselProject): Plan {
  const { updateShell, updateHead, addNozzle, updateNozzle } = useStore.getState();
  const groups: Group[] = [];
  const warnings: string[] = [];

  // --- Gövde: ilk gövde kesiti, alan alan onay ---
  const shell = project.shell_sections[0];
  if (result.shell && shell) {
    const shellId = shell.section_id;
    const linked = (project.diameter_relation ?? "linked") === "linked" && project.heads.length > 0;
    groups.push({
      kind: "fields", key: "shell", title: `Gövde (${shellId})`,
      rows: SHELL_FIELDS.map((field) => {
        const recognized = result.shell![field];
        const derivesOd = field === "inside_diameter" || (field === "nominal_thickness" && shell.inside_diameter != null);
        return {
          selectKey: `shell:${field}`, label: FIELD_LABELS[field], field, recognized, current: shell[field],
          effect: [
            derivesOd ? "Dış çap ID+2t'den yeniden türetilir." : field === "nominal_thickness" && "İç çap dış çaptan (OD−2t) türetilir.",
            field === "inside_diameter" && linked && "Bağlı çap modu: bombe iç çapları bu satırla değişmez — bombe satırlarını ayrıca onaylayın.",
          ].filter(Boolean).join(" ") || undefined,
          apply: () => {
            const fresh = useStore.getState().project.shell_sections.find((s) => s.section_id === shellId);
            if (fresh) updateShell(shellId, shellPatch(fresh, field, recognized.value));
          },
        };
      }),
    });
  }

  // --- Bombeler: sol/sağ eşlemesi component_sequence'a göre ---
  const headRefs = (project.component_sequence ?? []).filter((ref) => ref.component_type === "head");
  const findHead = (id?: string) => project.heads.find((h) => h.head_id === id);
  const leftHead = findHead(headRefs[0]?.component_id) ?? project.heads[0];
  const rightHead = findHead(headRefs[headRefs.length - 1]?.component_id) ?? project.heads[project.heads.length - 1];
  const singleHead = project.heads.length < 2 || leftHead === rightHead;
  const seqOrder = headRefs.map((ref) => ref.component_id).filter((id) => findHead(id));
  const listOrder = project.heads.map((h) => h.head_id).filter((id) => seqOrder.includes(id));
  if (seqOrder.join("|") !== listOrder.join("|")) {
    warnings.push(`Bileşen sırası ile bombe listesi sırası çelişiyor; sol/sağ eşlemesi bileşen sırasına göre yapıldı (sol: ${leftHead?.head_id ?? "—"}, sağ: ${rightHead?.head_id ?? "—"}). Hedefleri kontrol edin.`);
  }
  for (const head of result.heads) {
    if (head.side === "right" && singleHead) {
      if (project.heads.length > 0) warnings.push("Projede tek bombe var; sağ bombe önerisi uygulanmadı.");
      continue;
    }
    const target = head.side === "left" ? leftHead : rightHead;
    if (!target) { warnings.push("Projede bombe yok; bombe önerileri uygulanmadı."); continue; }
    const headId = target.head_id;
    const rows: FieldRow[] = [];
    for (const field of HEAD_FIELDS) {
      const recognized = head[field];
      if (!recognized) continue;
      const clearsH = (field === "type" || field === "inside_diameter") && target.crown_depth != null;
      const derivesOd = field === "inside_diameter" || field === "nominal_thickness";
      const effect = [derivesOd && "Dış çap ID+2t'den yeniden türetilir.", clearsH && "Eliptik derinlik (h) sıfırlanır."].filter(Boolean).join(" ") || undefined;
      rows.push({
        selectKey: `head:${head.side}:${field}`, label: FIELD_LABELS[field], field, recognized, current: target[field], effect,
        apply: () => updateHead(headId, headPatch(field, recognized.value)),
      });
    }
    groups.push({ kind: "fields", key: `head:${head.side}`, title: `${head.side === "left" ? "Sol" : "Sağ"} bombe (${headId})`, rows });
  }

  // --- Nozullar: her biri YENİ nozul, tek onay kutusu, etiket benzersiz ---
  const hostId = shell?.section_id;
  if (result.nozzles.length > 0 && !hostId) warnings.push("Projede gövde kesiti yok; nozul önerileri uygulanmadı.");
  const usedTags = new Set(project.nozzles.map((n) => n.tag));
  if (hostId) result.nozzles.forEach((nozzle, index) => {
    const tag = uniqueTag(nozzle.tag, usedTags);
    usedTags.add(tag);
    groups.push({
      kind: "nozzle", key: `nozzle:${index}`, selectKey: `nozzle:${index}`,
      title: tag === nozzle.tag ? `Nozul ${tag}` : `Nozul ${tag} (dosyada ${nozzle.tag})`,
      note: `Mevcut nozullara dokunulmaz. Host: ${hostId}, eğim 0°, anma ölçüsü boş. Tip, malzeme, korozyon payı ve iç çıkıntı varsayılan kalır — elle kontrol edin.`,
      rows: NOZZLE_FIELDS.map((field) => ({ label: FIELD_LABELS[field], field, recognized: nozzle[field], current: null })),
      apply: () => {
        addNozzle();
        updateNozzle(useStore.getState().project.nozzles.length - 1, nozzlePatch(nozzle, tag, hostId));
      },
    });
  });

  return { groups, warnings };
}

/** "N1" projede varsa "STEP-N1", o da varsa "STEP-N1-2"… */
function uniqueTag(tag: string, used: Set<string>): string {
  if (!used.has(tag)) return tag;
  let candidate = `STEP-${tag}`;
  for (let n = 2; used.has(candidate); n++) candidate = `STEP-${tag}-${n}`;
  return candidate;
}
