import { useMemo, useState } from "react";
import { Panel } from "../components";
import type { VesselProject } from "../types";
import { buildFlatParts } from "./fromProject";
import { toDxf, toSvg } from "./shapes";

function download(name: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: "application/dxf" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

/** Açınım şablonları kartı: SVG önizleme + parça başına DXF (R12). Bilgi amaçlı; hesap kontrolü değildir. */
export function FlatPatternCard({ project }: { project: VesselProject }) {
  const [weldGap, setWeldGap] = useState(0);
  const [petals, setPetals] = useState(8);
  const entries = useMemo(() => buildFlatParts(project, { weldGap, petals }), [project, weldGap, petals]);
  const base = project.project_number || "proje";
  return (
    <Panel title="Açınım şablonları" meta={`${entries.filter((e) => e.part).length} parça · DXF R12`}
      desc="Nötr eksen (orta yüzey) üzerinden, mm. Bombe petalleri yaklaşıktır: kalıp üreticisiyle doğrulayın.">
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 12 }}>
        <label>Kaynak ağzı payı (mm){" "}
          <input type="number" min={0} value={weldGap} onChange={(e) => setWeldGap(Math.max(0, Number(e.target.value) || 0))} style={{ width: 80 }} />
        </label>
        <label>Bombe petal sayısı{" "}
          <input type="number" min={3} step={1} value={petals} onChange={(e) => setPetals(Math.max(3, Math.round(Number(e.target.value) || 3)))} style={{ width: 70 }} />
        </label>
      </div>
      {entries.map((e) => (
        <div key={e.id} style={{ marginBottom: 16 }}>
          {e.part ? (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                <strong>{e.part.name}</strong>
                <button className="btn" onClick={() => download(`${base}-${e.id}.dxf`, toDxf(e.part!))}>DXF indir</button>
              </div>
              <div dangerouslySetInnerHTML={{ __html: toSvg(e.part, 420) }} />
              {e.part.notes.map((n, i) => <p key={i} className="muted" style={{ margin: "2px 0" }}>{n}</p>)}
            </>
          ) : (
            <p className="muted" style={{ margin: 0 }}><strong>{e.id}</strong>: şablon üretilmedi — {e.skipped}</p>
          )}
        </div>
      ))}
    </Panel>
  );
}
