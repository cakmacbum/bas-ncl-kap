import { Panel } from "./components";
import { downloadBomCsv } from "./bomCsv";
import type { BomPayload } from "./types";

const kg = (v: number | null) => (v === null ? "—" : v.toFixed(1));
const eur = (v: number | null | undefined) =>
  v === null || v === undefined ? "—" : v.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** BOM + maliyet kartı (bilgi bölümü; kontrol değildir). K4: eksik kütle/fiyat gizlenmez. */
export function BomCard({ bom, name }: { bom?: BomPayload; name: string }) {
  if (!bom) return null;
  if (bom.error) {
    return (
      <Panel title="Malzeme Listesi (BOM) ve Maliyet" meta="üretilmedi">
        <p className="muted" style={{ margin: 0 }}>{bom.error}</p>
      </Panel>
    );
  }
  const c = bom.cost;
  return (
    <Panel
      title="Malzeme Listesi (BOM) ve Maliyet"
      meta={`${bom.lines.length} kalem · ${bom.total_mass_kg.toFixed(0)} kg${bom.mass_complete ? "" : " (eksik)"}`}
      desc="Bilgi bölümüdür, hesap kontrolü değildir. Kesim firesi, kaynak metali, cıvata/conta dahil değildir."
      right={<button className="btn" onClick={() => downloadBomCsv(bom, name)}>CSV indir</button>}
    >
      {bom.warnings.map((w, i) => (
        <div key={i} className="alert alert--warn" role="alert">⚠ {w}</div>
      ))}
      <table className="table">
        <thead>
          <tr>
            <th>Parça</th><th>Malzeme</th><th>Ölçü (mm)</th>
            <th style={{ textAlign: "right" }}>Adet</th>
            <th style={{ textAlign: "right" }}>Birim (kg)</th>
            <th style={{ textAlign: "right" }}>Toplam (kg)</th>
          </tr>
        </thead>
        <tbody>
          {bom.lines.map((l, i) => (
            <tr key={i} title={l.note || undefined}>
              <td>{l.part}{l.note && <span className="field__hint"> — {l.note}</span>}</td>
              <td>{l.material}</td>
              <td className="mono">{l.dimensions}</td>
              <td style={{ textAlign: "right" }}>{l.qty}</td>
              <td style={{ textAlign: "right" }} className="mono">{kg(l.unit_mass_kg)}</td>
              <td style={{ textAlign: "right" }} className="mono">{kg(l.total_mass_kg)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h4 style={{ margin: "18px 0 8px" }}>Maliyet tahmini</h4>
      {c.status !== "OK" && (
        <div className="alert alert--warn" role="alert">
          ⚠ Maliyet tamamlanamadı, toplam üretilmedi. Eksik girdiler:
          <ul className="err-list">{c.missing.map((m, i) => <li key={i}>{m}</li>)}</ul>
          Birim fiyatları Geometri &gt; Hesap girdileri &gt; BOM maliyet girdileri bölümüne girin.
        </div>
      )}
      {c.items.length > 0 && (
        <table className="table">
          <thead><tr><th>Kalem</th><th>Dayanak</th><th style={{ textAlign: "right" }}>Tutar (€)</th></tr></thead>
          <tbody>
            {c.items.map((it, i) => (
              <tr key={i}><td>{it.item}</td><td className="mono">{it.basis}</td>
                <td style={{ textAlign: "right" }} className="mono">{eur(it.cost_eur)}</td></tr>
            ))}
            <tr>
              <td><strong>Toplam</strong></td>
              <td>{c.status === "OK" ? "" : `Kısmi toplam: ${eur(c.partial_eur)} € (eksik)`}</td>
              <td style={{ textAlign: "right" }} className="mono"><strong>{eur(c.total_eur)}</strong></td>
            </tr>
          </tbody>
        </table>
      )}
    </Panel>
  );
}
