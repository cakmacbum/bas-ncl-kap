// Sorunlar paneli: zincir tutarlılığı + nozul yerleşimi + destek konumu + katalog uyarısı.
// Her satır tıklanınca ilgili alt adıma gider ve parçayı seçer.

import { COUPLING_TYPES, useStore } from "../store";
import { catalogsUnverified } from "../data/catalogs";
import { geometryIssues } from "../geometryValidation";
import { chainIssues, componentFrames, nozzlePlacement, tangentDatum } from "../vesselModel";
import type { Selection, VesselProject } from "../geometryContract";
import { GEO_STEP_TR } from "../i18n";

export interface WizardIssue {
  id: string;
  level: "error" | "warn" | "info";
  step: 0 | 1 | 2 | 3 | 4;
  message: string;
  /** Sonuçlara geçişi engeller. */
  blocking: boolean;
  target?: Selection;
}

const COUPLING_SET = new Set<string>(COUPLING_TYPES);

// geometryValidation.ts bu kodları zincir uzunluğu/koni bilmeden üretir (yanlış pozitif);
// yerlerine çerçeve tabanlı kontroller kullanılır.
const SUPERSEDED = [/^junction-/, /stale-diameter$/, /^nozzle-\d+-(host|axial|head-position)$/];

function stepOfLegacy(code: string): WizardIssue["step"] {
  if (code.startsWith("head-")) return 1;
  if (code.startsWith("nozzle-")) return 2;
  return 0;
}

export function computeIssues(project: VesselProject): WizardIssue[] {
  const out: WizardIssue[] = [];
  const frames = componentFrames(project);
  const kindOf = new Map(frames.map((f) => [f.id, f.kind]));

  for (const c of chainIssues(project, frames)) {
    const kind = kindOf.get(c.id);
    out.push({
      id: `chain-${c.code}-${c.id}`, level: "error", blocking: true,
      step: kind === "head" ? 1 : 0, message: c.message,
      target: kind ? { kind, id: c.id } : undefined,
    });
  }

  for (const g of geometryIssues(project)) {
    if (SUPERSEDED.some((re) => re.test(g.code))) continue;
    out.push({ id: `geo-${g.code}`, level: g.blocking ? "error" : "warn", blocking: g.blocking,
      step: stepOfLegacy(g.code), message: g.message });
  }

  project.nozzles.forEach((nz) => {
    const res = nozzlePlacement(project, nz, frames);
    const step: WizardIssue["step"] = COUPLING_SET.has(nz.nozzle_type) ? 3 : 2;
    const target: Selection = { kind: "nozzle", id: nz.tag };
    if (!("error" in res)) return;
    const host = frames.find((f) => f.id === nz.host_component_id);
    const msg =
      res.error === "HOST_NOT_FOUND" ? `${nz.tag}: host (${nz.host_component_id}) zincirde yok.`
      : res.error === "INTERNAL_HEAD" ? `${nz.tag}: host zincir ortasındaki bombe — yerleşim yapılamaz.`
      : host && host.kind === "head"
        ? `${nz.tag}: yerleşim çapı ${nz.head_position_diameter ?? 0} mm bombe çapını aşıyor — kırpılmadı.`
        : `${nz.tag}: z = ${nz.axial_position} mm host boyunun (0–${host ? +(host.zEnd - host.zStart).toFixed(1) : "?"} mm) dışında — kırpılmadı.`;
    out.push({ id: `place-${nz.tag}`, level: "error", blocking: true, step, message: msg, target });
  });

  const { left, right } = tangentDatum(frames);
  const saddles = project.supports.filter((s) => s.type === "saddle");
  project.supports.forEach((s) => {
    const target: Selection = { kind: "support", id: s.support_id };
    const host = frames.find((f) => f.id === s.host_component_id);
    if (!s.host_component_id || !host) {
      out.push({ id: `sup-host-${s.support_id}`, level: "warn", blocking: false, step: 4, target,
        message: `${s.support_id}: host bileşen seçilmemiş.` });
      return;
    }
    if (s.type === "saddle") {
      const lo = host.zStart - left;
      const hi = host.zEnd - left;
      if (s.location_mm < lo || s.location_mm > hi) {
        out.push({ id: `sup-range-${s.support_id}`, level: "warn", blocking: false, step: 4, target,
          message: `${s.support_id}: eyer konumu ${s.location_mm} mm, host ${host.id} aralığının (${+lo.toFixed(0)}–${+hi.toFixed(0)} mm) dışında.` });
      }
      if (s.location_mm < 0 || s.location_mm > right - left) {
        out.push({ id: `sup-span-${s.support_id}`, level: "warn", blocking: false, step: 4, target,
          message: `${s.support_id}: eyer konumu teğet-teğet aralığın (0–${+(right - left).toFixed(0)} mm) dışında.` });
      }
    }
  });
  if (project.orientation !== "vertical" && saddles.length === 1) {
    out.push({ id: "sup-one-saddle", level: "info", blocking: false, step: 4,
      message: "Zick analizi iki eyer gerektirir; tek eyerle sonuç sınırlı olur." });
  }
  if (project.supports.length === 0) {
    out.push({ id: "sup-none", level: "info", blocking: false, step: 4,
      message: "Destek tanımlı değil — destek gerilme kontrolü yapılmaz." });
  }
  return out;
}

export function issueCountByStep(issues: WizardIssue[]): number[] {
  const counts = [0, 0, 0, 0, 0];
  for (const i of issues) if (i.level !== "info") counts[i.step] += 1;
  return counts;
}

const LEVEL_TR = { error: "Hata", warn: "Uyarı", info: "Bilgi" } as const;

export function CatalogBadge() {
  if (!catalogsUnverified) return null;
  return (
    <span className="gw-badge gw-badge--warn" title="Boru, flanş ve manşon ölçüleri kaynak kataloglarda doğrulanmamıştır (verified:false). İmalat öncesi tedarikçi/çizim verisiyle karşılaştırın.">
      Ölçüler doğrulanmamış katalogdan
    </span>
  );
}

export function IssuesPanel({ issues }: { issues: WizardIssue[] }) {
  const setGeoSubStep = useStore((s) => s.setGeoSubStep);
  const setSelection = useStore((s) => s.setSelection);
  const usesCatalog = useStore((s) => s.project.nozzles.some((n) => n.rating_class != null));
  const errors = issues.filter((i) => i.level === "error").length;
  const warns = issues.filter((i) => i.level === "warn").length;

  return (
    <section className="gw-issues" aria-label="Sorunlar paneli">
      <div className="gw-issues__head">
        <h3>Sorunlar</h3>
        <span className={`gw-count${errors ? " gw-count--err" : warns ? " gw-count--warn" : ""}`}>
          {errors} hata · {warns} uyarı
        </span>
        {usesCatalog && <CatalogBadge />}
      </div>
      {issues.length === 0 ? (
        <p className="gw-empty">Geometri tutarlı — zincir, nozul yerleşimi ve destekler için sorun yok.</p>
      ) : (
        <ul className="gw-issues__list">
          {issues.map((i) => (
            <li key={i.id}>
              <button type="button" className={`gw-issue gw-issue--${i.level}`}
                onClick={() => { setGeoSubStep(i.step); setSelection(i.target ?? null); }}>
                <b>{LEVEL_TR[i.level]}</b>
                <span>{i.message}</span>
                <em>{GEO_STEP_TR[i.step]}</em>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
