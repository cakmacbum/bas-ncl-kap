import { beforeEach, describe, expect, it } from "vitest";
import { getUpn, listUpn } from "../data/catalogs";
import { computeIssues } from "../geometrySteps/IssuesPanel";
import { addLegSupport, makeVertical, matchingUpn, upnPatch } from "../geometrySteps/legActions";
import { defaultProject, useStore } from "../store";
import { componentFrames, tangentDatum } from "../vesselModel";

const st = () => useStore.getState();
const codes = (re: RegExp) => computeIssues(st().project).filter((i) => re.test(i.id));

beforeEach(() => {
  useStore.setState({ project: defaultProject(), selection: null, geoSubStep: 0 });
});

/** Dikey kap + 1 ayak; yama ile ölçüler ayarlanır. */
function legSetup(patch: Record<string, unknown> = {}) {
  makeVertical();
  const id = addLegSupport(4);
  const idx = st().project.supports.findIndex((s) => s.support_id === id);
  st().updateSupport(idx, patch);
  return { id, idx };
}

describe("UPN katalog", () => {
  it("12 satır, UPN 80–300; getUpn", () => {
    expect(listUpn().map((r) => r.name)).toEqual(
      ["UPN 80", "UPN 100", "UPN 120", "UPN 140", "UPN 160", "UPN 180", "UPN 200", "UPN 220", "UPN 240", "UPN 260", "UPN 280", "UPN 300"]);
    expect(getUpn("UPN 120")).toMatchObject({ h: 120, b: 55, tw: 7, tf: 9 });
    expect(getUpn("upn200")).toMatchObject({ h: 200 });
    expect(getUpn("UPN 999")).toBeNull();
  });
});

describe("ayak editörü eylemleri", () => {
  it("UPN seçimi h, b, tw, tf alanlarını doldurur", () => {
    const { idx } = legSetup();
    st().updateSupport(idx, upnPatch("UPN 200")!);
    const s = st().project.supports[idx];
    expect([s.leg_profile_height_mm, s.leg_profile_width_mm, s.leg_web_thickness_mm, s.leg_flange_thickness_mm])
      .toEqual([200, 75, 8.5, 11.5]);
    expect(s.leg_section_type).toBe("channel");
    expect(matchingUpn(s, listUpn())).toBe("UPN 200");
    st().updateSupport(idx, { leg_web_thickness_mm: 9 });
    expect(matchingUpn(st().project.supports[idx], listUpn())).toBe("");
  });

  it("yeni ayak: channel + UPN 120 + 1500 mm", () => {
    const { idx } = legSetup();
    const s = st().project.supports[idx];
    expect(s).toMatchObject({ type: "leg", leg_count: 4, leg_section_type: "channel", leg_profile_height_mm: 120, height_mm: 1500 });
  });

  it("«Kabı dikey yap» orientation'ı değiştirir", () => {
    expect(st().project.orientation).toBe("horizontal");
    makeVertical();
    expect(st().project.orientation).toBe("vertical");
  });
});

describe("ayak issue kuralları", () => {
  it("LEG_TOO_SHORT: kısa ayak hata, yeterli boy temiz", () => {
    const { frames, left } = (() => { const f = componentFrames(st().project); return { frames: f, left: tangentDatum(f).left }; })();
    const bottom = frames[0].zStart - frames[0].thickness;
    const { idx } = legSetup({ location_mm: 1000, height_mm: 50 });
    const bad = codes(/^leg-short-/);
    expect(bad).toHaveLength(1);
    expect(bad[0]).toMatchObject({ level: "error", blocking: true });
    const need = Math.round(left + 1000 - bottom);
    expect(bad[0].message).toContain(`en az ${need} mm`);
    st().updateSupport(idx, { height_mm: need });
    expect(codes(/^leg-short-/)).toHaveLength(0);
  });

  it("LEG_TOO_SHORT: yatay kapta çalışmaz", () => {
    const id = st().addSupport("leg");
    const idx = st().project.supports.findIndex((s) => s.support_id === id);
    st().updateSupport(idx, { location_mm: 1000, height_mm: 50 });
    expect(codes(/^leg-short-/)).toHaveLength(0);
  });

  it("LEG_PAD_OFF_SHELL: ped gövdenin dışına taşarsa uyarı, içindeyse temiz", () => {
    const { idx } = legSetup({ height_mm: 5000 });
    const { left, right } = tangentDatum(componentFrames(st().project));
    const mid = Math.round((right - left) / 2);
    st().updateSupport(idx, { location_mm: mid, leg_pad_length_mm: 400, leg_pad_top_extension_mm: 50 });
    expect(codes(/^leg-pad-/)).toHaveLength(0);
    // alt uç teğet hattının altına iner
    st().updateSupport(idx, { location_mm: 200 });
    const off = codes(/^leg-pad-/);
    expect(off).toHaveLength(1);
    expect(off[0]).toMatchObject({ level: "warn", blocking: false });
    // üst taşma ile üst uç aşılır
    st().updateSupport(idx, { location_mm: right - left, leg_pad_top_extension_mm: 50 });
    expect(codes(/^leg-pad-/)).toHaveLength(1);
  });

  it("LEG_PROFILE_INVALID: tw ≥ h/2 veya tf ≥ b veya h ≤ 0 hata; geçerli UPN temiz", () => {
    const { idx } = legSetup();
    expect(codes(/^leg-profile-/)).toHaveLength(0);
    st().updateSupport(idx, { leg_web_thickness_mm: 60 }); // h=120 → h/2=60
    expect(codes(/^leg-profile-/)).toHaveLength(1);
    st().updateSupport(idx, { ...upnPatch("UPN 120")!, leg_flange_thickness_mm: 55 }); // tf ≥ b=55
    expect(codes(/^leg-profile-/)).toHaveLength(1);
    st().updateSupport(idx, { ...upnPatch("UPN 120")!, leg_profile_height_mm: 0 });
    const bad = codes(/^leg-profile-/);
    expect(bad).toHaveLength(1);
    expect(bad[0]).toMatchObject({ level: "error", blocking: true });
    st().updateSupport(idx, { ...upnPatch("UPN 120")!, leg_section_type: "pipe", leg_web_thickness_mm: 500 });
    expect(codes(/^leg-profile-/)).toHaveLength(0); // yalnız channel
  });
});
