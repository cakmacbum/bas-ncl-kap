import { describe, expect, it } from "vitest";
import { stepIssueCounts, type WizardIssue } from "../geometrySteps/IssuesPanel";

const issue = (
  step: WizardIssue["step"], level: WizardIssue["level"], id = `${step}-${level}`,
): WizardIssue => ({ id, level, step, message: "test", blocking: level === "error" });

describe("stepIssueCounts", () => {
  it("boş listede 0..4 anahtarlarının hepsi sıfır olarak döner", () => {
    expect(stepIssueCounts([])).toEqual({
      0: { error: 0, warn: 0 },
      1: { error: 0, warn: 0 },
      2: { error: 0, warn: 0 },
      3: { error: 0, warn: 0 },
      4: { error: 0, warn: 0 },
    });
  });

  it("anahtarlar her zaman 0..4 sırasıyla bulunur", () => {
    expect(Object.keys(stepIssueCounts([issue(2, "warn")])).map(Number)).toEqual([0, 1, 2, 3, 4]);
  });

  it("hata ve uyarıları kendi adımına sayar", () => {
    const counts = stepIssueCounts([
      issue(0, "error", "a"),
      issue(1, "error", "b"),
      issue(1, "error", "c"),
      issue(1, "warn", "d"),
      issue(4, "warn", "e"),
    ]);
    expect(counts[0]).toEqual({ error: 1, warn: 0 });
    expect(counts[1]).toEqual({ error: 2, warn: 1 });
    expect(counts[2]).toEqual({ error: 0, warn: 0 });
    expect(counts[4]).toEqual({ error: 0, warn: 1 });
  });

  it("bilgi seviyesi sayaca girmez", () => {
    const counts = stepIssueCounts([issue(4, "info", "sup-none"), issue(4, "info", "sup-one-saddle")]);
    expect(counts[4]).toEqual({ error: 0, warn: 0 });
  });
});
