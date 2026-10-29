import { describe, expect, it } from "vitest";
import {
  EXPORT_OPTIONS, PANEL_TAB_KEY, mobilePreviewHeight, panelWidthFor, readPanelTab, warningBadgeText, writePanelTab,
} from "../geometryLayout";

const memory = (init: Record<string, string> = {}) => {
  const m = { ...init };
  return { m, getItem: (k: string) => m[k] ?? null, setItem: (k: string, v: string) => { m[k] = v; } };
};

describe("geometri sayfası yerleşimi", () => {
  it("sol panel genişliği kırılmalara göre", () => {
    expect(panelWidthFor(1440)).toBe(480);
    expect(panelWidthFor(1200)).toBe(480);
    expect(panelWidthFor(1199)).toBe(420);
    expect(panelWidthFor(1000)).toBe(420);
    expect(panelWidthFor(999)).toBe(360);
    expect(panelWidthFor(769)).toBe(360);
    expect(panelWidthFor(768)).toBeNull();
  });
  it("mobil önizleme yüksekliği min(36vh, 300)", () => {
    expect(mobilePreviewHeight(600)).toBeCloseTo(216);
    expect(mobilePreviewHeight(1200)).toBe(300);
  });
  it("sekme seçimi hatırlanır; bozuk/yok depolamada varsayılan", () => {
    const st = memory();
    expect(readPanelTab(st)).toBe("geometry");
    writePanelTab("inputs", st);
    expect(st.m[PANEL_TAB_KEY]).toBe("inputs");
    expect(readPanelTab(st)).toBe("inputs");
    expect(readPanelTab(memory({ [PANEL_TAB_KEY]: "x" }))).toBe("geometry");
    const broken = { getItem: () => { throw new Error("no"); }, setItem: () => { throw new Error("no"); } };
    expect(readPanelTab(broken)).toBe("geometry");
    expect(() => writePanelTab("inputs", broken)).not.toThrow();
  });
  it("uyarı rozeti ve dışa aktarma seçenekleri", () => {
    expect(warningBadgeText(0)).toBeNull();
    expect(warningBadgeText(3)).toBe("⚠ 3 uyarı");
    expect(EXPORT_OPTIONS.map((o) => o.format)).toEqual(["step", "stl"]);
  });
});
