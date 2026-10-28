// 3.1 Gövde zinciri: [+ Sol] — halkalar — [+ Sağ]; halkaya tıklayınca altında düzenleme.

import { useMemo, useState } from "react";
import { useStore, type ChainSide } from "../store";
import { componentFrames } from "../vesselModel";
import { NumField, SelectField } from "../components";
import { RField, ChipGroup, Section, fmt } from "./shared";

type AddMode = "shell" | "cone" | "stepped";

const MODE_LABEL: Record<AddMode, string> = {
  shell: "Silindir",
  cone: "Koni",
  stepped: "Daralt + Silindir",
};

const SIDE_LABEL: Record<ChainSide, string> = { left: "Sol uca", right: "Sağ uca" };

function halfAngleDeg(a: number, b: number, length: number): number {
  return (Math.atan(Math.abs(a - b) / 2 / Math.max(length, 1e-9)) * 180) / Math.PI;
}

function AddPanel({ side, endD, neighborT, onClose }: {
  side: ChainSide; endD: number; neighborT: number; onClose: () => void;
}) {
  const appendShell = useStore((s) => s.appendShell);
  const appendCone = useStore((s) => s.appendCone);
  const appendStepped = useStore((s) => s.appendStepped);
  const setSelection = useStore((s) => s.setSelection);
  const setActiveShellId = useStore((s) => s.setActiveShellId);

  const [mode, setMode] = useState<AddMode>("shell");
  const [length, setLength] = useState(1000);
  const [t, setT] = useState(neighborT);
  const [targetD, setTargetD] = useState(Math.max(Math.round((endD * 0.6) / 10) * 10, 50));
  const [coneLen, setConeLen] = useState(500);
  const [warn, setWarn] = useState<string | null>(null);

  const equal = Math.abs(endD - targetD) < 1;
  const alpha = halfAngleDeg(endD, targetD, coneLen);
  const needsDiameter = mode === "cone" || mode === "stepped";
  const bad = (needsDiameter && (equal || !(targetD > 0)))
    || (mode === "shell" && !(length > 0))
    || (mode === "cone" && !(coneLen > 0))
    || (mode === "stepped" && !(coneLen > 0 && length > 0));

  const submit = () => {
    setWarn(null);
    let selectedKind: "shell" | "cone" = "shell";
    let id: string | null = null;
    if (mode === "shell") {
      id = appendShell(side, { tangent_length: length, nominal_thickness: t });
    } else if (mode === "cone") {
      id = appendCone(side, { endDiameter: targetD, length: coneLen, nominal_thickness: t });
      selectedKind = "cone";
    } else {
      const ids = appendStepped(side, { endDiameter: targetD, coneLength: coneLen, shellLength: length });
      id = ids ? ids[1] : null;
    }
    if (!id) {
      setWarn("Eklenemedi: çap/boy değerlerini kontrol edin (eşit çapta koni oluşmaz).");
      return;
    }
    setSelection({ kind: selectedKind, id });
    if (selectedKind === "shell") setActiveShellId(id);
    onClose();
  };

  return (
    <div className="gw-add" role="group" aria-label={`${SIDE_LABEL[side]} ekle`}>
      <div className="gw-add__head">
        <b>{SIDE_LABEL[side]} ekle</b>
        <button type="button" className="ghost-btn" onClick={onClose}>Vazgeç</button>
      </div>
      <ChipGroup label="Eklenecek parça" value={mode} onChange={setMode}
        options={(Object.keys(MODE_LABEL) as AddMode[]).map((m) => ({ value: m, label: MODE_LABEL[m] }))} />

      {needsDiameter && (
        <div className="gw-add__auto">
          Başlangıç çapı (otomatik): <b>Ø{fmt(endD)}</b> mm
          {!equal && targetD > 0 && (
            <> · yarı tepe açısı α = <b className={alpha > 30 ? "gw-bad" : ""}>{fmt(alpha, 2)}°</b></>
          )}
        </div>
      )}

      <div className="grid">
        {needsDiameter && (
          <RField label="Uç çapı" unit="mm" value={targetD} min={50} max={20000} onChange={setTargetD} />
        )}
        {needsDiameter && (
          <RField label="Koni boyu" unit="mm" value={coneLen} min={10} max={30000} onChange={setConeLen} />
        )}
        {mode !== "cone" && (
          <RField label={mode === "stepped" ? "Yeni silindir boyu" : "Teğet boyu"} unit="mm"
            value={length} min={10} max={60000} onChange={setLength} />
        )}
        {mode !== "stepped" && (
          <RField label="Et kalınlığı" unit="mm" value={t} min={1} max={250} onChange={setT} />
        )}
      </div>

      {needsDiameter && equal && (
        <p className="gw-note gw-note--bad" role="alert">
          Uç çapı mevcut çapa eşit — koni eklenemez. Silindir ekleyin ya da farklı bir çap girin.
        </p>
      )}
      {mode === "stepped" && !equal && (
        <p className="gw-note">Önce koni, ardından Ø{fmt(targetD)} çapında yeni silindir tek seferde eklenir; kalınlık komşudan devralınır.</p>
      )}
      {warn && <p className="gw-note gw-note--bad" role="alert">{warn}</p>}
      <button type="button" className="btn btn--primary btn--sm" disabled={bad} onClick={submit}>
        {MODE_LABEL[mode]} ekle
      </button>
    </div>
  );
}

