// 3.2 Sol/sağ bombe kartları: uç çapı zincirden otomatik, tip SVG ikonlarıyla seçilir.

import { useMemo, useState } from "react";
import { syncTerminalHeads, useStore } from "../store";
import { componentFrames, headDepth, headDomeHeight } from "../vesselModel";
import { HEAD_TYPE_TR } from "../i18n";
import { NumField, SelectField } from "../components";
import type { Head, HeadTypeT } from "../types";
import { RField, fmt } from "./shared";
import { crownDepthPatch, depthRatio, ellipticalK, typeChangePatch } from "./headDepth";

const TYPES: HeadTypeT[] = ["elliptical", "torispherical", "hemispherical", "flat"];

/** Sağa bakan bombe profili (ince çizgi). Sol kart için aynalanır. */
function HeadIcon({ type, mirror }: { type: HeadTypeT; mirror: boolean }) {
  const shape: Record<HeadTypeT, string> = {
    elliptical: "M4 6 H14 C30 6 34 12 34 18 C34 24 30 30 14 30 H4", // 2:1 elips
    torispherical: "M4 6 H18 Q30 6 30 12 L30 24 Q30 30 18 30 H4",   // sığ taç + mafsal
    hemispherical: "M4 6 H10 A12 12 0 0 1 10 30 H4",                  // yarım daire
    flat: "M4 6 H24 V30 H4",                                          // düz kapak
  };
  const d = shape[type];
  return (
    <svg viewBox="0 0 40 36" width="44" height="40" aria-hidden="true" className="gw-icon"
      style={mirror ? { transform: "scaleX(-1)" } : undefined}>
      <path d={d} fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      <line x1="4" y1="6" x2="4" y2="30" stroke="currentColor" strokeWidth="1" strokeDasharray="2 2" opacity="0.5" />
    </svg>
  );
}

