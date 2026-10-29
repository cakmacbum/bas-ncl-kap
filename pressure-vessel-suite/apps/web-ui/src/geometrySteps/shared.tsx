// Step 03 sihirbazı ortak parçaları: aralık ipuçlu alan, z kaydırıcı, yerleşim alanları.
// K4: aralık dışı değer sessizce kırpılmaz; kırmızı not gösterilir ve ilgili eylem engellenir.

import React from "react";
import { FRAME_KIND_TR } from "../i18n";
import { SelectField } from "../components";
import type { ComponentFrame } from "../geometryContract";
import type { Support } from "../types";
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

/** Uzun açıklama için etiket yanındaki `?` simgesi (title tooltip; odaklanabilir). */
function HelpMark({ text }: { text: string }) {
  return (
    <span className="gw-help" role="img" tabIndex={0} title={text} aria-label={`Yardım: ${text}`}>?</span>
  );
}

/**
 * Sayısal alan. İpucu tek satır: "izinli aralık · not". Aralık dışı değer kırmızı uyarı olur, kırpılmaz.
 * Salt-okunur alan "hesaplanan" rozeti alır. Uzun açıklama `help` ile `?` balonunda gösterilir.
 */
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
  help?: string;
}) {
  const { value, min, max, unit } = props;
  const bad = !props.readOnly && outOfRange(value, min, max);
  const hasRange = min != null || max != null;
  const hint = [!props.readOnly && hasRange ? `izinli ${rangeText(min, max, unit)}` : "", props.note ?? ""]
    .filter(Boolean).join(" · ");
  return (
    <label className="field gw-field" title={props.title}>
      <span className="field__label">
        <span>{props.label}</span>
        {unit && <span className="field__unit">{unit}</span>}
        {props.help && <HelpMark text={props.help} />}
        {props.readOnly && <span className="gw-calc">hesaplanan</span>}
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
      {bad ? (
        <span className="gw-range gw-range--bad" role="alert">
          {`${fmt(value, 2)}${unit ? ` ${unit}` : ""} aralık dışı (izinli ${rangeText(min, max, unit)}) — kırpılmadı`}
        </span>
      ) : hint ? (
        <span className="gw-hint">{hint}</span>
      ) : null}
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

/** Alt adımın başındaki tek cümle: bu adımda ne yapılır. */
export function StepIntro({ children }: { children: React.ReactNode }) {
  return <p className="gw-intro">{children}</p>;
}

/**
 * Açılır/kapanır alan grubu (native details: klavye hazır). Tıklama kart seçimine yayılmaz.
 * "Ana ölçüler" açık, "Ayrıntılar" varsayılan kapalı kullanılır.
 */
export function Group(props: { title: string; open?: boolean; children: React.ReactNode }) {
  return (
    <details className="gw-group" open={props.open} onClick={(e) => e.stopPropagation()}>
      <summary className="gw-group__sum">{props.title}</summary>
      <div className="gw-group__body">{props.children}</div>
    </details>
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

/**
 * Ayak ölçülerinin etkin değerleri: alan boşsa CAD'in (src/cad/parts/legs.ts) kullandığı varsayılan.
 * Editör bu değerleri gösterir; kullanıcı değiştirince alan doldurulur (null kalan alan = CAD varsayılanı).
 */
export function legDefaults(s: Support) {
  const type = s.leg_section_type ?? "pipe";
  const t = Math.max(s.leg_thickness_mm ?? 6, 1);
  const d = s.leg_diameter_mm ?? 114.3;
  const h = type === "pipe" ? d : (s.leg_profile_height_mm ?? s.leg_diameter_mm ?? 100);
  const w = type === "pipe" ? d : (s.leg_profile_width_mm ?? h);
  const area = s.base_plate_area_mm2 ? Math.sqrt(s.base_plate_area_mm2) : 0;
  return {
    type, h, w, t, d,
    tw: s.leg_web_thickness_mm ?? t,
    tf: s.leg_flange_thickness_mm ?? t,
    padL: s.leg_pad_length_mm ?? 2.5 * h,
    padW: s.leg_pad_width_mm ?? 2 * w,
    padT: s.leg_pad_thickness_mm ?? 10,
    padExt: s.leg_pad_top_extension_mm ?? 50,
    plateL: s.base_plate_length_mm ?? (area || 2 * h + 40),
    plateW: s.base_plate_width_mm ?? (area || 2 * w + 40),
    plateT: s.base_plate_thickness_mm ?? 16,
    boltCount: s.anchor_bolt_count ?? 4,
    boltD: s.anchor_bolt_diameter_mm ?? 20,
    startAngle: s.leg_start_angle_deg ?? 0,
  };
}