function ItemEditor() {
  const project = useStore((s) => s.project);
  const selection = useStore((s) => s.selection);
  const updateShell = useStore((s) => s.updateShell);
  const updateCone = useStore((s) => s.updateCone);
  const duplicateComponent = useStore((s) => s.duplicateComponent);
  const removeComponent = useStore((s) => s.removeComponent);
  const moveComponent = useStore((s) => s.moveComponent);
  const [more, setMore] = useState(false);

  const seq = project.component_sequence ?? [];
  const materialOpts = project.materials.map((m) => ({ value: m.material_id, label: `${m.material_id} — ${m.material_designation}` }));
  const weldOpts = [{ value: "", label: "— yok —" }, ...project.welds.map((w) => ({ value: w.joint_id, label: `${w.joint_id} — ${w.joint_type}` }))];

  if (!selection || (selection.kind !== "shell" && selection.kind !== "cone")) {
    return <p className="gw-empty">Düzenlemek için zincirdeki bir halkaya (veya 3D modelde bir gövde/koni parçasına) tıklayın.</p>;
  }
  const shell = selection.kind === "shell" ? project.shell_sections.find((x) => x.section_id === selection.id) : undefined;
  const cone = selection.kind === "cone" ? project.cones.find((x) => x.cone_id === selection.id) : undefined;
  const item = shell ?? cone;
  const index = seq.findIndex((r) => r.component_id === selection.id);
  if (!item || index < 0) return <p className="gw-empty">Seçili parça bulunamadı.</p>;

  const ref = seq[index];
  const canMoveL = index > 1;
  const canMoveR = index < seq.length - 2;
  const canRemove = seq.length > 3;

  return (
    <div className="gw-editor">
      <div className="gw-editor__head">
        <b>{selection.id}</b>
        <span className="gw-editor__actions">
          <button type="button" className="ghost-btn" disabled={!canMoveL} onClick={() => moveComponent(index, -1)} title="Sola taşı">← Taşı</button>
          <button type="button" className="ghost-btn" disabled={!canMoveR} onClick={() => moveComponent(index, 1)} title="Sağa taşı">Taşı →</button>
          <button type="button" className="ghost-btn" onClick={() => duplicateComponent(ref)}>Kopyala</button>
          <button type="button" className="ghost-btn gw-danger" disabled={!canRemove} onClick={() => removeComponent(ref)}
            title={canRemove ? "Parçayı sil" : "Son gövde elemanı silinemez"}>Sil</button>
        </span>
      </div>

      {shell && (
        <div className="grid">
          <RField label="İç çap (ID)" unit="mm" value={shell.inside_diameter ?? 0} min={50} max={20000}
            onChange={(v) => updateShell(shell.section_id, { inside_diameter: v, outside_diameter: null })} />
          <RField label="Et kalınlığı (t)" unit="mm" value={shell.nominal_thickness} min={1} max={250}
            onChange={(v) => updateShell(shell.section_id, { nominal_thickness: v })} />
          <RField label="Teğet boyu (L)" unit="mm" value={shell.tangent_length} min={10} max={60000}
            onChange={(v) => updateShell(shell.section_id, { tangent_length: v })} />
          <SelectField label="Malzeme" value={shell.material_id} options={materialOpts}
            onChange={(v) => updateShell(shell.section_id, { material_id: v })} />
        </div>
      )}
      {cone && (
        <div className="grid">
          <RField label="Büyük çap" unit="mm" value={cone.large_diameter} min={50} max={20000}
            onChange={(v) => updateCone(cone.cone_id, { large_diameter: v })} />
          <RField label="Küçük çap" unit="mm" value={cone.small_diameter} min={50} max={cone.large_diameter - 1}
            onChange={(v) => updateCone(cone.cone_id, { small_diameter: v })} />
          <RField label="Boy" unit="mm" value={cone.length} min={10} max={30000}
            onChange={(v) => updateCone(cone.cone_id, { length: v })} />
          <RField label="Et kalınlığı (t)" unit="mm" value={cone.nominal_thickness} min={1} max={250}
            onChange={(v) => updateCone(cone.cone_id, { nominal_thickness: v })} />
          <RField label="Yarı tepe açısı α (hesaplanan)" unit="°" value={cone.half_apex_angle} max={30} readOnly onChange={() => undefined}
            note={cone.half_apex_angle > 30 ? "α > 30° — torikonik/knuckle veya özel analiz gerekir." : "30° üzeri özel analiz, 60° üzeri Appendix 1-8 kapsam dışı."} />
          <SelectField label="Malzeme" value={cone.material_id} options={materialOpts}
            onChange={(v) => updateCone(cone.cone_id, { material_id: v })} />
        </div>
      )}

      <button type="button" className="ghost-btn gw-more" aria-expanded={more} onClick={() => setMore((m) => !m)}>
        {more ? "▾" : "▸"} Hesap ayrıntıları (korozyon, tolerans, kaynak{shell ? ", UG-28" : ""})
      </button>
      {more && (
        <div className="grid">
          <NumField label="İç korozyon payı" unit="mm" value={item.internal_corrosion_allowance}
            onChange={(v) => shell ? updateShell(shell.section_id, { internal_corrosion_allowance: v })
              : updateCone(cone!.cone_id, { internal_corrosion_allowance: v })} />
          <NumField label="Sac toleransı" unit="%" value={item.mill_tolerance}
            onChange={(v) => shell ? updateShell(shell.section_id, { mill_tolerance: v })
              : updateCone(cone!.cone_id, { mill_tolerance: v })} />
          <SelectField label="Kaynak birleşimi" value={item.weld_joint_id ?? ""} options={weldOpts}
            onChange={(v) => shell ? updateShell(shell.section_id, { weld_joint_id: v || null })
              : updateCone(cone!.cone_id, { weld_joint_id: v || null })} />
          {shell && (
            <>
              <NumField label="UG-28 A faktörü" value={shell.ug28_strain_factor_a ?? 0}
                hint="0 = girilmedi (dış basınç bloke)"
                onChange={(v) => updateShell(shell.section_id, { ug28_strain_factor_a: v > 0 ? v : null })} />
              <NumField label="UG-28 B faktörü" unit="MPa" value={shell.ug28_allowable_stress_b ?? 0}
                hint="0 = girilmedi"
                onChange={(v) => updateShell(shell.section_id, { ug28_allowable_stress_b: v > 0 ? v : null })} />
            </>
          )}
        </div>
      )}
    </div>
  );
}

