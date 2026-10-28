// 3.4 Manşonlar ve soket ağızlar (coupling / socket_welded).

import { useMemo, useState } from "react";
import { COUPLING_TYPES, useStore } from "../store";
import { couplingNozzleDims, listPipeSizes } from "../data/catalogAdapter";
import { componentFrames } from "../vesselModel";
import { COUPLING_FORM_TR, COUPLING_TYPE_TR } from "../i18n";
import { SelectField } from "../components";
import type { CouplingForm, CouplingRating } from "../geometryContract";
import type { Nozzle } from "../types";
import { CatalogBadge } from "./IssuesPanel";
import {
  ChipGroup, PlacementFields, Section, fmt, hostFrames, hostLength, headRadius, outOfRange,
  type Placement,
} from "./shared";

type CouplingType = (typeof COUPLING_TYPES)[number];
// 1/2" – 4" (DN15–DN100)
const SIZES = listPipeSizes().filter((s) => s.dn >= 15 && s.dn <= 100);
const FORMS: CouplingForm[] = ["full", "half", "weldolet"];

export function Step4Couplings() {
  const project = useStore((s) => s.project);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const addCoupling = useStore((s) => s.addCoupling);
  const updateNozzle = useStore((s) => s.updateNozzle);
  const removeNozzle = useStore((s) => s.removeNozzle);

  const frames = useMemo(() => componentFrames(project), [project]);
  const hosts = hostFrames(frames);
  const horizontal = project.orientation !== "vertical";

  const [type, setType] = useState<CouplingType>("coupling");
  const [form, setForm] = useState<CouplingForm>("full");
  const [nps, setNps] = useState("1");
  const [rating, setRating] = useState<CouplingRating>("3000#");
  const [pl, setPl] = useState<{ host: string; z: number | null; theta: number; headD: number }>(
    { host: "", z: null, theta: 0, headD: 0 },
  );
  const [warn, setWarn] = useState<string | null>(null);

  const hostId = hosts.some((f) => f.id === pl.host) ? pl.host : (frames.find((f) => f.kind === "shell")?.id ?? hosts[0]?.id ?? "");
  const host = frames.find((f) => f.id === hostId);
  const onHead = host?.kind === "head";
  const L = hostLength(host);
  const z = pl.z ?? Math.round(L / 2);
  const end = type === "socket_welded" ? "socket" : "threaded";
  const dims = couplingNozzleDims(nps, rating, form, end);
  const posBad = onHead
    ? host ? outOfRange(pl.headD, 0, 2 * headRadius(host)) : true
    : outOfRange(z, 0, L);
  const canAdd = !!host && !posBad && !outOfRange(pl.theta, 0, 360);

  const rows = project.nozzles
    .map((nz, index) => ({ nz, index }))
    .filter(({ nz }) => (COUPLING_TYPES as readonly string[]).includes(nz.nozzle_type));
  const selRow = rows.find(({ nz }) => selection?.kind === "nozzle" && selection.id === nz.tag);

  const add = () => {
    setWarn(null);
    if (!host) return;
    const tag = addCoupling({
      host_component_id: host.id, nozzle_type: type, nps, rating_class: rating, coupling_form: form,
      axial_position: onHead ? 0 : z, circumferential_angle: pl.theta,
      head_position_diameter: onHead && pl.headD > 0 ? pl.headD : null,
    });
    if (tag == null) {
      setWarn(`Katalogda yok: ${nps}" ${rating} ${COUPLING_FORM_TR[form] ?? form} (${type === "socket_welded" ? "soket" : "dişli"}) — manşon eklenmedi.`);
      return;
    }
    setSelection({ kind: "nozzle", id: tag });
  };

  const sizeText = (nz: Nozzle) => nz.size_designation ?? `Ø${fmt(nz.outside_diameter)}`;

  return (
    <div className="gw-step">
      <Section title="Yeni manşon" meta={<CatalogBadge />}>
        <div className="grid">
          <SelectField label="Bağlantı" value={type}
            options={COUPLING_TYPES.map((t) => ({ value: t, label: COUPLING_TYPE_TR[t] }))}
            onChange={(v) => setType(v as CouplingType)} />
          <SelectField label="Boyut (NPS / DN)" value={nps}
            options={SIZES.map((s) => ({ value: s.nps, label: `${s.label} (DN${s.dn})` }))}
            onChange={setNps} />
        </div>
        <ChipGroup label="Manşon formu" value={form} onChange={setForm}
          options={FORMS.map((f) => ({
            value: f, label: COUPLING_FORM_TR[f]?.replace(" (katalogda yok)", "") ?? f,
            disabled: f === "weldolet", title: f === "weldolet" ? "Weldolet katalogda yok" : undefined,
          }))} />
        <ChipGroup label="Sınıf" value={rating} onChange={setRating}
          options={(["3000#", "6000#"] as CouplingRating[]).map((r) => ({ value: r, label: r }))} />

        {dims ? (
          <div className="derived-dims" aria-label="Manşon ölçüleri">
            <span>Gövde dış çapı</span><b>{fmt(dims.od, 2)} mm</b>
            <span>İç çap / delik</span><b>{fmt(dims.id, 2)} mm</b>
            <span>Boy (dış çıkıntı)</span><b>{fmt(dims.length, 1)} mm</b>
          </div>
        ) : (
          <p className="gw-note gw-note--bad" role="alert">
            Bu kombinasyon için ölçüler katalogda yok ({nps}" {rating} {COUPLING_FORM_TR[form]?.replace(" (katalogda yok)", "")}, {type === "socket_welded" ? "soket" : "dişli"}).
          </p>
        )}

        <PlacementFields frames={frames} horizontal={horizontal}
          value={{ host: hostId, z, theta: pl.theta, headD: pl.headD }}
          onChange={(p: Partial<Placement>) => setPl((cur) => ({
            host: p.host ?? cur.host, theta: p.theta ?? cur.theta, headD: p.headD ?? cur.headD,
            z: p.host !== undefined ? null : p.z !== undefined ? p.z : cur.z,
          }))} />

        {warn && <p className="gw-note gw-note--bad" role="alert">{warn}</p>}
        {posBad && host && (
          <p className="gw-note gw-note--bad" role="alert">
            Konum host sınırları dışında — düzeltmeden eklenemez (kırpılmaz).
          </p>
        )}
        <button type="button" className="btn btn--primary btn--sm" disabled={!canAdd} onClick={add}>
          ＋ Manşon ekle
        </button>
      </Section>

      <Section title="Manşonlar" meta={`${rows.length} adet`}>
        {rows.length === 0 ? (
          <p className="gw-empty">Henüz manşon yok.</p>
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
                    <td>{sizeText(nz)}</td>
                    <td>{fmt(hf?.kind === "head" ? (nz.head_position_diameter ?? 0) : nz.axial_position, 0)}</td>
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
        {selRow && (
          <div className="gw-editor">
            <div className="gw-editor__head"><b>{selRow.nz.tag} düzenle</b>
              <span className="gw-editor__meta">boyut değişimi için silip yeniden ekleyin</span>
            </div>
            <PlacementFields frames={frames} horizontal={horizontal}
              value={{ host: selRow.nz.host_component_id, z: selRow.nz.axial_position,
                theta: selRow.nz.circumferential_angle, headD: selRow.nz.head_position_diameter ?? 0 }}
              onChange={(p) => updateNozzle(selRow.index, {
                ...(p.host !== undefined ? { host_component_id: p.host } : {}),
                ...(p.z !== undefined ? { axial_position: p.z } : {}),
                ...(p.theta !== undefined ? { circumferential_angle: p.theta } : {}),
                ...(p.headD !== undefined ? { head_position_diameter: p.headD > 0 ? p.headD : null } : {}),
              })} />
          </div>
        )}
      </Section>
    </div>
  );
}
