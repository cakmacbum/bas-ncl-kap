// Gerilme haritası: vertex boyama yardımcıları + lejant/bilgi kartı (HUD).
// Mesh pozisyonları zaten model çerçevesindedir (eksen +Z); yatay/dikey dönüşüm
// üst gruptaki rotasyondur, bu yüzden hover'da dünya noktası mesh.worldToLocal ile geri çevrilir.

import { useEffect, useState, type MutableRefObject } from "react";
import type { StressField, StressSample } from "./types";
import { KNUCKLE_WARNING } from "./knuckleNote";
import { allowablePosition, scaleGradientCss, scaleTicks, stressColor } from "./colorScale";

export type StressProbe = StressSample & { point: [number, number, number] };
export type ProbeSetter = (p: StressProbe | null) => void;

const NO_VALUE_COLOR: [number, number, number] = [0.55, 0.55, 0.58];

/** Her vertex için model çerçevesinde gerilme sorgular, 0…maxVm skalasında renk dizisi üretir. */
export function stressVertexColors(positions: Float32Array, field: StressField): Float32Array {
  const n = positions.length / 3;
  const out = new Float32Array(n * 3);
  const max = field.maxVm;
  for (let i = 0; i < n; i++) {
    const s = field.at([positions[3 * i], positions[3 * i + 1], positions[3 * i + 2]]);
    // vm=NaN: güvenilir değer yok (ör. analitik torisferik hamut) → gri, skalada sahte renk yok.
    const [r, g, b] = Number.isFinite(s.vm) ? stressColor(s.vm, max) : NO_VALUE_COLOR;
    out[3 * i] = r; out[3 * i + 1] = g; out[3 * i + 2] = b;
  }
  return out;
}

const ZONE_TR: Record<StressSample["zone"], string> = {
  membrane: "Membran", discontinuity: "Süreksizlik", nozzle: "Nozul çevresi",
  head: "Bombe", support: "Mesnet", unknown: "—",
};
const mpa = (v: number) => (Number.isFinite(v) ? `${v.toFixed(1)} MPa` : "—");

/** Sağda dikey skala + üstte bilgi kartı + fare altındaki nokta okuması. */
export function StressHud({ field, probeRef, source = "analytic", knuckleCheck, knuckleSelected = false }: {
  field: StressField;
  probeRef: MutableRefObject<ProbeSetter | null>;
  source?: "analytic" | "fea";
  /** Analitik modda: nokta torisferik hamut bölgesinde mi? */
  knuckleCheck?: (p: [number, number, number]) => boolean;
  /** Analitik modda: seçili bileşen torisferik bombe. */
  knuckleSelected?: boolean;
}) {
  const [probe, setProbe] = useState<StressProbe | null>(null);
  useEffect(() => {
    probeRef.current = setProbe;
    return () => { probeRef.current = null; };
  }, [probeRef]);

  const max = field.maxVm;
  const allowPos = allowablePosition(field.allowable, max);
  const noValue = probe != null && !Number.isFinite(probe.vm);
  const knuckleWarn = source === "analytic" && (knuckleSelected || noValue || (probe != null && !!knuckleCheck?.(probe.point)));

  return (
    <>
      <div className="stress-legend" role="img" aria-label={`Gerilme skalası 0 ile ${max.toFixed(0)} MPa arası`}>
        <span className="stress-legend__title">σ<sub>vm</sub> (MPa)</span>
        <div className="stress-legend__body">
          <div className="stress-legend__bar" style={{ background: scaleGradientCss() }}>
            {allowPos != null && (
              <span className="stress-legend__allow" style={{ bottom: `${allowPos * 100}%` }}
                title={`İzin verilen S = ${field.allowable!.toFixed(1)} MPa`}>
                <i /> S
              </span>
            )}
          </div>
          <div className="stress-legend__ticks">
            {scaleTicks(max).reverse().map((t) => <span key={t}>{t.toFixed(0)}</span>)}
          </div>
        </div>
      </div>

      <div className="stress-info" aria-live="polite">
        <p className="stress-info__note">
          {source === "fea"
            ? "Eksenel simetrik sonlu eleman çözümü (lineer elastik). Renkler duvardaki gerilmeyi gösterir."
            : "Kap içinde basınç her yerde aynıdır (giriş jetinin etkisi ~%0,04). Renkler duvardaki gerilmeyi gösterir."}
        </p>
        <p className="stress-info__badge">Gösterge amaçlı — ASME tasarım onayı değildir</p>
        {knuckleWarn && (
          <p className="stress-info__warn" role="alert">
            <strong>Hamut bölgesi:</strong> {KNUCKLE_WARNING}
          </p>
        )}
        {probe ? (
          <dl className="stress-info__probe">
            <dt>vm</dt><dd>{mpa(probe.vm)}</dd>
            <dt>Çevresel</dt><dd>{mpa(probe.hoop)}</dd>
            <dt>Eksenel</dt><dd>{mpa(probe.axial)}</dd>
            <dt>Bölge</dt><dd>{noValue ? "Düşük güven — FEA kullanın" : ZONE_TR[probe.zone]}</dd>
          </dl>
        ) : (
          <p className="stress-info__hint">Ayrıntı için fareyi modelin üzerine getirin.</p>
        )}
      </div>
    </>
  );
}
