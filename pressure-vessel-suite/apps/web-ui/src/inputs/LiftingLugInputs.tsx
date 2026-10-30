import React, { useState } from "react";
import { AccordionSection, NumField, SelectField } from "../components";
import { useStore } from "../store";
import type { LiftingLugSpec } from "../types";

/** Başlangıç değerleri yalnız UI kolaylığı; hesap kullanıcının onayladığı değerle yapılır. */
export const DEFAULT_LUG: LiftingLugSpec = {
  lug_count: 2, location: "shell_top", host_component_id: null,
  plate_thickness_mm: 20, plate_width_mm: 150, hole_diameter_mm: 50, pin_diameter_mm: null,
  edge_distance_mm: 75, hole_height_mm: 100, base_width_mm: 150,
  weld_length_mm: 400, weld_leg_mm: 10, lift_angle_deg: 0, impact_factor: 1.5,
  yield_strength_MPa: 250, weld_electrode_Fu_MPa: null, extra_mass_kg: 0,
};

/** Kaldırma kulağı girdileri (P06). Kulak yoksa kontrol yapılmaz. */
export function LiftingLugInputs() {
  const lug = useStore((s) => s.project.lifting_lugs ?? null);
  const setProject = useStore((s) => s.setProject);
  const [open, setOpen] = useState(false);
  const set = (patch: Partial<LiftingLugSpec>) =>
    setProject((p) => ({ ...p, lifting_lugs: { ...(p.lifting_lugs ?? DEFAULT_LUG), ...patch } }));
  const pos = (v: number) => (v > 0 ? v : 0);

  return (
    <AccordionSection id="lifting-lug" title="Kaldırma kulağı" open={open} onToggle={() => setOpen((o) => !o)}
      meta={lug ? `${lug.lug_count} adet` : "tanımsız"}
      desc="Kap kaldırma kulağı: plaka çekme/kesme/yatak, kaynak ve gövde yerel kontrolü (yaklaşık, mühendis incelemesi ister).">
      {!lug ? (
        <button type="button" onClick={() => setProject((p) => ({ ...p, lifting_lugs: { ...DEFAULT_LUG } }))}>
          Kaldırma kulağı ekle
        </button>
      ) : (
        <div className="form-grid">
          <NumField label="Kulak sayısı" value={lug.lug_count} step={1}
            onChange={(v) => set({ lug_count: Math.min(4, Math.max(1, Math.round(v))) })}
            help="3+ kulakta yalnız 2 kulağın yük taşıdığı tutucu varsayılır." />
          <SelectField label="Konum" value={lug.location}
            options={[{ value: "shell_top", label: "Gövde üstü" }, { value: "head", label: "Bombe" }]}
            onChange={(v) => set({ location: v as LiftingLugSpec["location"] })} />
          <NumField label="Plaka kalınlığı t" unit="mm" value={lug.plate_thickness_mm}
            onChange={(v) => set({ plate_thickness_mm: pos(v) })} />
          <NumField label="Plaka genişliği b" unit="mm" value={lug.plate_width_mm}
            onChange={(v) => set({ plate_width_mm: pos(v) })} />
          <NumField label="Delik çapı" unit="mm" value={lug.hole_diameter_mm}
            onChange={(v) => set({ hole_diameter_mm: pos(v) })} />
          <NumField label="Delik merkezi-kenar mesafesi e" unit="mm" value={lug.edge_distance_mm}
            onChange={(v) => set({ edge_distance_mm: pos(v) })} />
          <NumField label="Delik yüksekliği h (kabuktan)" unit="mm" value={lug.hole_height_mm}
            onChange={(v) => set({ hole_height_mm: pos(v) })} />
          <NumField label="Taban genişliği" unit="mm" value={lug.base_width_mm}
            onChange={(v) => set({ base_width_mm: pos(v) })} />
          <NumField label="Kaynak boyu (toplam)" unit="mm" value={lug.weld_length_mm}
            onChange={(v) => set({ weld_length_mm: pos(v) })} />
          <NumField label="Kaynak ayak ölçüsü" unit="mm" value={lug.weld_leg_mm}
            onChange={(v) => set({ weld_leg_mm: pos(v) })} />
          <NumField label="Sapan açısı (düşeyden)" unit="°" value={lug.lift_angle_deg}
            onChange={(v) => set({ lift_angle_deg: Math.min(89, Math.max(0, v)) })} />
          <NumField label="Darbe katsayısı" value={lug.impact_factor} step={0.1}
            onChange={(v) => set({ impact_factor: Math.max(1, v) })}
            hint={lug.impact_factor < 1.5 || lug.impact_factor > 2 ? "Tipik aralık 1,5-2,0" : undefined} />
          <NumField label="Plaka akma dayanımı Fy" unit="MPa" value={lug.yield_strength_MPa}
            onChange={(v) => set({ yield_strength_MPa: pos(v) })} />
          <NumField label="Ek kaldırılan kütle" unit="kg" value={lug.extra_mass_kg}
            onChange={(v) => set({ extra_mass_kg: pos(v) })} />
          <button type="button" onClick={() => setProject((p) => ({ ...p, lifting_lugs: null }))}>
            Kulakları kaldır
          </button>
        </div>
      )}
    </AccordionSection>
  );
}
