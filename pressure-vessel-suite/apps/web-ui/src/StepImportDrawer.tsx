import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { useStore } from "./store";
import type { RecognitionConfidence, RecognizedField, StepRecognition, VesselProject } from "./types";

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

type Value = number | string | null | undefined;
type Row = {
  key: string; group: string; label: string; field: string;
  recognized: RecognizedField<number | string>; current: Value; apply: () => void;
};

function formatValue(field: string, value: Value): string {
  if (value == null) return "—";
  if (typeof value === "string") return HEAD_TYPE_LABELS[value] ?? value;
  const text = value.toLocaleString("tr-TR", { maximumFractionDigits: 2 });
  return `${text} ${field === "circumferential_angle" ? "°" : "mm"}`;
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
      const initial: Record<string, boolean> = {};
      buildRows(value, useStore.getState().project).forEach((row) => { initial[row.key] = row.recognized.confidence !== "low"; });
      setSelected(initial);
    }).catch((caught: unknown) => {
      if (!cancelled) setError(caught instanceof Error ? caught.message : "STEP dosyası okunamadı.");
    });
    return () => { cancelled = true; };
  }, [file]);

  const rows = useMemo(() => (result ? buildRows(result, project) : []), [result, project]);
  const groups = useMemo(() => {
    const map = new Map<string, Row[]>();
    rows.forEach((row) => map.set(row.group, [...(map.get(row.group) ?? []), row]));
    return [...map.entries()];
  }, [rows]);
  const rejected = result?.status === "REJECTED" || result?.status === "BLOCKED";
  const apply = () => {
    if (!result || rejected) return;
    rows.filter((row) => selected[row.key]).forEach((row) => row.apply());
    useStore.getState().setDirty(true);
    onClose();
  };

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
          {groups.map(([group, items]) => <section key={group} className="step-group" aria-label={group}>
            <h3 className="step-group__title">{group}</h3>
            {items.map((row) => <label className="agent-change step-row" key={row.key}>
              <input type="checkbox" checked={!!selected[row.key]} onChange={(e) => setSelected((s) => ({ ...s, [row.key]: e.target.checked }))} />
              <span className="step-row__main">
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
              </span>
            </label>)}
          </section>)}
          {(result.unrecognized.length > 0 || result.warnings.length > 0) && <div className="agent-warnings"><strong>Uyarılar</strong><ul>{result.unrecognized.map((item, i) => <li key={`u${i}`}>{item.feature}: {item.reason}</li>)}{result.warnings.map((item, i) => <li key={`w${i}`}>{item}</li>)}</ul></div>}
          {result.not_in_file.length > 0 && <div className="agent-warnings"><strong>Dosyada yok — elle girin</strong><ul>{result.not_in_file.map((field) => <li key={field}>{NOT_IN_FILE[field] ?? field}</li>)}</ul></div>}
          <div className="agent-actions">
            <button className="btn" type="button" onClick={onClose}>İptal</button>
            <button className="btn btn--primary" type="button" disabled={rejected || !rows.some((row) => selected[row.key])} onClick={apply}>Seçilenleri uygula</button>
          </div>
        </>}
      </div>
    </aside>
  </>;
}

function buildRows(result: StepRecognition, project: VesselProject): Row[] {
  const { updateShell, updateHead, addNozzle, updateNozzle } = useStore.getState();
  const rows: Row[] = [];
  const shell = project.shell_sections[0];
  if (result.shell && shell) for (const field of ["inside_diameter", "nominal_thickness", "tangent_length"] as const) {
    const recognized = result.shell[field];
    rows.push({ key: `shell:${field}`, group: "Gövde", label: FIELD_LABELS[field], field, recognized, current: shell[field], apply: () => updateShell(shell.section_id, { [field]: recognized.value }) });
  }
  const headRefs = (project.component_sequence ?? []).filter((ref) => ref.component_type === "head");
  const findHead = (id?: string) => project.heads.find((h) => h.head_id === id);
  const leftHead = findHead(headRefs[0]?.component_id) ?? project.heads[0];
  const rightHead = findHead(headRefs[headRefs.length - 1]?.component_id) ?? project.heads[project.heads.length - 1];
  for (const head of result.heads) {
    const target = head.side === "left" ? leftHead : rightHead;
    if (!target) continue;
    const group = head.side === "left" ? "Sol bombe" : "Sağ bombe";
    for (const field of ["type", "inside_diameter", "nominal_thickness", "straight_flange_length", "crown_radius", "knuckle_radius"] as const) {
      const recognized = head[field];
      if (!recognized) continue;
      rows.push({ key: `head:${head.side}:${field}`, group, label: FIELD_LABELS[field], field, recognized, current: target[field], apply: () => updateHead(target.head_id, { [field]: recognized.value }) });
    }
  }
  result.nozzles.forEach((nozzle) => {
    const existing = project.nozzles.find((item) => item.tag === nozzle.tag);
    for (const field of ["outside_diameter", "inside_diameter", "neck_thickness", "axial_position", "circumferential_angle", "outside_projection"] as const) {
      const recognized = nozzle[field];
      rows.push({
        key: `nozzle:${nozzle.tag}:${field}`, group: `Nozul ${nozzle.tag}`, label: FIELD_LABELS[field], field, recognized,
        current: existing ? existing[field] : null,
        apply: () => {
          let index = useStore.getState().project.nozzles.findIndex((item) => item.tag === nozzle.tag);
          if (index < 0) { addNozzle(); index = useStore.getState().project.nozzles.length - 1; }
          updateNozzle(index, { tag: nozzle.tag, [field]: recognized.value });
        },
      });
    }
  });
  return rows;
}
