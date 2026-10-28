import { describe, expect, it } from "vitest";
import { defaultProject } from "../store";
import type { Cone, Nozzle, ShellSection, VesselProject } from "../types";
import {
  chainIssues, componentFrames, headDepth, headDomeHeight, nozzlePlacement, supportZ, tangentDatum,
  vesselProfileChain, type NozzlePlacement,
} from "../vesselModel";

function shell(id: string, di: number, L: number): ShellSection {
  return { ...defaultProject().shell_sections[0], section_id: id, inside_diameter: di, tangent_length: L };
}

function cone(id: string, large: number, small: number, length: number): Cone {
  return {
    cone_id: id, large_diameter: large, small_diameter: small, half_apex_angle: 0, length,
    nominal_thickness: 12, material_id: "MAT-01", weld_joint_id: "WJ-01",
    internal_corrosion_allowance: 2, mill_tolerance: 12.5,
  };
}

/** HEAD-L, a…, HEAD-R zinciri. */
function chain(items: (ShellSection | Cone)[], leftDi: number, rightDi: number): VesselProject {
  const p = defaultProject();
  return {
    ...p,
    shell_sections: items.filter((x): x is ShellSection => "section_id" in x),
    cones: items.filter((x): x is Cone => "cone_id" in x),
    heads: [{ ...p.heads[0], inside_diameter: leftDi }, { ...p.heads[1], inside_diameter: rightDi }],
    component_sequence: [
      { component_type: "head", component_id: "HEAD-L" },
      ...items.map((x) => "section_id" in x
        ? { component_type: "shell" as const, component_id: x.section_id }
        : { component_type: "cone" as const, component_id: x.cone_id }),
      { component_type: "head", component_id: "HEAD-R" },
    ],
  };
}

function nozzle(host: string, s: number, theta = 90, alpha = 0): Nozzle {
  return { ...defaultProject().nozzles[0], host_component_id: host, axial_position: s, circumferential_angle: theta, inclination_angle: alpha };
}

function placed(r: ReturnType<typeof nozzlePlacement>): NozzlePlacement {
  if ("error" in r) throw new Error(r.error);
  return r;
}

const reducing = () => chain([shell("SHELL-01", 1000, 2000), cone("CONE-01", 1000, 600, 500), shell("SHELL-02", 600, 1000)], 1000, 600);

describe("componentFrames", () => {
  it("daralan zincir: SHELL-01(Ø1000,L2000) → CONE-01(1000→600) → SHELL-02(Ø600)", () => {
    const p = reducing();
    const f = componentFrames(p);
    const hL = p.heads[0];
    expect(f.map((x) => x.id)).toEqual(["HEAD-L", "SHELL-01", "CONE-01", "SHELL-02", "HEAD-R"]);
    expect(f[2].zStart).toBeCloseTo(headDepth(hL.inside_diameter, hL.type, hL.straight_flange_length) + 2000, 9);
    expect(f[3].rInStart).toBe(300);
    expect(f[2].rInStart).toBe(500);
    expect(f[2].rInEnd).toBe(300);
    expect(f[2].cone?.largeAtStart).toBe(true);
    for (let i = 1; i < f.length; i++) expect(f[i].zStart).toBe(f[i - 1].zEnd);
    expect(chainIssues(p, f)).toEqual([]);
  });

  it("genişleyen koni doğru yönde çizilir", () => {
    const p = chain([shell("SHELL-01", 600, 1000), cone("CONE-01", 1000, 600, 500), shell("SHELL-02", 1000, 2000)], 600, 1000);
    const f = componentFrames(p);
    expect(f[2].rInStart).toBe(300);
    expect(f[2].rInEnd).toBe(500);
    expect(f[2].cone?.largeAtStart).toBe(false);
    expect(chainIssues(p, f)).toEqual([]);
    // Profil konide küçük uçtan büyük uca gider
    const prof = vesselProfileChain(p.shell_sections, p.heads, p.cones, p.component_sequence);
    const atConeStart = prof.find((pt) => Math.abs(pt.z - f[2].zStart) < 1e-9 && pt.r < 305);
    expect(atConeStart).toBeDefined();
  });

  it("bombe çerçevesi: sol kutup z=0, ekvator ve teğet datumları", () => {
    const p = defaultProject();
    const f = componentFrames(p);
    const h = headDomeHeight(1000, "elliptical");
    expect(f[0].zStart).toBe(0);
    expect(f[0].head).toMatchObject({ side: "left", domeHeight: h, sf: 40, equatorZ: h });
    expect(f[2].head?.equatorZ).toBe(f[2].zStart + 40);
    const d = tangentDatum(f);
    expect(d.left).toBe(h + 40);
    expect(d.right).toBe(h + 40 + 2000);
    expect(supportZ({ type: "saddle", location_mm: 400 }, f)).toBe(h + 40 + 400);
    expect(supportZ({ type: "skirt", location_mm: 400 }, f)).toBe(h + 40);
  });

  it("headDomeHeight: crown_depth ve torisferik R,r önceliği", () => {
    expect(headDomeHeight(1000, "elliptical", { crown_depth: 123, crown_radius: null, knuckle_radius: null })).toBe(123);
    const R = 1000, r = 60;
    const expected = R - Math.sqrt((R - r) ** 2 - (500 - r) ** 2);
    expect(headDomeHeight(1000, "torispherical", { crown_radius: R, knuckle_radius: r })).toBeCloseTo(expected, 9);
    expect(headDomeHeight(1000, "torispherical")).toBeCloseTo(1000 / 6, 9);
  });

  it("chainIssues: çap uyuşmazlığı, eksik referans, ara bombe", () => {
    const p = chain([shell("SHELL-01", 1000, 2000), shell("SHELL-02", 800, 1000)], 1000, 800);
    p.component_sequence.splice(2, 0, { component_type: "cone", component_id: "YOK" });
    const codes = chainIssues(p, componentFrames(p)).map((i) => `${i.code}:${i.id}`);
    expect(codes).toContain("DIAMETER_MISMATCH:SHELL-02");
    expect(codes).toContain("MISSING_REF:YOK");
  });
});

