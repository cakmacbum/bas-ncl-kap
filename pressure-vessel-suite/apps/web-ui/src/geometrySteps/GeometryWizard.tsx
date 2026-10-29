// Step 03 — beş alt adımlı geometri sihirbazı (3.1 gövde · 3.2 bombe · 3.3 flanşlı nozul · 3.4 manşon · 3.5 mesnet).
// Alt adım şeridi serbest gezilebilir; her sekmede adımın durumu (✓ / ⚠n / ✕n) gösterilir.

import { useMemo } from "react";
import { useStore, type GeoSubStep } from "../store";
import { GEO_STEP_TR } from "../i18n";
import { Step1BodyChain } from "./Step1BodyChain";
import { Step2Heads } from "./Step2Heads";
import { Step3FlangedNozzles } from "./Step3FlangedNozzles";
import { Step4Couplings } from "./Step4Couplings";
import { Step5Supports } from "./Step5Supports";
import { IssuesPanel, computeIssues, stepIssueCounts, type WizardIssue } from "./IssuesPanel";
import "./wizard.css";

const STEPS = [Step1BodyChain, Step2Heads, Step3FlangedNozzles, Step4Couplings, Step5Supports];

/** Sekme durumu: ✕n hata · ⚠n uyarı; ikisi de yoksa ✓ (bilgi seviyesi sayılmaz). */
function StepStatus({ error, warn }: { error: number; warn: number }) {
  if (error === 0 && warn === 0) {
    return <span className="gw-tab__badge gw-tab__badge--ok" title="Sorun yok">✓</span>;
  }
  return (
    <span className="gw-tab__badge" title={`${error} hata, ${warn} uyarı`}>
      {error > 0 && <span className="gw-tab__badge--err">✕{error}</span>}
      {warn > 0 && <span className="gw-tab__badge--warn">⚠{warn}</span>}
    </span>
  );
}

export function GeometryWizard({ issues: given }: { issues?: WizardIssue[] }) {
  const project = useStore((s) => s.project);
  const sub = useStore((s) => s.geoSubStep);
  const setSub = useStore((s) => s.setGeoSubStep);

  const own = useMemo(() => computeIssues(project), [project]);
  const issues = given ?? own;
  const counts = stepIssueCounts(issues);
  const Active = STEPS[sub] ?? STEPS[0];

  return (
    <div className="gw">
      <nav className="gw-bar" role="tablist" aria-label="Geometri alt adımları">
        {GEO_STEP_TR.map((title, i) => (
          <button key={title} type="button" role="tab" id={`gw-tab-${i}`} aria-selected={sub === i}
            aria-controls="gw-panel" className={`gw-tab${sub === i ? " is-active" : ""}`} title={title}
            onClick={() => setSub(i as GeoSubStep)}>
            <span className="gw-tab__no">3.{i + 1}</span>
            <span className="gw-tab__title">{title}</span>
            <StepStatus error={counts[i].error} warn={counts[i].warn} />
          </button>
        ))}
      </nav>
      <IssuesPanel issues={issues} />
      <div id="gw-panel" role="tabpanel" aria-labelledby={`gw-tab-${sub}`} className="gw-panel">
        <Active />
      </div>
      <nav className="gw-nav" aria-label="Alt adım gezinmesi">
        <button type="button" className="btn btn--ghost btn--sm" disabled={sub === 0}
          onClick={() => setSub((sub - 1) as GeoSubStep)}>← Önceki adım</button>
        <span className="gw-nav__pos">3.{sub + 1} / 5</span>
        <button type="button" className="btn btn--ghost btn--sm" disabled={sub === 4}
          onClick={() => setSub((sub + 1) as GeoSubStep)}>Sonraki adım →</button>
      </nav>
    </div>
  );
}
