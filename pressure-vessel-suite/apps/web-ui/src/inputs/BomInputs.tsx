import { useStore } from "../store";
import type { CostInputs } from "../types";

const EMPTY: CostInputs = {
  material_price_eur_per_kg: {},
  welding_hours: null,
  labor_rate_eur_per_hour: null,
  ndt_cost_eur: null,
  paint_cost_eur: null,
};

/** Boş alan = null (hesaplanmaz); 0'a çevrilmez — K4. */
function OptNum({ label, unit, value, onChange }: {
  label: string; unit: string; value: number | null | undefined; onChange: (v: number | null) => void;
}) {
  return (
    <label className="field">
      <span className="field__label"><span>{label}</span><span className="field__unit">{unit}</span></span>
      <input
        className="input" type="number" min={0} step="any" value={value ?? ""}
        onChange={(e) => {
          const raw = e.target.value;
          if (raw === "") return onChange(null);
          const n = parseFloat(raw);
          if (Number.isFinite(n) && n >= 0) onChange(n);
        }}
      />
    </label>
  );
}

/** BOM maliyet birim fiyatları — tümü kullanıcı girer; boşsa maliyet hesaplanmaz. */
export function BomInputs() {
  const project = useStore((s) => s.project);
  const setProject = useStore((s) => s.setProject);
  const ci = project.cost_inputs ?? EMPTY;
  const patch = (p: Partial<CostInputs>) =>
    setProject((pr) => ({ ...pr, cost_inputs: { ...(pr.cost_inputs ?? EMPTY), ...p } }));
  const setPrice = (id: string, v: number | null) => {
    const next = { ...ci.material_price_eur_per_kg };
    if (v === null) delete next[id]; else next[id] = v;
    patch({ material_price_eur_per_kg: next });
  };

  return (
    <div className="panel" style={{ marginTop: 14 }}>
      <div className="panel__head"><div className="panel__title">BOM maliyet girdileri</div></div>
      <p className="field__hint">Birim fiyat varsayılanı yoktur; boş bırakılan kalem için maliyet hesaplanmaz ve Sonuçlar'da uyarı çıkar.</p>
      <div className="grid">
        {project.materials.map((m) => (
          <OptNum key={m.material_id} label={`${m.material_designation} (${m.material_id})`} unit="€/kg"
            value={ci.material_price_eur_per_kg[m.material_id]} onChange={(v) => setPrice(m.material_id, v)} />
        ))}
        <OptNum label="Kaynak / işçilik süresi" unit="saat" value={ci.welding_hours} onChange={(v) => patch({ welding_hours: v })} />
        <OptNum label="Saat ücreti" unit="€/saat" value={ci.labor_rate_eur_per_hour} onChange={(v) => patch({ labor_rate_eur_per_hour: v })} />
        <OptNum label="NDT toplam bedeli" unit="€" value={ci.ndt_cost_eur} onChange={(v) => patch({ ndt_cost_eur: v })} />
        <OptNum label="Boya / kaplama toplam bedeli" unit="€" value={ci.paint_cost_eur} onChange={(v) => patch({ paint_cost_eur: v })} />
      </div>
    </div>
  );
}
