import { describe, expect, it } from "vitest";
import { allowablePosition, scaleColor, scaleTicks, stressColor } from "../stress/colorScale";

describe("colorScale", () => {
  it("uç renkler: 0 mavi, 1 kırmızı", () => {
    const lo = scaleColor(0), hi = scaleColor(1);
    expect(lo[2]).toBeGreaterThan(lo[0]);
    expect(hi[0]).toBeGreaterThan(hi[2]);
  });
  it("aralık dışı ve NaN güvenli", () => {
    expect(scaleColor(-5)).toEqual(scaleColor(0));
    expect(scaleColor(9)).toEqual(scaleColor(1));
    expect(scaleColor(NaN)).toEqual(scaleColor(0));
  });
  it("stressColor max<=0 iken çökmez", () => {
    expect(stressColor(10, 0)).toEqual(scaleColor(0));
    expect(stressColor(50, 100)).toEqual(scaleColor(0.5));
  });
  it("ticks ve allowable konumu", () => {
    expect(scaleTicks(100, 4)).toEqual([0, 25, 50, 75, 100]);
    expect(allowablePosition(60, 120)).toBe(0.5);
    expect(allowablePosition(null, 120)).toBeNull();
    expect(allowablePosition(200, 120)).toBeNull();
  });
});