export function Step1BodyChain() {
  const project = useStore((s) => s.project);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const setActiveShellId = useStore((s) => s.setActiveShellId);
  const setGeoSubStep = useStore((s) => s.setGeoSubStep);
  const [adding, setAdding] = useState<ChainSide | null>(null);

  const frames = useMemo(() => componentFrames(project), [project]);
  const n = frames.length;
  const seq = project.component_sequence ?? [];
  const rings = frames.filter((f) => f.kind !== "head");
  const canAdd = n >= 3;
  const endD = canAdd ? (adding === "left" ? 2 * frames[1].rInStart : 2 * frames[n - 2].rInEnd) : 0;
  const neighborT = canAdd ? (adding === "left" ? frames[1].thickness : frames[n - 2].thickness) : 12;

  return (
    <div className="gw-step">
      <Section title="Gövde zinciri" meta={`${rings.length} halka`}>
        <div className="gw-strip" role="group" aria-label="Gövde zinciri şeridi">
          <button type="button" className="gw-cap" title="Bombeleri düzenle" onClick={() => setGeoSubStep(1)}>
            {seq[0]?.component_id ?? "HEAD-L"}
          </button>
          <button type="button" className="gw-plus" disabled={!canAdd} aria-expanded={adding === "left"}
            onClick={() => setAdding(adding === "left" ? null : "left")}>+ Sol</button>
          {rings.map((f) => {
            const active = selection?.id === f.id;
            const dLabel = f.kind === "cone"
              ? `Ø${fmt(2 * f.rInStart, 0)}→${fmt(2 * f.rInEnd, 0)}`
              : `Ø${fmt(2 * f.rInStart, 0)}`;
            return (
              <button key={f.id} type="button" aria-pressed={active}
                className={`gw-ring gw-ring--${f.kind}${active ? " is-active" : ""}`}
                onClick={() => {
                  setSelection({ kind: f.kind as "shell" | "cone", id: f.id });
                  if (f.kind === "shell") setActiveShellId(f.id);
                }}>
                <b>{f.id}</b>
                <span>{dLabel} × {fmt(f.zEnd - f.zStart, 0)}</span>
              </button>
            );
          })}
          <button type="button" className="gw-plus" disabled={!canAdd} aria-expanded={adding === "right"}
            onClick={() => setAdding(adding === "right" ? null : "right")}>+ Sağ</button>
          <button type="button" className="gw-cap" title="Bombeleri düzenle" onClick={() => setGeoSubStep(1)}>
            {seq[seq.length - 1]?.component_id ?? "HEAD-R"}
          </button>
        </div>

        {adding && canAdd && (
          <AddPanel key={adding} side={adding} endD={endD} neighborT={neighborT} onClose={() => setAdding(null)} />
        )}
        {!canAdd && <p className="gw-note gw-note--bad" role="alert">Zincir en az bombe–gövde–bombe olmalı; uç ekleme kapalı.</p>}
      </Section>

      <Section title="Seçili halka">
        <ItemEditor />
      </Section>
    </div>
  );
}
