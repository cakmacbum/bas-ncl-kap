// Step 03 sihirbazı ortak parçaları: aralık ipuçlu alan, z kaydırıcı, yerleşim alanları.
// K4: aralık dışı değer sessizce kırpılmaz; kırmızı not gösterilir ve ilgili eylem engellenir.

import React from "react";
import { FRAME_KIND_TR } from "../i18n";
import { SelectField } from "../components";
import type { ComponentFrame } from "../geometryContract";
import "./wizard.css";

export const fmt = (n: number, d = 1) =>
  Number.isFinite(n) ? String(+n.toFixed(d)) : "—";

export function outOfRange(value: number, min?: number, max?: number): boolean {
  if (!Number.isFinite(value)) return true;
  return (min != null && value < min) || (max != null && value > max);
}

function rangeText(min?: number, max?: number, unit = ""): string {
  const u = unit ? ` ${unit}` : "";
  if (min != null && max != null) return `${fmt(min, 2)}–${fmt(max, 2)}${u}`;
  if (min != null) return `≥ ${fmt(min, 2)}${u}`;
  if (max != null) return `≤ ${fmt(max, 2)}${u}`;
  return "";
}

/** "değer · izinli aralık" ipuçlu sayısal alan. */
export function RField(props: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
  readOnly?: boolean;
  note?: string;
  title?: string;
}) {
  const { value, min, max, unit } = props;
  const bad = !props.readOnly && outOfRange(value, min, max);
  const hasRange = min != null || max != null;
  return (
    <label className="field gw-field" title={props.title}>
      <span className="field__label">
        <span>{props.label}</span>
        {unit && <span className="field__unit">{unit}</span>}
      </span>
      <input
        className={`input${bad ? " gw-input--bad" : ""}`}
        type="number"
        step={props.step ?? "any"}
        readOnly={props.readOnly}
        aria-invalid={bad || undefined}
        value={Number.isFinite(value) ? value : ""}
        onChange={(e) => {
          const raw = e.target.value;
          if (raw === "") return props.onChange(0);
          const n = parseFloat(raw);
          if (Number.isFinite(n)) props.onChange(n);
        }}
      />
      {hasRange && !props.readOnly && (
        <span className={`gw-range${bad ? " gw-range--bad" : ""}`} role={bad ? "alert" : undefined}>
          {bad
            ? `${fmt(value, 2)}${unit ? ` ${unit}` : ""} aralık dışı (izinli ${rangeText(min, max, unit)}) — kırpılmadı`
            : `${fmt(value, 2)}${unit ? ` ${unit}` : ""} · izinli ${rangeText(min, max, unit)}`}
        </span>
      )}
      {props.note && <span className="field__hint">{props.note}</span>}
    </label>
  );
}

/** Sayı kutusu + kaydırıcı. Kaydırıcı görsel olarak sınırlıdır; sayı kutusu kırpılmaz. */
export function SliderField(props: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (v: number) => void;
  unit?: string;
  step?: number;
}) {
  const span = Math.max(props.max - props.min, 0);
  const shown = Math.min(Math.max(props.value, props.min), props.max);
  return (
    <div className="gw-slider">
      <RField label={props.label} unit={props.unit} value={props.value}
        min={props.min} max={props.max} step={props.step} onChange={props.onChange} />
      <input type="range" className="gw-slider__range" aria-label={`${props.label} kaydırıcı`}
        min={props.min} max={props.max} step={props.step ?? (span > 200 ? 1 : 0.5)}
        value={Number.isFinite(shown) ? shown : props.min}
        onChange={(e) => props.onChange(parseFloat(e.target.value))} />
    </div>
  );
}

/** Küçük segment düğmeleri (radyo grubu). */
export function ChipGroup<T extends string | number>(props: {
  label: string;
  value: T;
  options: { value: T; label: string; disabled?: boolean; title?: string }[];
  onChange: (v: T) => void;
}) {
  return (
    <div className="gw-chips" role="radiogroup" aria-label={props.label}>
      {props.options.map((o) => (
        <button key={String(o.value)} type="button" role="radio" aria-checked={props.value === o.value}
          disabled={o.disabled} title={o.title}
          className={`gw-chip${props.value === o.value ? " is-active" : ""}`}
          onClick={() => props.onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function frameLabel(f: ComponentFrame): string {
  return `${f.id} (${FRAME_KIND_TR[f.kind]?.toLowerCase() ?? f.kind})`;
}

/** Nozul/manşon için seçilebilir host'lar: tüm gövde/koni ve uç bombeler. */
export function hostFrames(frames: ComponentFrame[]): ComponentFrame[] {
  return frames.filter((f) => !(f.kind === "head" && f.head?.side === "internal"));
}

export function hostLength(f: ComponentFrame | undefined): number {
  return f ? Math.max(f.zEnd - f.zStart, 0) : 0;
}

/** Bombe iç yarıçapı (ekvator). */
export function headRadius(f: ComponentFrame): number {
  return f.head?.side === "left" ? f.rInEnd : f.rInStart;
}

export const THETA_QUICK = [
  { v: 0, h: "0° Üst", p: "0°" },
  { v: 90, h: "90° Sağ", p: "90°" },
  { v: 180, h: "180° Alt", p: "180°" },
  { v: 270, h: "270° Sol", p: "270°" },
];

export interface Placement {
  host: string;
  z: number;
  theta: number;
  headD: number; // bombe host'ta yerleşim çapı (0 = tepe)
}

/** host + z (veya bombe yerleşim çapı) + θ alanları — nozul ve manşon formlarında ortak. */
export function PlacementFields(props: {
  frames: ComponentFrame[];
  value: Placement;
  onChange: (patch: Partial<Placement>) => void;
  horizontal: boolean;
}) {
  const { frames, value, onChange } = props;
  const hosts = hostFrames(frames);
  const host = frames.find((f) => f.id === value.host);
  const onHead = host?.kind === "head";
  const L = hostLength(host);
  return (
    <>
      <SelectField label="Host (nereye gelecek?)" value={host ? value.host : ""}
        options={[
          ...(host ? [] : [{ value: "", label: "— host seç —" }]),
          ...hosts.map((f) => ({ value: f.id, label: frameLabel(f) })),
        ]}
        onChange={(v) => onChange({ host: v })} />
      {onHead && host ? (
        <SliderField label="Yerleşim çapı (bombe ekseninden)" unit="mm" value={value.headD}
          min={0} max={2 * headRadius(host)} onChange={(v) => onChange({ headD: v })} />
      ) : (
        <SliderField label="Konum z (host başından)" unit="mm" value={value.z}
          min={0} max={L} onChange={(v) => onChange({ z: v })} />
      )}
      <div className="gw-theta">
        <RField label="Çevresel açı θ" unit="°" value={value.theta} min={0} max={360}
          onChange={(v) => onChange({ theta: v })} />
        <div className="gw-chips" role="group" aria-label="θ hızlı seçim">
          {THETA_QUICK.map((q) => (
            <button key={q.v} type="button" className={`gw-chip${value.theta === q.v ? " is-active" : ""}`}
              onClick={() => onChange({ theta: q.v })}>
              {props.horizontal ? q.h : q.p}
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

export function Section(props: { title: string; meta?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="gw-sec">
      <h3 className="gw-sec__title">{props.title}{props.meta && <span>{props.meta}</span>}</h3>
      {props.children}
    </section>
  );
}
