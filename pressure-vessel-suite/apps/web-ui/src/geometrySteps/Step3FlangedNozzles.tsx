// 3.3 Flanşlı boru nozulları (flanged / slip_on / pad_reinforced / manway).

import { useMemo, useState } from "react";
import { PIPE_NOZZLE_TYPES, useStore } from "../store";
import { catalogs, listPipeSizes } from "../data/catalogAdapter";
import { componentFrames } from "../vesselModel";
import { NOZZLE_TYPE_TR } from "../i18n";
import { SelectField } from "../components";
import type { FlangeClass } from "../geometryContract";
import type { Nozzle } from "../types";
import { CatalogBadge } from "./IssuesPanel";
import {
  Group, PlacementFields, RField, Section, StepIntro, fmt, hostFrames, hostLength, headRadius, outOfRange,
  type Placement,
} from "./shared";

const PIPE_SIZES = listPipeSizes();
const CLASSES: FlangeClass[] = ["CL150", "CL300", "CL600", "CL900", "CL1500", "CL2500"];
type PipeType = (typeof PIPE_NOZZLE_TYPES)[number];

function schedulesOf(nps: string): string[] {
  const p = catalogs.pipe(nps);
  return p ? Object.entries(p.walls).filter(([, v]) => v != null).map(([k]) => k) : [];
}

function nozzleZ(nz: Nozzle, onHead: boolean): number {
  return onHead ? (nz.head_position_diameter ?? 0) : nz.axial_position;
}

