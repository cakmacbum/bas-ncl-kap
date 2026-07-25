import React, { useState } from "react";
import { STATUS_TR, STATUS_CLASS } from "./i18n";
import type { CalcResult } from "./types";

// ---------- Panel ----------
export function Panel(props: {
  title: string;
  meta?: string;
  desc?: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="panel">
      <div className="panel__head">
        <div className="panel__title">
          {props.title}
          {props.meta && <span>{props.meta}</span>}
        </div>
        {props.right}
      </div>
      {props.desc && <div className="panel__desc">{props.desc}</div>}
      <div className="panel__body">{props.children}</div>
    </div>
  );
}

// ---------- Akordeon bölümü (dar formda tek bölüm açık) ----------
export function AccordionSection(props: {
  id: string;
  title: string;
  meta?: string;
  desc?: string;
  open: boolean;
  onToggle: (id: string) => void;
  children: React.ReactNode;
}) {
  const panelId = `acc-panel-${props.id}`;
  return (
    <div className={`accordion${props.open ? " accordion--open" : ""}`}>
      <button
        type="button"
        className="accordion__head"
        aria-expanded={props.open}
        aria-controls={panelId}
        onClick={() => props.onToggle(props.id)}
      >
        <svg className="accordion__chevron" width="14" height="14" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="accordion__title">{props.title}</span>
        {props.meta && <span className="accordion__meta">{props.meta}</span>}
      </button>
      {props.open && (
        <div className="accordion__body" id={panelId}>
          {props.desc && <div className="panel__desc accordion__desc">{props.desc}</div>}
          {props.children}
        </div>
      )}
    </div>
  );
}

// ---------- Segment sekmesi (önizleme: 2D / 3D / kesin model) ----------
export function SegmentTabs<T extends string>(props: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
  ariaLabel: string;
}) {
  return (
    <div className="seg-tabs" role="tablist" aria-label={props.ariaLabel}>
      {props.options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="tab"
          aria-selected={props.value === o.value}
          className={`seg-tabs__btn${props.value === o.value ? " is-active" : ""}`}
          onClick={() => props.onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

// ---------- Yardım ipucu (?) ----------
function HelpDot({ text }: { text: string }) {
  return (
    <span className="help-dot" tabIndex={0}>
      ?<span className="help-pop">{text}</span>
    </span>
  );
}

// ---------- Sayısal alan ----------
export function NumField(props: {
  label: string;
  unit?: string;
  value: number;
  onChange: (v: number) => void;
  hint?: string;
  help?: string;
  step?: number;
  onFocus?: () => void;
  onBlur?: () => void;
}) {
  return (
    <label className="field" onMouseEnter={props.onFocus}>
      <span className="field__label">
        <span>
          {props.label}
          {props.help && <HelpDot text={props.help} />}
        </span>
        {props.unit && <span className="field__unit">{props.unit}</span>}
      </span>
      <input
        className="input"
        type="number"
        step={props.step ?? "any"}
        value={Number.isFinite(props.value) ? props.value : ""}
        onChange={(e) => {
          // Boş alan parseFloat("")=NaN üretir; NaN JSON'da null olup backend'de
          // hataya/500'e yol açabilir. Boşsa 0 gönder, geçersizse yok say.
          const raw = e.target.value;
          if (raw === "") return props.onChange(0);
          const n = parseFloat(raw);
          if (Number.isFinite(n)) props.onChange(n);
        }}
        onFocus={props.onFocus}
        onBlur={props.onBlur}
      />
      {props.hint && <span className="field__hint">{props.hint}</span>}
    </label>
  );
}

// ---------- Metin alanı ----------
export function TextField(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  hint?: string;
}) {
  return (
    <label className="field">
      <span className="field__label">{props.label}</span>
      <input
        className="input"
        style={{ fontFamily: "var(--font-sans)" }}
        type="text"
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
      />
      {props.hint && <span className="field__hint">{props.hint}</span>}
    </label>
  );
}

// ---------- Seçim alanı ----------
export function SelectField(props: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (v: string) => void;
  help?: string;
  onFocus?: () => void;
}) {
  return (
    <label className="field" onMouseEnter={props.onFocus}>
      <span className="field__label">
        <span>
          {props.label}
          {props.help && <HelpDot text={props.help} />}
        </span>
      </span>
      <select
        className="select"
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        onFocus={props.onFocus}
      >
        {props.options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

// ---------- Durum rozeti ----------
export function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_CLASS[status] ?? "badge--nc";
  return <span className={`badge ${cls}`}>{STATUS_TR[status] ?? status}</span>;
}

// ---------- Genişleyebilir sonuç satırı ----------
export function ResultRow({ r }: { r: CalcResult }) {
  const [open, setOpen] = useState(false);
  const hasDetail = r.intermediate_values.length > 0 || r.warnings.length > 0 || r.assumptions.length > 0;
  const util =
    r.utilization_ratio != null ? `${(r.utilization_ratio * 100).toFixed(1)}%` : "—";
  const result =
    r.final_result != null ? `${r.final_result.toFixed(2)} ${r.final_result_unit}` : "—";

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpen(!open);
    }
  };

  return (
    <>
      <tr
        className={`result-row${hasDetail ? " table__expand" : ""}${r.governing ? " result-row--governing" : ""}`}
        onClick={() => hasDetail && setOpen(!open)}
        onKeyDown={hasDetail ? handleKeyDown : undefined}
        role={hasDetail ? "button" : undefined}
        tabIndex={hasDetail ? 0 : undefined}
        aria-expanded={hasDetail ? open : undefined}
        aria-label={hasDetail ? `${r.component_id ?? "—"} ${r.status} detaylarını ${open ? "kapat" : "aç"}` : undefined}
      >
        <td>
          {hasDetail && (
            <span className="dim mono" style={{ marginRight: 8 }} aria-hidden="true">
              {open ? "▾" : "▸"}
            </span>
          )}
          {r.component_id ?? "—"}
          {r.governing && (
            <span className="badge badge--review" style={{ marginLeft: 8, fontSize: "var(--fs-2xs)" }}>
              Yöneten
            </span>
          )}
        </td>
        <td className="mono dim">{r.clause_reference || "—"}</td>
        <td className="num">{result}</td>
        <td className="num">{util}</td>
        <td>
          <StatusBadge status={r.status} />
        </td>
      </tr>
      {open &&
        r.intermediate_values.map((iv, i) => (
          <tr className="subtable" key={i}>
            <td colSpan={2} className="k">
              {iv.name} — {iv.description}
            </td>
            <td colSpan={3} className="v">
              {typeof iv.value === "number" ? iv.value.toFixed(3) : iv.value}{" "}
              {iv.unit}
            </td>
          </tr>
        ))}
      {open &&
        r.warnings.map((w, i) => (
          <tr className="subtable" key={`w${i}`}>
            <td colSpan={5} style={{ color: "var(--review)" }}>
              ⚠ {w}
            </td>
          </tr>
        ))}
      {open &&
        r.assumptions.map((a, i) => (
          <tr className="subtable" key={`a${i}`}>
            <td colSpan={5} style={{ color: "var(--text-dim)" }}>
              • {a}
            </td>
          </tr>
        ))}
    </>
  );
}
