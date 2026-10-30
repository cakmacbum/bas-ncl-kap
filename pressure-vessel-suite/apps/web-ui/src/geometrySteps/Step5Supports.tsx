// 3.5 Mesnetler: yatayda 2 eyer önerisi, dikeyde etek veya 3/4 ayak.

import { useMemo, useState } from "react";
import { useStore } from "../store";
import { componentFrames, tangentDatum } from "../vesselModel";
import { ORIENTATION_TR, SUPPORT_TYPE_TR } from "../i18n";
import { SelectField } from "../components";
import type { Support } from "../types";
import { listUpn } from "../data/catalogs";
import { Group, RField, Section, StepIntro, fmt, frameLabel, hostFrames, legDefaults } from "./shared";
import { UpnBadge } from "./IssuesPanel";
import { addLegSupport, makeVertical, matchingUpn, upnPatch } from "./legActions";

const SECTION_TR: Record<string, string> = {
  channel: "U profil (UPN)", pipe: "Boru", box: "Kutu profil", angle: "Köşebent (L)",
};

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

  const addLegs = (count: number) => { addLegSupport(count); };

  const sel = selection?.kind === "support" ? project.supports.find((s) => s.support_id === selection.id) : undefined;
  const selIndex = sel ? project.supports.indexOf(sel) : -1;
  const host = sel ? frames.find((f) => f.id === sel.host_component_id) : undefined;
  const hostLo = host ? host.zStart - left : 0;
  const hostHi = host ? host.zEnd - left : span;
  const upd = (patch: Partial<Support>) => updateSupport(selIndex, patch);
  const legD = sel?.type === "leg" ? legDefaults(sel) : null;
  const upnRows = listUpn();

  const hostSelect = sel && (
    <SelectField label="Host bileşen" value={sel.host_component_id ?? ""}
      options={[
        { value: "", label: "— seç —" },
        ...(sel.type === "saddle" ? frames.filter((f) => f.kind === "shell") : hostFrames(frames))
          .map((f) => ({ value: f.id, label: frameLabel(f) })),
      ]}
      onChange={(v) => updateSupport(selIndex, { host_component_id: v || null })} />
  );

  return (
    <div className="gw-step">
      <StepIntro>Destek tipini ekle; seçili desteğin ana ölçüleri açık, ped ve taban sacı ayrıntılarda.</StepIntro>

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
            <div className="gw-chips">
              <button type="button" className="btn btn--ghost btn--sm" onClick={suggestSaddles}>2 eyer öner</button>
              <button type="button" className="btn btn--ghost btn--sm" onClick={makeVertical}>Kabı dikey yap</button>
            </div>
          </div>
        )}
        <div className="gw-addrow">
          <SelectField label="Başka destek ekle" value={addType}
            options={(Object.keys(SUPPORT_TYPE_TR) as Support["type"][]).map((t) => ({ value: t, label: SUPPORT_TYPE_TR[t] }))}
            onChange={(v) => setAddType(v as Support["type"])} />
          <button type="button" className="btn btn--primary btn--sm" onClick={() => {
            if (addType === "leg") { addLegSupport(); return; }
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
              <span className="gw-editor__meta">Hesap ayrıntıları «Hesap girdileri» sekmesinde</span>
            </div>

            {sel.type === "leg" && legD ? (
              <>
                <Group title="Ana ölçüler" open>
                  {legD.type === "channel" && <UpnBadge />}
                  <div className="grid">
                    <SelectField label="Kesit tipi" value={legD.type}
                      options={(Object.keys(SECTION_TR)).map((k) => ({ value: k, label: SECTION_TR[k] }))}
                      onChange={(v) => upd({ leg_section_type: v as NonNullable<Support["leg_section_type"]> })} />
                    {legD.type === "channel" && (
                      <>
                        <SelectField label="Hazır UPN seç (EN 10279)" value={matchingUpn(sel, upnRows)}
                          options={[{ value: "", label: "— elle gir —" }, ...upnRows.map((r) => ({ value: r.name, label: r.name }))]}
                          onChange={(v) => { const p = upnPatch(v); if (p) upd(p); }} />
                        <SelectField label="U yönü" value={sel.leg_channel_facing ?? "web"}
                          options={[{ value: "web", label: "Sırtı pede" }, { value: "flanges", label: "Kanatlar pede" }]}
                          onChange={(v) => upd({ leg_channel_facing: v as "web" | "flanges" })} />
                      </>
                    )}
                    {legD.type === "pipe" && (
                      <>
                        <RField label="Boru dış çapı" unit="mm" value={legD.d} min={1}
                          onChange={(v) => upd({ leg_diameter_mm: v })} />
                        <RField label="Et kalınlığı" unit="mm" value={legD.t} min={1} max={legD.d / 2}
                          onChange={(v) => upd({ leg_thickness_mm: v })} />
                      </>
                    )}
                    {(legD.type === "box" || legD.type === "angle") && (
                      <>
                        <RField label="Profil yüksekliği h" unit="mm" value={legD.h} min={1}
                          onChange={(v) => upd({ leg_profile_height_mm: v })} />
                        <RField label="Kanat genişliği b" unit="mm" value={legD.w} min={1}
                          onChange={(v) => upd({ leg_profile_width_mm: v })} />
                      </>
                    )}
                    <RField label="Ayak sayısı" value={sel.leg_count ?? 4} min={3} max={8} step={1}
                      onChange={(v) => upd({ leg_count: Math.round(v) })} />
                    <RField label="Profil boyu" unit="mm" value={sel.height_mm} min={50} max={20000}
                      help={vertical ? "Ayak üst ucundan taban sacına." : undefined}
                      onChange={(v) => upd({ height_mm: v })} />
                    <RField label={vertical ? "Üst ucu kotu (alt teğetten)" : "Konum (sol teğetten)"} unit="mm"
                      value={sel.location_mm} onChange={(v) => upd({ location_mm: v })} />
                  </div>
                  {!vertical && (
                    <p className="gw-note gw-note--warn">Ayak ölçüleri dikey kapta anlamlıdır — Öneri bölümündeki «Kabı dikey yap» ile yönelimi değiştirin.</p>
                  )}
                </Group>

                <Group title="Ayrıntılar">
                  <div className="grid">
                    {hostSelect}
                    {legD.type === "channel" && (
                      <>
                        <RField label="Profil yüksekliği h" unit="mm" value={legD.h} min={1}
                          onChange={(v) => upd({ leg_profile_height_mm: v })} />
                        <RField label="Kanat genişliği b" unit="mm" value={legD.w} min={1}
                          onChange={(v) => upd({ leg_profile_width_mm: v })} />
                      </>
                    )}
                    {legD.type === "angle" && (
                      <RField label="Et kalınlığı" unit="mm" value={legD.t} min={1}
                        onChange={(v) => upd({ leg_thickness_mm: v })} />
                    )}
                    {(legD.type === "channel" || legD.type === "box") && (
                      <>
                        <RField label="Gövde kalınlığı tw" unit="mm" value={legD.tw} min={0.1}
                          max={legD.type === "channel" ? legD.h / 2 : undefined}
                          onChange={(v) => upd({ leg_web_thickness_mm: v })} />
                        <RField label="Kanat kalınlığı tf" unit="mm" value={legD.tf} min={0.1}
                          max={legD.type === "channel" ? legD.w : undefined}
                          onChange={(v) => upd({ leg_flange_thickness_mm: v })} />
                      </>
                    )}
                    <RField label="İlk ayak açısı" unit="°" value={legD.startAngle} min={-360} max={360}
                      onChange={(v) => upd({ leg_start_angle_deg: v })} />
                    <RField label="Yerleşim yarıçapı" unit="mm" value={sel.support_radius_mm ?? 0} min={0}
                      max={host ? 2 * host.rOutStart : undefined}
                      help="0 = otomatik (dış yarıçap + ped kalınlığı + kanat genişliği/2)."
                      onChange={(v) => upd({ support_radius_mm: v > 0 ? v : null })} />
                  </div>

                  <h4 className="gw-subhead">Ayak pedi</h4>
                  <div className="grid">
                    <RField label="Ped boyu" unit="mm" value={legD.padL} min={1}
                      note="varsayılan 2.5·h" onChange={(v) => upd({ leg_pad_length_mm: v })} />
                    <RField label="Ped eni" unit="mm" value={legD.padW} min={1}
                      note="varsayılan 2·b" onChange={(v) => upd({ leg_pad_width_mm: v })} />
                    <RField label="Ped kalınlığı" unit="mm" value={legD.padT} min={1}
                      onChange={(v) => upd({ leg_pad_thickness_mm: v })} />
                    <RField label="Üst taşma" unit="mm" value={legD.padExt} min={0}
                      help="Pedin ayak üst ucunun üstüne çıkan kısmı."
                      onChange={(v) => upd({ leg_pad_top_extension_mm: v })} />
                  </div>

                  <h4 className="gw-subhead">Taban sacı</h4>
                  <div className="grid">
                    <RField label="Sac boyu" unit="mm" value={legD.plateL} min={1}
                      note="varsayılan 2·h + 40" onChange={(v) => upd({ base_plate_length_mm: v })} />
                    <RField label="Sac eni" unit="mm" value={legD.plateW} min={1}
                      note="varsayılan 2·b + 40" onChange={(v) => upd({ base_plate_width_mm: v })} />
                    <RField label="Sac kalınlığı" unit="mm" value={legD.plateT} min={1}
                      onChange={(v) => upd({ base_plate_thickness_mm: v })} />
                    <RField label="Ankraj adedi" value={legD.boltCount} min={1} step={1}
                      onChange={(v) => upd({ anchor_bolt_count: Math.round(v) })} />
                    <RField label="Ankraj çapı" unit="mm" value={legD.boltD} min={1}
                      onChange={(v) => upd({ anchor_bolt_diameter_mm: v })} />
                  </div>
                </Group>
              </>
            ) : (
              <>
                <Group title="Ana ölçüler" open>
                  <div className="grid">
                    {hostSelect}
                    {sel.type === "saddle" && (
                      <RField label="Konum (sol teğetten)" unit="mm"
                        value={sel.location_mm}
                        min={Math.max(hostLo, 0)}
                        max={Math.min(hostHi, span)}
                        onChange={(v) => updateSupport(selIndex, { location_mm: v })} />
                    )}
                    <RField label="Yükseklik" unit="mm" value={sel.height_mm} min={50} max={sel.type === "saddle" ? 3000 : 20000}
                      onChange={(v) => updateSupport(selIndex, { height_mm: v })} />
                    {sel.type === "saddle" && (
                      <RField label="Genişlik" unit="mm" value={sel.width_mm} min={50} max={2000}
                        onChange={(v) => updateSupport(selIndex, { width_mm: v })} />
                    )}
                  </div>
                  {sel.type === "skirt" && (
                    <p className="gw-note">Etek sol bombenin teğet hattından aşağı doğru uzanır; konum girdisi kullanılmaz.</p>
                  )}
                </Group>
                {sel.type === "saddle" && (
                  <Group title="Ayrıntılar">
                    <div className="grid">
                      <RField label="Temas (sarma) açısı" unit="°" value={sel.contact_angle_deg ?? 120} min={120} max={180}
                        onChange={(v) => updateSupport(selIndex, { contact_angle_deg: v })} />
                    </div>
                    <p className="gw-note">Zick K1…K7 alanları boş bırakılırsa tablodan (θ={sel.contact_angle_deg ?? 120}°) alınır; tabloda yoksa hesap "Veri Engelli" kalır.</p>
                  </Group>
                )}
              </>
            )}
          </div>
        )}
      </Section>
    </div>
  );
}
