import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { useStore } from "./store";
import type { RecognizedField, StepRecognition } from "./types";

const NOT_IN_FILE: Record<string, string> = {
  material: "Malzeme", design_pressure: "Tasarım basıncı", design_temperature: "Tasarım sıcaklığı",
  joint_efficiency: "Kaynak verimi", corrosion_allowance: "Korozyon payı",
};
type Row = { key: string; label: string; field: RecognizedField<any>; current: unknown; apply: () => void };

export function StepImportDrawer({ file, onClose }: { file: File; onClose: () => void }) {
  const { project, updateShell, updateHead, addNozzle, updateNozzle, setDirty } = useStore();
  const [result, setResult] = useState<StepRecognition | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", closeOnEscape);
    api.importStep(file).then((value) => {
      setResult(value);
      const initial: Record<string, boolean> = {};
      rowsFor(value, project, updateShell, updateHead, addNozzle, updateNozzle).forEach((row) => { initial[row.key] = row.field.confidence !== "low"; });
      setSelected(initial);
    }).catch((caught: any) => setError(caught?.message ?? "STEP dosyası okunamadı."));
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [file]);
  const rows = useMemo(() => result ? rowsFor(result, project, updateShell, updateHead, addNozzle, updateNozzle) : [], [result, project]);
  const rejected = result?.status === "REJECTED" || result?.status === "BLOCKED";
  const apply = () => {
    if (!result || rejected) return;
    rows.filter((row) => selected[row.key]).forEach((row) => row.apply());
    setDirty(true);
    onClose();
  };
  if (!result && !error) return <div className="agent-drawer" role="dialog" aria-label="STEP içe aktarımı"><div className="agent-drawer__body">Model tanınıyor…</div></div>;
  const status = result?.status === "RECOGNIZED" ? "Tanındı" : result?.status === "PARTIAL" ? "Kısmen tanındı" : result?.status === "BLOCKED" ? "CAD yok" : "Reddedildi";
  return <><button className="agent-backdrop" aria-label="Paneli kapat" onClick={onClose} /><aside className="agent-drawer" role="dialog" aria-modal="true" aria-label="STEP önerilerini onayla">
    <div className="agent-drawer__head"><div><span className="agent-drawer__eyebrow">MODEL İÇE AKTARMA</span><h2>{file.name}</h2></div><button className="icon-btn" onClick={onClose} aria-label="Kapat">×</button></div>
    <div className="agent-drawer__body">{error ? <div className="agent-message agent-message--error" role="alert">{error}</div> : result && <>
      <div className="agent-target"><span>Tanıma durumu</span><strong>{status}</strong></div>
      {rows.map((row) => <label className="agent-change" key={row.key} style={{ display: "block" }}><input type="checkbox" checked={!!selected[row.key]} onChange={(e) => setSelected((s) => ({ ...s, [row.key]: e.target.checked }))} /> {row.label} · <strong>{String(row.field.value)} mm</strong> · mevcut: {String(row.current ?? "—")} · {row.field.confidence}</label>)}
      {(result.unrecognized.length > 0 || result.warnings.length > 0) && <div className="agent-warnings"><strong>Uyarılar</strong><ul>{result.unrecognized.map((item, i) => <li key={`u${i}`}>{item.feature}: {item.reason}</li>)}{result.warnings.map((item, i) => <li key={`w${i}`}>{item}</li>)}</ul></div>}
      {result.not_in_file.length > 0 && <div className="agent-warnings"><strong>Dosyada yok — elle girin</strong><ul>{result.not_in_file.map((field) => <li key={field}>{NOT_IN_FILE[field] ?? field}</li>)}</ul></div>}
      <div className="agent-actions"><button className="btn" onClick={onClose}>İptal</button><button className="btn btn--primary" disabled={rejected || !rows.some((row) => selected[row.key])} onClick={apply}>Seçilenleri uygula</button></div>
    </>}</div>
  </aside></>;
}

function rowsFor(result: StepRecognition, project: ReturnType<typeof useStore.getState> extends never ? never : any, updateShell: any, updateHead: any, addNozzle: any, updateNozzle: any): Row[] {
  const rows: Row[] = [];
  const shell = project.shell_sections[0];
  if (result.shell && shell) for (const field of ["inside_diameter", "nominal_thickness", "tangent_length"] as const) {
    const recognized = result.shell[field]; rows.push({ key: `shell:${field}`, label: `Gövde ${field}`, field: recognized, current: shell[field], apply: () => updateShell(shell.section_id, { [field]: recognized.value }) });
  }
  for (const head of result.heads) {
    const target = head.side === "left" ? project.heads[0] : project.heads[project.heads.length - 1]; if (!target) continue;
    for (const field of ["type", "inside_diameter", "nominal_thickness", "straight_flange_length", "crown_radius", "knuckle_radius"] as const) {
      const recognized = head[field]; if (!recognized) continue;
      rows.push({ key: `head:${head.side}:${field}`, label: `${head.side === "left" ? "Sol" : "Sağ"} bombe ${field}`, field: recognized, current: target[field], apply: () => updateHead(target.head_id, { [field]: recognized.value }) });
    }
  }
  result.nozzles.forEach((nozzle) => {
    const idx = project.nozzles.findIndex((item: any) => item.tag === nozzle.tag);
    for (const field of ["outside_diameter", "inside_diameter", "neck_thickness", "axial_position", "circumferential_angle", "outside_projection"] as const) {
      const recognized = nozzle[field]; rows.push({ key: `nozzle:${nozzle.tag}:${field}`, label: `Nozul ${nozzle.tag} ${field}`, field: recognized, current: idx >= 0 ? project.nozzles[idx][field] : "yeni", apply: () => { let state = useStore.getState(); let index = state.project.nozzles.findIndex((item) => item.tag === nozzle.tag); if (index < 0) { addNozzle(); state = useStore.getState(); index = state.project.nozzles.length - 1; } updateNozzle(index, { tag: nozzle.tag, [field]: recognized.value }); } });
    }
  });
  return rows;
}