export function Step3FlangedNozzles() {
  const project = useStore((s) => s.project);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const addPipeNozzle = useStore((s) => s.addPipeNozzle);
  const updateNozzle = useStore((s) => s.updateNozzle);
  const removeNozzle = useStore((s) => s.removeNozzle);

  const frames = useMemo(() => componentFrames(project), [project]);
  const hosts = hostFrames(frames);
  const horizontal = project.orientation !== "vertical";

  const [type, setType] = useState<PipeType>("flanged");
  const [nps, setNps] = useState("4");
  const [schedule, setSchedule] = useState("SCH40");
  const [cls, setCls] = useState<FlangeClass>("CL150");
  const [pl, setPl] = useState<{ host: string; z: number | null; theta: number; headD: number }>(
    { host: "", z: null, theta: 0, headD: 0 },
  );
  const [padOn, setPadOn] = useState(false);
  const [padOdEdit, setPadOdEdit] = useState<number | null>(null);
  const [padTEdit, setPadTEdit] = useState<number | null>(null);
  const [warn, setWarn] = useState<string | null>(null);

  const hostId = hosts.some((f) => f.id === pl.host) ? pl.host : (frames.find((f) => f.kind === "shell")?.id ?? hosts[0]?.id ?? "");
  const host = frames.find((f) => f.id === hostId);
  const onHead = host?.kind === "head";
  const L = hostLength(host);
  const z = pl.z ?? Math.round(L / 2);
  const pipe = catalogs.pipe(nps);
  const scheds = schedulesOf(nps);
  const effSchedule = scheds.includes(schedule) ? schedule : (scheds.includes("SCH40") ? "SCH40" : (scheds.includes("STD") ? "STD" : scheds[0] ?? ""));
  const flange = catalogs.flange(nps, cls);
  const pad = type === "pad_reinforced" || padOn;
  const padOd = padOdEdit ?? (pipe ? +(2 * pipe.od).toFixed(1) : 0);
  const padT = padTEdit ?? (host?.thickness ?? 10);

  const posBad = onHead
    ? host ? outOfRange(pl.headD, 0, 2 * headRadius(host)) : true
    : outOfRange(z, 0, L);
  const canAdd = !!host && !!pipe && !!effSchedule && !posBad && !outOfRange(pl.theta, 0, 360);

  const rows = project.nozzles
    .map((nz, index) => ({ nz, index }))
    .filter(({ nz }) => (PIPE_NOZZLE_TYPES as readonly string[]).includes(nz.nozzle_type));
  const selRow = rows.find(({ nz }) => selection?.kind === "nozzle" && selection.id === nz.tag);

  const add = () => {
    setWarn(null);
    if (!host) return;
    const tag = addPipeNozzle({
      host_component_id: host.id, nozzle_type: type, nps, schedule: effSchedule, rating_class: cls,
      axial_position: onHead ? 0 : z, circumferential_angle: pl.theta,
      head_position_diameter: onHead && pl.headD > 0 ? pl.headD : null,
    });
    if (!tag) {
      setWarn(`Katalogda yok: ${nps}" ${effSchedule} — nozul eklenmedi.`);
      return;
    }
    const idx = useStore.getState().project.nozzles.findIndex((n) => n.tag === tag);
    if (idx >= 0) {
      updateNozzle(idx, pad
        ? { reinforcement_pad: true, reinforcement_pad_od: padOd, reinforcement_pad_thickness: padT }
        : { reinforcement_pad: false, reinforcement_pad_od: null, reinforcement_pad_thickness: null });
    }
    setSelection({ kind: "nozzle", id: tag });
  };

  return (
    <div className="gw-step">
      <StepIntro>Tip, boyut ve konumu seçip nozulu ekle; flanş ve boru ölçüleri katalogdan gelir.</StepIntro>

      <Section title="Yeni flanşlı nozul" meta={<CatalogBadge />}>
        <Group title="Ana ölçüler" open>
          <div className="grid">
            <SelectField label="Tip" value={type}
              options={PIPE_NOZZLE_TYPES.map((t) => ({ value: t, label: NOZZLE_TYPE_TR[t] ?? t }))}
              onChange={(v) => setType(v as PipeType)} />
            <SelectField label="Boyut (NPS / DN)" value={nps}
              options={PIPE_SIZES.map((s) => ({ value: s.nps, label: `${s.label} (DN${s.dn})` }))}
              onChange={setNps} />
            <SelectField label="Et serisi (SCH)" value={effSchedule}
              options={scheds.map((s) => ({ value: s, label: `${s} — et ${fmt(pipe?.walls[s] ?? 0, 2)} mm` }))}
              onChange={setSchedule} />
          </div>
          {pipe && (
            <div className="derived-dims" aria-label="Seçili boru ölçüleri">
              <span>Boru dış çapı</span><b>{fmt(pipe.od, 2)} mm</b>
              <span>Boru iç çapı</span><b>{fmt(pipe.od - 2 * (pipe.walls[effSchedule] ?? 0), 2)} mm</b>
              <span>Flanş dış çapı ({cls})</span><b>{flange?.outside_diameter != null ? `${fmt(flange.outside_diameter, 1)} mm` : "katalogda yok"}</b>
            </div>
          )}
          <PlacementFields frames={frames} horizontal={horizontal}
            value={{ host: hostId, z, theta: pl.theta, headD: pl.headD }}
            onChange={(p: Partial<Placement>) => setPl((cur) => ({
              host: p.host ?? cur.host, theta: p.theta ?? cur.theta, headD: p.headD ?? cur.headD,
              z: p.host !== undefined ? null : p.z !== undefined ? p.z : cur.z,
            }))} />
        </Group>

        <Group title="Ayrıntılar">
          <div className="grid">
            <SelectField label="Flanş sınıfı" value={cls}
              options={CLASSES.map((c) => ({ value: c, label: c.replace("CL", "Class ") }))}
              onChange={(v) => setCls(v as FlangeClass)} />
          </div>
          <label className="gw-check">
            <input type="checkbox" checked={pad} disabled={type === "pad_reinforced"}
              onChange={(e) => setPadOn(e.target.checked)} />
            Takviye pedi {type === "pad_reinforced" && "(tip gereği açık)"}
          </label>
          {pad && (
            <div className="grid">
              <RField label="Ped dış çapı" unit="mm" value={padOd} min={pipe ? pipe.od * 1.1 : 0} max={pipe ? pipe.od * 4 : undefined}
                onChange={setPadOdEdit} />
              <RField label="Ped kalınlığı" unit="mm" value={padT} min={1} max={200} onChange={setPadTEdit} />
            </div>
          )}
        </Group>

        {!flange && (
          <p className="gw-note gw-note--bad" role="alert">
            Bu NPS / sınıf için flanş ölçüsü katalogda yok — 3D flanş çizilemez.
          </p>
        )}
        {warn && <p className="gw-note gw-note--bad" role="alert">{warn}</p>}
        {posBad && host && (
          <p className="gw-note gw-note--bad" role="alert">
            Konum host sınırları dışında — düzeltmeden eklenemez (kırpılmaz).
          </p>
        )}
        <button type="button" className="btn btn--primary btn--sm" disabled={!canAdd} onClick={add}>
          ＋ Nozul ekle
        </button>
      </Section>

      <Section title="Flanşlı nozullar" meta={`${rows.length} adet`}>
        {rows.length === 0 ? (
          <p className="gw-empty">Henüz flanşlı nozul yok.</p>
        ) : (
          <table className="gw-table">
            <thead>
              <tr><th>Etiket</th><th>Host</th><th>Ölçü</th><th>z / D</th><th>θ</th><th /></tr>
            </thead>
            <tbody>
              {rows.map(({ nz, index }) => {
                const hf = frames.find((f) => f.id === nz.host_component_id);
                const isSel = selection?.kind === "nozzle" && selection.id === nz.tag;
                return (
                  <tr key={nz.tag} className={isSel ? "is-active" : undefined}
                    tabIndex={0} aria-selected={isSel}
                    onClick={() => setSelection({ kind: "nozzle", id: nz.tag })}
                    onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setSelection({ kind: "nozzle", id: nz.tag }); } }}>
                    <td><b>{nz.tag}</b></td>
                    <td>{nz.host_component_id}</td>
                    <td>{nz.size_designation ?? `Ø${fmt(nz.outside_diameter)}×${fmt(nz.neck_thickness, 2)}`}</td>
                    <td>{fmt(nozzleZ(nz, hf?.kind === "head"), 0)}</td>
                    <td>{fmt(nz.circumferential_angle, 0)}°</td>
                    <td>
                      <button type="button" className="gw-del" aria-label={`${nz.tag} sil`}
                        onClick={(e) => { e.stopPropagation(); removeNozzle(index); }}>✕</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {selRow && (() => {
          const { nz, index } = selRow;
          const hf = frames.find((f) => f.id === nz.host_component_id);
          return (
            <div className="gw-editor">
              <div className="gw-editor__head"><b>{nz.tag} düzenle</b>
                <span className="gw-editor__meta">{nz.size_designation ?? "özel ölçü"} — boyut değişimi için silip yeniden ekleyin</span>
              </div>
              <Group title="Ana ölçüler" open>
                <PlacementFields frames={frames} horizontal={horizontal}
                  value={{ host: nz.host_component_id, z: nz.axial_position, theta: nz.circumferential_angle, headD: nz.head_position_diameter ?? 0 }}
                  onChange={(p) => updateNozzle(index, {
                    ...(p.host !== undefined ? { host_component_id: p.host } : {}),
                    ...(p.z !== undefined ? { axial_position: p.z } : {}),
                    ...(p.theta !== undefined ? { circumferential_angle: p.theta } : {}),
                    ...(p.headD !== undefined ? { head_position_diameter: p.headD > 0 ? p.headD : null } : {}),
                  })} />
              </Group>
              <Group title="Ayrıntılar">
                <label className="gw-check">
                  <input type="checkbox" checked={nz.reinforcement_pad}
                    onChange={(e) => updateNozzle(index, e.target.checked
                      ? { reinforcement_pad: true, reinforcement_pad_od: nz.reinforcement_pad_od ?? +(2 * nz.outside_diameter).toFixed(1),
                          reinforcement_pad_thickness: nz.reinforcement_pad_thickness ?? hf?.thickness ?? 10 }
                      : { reinforcement_pad: false, reinforcement_pad_od: null, reinforcement_pad_thickness: null })} />
                  Takviye pedi
                </label>
                {nz.reinforcement_pad && (
                  <div className="grid">
                    <RField label="Ped dış çapı" unit="mm" value={nz.reinforcement_pad_od ?? 0}
                      min={nz.outside_diameter * 1.1} max={nz.outside_diameter * 4}
                      onChange={(v) => updateNozzle(index, { reinforcement_pad_od: v })} />
                    <RField label="Ped kalınlığı" unit="mm" value={nz.reinforcement_pad_thickness ?? 0} min={1} max={200}
                      onChange={(v) => updateNozzle(index, { reinforcement_pad_thickness: v })} />
                  </div>
                )}
              </Group>
            </div>
          );
        })()}
      </Section>
    </div>
  );
}
