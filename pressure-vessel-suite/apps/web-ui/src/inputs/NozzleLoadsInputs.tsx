// P07 — Nozul dış yükleri (WRC 537 / 297) girdi paneli.
// Eğri değerleri programda YOK (telifli bülten, K6): kullanıcı lisanslı bültenden okuyup girer;
// boş bırakılan değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner.
import { useState } from "react";
import { useStore } from "../store";
import { AccordionSection, NumField, SelectField } from "../components";
import type { NozzleLoadAnalysis, NozzleLoadEntry } from "../types";

const COMPONENTS = ["Nphi", "Nx", "Mphi", "Mx"] as const;
const COEFF_ROWS: { load: string; group: string; label: string }[] = [
  { load: "P", group: "AB", label: "P (radyal) — A/B" },
  { load: "P", group: "CD", label: "P (radyal) — C/D" },
  { load: "MC", group: "CD", label: "Mc — C/D" },
  { load: "ML", group: "AB", label: "ML — A/B" },
];

const LOAD_FIELDS: { key: keyof NozzleLoadEntry; label: string; unit: string; help: string }[] = [
  { key: "Fr_N", label: "Fr (radyal)", unit: "N", help: "Radyal kuvvet; + = dışa çekme." },
  { key: "Vc_N", label: "Vc (çevresel kesme)", unit: "N", help: "Çevre yönünde kesme kuvveti." },
  { key: "VL_N", label: "VL (boyuna kesme)", unit: "N", help: "Kap ekseni yönünde kesme kuvveti." },
  { key: "Mc_Nmm", label: "Mc (çevresel moment)", unit: "N·mm", help: "Çevre doğrultusunda eğen moment." },
  { key: "ML_Nmm", label: "ML (boyuna moment)", unit: "N·mm", help: "Kap ekseni doğrultusunda eğen moment." },
  { key: "Mt_Nmm", label: "Mt (burulma)", unit: "N·mm", help: "Nozul ekseni etrafında burulma momenti." },
];

const emptyEntry = (tag: string): NozzleLoadEntry => ({
  nozzle_tag: tag, method: "WRC537", Fr_N: 0, Vc_N: 0, VL_N: 0, Mc_Nmm: 0, ML_Nmm: 0, Mt_Nmm: 0,
  coefficients: null, Kn: 1, Kb: 1, include_pressure: true,
});

export function NozzleLoadsInputs() {
  const project = useStore((s) => s.project);
  const setProject = useStore((s) => s.setProject);
  const [open, setOpen] = useState(false);
  const [tag, setTag] = useState<string>("");
  const analysis: NozzleLoadAnalysis = project.nozzle_loads ?? { entries: [], stress_criterion: "tresca" };
  const selectedTag = tag || project.nozzles[0]?.tag || "";
  const entry = analysis.entries.find((e) => e.nozzle_tag === selectedTag);

  const write = (next: NozzleLoadAnalysis) =>
    setProject((p) => ({ ...p, nozzle_loads: next.entries.length ? next : null }));
  const patch = (upd: Partial<NozzleLoadEntry>) => {
    const base = entry ?? emptyEntry(selectedTag);
    const merged = { ...base, ...upd };
    const others = analysis.entries.filter((e) => e.nozzle_tag !== selectedTag);
    write({ ...analysis, entries: [...others, merged] });
  };
  const setCoeff = (key: string, raw: string) => {
    const coeffs = { ...(entry?.coefficients ?? {}) };
    const n = parseFloat(raw);
    if (raw.trim() === "" || !Number.isFinite(n)) delete coeffs[key];
    else coeffs[key] = n;
    patch({ coefficients: Object.keys(coeffs).length ? coeffs : null });
  };

  return (
    <AccordionSection id="nozzle-loads" open={open} onToggle={() => setOpen(!open)}
      title="Nozul dış yükleri (WRC 537 / 297)"
      meta={`${analysis.entries.length} yük takımı`}
      desc="Boru hattı yüklerini girin. WRC eğri değerleri programda yoktur (telifli bülten); lisanslı bültenden okuyup girin — boş değer sıfır sayılmaz, sonuç 'kod verisi bekliyor' olur.">
      {project.nozzles.length === 0 && <p className="field__hint">Önce bir nozul tanımlayın.</p>}
      {project.nozzles.length > 0 && (
        <div className="grid" style={{ marginTop: 14 }}>
          <SelectField label="Nozul" value={selectedTag}
            options={project.nozzles.map((n) => ({ value: n.tag, label: n.tag }))}
            onChange={setTag} />
          <SelectField label="Yöntem" value={entry?.method ?? "WRC537"}
            options={[{ value: "WRC537", label: "WRC 537 (gövde tarafı)" },
                      { value: "WRC297", label: "WRC 297 (gövde + nozul)" }]}
            onChange={(v) => patch({ method: v as NozzleLoadEntry["method"], coefficients: null })}
            help="WRC 297 bu sürümde eğri normalizasyonu doğrulanmadığı için her zaman 'kod verisi bekliyor' döner." />
          <SelectField label="Eşdeğer gerilme" value={analysis.stress_criterion}
            options={[{ value: "tresca", label: "Tresca (WRC 107)" }, { value: "von_mises", label: "von Mises" }]}
            onChange={(v) => write({ ...analysis, stress_criterion: v as NozzleLoadAnalysis["stress_criterion"] })} />
          {LOAD_FIELDS.map((f) => (
            <NumField key={f.key} label={f.label} unit={f.unit} help={f.help}
              value={(entry?.[f.key] as number | undefined) ?? 0}
              onChange={(v) => patch({ [f.key]: v } as Partial<NozzleLoadEntry>)} />
          ))}
          <NumField label="Kn (membran yığılma)" value={entry?.Kn ?? 1} onChange={(v) => patch({ Kn: v >= 1 ? v : 1 })} />
          <NumField label="Kb (eğilme yığılma)" value={entry?.Kb ?? 1} onChange={(v) => patch({ Kb: v >= 1 ? v : 1 })} />
          {entry && (
            <button type="button" className="btn btn--ghost btn--sm"
              onClick={() => write({ ...analysis, entries: analysis.entries.filter((e) => e.nozzle_tag !== selectedTag) })}>
              Bu nozulun yük takımını sil
            </button>
          )}
        </div>
      )}
      {entry && entry.method === "WRC537" && (
        <table className="table" style={{ marginTop: 14 }}>
          <thead>
            <tr><th>Eğri (bülten okuması)</th>{COMPONENTS.map((c) => <th key={c}>{c}</th>)}</tr>
          </thead>
          <tbody>
            {COEFF_ROWS.map((row) => (
              <tr key={`${row.load}.${row.group}`}>
                <td>{row.label}</td>
                {COMPONENTS.map((c) => {
                  const key = `${row.load}.${c}.${row.group}`;
                  const v = entry.coefficients?.[key];
                  return (
                    <td key={key}>
                      <input className="input" type="number" step="any" aria-label={key}
                        value={v ?? ""} onChange={(e) => setCoeff(key, e.target.value)} />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </AccordionSection>
  );
}
