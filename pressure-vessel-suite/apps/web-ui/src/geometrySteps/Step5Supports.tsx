// 3.5 Mesnetler: yatayda 2 eyer önerisi, dikeyde etek veya 3/4 ayak.

import { useMemo, useState } from "react";
import { useStore } from "../store";
import { componentFrames, tangentDatum } from "../vesselModel";
import { ORIENTATION_TR, SUPPORT_TYPE_TR } from "../i18n";
import { SelectField } from "../components";
import type { Support } from "../types";
import { RField, Section, fmt, frameLabel, hostFrames } from "./shared";

export function Step5Supports() {
  const project = useStore((s) => s.project);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const addSupport = useStore((s) => s.addSupport);
  const updateSupport = useStore((s) => s.updateSupport);
  const removeSupport = useStore((s) => s.removeSupport);

  const frames = useMemo(() => componentFrames(project), [project]);
  const { left, right } = tangentDatum(frames);
  const span = Math.max(right - left, 0);
  const vertical = project.orientation === "vertical";
  const [addType, setAddType] = useState<Support["type"]>(vertical ? "skirt" : "saddle");

  const patchById = (id: string, patch: Partial<Support>) => {
    const idx = useStore.getState().project.supports.findIndex((s) => s.support_id === id);
    if (idx >= 0) updateSupport(idx, patch);
  };

  const shellAt = (loc: number) =>
    frames.find((f) => f.kind === "shell" && f.zStart - left <= loc && loc <= f.zEnd - left)
    ?? frames.find((f) => f.kind === "shell");

  const suggestSaddles = () => {
    let first = "";
    for (const frac of [0.2, 0.8]) {
      const loc = Math.round(span * frac);
      const id = addSupport("saddle", shellAt(loc)?.id);
      patchById(id, { location_mm: loc });
      first ||= id;
    }
    setSelection({ kind: "support", id: first });
  };

  const addLegs = (count: number) => {
    const id = addSupport("leg");
    patchById(id, { leg_count: count });
    setSelection({ kind: "support", id });
  };

  const sel = selection?.kind === "support" ? project.supports.find((s) => s.support_id === selection.id) : undefined;
  const selIndex = sel ? project.supports.indexOf(sel) : -1;
  const host = sel ? frames.find((f) => f.id === sel.host_component_id) : undefined;
  const hostLo = host ? host.zStart - left : 0;
  const hostHi = host ? host.zEnd - left : span;

  return (
    <div className="gw-step">
      <Section title="Öneri" meta={`Yönelim: ${ORIENTATION_TR[project.orientation] ?? project.orientation}`}>
        {vertical ? (
          <div className="gw-suggest">
            <p className="gw-note">Dikey kap: etek ya da 3 / 4 ayak önerilir.</p>
            <div className="gw-chips">
              <button type="button" className="btn btn--ghost btn--sm" onClick={() => {
                const id = addSupport("skirt"); setSelection({ kind: "support", id });
              }}>Etek ekle</button>
              <button type="button" className="btn btn--ghost btn--sm" onClick={() => addLegs(3)}>3 ayak</button>
              <button type="button" className="btn btn--ghost btn--sm" onClick={() => addLegs(4)}>4 ayak</button>
            </div>
          </div>
        ) : (
          <div className="gw-suggest">
            <p className="gw-note">Yatay kap: teğet-teğet aralığın %20 ve %80 noktalarına 2 eyer (Zick).</p>
            <button type="button" className="btn btn--ghost btn--sm" onClick={suggestSaddles}>2 eyer öner</button>
          </div>
        )}
        <div className="gw-addrow">
          <SelectField label="Başka destek ekle" value={addType}
            options={(Object.keys(SUPPORT_TYPE_TR) as Support["type"][]).map((t) => ({ value: t, label: SUPPORT_TYPE_TR[t] }))}
            onChange={(v) => setAddType(v as Support["type"])} />
          <button type="button" className="btn btn--primary btn--sm" onClick={() => {
            const id = addSupport(addType); setSelection({ kind: "support", id });
          }}>＋ Ekle</button>
        </div>
        {(vertical && addType === "saddle") || (!vertical && addType !== "saddle") ? (
          <p className="gw-note gw-note--warn">
            {vertical ? "Dikey kapta eyer olağan değildir." : "Yatay kapta etek/ayak olağan değildir."} Yine de eklenebilir.
          </p>
        ) : null}
      </Section>

      <Section title="Mesnetler" meta={`${project.supports.length} adet`}>
        {project.supports.length === 0 ? (
          <p className="gw-empty">Destek tanımlı değil — destek gerilme kontrolü yapılmaz.</p>
        ) : (
          <table className="gw-table">
            <thead>
              <tr><th>Kimlik</th><th>Tip</th><th>Host</th><th>Konum</th><th>Yük.</th><th /></tr>
            </thead>
            <tbody>
              {project.supports.map((s, index) => {
                const isSel = selection?.kind === "support" && selection.id === s.support_id;
                return (
                  <tr key={s.support_id} className={isSel ? "is-active" : undefined} tabIndex={0} aria-selected={isSel}
                    onClick={() => setSelection({ kind: "support", id: s.support_id })}
                    onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setSelection({ kind: "support", id: s.support_id }); } }}>
                    <td><b>{s.support_id}</b></td>
                    <td>{SUPPORT_TYPE_TR[s.type] ?? s.type}</td>
                    <td>{s.host_component_id ?? "—"}</td>
                    <td>{s.type === "skirt" ? "—" : fmt(s.location_mm, 0)}</td>
                    <td>{fmt(s.height_mm, 0)}</td>
                    <td>
                      <button type="button" className="gw-del" aria-label={`${s.support_id} sil`}
                        onClick={(e) => { e.stopPropagation(); removeSupport(index); }}>✕</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {sel && (
          <div className="gw-editor">
            <div className="gw-editor__head"><b>{sel.support_id} — {SUPPORT_TYPE_TR[sel.type]}</b>
              <span className="gw-editor__meta">hesap girdileri (Zick K, ankraj…) aşağıdaki «Destek ayrıntıları»nda</span>
            </div>
            <div className="grid">
              <SelectField label="Host bileşen" value={sel.host_component_id ?? ""}
                options={[
                  { value: "", label: "— seç —" },
                  ...(sel.type === "saddle" ? frames.filter((f) => f.kind === "shell") : hostFrames(frames))
                    .map((f) => ({ value: f.id, label: frameLabel(f) })),
                ]}
                onChange={(v) => updateSupport(selIndex, { host_component_id: v || null })} />
              {sel.type !== "skirt" && (
                <RField label={sel.type === "saddle" ? "Konum (sol teğetten)" : "Taban kotu (sol teğetten)"} unit="mm"
                  value={sel.location_mm}
                  min={sel.type === "saddle" ? Math.max(hostLo, 0) : undefined}
                  max={sel.type === "saddle" ? Math.min(hostHi, span) : undefined}
                  onChange={(v) => updateSupport(selIndex, { location_mm: v })} />
              )}
              <RField label="Yükseklik" unit="mm" value={sel.height_mm} min={50} max={sel.type === "saddle" ? 3000 : 20000}
                onChange={(v) => updateSupport(selIndex, { height_mm: v })} />
              {sel.type === "saddle" && (
                <>
                  <RField label="Genişlik" unit="mm" value={sel.width_mm} min={50} max={2000}
                    onChange={(v) => updateSupport(selIndex, { width_mm: v })} />
                  <RField label="Temas (sarma) açısı" unit="°" value={sel.contact_angle_deg ?? 120} min={120} max={180}
                    onChange={(v) => updateSupport(selIndex, { contact_angle_deg: v })} />
                </>
              )}
              {sel.type === "leg" && (
                <>
                  <RField label="Ayak sayısı" value={sel.leg_count ?? 4} min={3} max={8} step={1}
                    onChange={(v) => updateSupport(selIndex, { leg_count: Math.round(v) })} />
                  <RField label="Ayak yarıçapı (support_radius)" unit="mm" value={sel.support_radius_mm ?? 0} min={0}
                    max={host ? 2 * host.rOutStart : undefined}
                    note="0 = otomatik (dış yarıçap + ayak çapı/2)"
                    onChange={(v) => updateSupport(selIndex, { support_radius_mm: v > 0 ? v : null })} />
                </>
              )}
            </div>
            {sel.type === "skirt" && (
              <p className="gw-note">Etek sol bombenin teğet hattından aşağı doğru uzanır; konum girdisi kullanılmaz.</p>
            )}
          </div>
        )}
      </Section>
    </div>
  );
}
