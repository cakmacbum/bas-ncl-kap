// Kap Geometrisi sayfası yerleşim yardımcıları (saf fonksiyonlar; test edilebilir).

export type PanelTab = "geometry" | "inputs";
export const PANEL_TAB_KEY = "geometry-panel-tab";

/** Sol parametre paneli genişliği (px); ≤768px'te tek sütun → null. */
export function panelWidthFor(viewportWidth: number): number | null {
  if (viewportWidth <= 768) return null;
  if (viewportWidth < 1000) return 360;
  if (viewportWidth < 1200) return 420;
  return 480;
}

/** Mobilde sticky önizleme yüksekliği: min(36vh, 300px). */
export function mobilePreviewHeight(viewportHeight: number): number {
  return Math.min(viewportHeight * 0.36, 300);
}

type StorageLike = Pick<Storage, "getItem" | "setItem">;

export function readPanelTab(storage?: StorageLike): PanelTab {
  try {
    const s = storage ?? localStorage;
    return s.getItem(PANEL_TAB_KEY) === "inputs" ? "inputs" : "geometry";
  } catch {
    return "geometry";
  }
}

export function writePanelTab(tab: PanelTab, storage?: StorageLike): void {
  try {
    (storage ?? localStorage).setItem(PANEL_TAB_KEY, tab);
  } catch { /* depolama yok */ }
}

export function warningBadgeText(count: number): string | null {
  return count > 0 ? `⚠ ${count} uyarı` : null;
}

export type ExportFormat = "step" | "stl" | "drawing-svg" | "drawing-dxf";
export const EXPORT_OPTIONS: { format: ExportFormat; label: string }[] = [
  { format: "step", label: "STEP (.step)" },
  { format: "stl", label: "STL (.stl)" },
  { format: "drawing-svg", label: "İmalat resmi (SVG)" },
  { format: "drawing-dxf", label: "İmalat resmi (DXF)" },
];
