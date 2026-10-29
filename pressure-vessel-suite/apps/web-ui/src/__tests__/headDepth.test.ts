import { describe, expect, it } from "vitest";
import { defaultProject, useStore } from "../store";
import { computeIssues } from "../geometrySteps/IssuesPanel";
import { crownDepthPatch, typeChangePatch } from "../geometrySteps/headDepth";

const withDepth = (ratio: number) => {
  const p = defaultProject();
  const h0 = { ...p.heads[0], type: "elliptical" as const };
  const h = { ...h0, crown_depth: h0.inside_diameter / (2 * ratio) };
  return { ...p, heads: [h, ...p.heads.slice(1)] };
};
const depthIssues = (p: ReturnType<typeof defaultProject>) =>
  computeIssues(p).filter((i) => i.message.includes("HEAD_DEPTH_RANGE"));

describe("eliptik kubbe derinliği alanı", () => {
  it("crown_depth yazar, 0 → null", () => {
    expect(crownDepthPatch(250)).toEqual({ crown_depth: 250 });
    expect(crownDepthPatch(0)).toEqual({ crown_depth: null });
    const id = useStore.getState().project.heads[0].head_id;
    useStore.getState().updateHead(id, crownDepthPatch(300));
    expect(useStore.getState().project.heads[0].crown_depth).toBe(300);
    useStore.getState().updateHead(id, crownDepthPatch(0));
    expect(useStore.getState().project.heads[0].crown_depth).toBeNull();
  });

  it("eliptik dışına geçişte crown_depth temizlenir", () => {
    const id = useStore.getState().project.heads[0].head_id;
    useStore.getState().updateHead(id, { type: "elliptical", crown_depth: 300 });
    useStore.getState().updateHead(id, typeChangePatch("torispherical"));
    const h = useStore.getState().project.heads[0];
    expect(h.type).toBe("torispherical");
    expect(h.crown_depth).toBeNull();
    expect(typeChangePatch("elliptical")).toEqual({ type: "elliptical" });
  });
});

describe("HEAD_DEPTH_RANGE issue sınırları", () => {
  it("D/2h = 0,9 hata", () => {
    const i = depthIssues(withDepth(0.9));
    expect(i).toHaveLength(1);
    expect(i[0]).toMatchObject({ level: "error", blocking: true, step: 1 });
  });
  it("D/2h = 1 ve 3 geçerli", () => {
    expect(depthIssues(withDepth(1))).toHaveLength(0);
    expect(depthIssues(withDepth(3))).toHaveLength(0);
  });
  it("D/2h = 3,1 hata", () => {
    expect(depthIssues(withDepth(3.1))).toHaveLength(1);
  });
  it("crown_depth boşsa issue yok", () => {
    const p = withDepth(2);
    p.heads[0].crown_depth = null;
    expect(depthIssues(p)).toHaveLength(0);
  });
});
