// Step 03 — beş alt adımlı geometri sihirbazı (3.1 gövde · 3.2 bombe · 3.3 flanşlı nozul · 3.4 manşon · 3.5 mesnet).
// Alt adım çubuğu serbest gezilebilir; her sekmede o adımın sorun sayısı rozet olarak görünür.

import { useMemo } from "react";
import { useStore, type GeoSubStep } from "../store";
import { GEO_STEP_TR } from "../i18n";
import { Step1BodyChain } from "./Step1BodyChain";
import { Step2Heads } from "./Step2Heads";
import { Step3FlangedNozzles } from "./Step3FlangedNozzles";
import { Step4Couplings } from "./Step4Couplings";
import { Step5Supports } from "./Step5Supports";
import { IssuesPanel, computeIssues, issueCountByStep, type WizardIssue } from "./IssuesPanel";
import "./wizard.css";

const STEPS = [Step1BodyChain, Step2Heads, Step3FlangedNozzles, Step4Couplings, Step5Supports];

export function GeometryWizard({ issues: given }: { issues?: WizardIssue[] }) {
  const project = useStore((s) => s.project);
  const sub = useStore((s) => s.geoSubStep);
  const setSub = useStore((s) => s.setGeoSubStep);

  const own = useMemo(() => computeIssues(project), [project]);
  const issues = given ?? own;
  const counts = issueCountByStep(issues);
  const Active = STEPS[sub] ?? STEPS[0];

  return (
    <div className="gw">
      <nav className="gw-bar" role="tablist" aria-label="Geometri alt adımları">
        {GEO_STEP_TR.map((title, i) => (
          <button key={title} type="button" role="tab" id={`gw-tab-${i}`} aria-selected={sub === i}
            aria-controls="gw-panel" className={`gw-tab${sub === i ? " is-active" : ""}`}
            onClick={() => setSub(i as GeoSubStep)}>
            <span className="gw-tab__no">3.{i + 1}</span>
            <span className="gw-tab__title">{title}</span>
            {counts[i] > 0 && (
              <span className="gw-tab__badge" aria-label={`${counts[i]} sorun`}>{counts[i]}</span>
            )}
          </button>
        ))}
      </nav>
      <div id="gw-panel" role="tabpanel" aria-labelledby={`gw-tab-${sub}`} className="gw-panel">
        <Active />
      </div>
      <div className="gw-nav">
        <button type="button" className="btn btn--ghost btn--sm" disabled={sub === 0}
          onClick={() => setSub((sub - 1) as GeoSubStep)}>← Önceki adım</button>
        <button type="button" className="btn btn--ghost btn--sm" disabled={sub === 4}
          onClick={() => setSub((sub + 1) as GeoSubStep)}>Sonraki adım →</button>
      </div>
      <IssuesPanel issues={issues} />
    </div>
  );
}
