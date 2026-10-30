import { AccordionSection, NumField } from "../components";
import { useStore } from "../store";
import type { ConeBaseInputs as ConeBase, SkirtBaseRingInput } from "../types";

const EMPTY_RING: SkirtBaseRingInput = {
  support_id: null,
  ring_outer_diameter_mm: 0,
  ring_inner_diameter_mm: 0,
  ring_thickness_mm: 0,
  ring_yield_MPa: 250,
  bolt_circle_diameter_mm: 0,
  bolt_count: 8,
  bolt_diameter_mm: 24,
  concrete_fc_MPa: 25,
};

const opt = (v: number) => (v > 0 ? v : null);

/** P08: koni birleşimi App. 1-5 (Δ) ve etek taban halkası / ankraj girdileri. */
export function ConeBaseInputs(props: { id: string; open: boolean; onToggle: (id: string) => void }) {
  const { project, setProject } = useStore();
  const cb: ConeBase = project.cone_base ?? { junctions: [], skirt_base_ring: null };
  const setCb = (patch: Partial<ConeBase>) =>
    setProject((p) => ({ ...p, cone_base: { ...(p.cone_base ?? { junctions: [], skirt_base_ring: null }), ...patch } }));
  const ring = cb.skirt_base_ring;
  const setRing = (patch: Partial<SkirtBaseRingInput>) =>
    setCb({ skirt_base_ring: { ...(ring ?? EMPTY_RING), ...patch } });
  const hasSkirt = project.supports.some((s) => s.type === "skirt");
  const coneJunctions = project.junctions.filter((j) => j.junction_type !== "shell_to_shell");
  const delta = (id: string) => cb.junctions.find((j) => j.junction_id === id);
  const setDelta = (id: string, patch: { delta_deg?: number | null; extra_ring_area_mm2?: number }) => {
    const rest = cb.junctions.filter((j) => j.junction_id !== id);
    setCb({ junctions: [...rest, { junction_id: id, delta_deg: null, extra_ring_area_mm2: 0, ...delta(id), ...patch }] });
  };
  const r = ring ?? EMPTY_RING;

  return (
    <AccordionSection id={props.id} open={props.open} onToggle={props.onToggle}
      title="Koni birleşimi (App. 1-5) ve etek taban halkası"
      meta={ring ? "taban halkası girildi" : "girdi yok"}
      desc="Δ (Table 1-5.2) ve cıvata/beton izinleri lisanslı kaynaklardan sizin girdiğiniz değerlerdir; boş (0) bırakılan alanlar varsayılana düşer ve raporda belirtilir.">
      <div className="grid" style={{ marginTop: 14 }}>
        {coneJunctions.length === 0 && <p className="field__hint">Koni birleşimi tanımlı değil.</p>}
        {coneJunctions.map((j) => (
          <div key={j.junction_id} className="grid">
            <NumField label={`${j.junction_id} Δ (Table 1-5.2)`} unit="°" value={delta(j.junction_id)?.delta_deg ?? 0}
              help="Boş/0 bırakılırsa Δ=0 (güvenli taraf) alınır."
              onChange={(v) => setDelta(j.junction_id, { delta_deg: opt(v) })} />
            <NumField label={`${j.junction_id} ek halka alanı`} unit="mm²" value={delta(j.junction_id)?.extra_ring_area_mm2 ?? 0}
              onChange={(v) => setDelta(j.junction_id, { extra_ring_area_mm2: Math.max(0, v) })} />
          </div>
        ))}
        {!hasSkirt && <p className="field__hint">Etek (skirt) desteği yok; taban halkası girdileri kullanılmaz.</p>}
        {hasSkirt && (<>
          <NumField label="Halka dış çapı" unit="mm" value={r.ring_outer_diameter_mm} onChange={(v) => setRing({ ring_outer_diameter_mm: v })} />
          <NumField label="Halka iç çapı" unit="mm" value={r.ring_inner_diameter_mm} onChange={(v) => setRing({ ring_inner_diameter_mm: v })} />
          <NumField label="Halka kalınlığı" unit="mm" value={r.ring_thickness_mm} onChange={(v) => setRing({ ring_thickness_mm: v })} />
          <NumField label="Halka Fy" unit="MPa" value={r.ring_yield_MPa} onChange={(v) => setRing({ ring_yield_MPa: v })} />
          <NumField label="Cıvata dairesi çapı" unit="mm" value={r.bolt_circle_diameter_mm} onChange={(v) => setRing({ bolt_circle_diameter_mm: v })} />
          <NumField label="Cıvata adedi" value={r.bolt_count} step={1} onChange={(v) => setRing({ bolt_count: Math.round(v) })} />
          <NumField label="Cıvata çapı" unit="mm" value={r.bolt_diameter_mm} onChange={(v) => setRing({ bolt_diameter_mm: v })} />
          <NumField label="Cıvata izin çekme" unit="MPa" value={r.bolt_allowable_tension_MPa ?? 0}
            help="Zorunlu (K6): bu değer yoksa hesap BLOCKED döner."
            onChange={(v) => setRing({ bolt_allowable_tension_MPa: opt(v) })} />
          <NumField label="Cıvata izin kesme" unit="MPa" value={r.bolt_allowable_shear_MPa ?? 0}
            help="Yatay yük varsa zorunlu."
            onChange={(v) => setRing({ bolt_allowable_shear_MPa: opt(v) })} />
          <NumField label="Beton f'c" unit="MPa" value={r.concrete_fc_MPa} onChange={(v) => setRing({ concrete_fc_MPa: v })} />
          <NumField label="Beton izin yataklık (opsiyonel)" unit="MPa" value={r.concrete_allowable_bearing_MPa ?? 0}
            help="Boşsa 0,85·f'c/2,31 varsayılır."
            onChange={(v) => setRing({ concrete_allowable_bearing_MPa: opt(v) })} />
        </>)}
      </div>
    </AccordionSection>
  );
}