describe("nozzlePlacement", () => {
  it("gövdede eski formülle birebir (regresyon)", () => {
    const p = reducing();
    const f = componentFrames(p);
    const theta = (37 * Math.PI) / 180;
    const alpha = (15 * Math.PI) / 180;
    const R = 500;
    const pl = placed(nozzlePlacement(p, nozzle("SHELL-01", 800, 37, 15), f));
    // Eski: position=[R cosθ, R sinθ, s] (gövde başı=0), axis=[cosθ cosα, sinθ cosα, sinα]
    const old = {
      position: [R * Math.cos(theta), R * Math.sin(theta), 800],
      axis: [Math.cos(theta) * Math.cos(alpha), Math.sin(theta) * Math.cos(alpha), Math.sin(alpha)],
    };
    expect(pl.position[0]).toBeCloseTo(old.position[0], 9);
    expect(pl.position[1]).toBeCloseTo(old.position[1], 9);
    expect(pl.position[2] - f[1].zStart).toBeCloseTo(old.position[2], 9);
    pl.axis.forEach((v, i) => expect(v).toBeCloseTo(old.axis[i], 9));
    expect(pl.hostKind).toBe("shell");
    expect(pl.rAtAnchor).toBe(500);
  });

  it("daralan konide normal.z > 0 (k<0)", () => {
    const p = reducing();
    const f = componentFrames(p);
    const pl = placed(nozzlePlacement(p, nozzle("CONE-01", 250, 0), f));
    expect(pl.hostKind).toBe("cone");
    expect(pl.normal[2]).toBeGreaterThan(0);
    expect(pl.rAtAnchor).toBeCloseTo(400, 9);
    expect(pl.position[2]).toBeCloseTo(f[2].zStart + 250, 9);
  });

  it("ikinci gövdedeki nozul kendi host'una göre yerleşir", () => {
    const p = reducing();
    const f = componentFrames(p);
    const pl = placed(nozzlePlacement(p, nozzle("SHELL-02", 100, 0), f));
    expect(pl.position[0]).toBeCloseTo(300, 9);
    expect(pl.position[2]).toBeCloseTo(f[3].zStart + 100, 9);
  });

  it("hatalar: host yok, host dışı (kırpma yok)", () => {
    const p = reducing();
    const f = componentFrames(p);
    expect(nozzlePlacement(p, nozzle("SHELL-99", 10), f)).toEqual({ error: "HOST_NOT_FOUND" });
    expect(nozzlePlacement(p, nozzle("SHELL-01", 2500), f)).toEqual({ error: "OUT_OF_HOST" });
    expect(nozzlePlacement(p, { ...nozzle("HEAD-R", 0), head_position_diameter: 2000 }, f)).toEqual({ error: "OUT_OF_HOST" });
  });

  it("bombede: sağ kutup +Z, sol kutup −Z", () => {
    const p = defaultProject();
    const f = componentFrames(p);
    const right = placed(nozzlePlacement(p, nozzle("HEAD-R", 0), f));
    expect(right.position[2]).toBeCloseTo(f[2].zEnd, 9);
    expect(right.axis[2]).toBeCloseTo(1, 9);
    const left = placed(nozzlePlacement(p, nozzle("HEAD-L", 0), f));
    expect(left.position[2]).toBeCloseTo(0, 9);
    expect(left.axis[2]).toBeCloseTo(-1, 9);
  });
});
