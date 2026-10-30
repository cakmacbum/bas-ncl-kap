// FEA modu arayüzü (P13): Analitik/FEA anahtarı + ilerleme + SCL linearizasyon tablosu.
// GÖSTERGE AMAÇLI — ASME onayı / mühendis değerlendirmesi değildir.
import { useMemo, useState } from "react";
import { SegmentTabs } from "../components";
import { CLASSIFICATION_NOTE, evaluateAll, type EquivMethod } from "./linearize";
import type { FeaState } from "./useFea";
import { FEA_DISCLAIMER } from "./types";

export type StressSource = "analytic" | "fea";

const PHASE_TR: Record<string, string> = { mesh: "Ağ üretiliyor", assemble: "Rijitlik matrisi", factor: "Çözüm", stress: "Gerilmeler" };

export function FeaToggle({ source, onChange, fea }: { source: StressSource; onChange: (s: StressSource) => void; fea: FeaState }) {
  return (
    <div className="fea-toggle">
      <SegmentTabs<StressSource>
        ariaLabel="Gerilme kaynağı"
        value={source}
        onChange={onChange}
        options={[{ value: "analytic", label: "Analitik" }, { value: "fea", label: "FEA" }]}
      />
      {source === "fea" && fea.status === "running" && (
        <>
          <div className="fea-toggle__bar" role="progressbar" aria-valuemin={0} aria-valuemax={100}
            aria-valuenow={Math.round(fea.progress * 100)} aria-label="FEA çözüm ilerlemesi">
            <i style={{ width: `${Math.round(fea.progress * 100)}%` }} />
          </div>
          <span className="fea-toggle__msg">{PHASE_TR[fea.phase ?? ""] ?? "Çözülüyor"} · %{Math.round(fea.progress * 100)}</span>
        </>
      )}
      {source === "fea" && fea.status === "error" && <span className="fea-toggle__msg" role="alert">FEA hatası: {fea.error}</span>}
    </div>
  );
}

const f1 = (v: number) => (Number.isFinite(v) ? v.toFixed(1) : "—");

export function SclCard({ fea, allowable }: { fea: FeaState; allowable: number | null }) {
  const [method, setMethod] = useState<EquivMethod>("vonMises");
  const res = fea.result;
  const rows = useMemo(() => (res ? evaluateAll(res, allowable, method) : []), [res, allowable, method]);
  if (!res || fea.status === "running") return null;
  const warnings = res.warnings ?? [];
  return (
    <details className="fea-scl" open>
      <summary>SCL linearizasyonu (Div.2 Part 5) — {rows.length} çizgi</summary>
      <div className="fea-scl__ctl">
        <label>
          Eşdeğer gerilme{" "}
          <select value={method} onChange={(e) => setMethod(e.target.value as EquivMethod)}>
            <option value="vonMises">von Mises</option>
            <option value="tresca">Tresca</option>
          </select>
        </label>
        <span>S = {allowable != null ? `${allowable.toFixed(1)} MPa` : "tanımsız (sınır kontrolü yok)"}</span>
      </div>
      <table>
        <thead>
          <tr><th>SCL</th><th>Pm/PL</th><th>Pb</th><th>PL+Pb(+Q)</th><th>Tepe</th><th>Kontrol</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.spec.id}>
              <td title={r.classification}>{r.spec.label}</td>
              <td>{r.eq ? f1(r.eq.membrane) : "—"}</td>
              <td>{r.eq ? f1(r.eq.bending) : "—"}</td>
              <td>{r.eq ? f1(Math.max(r.eq.mbInner, r.eq.mbOuter)) : "—"}</td>
              <td>{r.eq ? f1(Math.max(r.eq.peakInner, r.eq.peakOuter)) : "—"}</td>
              <td>
                {r.checks.length === 0 ? "—" : r.checks.map((c) => (
                  <span key={c.name} className={c.pass ? "is-pass" : "is-fail"} title={`${c.name}: ${f1(c.value)} / ${f1(c.limit)} MPa`}>
                    {c.name} {(c.ratio * 100).toFixed(0)}%{c.pass ? " ✓" : " ✗"}{" "}
                  </span>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="fea-scl__note">
        MPa. {CLASSIFICATION_NOTE}
        {warnings.length > 0 && <><br />Uyarılar: {warnings.join(" · ")}</>}
        <br /><strong>{res.disclaimer ?? FEA_DISCLAIMER}</strong>
      </p>
    </details>
  );
}