function HeadCard({ head, side, chainD }: { head: Head; side: "left" | "right"; chainD: number }) {
  const updateHead = useStore((s) => s.updateHead);
  const setProject = useStore((s) => s.setProject);
  const relation = useStore((s) => s.project.diameter_relation ?? "linked");
  const materials = useStore((s) => s.project.materials);
  const welds = useStore((s) => s.project.welds);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const [more, setMore] = useState(false);

  const linked = relation === "linked";
  const mismatch = Math.abs(head.inside_diameter - chainD) > 0.5;
  const dome = headDomeHeight(head.inside_diameter, head.type, head);
  const depth = headDepth(head.inside_diameter, head.type, head.straight_flange_length ?? 0, head);
  const selected = selection?.kind === "head" && selection.id === head.head_id;
  const sideTitle = side === "left" ? "Sol / alt bombe" : "Sağ / üst bombe";

  const setRelation = (rel: "linked" | "independent") =>
    setProject((p) => (rel === "linked"
      ? syncTerminalHeads({ ...p, diameter_relation: "linked" })
      : { ...p, diameter_relation: "independent" }));

  return (
    <article className={`gw-card${selected ? " is-active" : ""}`} aria-label={sideTitle}
      onClick={() => setSelection({ kind: "head", id: head.head_id })}>
      <header className="gw-card__head">
        <b>{sideTitle}</b>
        <span>{head.head_id}</span>
      </header>

      <div className="gw-types" role="radiogroup" aria-label={`${sideTitle} tipi`}>
        {TYPES.map((t) => (
          <button key={t} type="button" role="radio" aria-checked={head.type === t}
            className={`gw-type${head.type === t ? " is-active" : ""}`}
            onClick={(e) => { e.stopPropagation(); updateHead(head.head_id, typeChangePatch(t)); }}>
            <HeadIcon type={t} mirror={side === "left"} />
            <span>{HEAD_TYPE_TR[t]}</span>
          </button>
        ))}
      </div>

      <div className="gw-readout">
        <span>Zincir uç çapı</span>
        <b>Ø{fmt(chainD)} mm</b>
        <button type="button" className={`gw-chip is-active`}
          title="Bağlı: bombe çapı zincirden otomatik. Bağımsız: bombe çapını elle gir."
          onClick={(e) => { e.stopPropagation(); setRelation(linked ? "independent" : "linked"); }}>
          {linked ? "Bağlı (linked)" : "Bağımsız (independent)"}
        </button>
      </div>

      <div className="grid">
        <RField label="Bombe iç çapı" unit="mm" value={head.inside_diameter} min={50} max={20000}
          readOnly={linked}
          note={linked ? "Zincir ucundan otomatik; elle girmek için «Bağımsız» seçin." : undefined}
          onChange={(v) => updateHead(head.head_id, { inside_diameter: v })} />
        <RField label="Et kalınlığı (t)" unit="mm" value={head.nominal_thickness} min={1} max={250}
          onChange={(v) => updateHead(head.head_id, { nominal_thickness: v })} />
        <RField label="Düz flanş boyu (sf)" unit="mm" value={head.straight_flange_length} min={0} max={500}
          onChange={(v) => updateHead(head.head_id, { straight_flange_length: v })} />
      </div>

      {mismatch && (
        <p className="gw-note gw-note--bad" role="alert">
          Bombe çapı (Ø{fmt(head.inside_diameter)}) zincir ucuyla (Ø{fmt(chainD)}) uyuşmuyor.
        </p>
      )}

      {head.type === "elliptical" && (
        <>
          <div className="grid">
            <RField label="Kubbe derinliği (h)" unit="mm" value={head.crown_depth ?? 0} min={0} max={head.inside_diameter}
              note={`0 = standart 2:1 (h = Di/4 = ${fmt(head.inside_diameter / 4)} mm)`}
              onChange={(v) => updateHead(head.head_id, crownDepthPatch(v))} />
          </div>
          <p className="gw-note" aria-label="Eliptik oran">
            D/2h = {fmt(depthRatio(head.inside_diameter, dome), 2).replace(".", ",")} · K = {fmt(ellipticalK(depthRatio(head.inside_diameter, dome)), 3).replace(".", ",")}
          </p>
        </>
      )}
      {head.type === "torispherical" && (
        <div className="grid">
          <RField label="Taç yarıçapı (R)" unit="mm" value={head.crown_radius ?? 0} min={0} max={head.inside_diameter * 1.5}
            note="0 = standart (R = Di)" onChange={(v) => updateHead(head.head_id, { crown_radius: v > 0 ? v : null })} />
          <RField label="Mafsal yarıçapı (r)" unit="mm" value={head.knuckle_radius ?? 0} min={0} max={head.inside_diameter / 2}
            note="0 = standart (r = 0,06·Di)" onChange={(v) => updateHead(head.head_id, { knuckle_radius: v > 0 ? v : null })} />
        </div>
      )}
      {head.type === "flat" && (
        <NumField label="Düz kapak C katsayısı (UG-34)" value={head.flat_attachment_factor ?? 0}
          hint="0 = girilmedi" onChange={(v) => updateHead(head.head_id, { flat_attachment_factor: v > 0 ? v : null })} />
      )}

      <div className="derived-dims" aria-label="Bombe türetilmiş ölçüleri">
        <span>Dış çap</span><b>{fmt(head.inside_diameter + 2 * head.nominal_thickness)} mm</b>
        <span>Kubbe yüksekliği</span><b>{fmt(dome)} mm</b>
        <span>Toplam derinlik (kubbe + sf)</span><b>{fmt(depth)} mm</b>
      </div>

      <button type="button" className="ghost-btn gw-more" aria-expanded={more}
        onClick={(e) => { e.stopPropagation(); setMore((m) => !m); }}>
        {more ? "▾" : "▸"} Hesap ayrıntıları
      </button>
      {more && (
        <div className="grid" onClick={(e) => e.stopPropagation()}>
          <SelectField label="Malzeme" value={head.material_id}
            options={materials.map((m) => ({ value: m.material_id, label: `${m.material_id} — ${m.material_designation}` }))}
            onChange={(v) => updateHead(head.head_id, { material_id: v })} />
          <SelectField label="Kaynak birleşimi" value={head.weld_joint_id ?? ""}
            options={[{ value: "", label: "— yok —" }, ...welds.map((w) => ({ value: w.joint_id, label: `${w.joint_id} — ${w.joint_type}` }))]}
            onChange={(v) => updateHead(head.head_id, { weld_joint_id: v || null })} />
          <NumField label="İç korozyon payı" unit="mm" value={head.internal_corrosion_allowance}
            onChange={(v) => updateHead(head.head_id, { internal_corrosion_allowance: v })} />
          <NumField label="Sac toleransı" unit="%" value={head.mill_tolerance}
            onChange={(v) => updateHead(head.head_id, { mill_tolerance: v })} />
          <NumField label="UG-33 A faktörü" value={head.ug28_strain_factor_a ?? 0} hint="0 = girilmedi (dış basınç bloke)"
            onChange={(v) => updateHead(head.head_id, { ug28_strain_factor_a: v > 0 ? v : null })} />
          <NumField label="UG-33 B faktörü" unit="MPa" value={head.ug28_allowable_stress_b ?? 0} hint="0 = girilmedi"
            onChange={(v) => updateHead(head.head_id, { ug28_allowable_stress_b: v > 0 ? v : null })} />
        </div>
      )}
    </article>
  );
}

export function Step2Heads() {
  const project = useStore((s) => s.project);
  const frames = useMemo(() => componentFrames(project), [project]);
  const seq = project.component_sequence ?? [];
  const n = frames.length;
  const left = project.heads.find((h) => h.head_id === seq[0]?.component_id);
  const right = project.heads.find((h) => h.head_id === seq[seq.length - 1]?.component_id);
  if (n < 3 || !left || !right) {
    return <p className="gw-empty">Zincirde iki uç bombe ve en az bir gövde elemanı bulunmalı.</p>;
  }
  return (
    <div className="gw-step gw-heads">
      <HeadCard head={left} side="left" chainD={2 * frames[1].rInStart} />
      <HeadCard head={right} side="right" chainD={2 * frames[n - 2].rInEnd} />
    </div>
  );
}
