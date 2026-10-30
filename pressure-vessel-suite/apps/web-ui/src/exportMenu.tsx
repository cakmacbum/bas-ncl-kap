import React, { useEffect, useRef, useState } from "react";
import { exportModel } from "./cad/cadClient";
import { EXPORT_OPTIONS, warningBadgeText, type ExportFormat } from "./geometryLayout";
import { exportDrawing, isDrawingFormat } from "./drawing/download";
import type { VesselProject } from "./types";

/** Önizleme sağ üstü: uyarı rozeti + "Dışa aktar ▾" menüsü (STEP/STL). */
export function PreviewActions({ project, warnings }: { project: VesselProject; warnings: string[] }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState<ExportFormat | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => { if (!root.current?.contains(e.target as Node)) setOpen(false); };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("mousedown", onDown); document.removeEventListener("keydown", onKey); };
  }, [open]);

  const run = async (fmt: ExportFormat) => {
    setOpen(false);
    setBusy(fmt);
    setErr(null);
    try {
      if (isDrawingFormat(fmt)) exportDrawing(project, fmt);
      else await exportModel(project, fmt);
    }
    catch (e) { setErr(e instanceof Error ? e.message : "Dışa aktarma başarısız"); }
    finally { setBusy(null); }
  };

  const badge = warningBadgeText(warnings.length);
  return (
    <div className="geo-actions" ref={root}>
      {err && <span className="geo-actions__err" role="alert">{err}</span>}
      {badge && <span className="geo-actions__warn" title={warnings.join("\n")}>{badge}</span>}
      <div className="geo-actions__menu">
        <button type="button" className="btn btn--sm" aria-haspopup="menu" aria-expanded={open}
          disabled={busy !== null} onClick={() => setOpen((v) => !v)}>
          {busy ? "Hazırlanıyor…" : "Dışa aktar ▾"}
        </button>
        {open && (
          <div className="geo-actions__list" role="menu">
            {EXPORT_OPTIONS.map((o) => (
              <button key={o.format} type="button" role="menuitem" onClick={() => run(o.format)}>{o.label}</button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
