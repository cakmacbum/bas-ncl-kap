// Sorunlar paneli: zincir tutarlılığı + nozul yerleşimi + destek konumu + katalog uyarısı.
// Her satır tıklanınca ilgili alt adıma gider ve parçayı seçer.

import { useState } from "react";
import { COUPLING_TYPES, useStore } from "../store";
import { catalogsUnverified, upnCatalog } from "../data/catalogs";
import { legDefaults } from "./shared";
import { geometryIssues } from "../geometryValidation";
import { chainIssues, componentFrames, nozzlePlacement, tangentDatum } from "../vesselModel";
import type { Selection, VesselProject } from "../geometryContract";
import { GEO_STEP_TR } from "../i18n";
import { headDepthIssueMessage } from "./headDepth";

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

  for (const h of project.heads) {
    const msg = headDepthIssueMessage(h);
    if (msg) {
      out.push({ id: `head-depth-${h.head_id}`, level: "error", blocking: true, step: 1, message: msg,
        target: { kind: "head", id: h.head_id } });
    }
  }

  for (const g of geometryIssues(project)) {
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

  // Ayak ölçü kuralları (geometri; hesap değil). Dikey kapta location_mm = ayak üst ucu kotu (alt teğetten).
  const first = frames[0];
  // supportGeom.vesselBottomZ ile aynı mantık (replicad'i UI paketine çekmemek için yerel kopya).
  const vesselBottom = first?.head?.side === "left" ? first.zStart - first.thickness : (first?.zStart ?? 0);
  const shells = frames.filter((f) => f.kind === "shell" || f.kind === "cone");
  const shellLo = shells.length ? Math.min(...shells.map((f) => f.zStart)) : 0;
  const shellHi = shells.length ? Math.max(...shells.map((f) => f.zEnd)) : 0;
  project.supports.forEach((s) => {
    if (s.type !== "leg") return;
    const target: Selection = { kind: "support", id: s.support_id };
    const d = legDefaults(s);
    if (d.type === "channel" && (!(d.h > 0) || !(d.w > 0) || d.tw >= d.h / 2 || d.tf >= d.w)) {
      out.push({ id: `leg-profile-${s.support_id}`, level: "error", blocking: true, step: 4, target,
        message: !(d.h > 0) || !(d.w > 0)
          ? `${s.support_id}: U profil boyutları (h = ${d.h}, b = ${d.w} mm) pozitif olmalı. [LEG_PROFILE_INVALID]`
          : `${s.support_id}: U profil geçersiz — gövde tw = ${d.tw} mm < h/2 = ${+(d.h / 2).toFixed(1)} mm ve kanat tf = ${d.tf} mm < b = ${d.w} mm olmalı. [LEG_PROFILE_INVALID]` });
    }
    if (project.orientation !== "vertical") return;
    const zTop = left + s.location_mm;
    const baseBottom = zTop - s.height_mm;
    if (baseBottom > vesselBottom + 1e-6) {
      out.push({ id: `leg-short-${s.support_id}`, level: "error", blocking: true, step: 4, target,
        message: `${s.support_id}: ayak kap altına ulaşmıyor — taban sacı alt kotu kap altından ${+(baseBottom - vesselBottom).toFixed(0)} mm yukarıda; profil boyu en az ${+(zTop - vesselBottom).toFixed(0)} mm olmalı (şu an ${+s.height_mm.toFixed(0)} mm). [LEG_TOO_SHORT]` });
    }
    if (shells.length) {
      const padTop = zTop + d.padExt;
      const padBot = padTop - d.padL;
      if (padBot < shellLo - 1e-6 || padTop > shellHi + 1e-6) {
        out.push({ id: `leg-pad-${s.support_id}`, level: "warn", blocking: false, step: 4, target,
          message: `${s.support_id}: ayak pedi z aralığı (${+(padBot - left).toFixed(0)}…${+(padTop - left).toFixed(0)} mm) gövde/koni aralığının (${+(shellLo - left).toFixed(0)}…${+(shellHi - left).toFixed(0)} mm) dışına taşıyor. [LEG_PAD_OFF_SHELL]` });
      }
    }
  });
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

/**
 * Adım başına hata/uyarı sayısı. 0..4 anahtarları her zaman vardır (sorun yoksa 0).
 * Bilgi (info) seviyesi sayaca girmez.
 */
export function stepIssueCounts(issues: WizardIssue[]): Record<number, { error: number; warn: number }> {
  const out: Record<number, { error: number; warn: number }> = {};
  for (let s = 0; s <= 4; s++) out[s] = { error: 0, warn: 0 };
  for (const i of issues) {
    if (i.level === "info") continue;
    if (i.level === "error") out[i.step].error += 1;
    else out[i.step].warn += 1;
  }
  return out;
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

/** UPN katalog satırı doğrulanmamışsa uyarı rozeti (CatalogBadge deseni). */
export function UpnBadge() {
  if (upnCatalog.verified) return null;
  return (
    <span className="gw-badge gw-badge--warn" title="UPN ölçüleri (EN 10279) standarttan elle girilmiştir, doğrulanmamıştır (verified:false). İmalat öncesi tedarikçi tablosuyla karşılaştırın.">
      UPN ölçüleri doğrulanmamış
    </span>
  );
}

/**
 * Daraltılmış tek satır "n hata · m uyarı ▸"; tıklanınca liste açılır.
 * Hata/uyarı yoksa panel gizlenir (adım şeridindeki rozetler yeterli).
 */
export function IssuesPanel({ issues }: { issues: WizardIssue[] }) {
  const [open, setOpen] = useState(false);
  const setGeoSubStep = useStore((s) => s.setGeoSubStep);
  const setSelection = useStore((s) => s.setSelection);
  const usesCatalog = useStore((s) => s.project.nozzles.some((n) => n.rating_class != null));
  const errors = issues.filter((i) => i.level === "error").length;
  const warns = issues.filter((i) => i.level === "warn").length;

  if (errors === 0 && warns === 0) return null;

  return (
    <section className="gw-issues" aria-label="Sorunlar paneli">
      <button type="button" className="gw-issues__sum" aria-expanded={open}
        onClick={() => setOpen((o) => !o)}>
        <span className={`gw-count${errors ? " gw-count--err" : " gw-count--warn"}`}>
          {errors} hata · {warns} uyarı
        </span>
        <span aria-hidden="true">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <>
          {usesCatalog && <div><CatalogBadge /></div>}
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
        </>
      )}
    </section>
  );
}
