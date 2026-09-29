import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";
import {
  applyGeometryAgentChanges,
  expandGeometryAgentChanges,
  geometryAgentCurrentValue,
} from "./geometryAgent";
import { useStore } from "./store";
import type { GeometryAgentChange, GeometryAgentSuggestion } from "./types";

const FIELD_LABELS: Record<string, string> = {
  inside_diameter: "İç çap",
  tangent_length: "Teğet uzunluğu",
  nominal_thickness: "Nominal kalınlık",
  type: "Bombe tipi",
  straight_flange_length: "Düz flanş uzunluğu",
  orientation: "Kap yönü",
};

const VALUE_LABELS: Record<string, string> = {
  elliptical: "Elipsoidal (2:1)",
  torispherical: "Torisferik",
  hemispherical: "Yarım küresel",
  flat: "Düz",
  horizontal: "Yatay",
  vertical: "Dikey",
};

function displayValue(_field: string, value: number | string | null): string {
  if (value == null) return "—";
  if (typeof value === "number") return `${value} mm`;
  return VALUE_LABELS[value] ?? value;
}

function changeKey(change: GeometryAgentChange): string {
  return `${change.target_type}:${change.target_id}:${change.field}`;
}

export function GeometryAgentDrawer(props: { open: boolean; onClose: () => void }) {
  const { project, activeShellId, setProject } = useStore();
  const [instruction, setInstruction] = useState("");
  const [suggestion, setSuggestion] = useState<GeometryAgentSuggestion | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const activeShell = project.shell_sections.find((shell) => shell.section_id === activeShellId)
    ?? project.shell_sections[0];

  useEffect(() => {
    if (!props.open) return;
    textareaRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") props.onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [props.open, props.onClose]);

  const effectiveChanges = useMemo(
    () => suggestion ? expandGeometryAgentChanges(project, suggestion.changes) : [],
    [project, suggestion]
  );

  const interpret = async () => {
    if (!instruction.trim() || !activeShell) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    setSuggestion(null);
    try {
      const result = await api.interpretGeometry({
        instruction: instruction.trim(),
        context: {
          active_shell_id: activeShell.section_id,
          shell_ids: project.shell_sections.map((shell) => shell.section_id),
          heads: project.heads.map((head, index) => ({
            head_id: head.head_id,
            side: index === 0 ? "left" : index === project.heads.length - 1 ? "right" : "other",
          })),
          diameter_relation: project.diameter_relation ?? "linked",
        },
      });
      setSuggestion(result);
    } catch (caught: any) {
      setError(caught?.message ?? "Ajan komutu yorumlayamadı.");
    } finally {
      setBusy(false);
    }
  };

  const apply = () => {
    if (!suggestion || effectiveChanges.length === 0) return;
    setProject((current) => applyGeometryAgentChanges(current, suggestion.changes));
    setSuggestion(null);
    setInstruction("");
    setNotice("Onaylanan geometri değişiklikleri projeye uygulandı.");
  };

  if (!props.open) return null;
  return (
    <>
      <button className="agent-backdrop" aria-label="Ajan panelini kapat" onClick={props.onClose} />
      <aside className="agent-drawer" role="dialog" aria-modal="true" aria-labelledby="agent-title">
        <div className="agent-drawer__head">
          <div>
            <span className="agent-drawer__eyebrow">HIZLI GİRİŞ</span>
            <h2 id="agent-title">Geometri Ajanı</h2>
          </div>
          <button className="icon-btn" type="button" onClick={props.onClose} aria-label="Kapat">×</button>
        </div>

        <div className="agent-drawer__body">
          <p className="agent-drawer__intro">
            Yalnızca söylediğiniz temel ölçüleri önerir. Hiçbir değişiklik onayınız olmadan uygulanmaz.
          </p>
          <div className="agent-target">
            <span>Aktif gövde</span>
            <strong>{activeShell?.section_id ?? "Gövde yok"}</strong>
          </div>
          <label className="field">
            <span className="field__label">Komut</span>
            <textarea
              ref={textareaRef}
              className="input agent-prompt"
              value={instruction}
              onChange={(event) => setInstruction(event.target.value)}
              onKeyDown={(event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === "Enter") interpret();
              }}
              placeholder="Örn. Çapı 1200 mm, boyu 2500 mm olsun; sol bombe eliptik ve 14 mm olsun."
              maxLength={2000}
            />
          </label>
          <button
            type="button"
            className="btn btn--primary agent-submit"
            disabled={busy || !instruction.trim() || !activeShell}
            onClick={interpret}
          >
            {busy ? "Yorumlanıyor…" : "Yorumla"}
          </button>
          <span className="agent-shortcut">Ctrl + Enter ile gönder</span>

          {error && <div className="agent-message agent-message--error" role="alert">{error}</div>}
          {notice && <div className="agent-message agent-message--success" role="status">{notice}</div>}

          {suggestion && (
            <section className="agent-preview" aria-label="Ajan değişiklik önizlemesi">
              <div className="agent-preview__head">
                <h3>Öneri Önizlemesi</h3>
                <span>{effectiveChanges.length} değişiklik</span>
              </div>
              {suggestion.summary && <p>{suggestion.summary}</p>}
              {effectiveChanges.length > 0 ? (
                <div className="agent-change-list">
                  {effectiveChanges.map((change) => (
                    <div className="agent-change" key={changeKey(change)}>
                      <div><strong>{FIELD_LABELS[change.field] ?? change.field}</strong><span>{change.target_id}</span></div>
                      <div className="agent-change__values">
                        <del>{displayValue(change.field, geometryAgentCurrentValue(project, change))}</del>
                        <span aria-hidden="true">→</span>
                        <ins>{displayValue(change.field, change.value)}</ins>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="agent-empty">Uygulanabilir bir değişiklik bulunmadı.</div>
              )}
              {suggestion.warnings.length > 0 && (
                <div className="agent-warnings">
                  <strong>Dikkat</strong>
                  <ul>{suggestion.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>
                </div>
              )}
              <div className="agent-actions">
                <button type="button" className="btn" onClick={() => setSuggestion(null)}>İptal</button>
                <button type="button" className="btn btn--primary" disabled={effectiveChanges.length === 0} onClick={apply}>
                  Değişiklikleri Uygula
                </button>
              </div>
            </section>
          )}
        </div>
      </aside>
    </>
  );
}
