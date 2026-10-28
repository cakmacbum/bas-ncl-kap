import { beforeEach, describe, expect, it } from "vitest";
import { catalogs } from "../data/catalogAdapter";
import { defaultProject, nextId, nextTag, syncTerminalHeads, useStore } from "../store";
import { chainIssues, componentFrames } from "../vesselModel";

const st = () => useStore.getState();
const ids = () => st().project.component_sequence.map((c) => c.component_id);

beforeEach(() => {
  useStore.setState({ project: defaultProject(), selection: null, geoSubStep: 0 });
});

describe("kimlik üreticileri", () => {
  it("nextId / nextTag", () => {
    expect(nextId("SHELL", ["SHELL-01", "SHELL-07"])).toBe("SHELL-08");
    expect(nextId("HEAD", ["HEAD-L", "HEAD-R"])).toBe("HEAD-01");
    expect(nextTag("N", ["N1", "N3", "C1"])).toBe("N4");
    expect(nextTag("C", ["N1"])).toBe("C1");
  });
});

describe("zincir aksiyonları", () => {
  it("appendShell sağa/sola: komşu kopyası, uçtaki iç çap", () => {
    expect(st().appendShell("right")).toBe("SHELL-02");
    expect(st().appendShell("left", { tangent_length: 500 })).toBe("SHELL-03");
    expect(ids()).toEqual(["HEAD-L", "SHELL-03", "SHELL-01", "SHELL-02", "HEAD-R"]);
    const s3 = st().project.shell_sections.find((s) => s.section_id === "SHELL-03")!;
    expect(s3.inside_diameter).toBe(1000);
    expect(s3.tangent_length).toBe(500);
  });

  it("appendCone sağa: daralan koni, yarı tepe açısı, bombe senkronu", () => {
    const id = st().appendCone("right", { endDiameter: 600, length: 500 });
    expect(id).toBe("CONE-01");
    const c = st().project.cones[0];
    expect(c.large_diameter).toBe(1000);
    expect(c.small_diameter).toBe(600);
    expect(c.half_apex_angle).toBeCloseTo((Math.atan(200 / 500) * 180) / Math.PI, 3);
    expect(c.nominal_thickness).toBe(12);
    expect(ids()).toEqual(["HEAD-L", "SHELL-01", "CONE-01", "HEAD-R"]);
    expect(st().project.heads[1].inside_diameter).toBe(600);
    expect(st().project.heads[0].inside_diameter).toBe(1000);
  });

  it("appendCone: eşit çap → null, mutasyon yok", () => {
    const before = st().project;
    expect(st().appendCone("right", { endDiameter: 1000.5, length: 300 })).toBeNull();
    expect(st().project).toBe(before);
  });

  it("appendCone sola: genişleyen yön + sol bombe senkronu, zincir tutarlı", () => {
    st().appendCone("left", { endDiameter: 600, length: 400 });
    const p = st().project;
    const f = componentFrames(p);
    expect(f[1].kind).toBe("cone");
    expect(f[1].rInStart).toBe(300);
    expect(f[1].rInEnd).toBe(500);
    expect(p.heads[0].inside_diameter).toBe(600);
    expect(chainIssues(p, f)).toEqual([]);
  });

  it("appendStepped: tek set'te koni + yeni gövde", () => {
    let calls = 0;
    const unsub = useStore.subscribe(() => { calls++; });
    const r = st().appendStepped("right", { endDiameter: 1400, coneLength: 300, shellLength: 1200 });
    unsub();
    expect(calls).toBe(1);
    expect(r).toEqual(["CONE-01", "SHELL-02"]);
    expect(ids()).toEqual(["HEAD-L", "SHELL-01", "CONE-01", "SHELL-02", "HEAD-R"]);
    const p = st().project;
    const s2 = p.shell_sections.find((s) => s.section_id === "SHELL-02")!;
    expect(s2.inside_diameter).toBe(1400);
    expect(s2.tangent_length).toBe(1200);
    expect(p.heads[1].inside_diameter).toBe(1400);
    expect(chainIssues(p, componentFrames(p))).toEqual([]);
  });

  it("syncTerminalHeads: uç bombeleri komşu çapına eşitler; independent'ta store senkron yapmaz", () => {
    const p = defaultProject();
    p.shell_sections[0].inside_diameter = 900;
    const synced = syncTerminalHeads(p);
    expect(synced.heads.map((h) => h.inside_diameter)).toEqual([900, 900]);
    expect(syncTerminalHeads(synced)).toBe(synced);

    useStore.setState({ project: { ...defaultProject(), diameter_relation: "independent" } });
    st().updateShell("SHELL-01", { inside_diameter: 900 });
    expect(st().project.heads.map((h) => h.inside_diameter)).toEqual([1000, 1000]);
  });

  it("updateCone: çap/boy değişince yarı tepe açısı yeniden", () => {
    st().appendCone("right", { endDiameter: 600, length: 500 });
    st().updateCone("CONE-01", { length: 200 });
    expect(st().project.cones[0].half_apex_angle).toBeCloseTo(45, 6);
  });

  it("removeComponent: uç bombe ve tek gövde silinmez; host nozulları + seçim temizlenir", () => {
    const before = st().project;
    st().removeComponent({ component_type: "head", component_id: "HEAD-R" });
    st().removeComponent({ component_type: "shell", component_id: "SHELL-01" });
    expect(st().project).toBe(before);

    st().appendShell("right");
    st().setSelection({ kind: "nozzle", id: "N1" });
    st().removeComponent({ component_type: "shell", component_id: "SHELL-01" });
    expect(ids()).toEqual(["HEAD-L", "SHELL-02", "HEAD-R"]);
    expect(st().project.nozzles).toEqual([]);
    expect(st().selection).toBeNull();
  });

  it("moveComponent yalnız iç elemanlar; duplicateComponent nextId", () => {
    st().appendShell("right");
    st().moveComponent(0, 1);
    st().moveComponent(2, 1);
    expect(ids()).toEqual(["HEAD-L", "SHELL-01", "SHELL-02", "HEAD-R"]);
    st().moveComponent(1, 1);
    expect(ids()).toEqual(["HEAD-L", "SHELL-02", "SHELL-01", "HEAD-R"]);
    st().duplicateComponent({ component_type: "shell", component_id: "SHELL-01" });
    expect(ids()).toEqual(["HEAD-L", "SHELL-02", "SHELL-01", "SHELL-03", "HEAD-R"]);
  });
});

describe("nozul ve destek aksiyonları", () => {
  it("addPipeNozzle: katalog OD/et, etiket, ped", () => {
    const tag = st().addPipeNozzle({
      host_component_id: "SHELL-01", nozzle_type: "pad_reinforced", nps: "4", schedule: "SCH40",
      rating_class: "CL150", axial_position: 500, circumferential_angle: 0,
    });
    expect(tag).toBe("N2");
    const nz = st().project.nozzles.find((n) => n.tag === tag)!;
    const pipe = catalogs.pipe("4")!;
    expect(nz.outside_diameter).toBe(pipe.od);
    expect(nz.neck_thickness).toBe(pipe.walls.SCH40);
    expect(nz.inside_diameter).toBeCloseTo(pipe.od - 2 * pipe.walls.SCH40!, 6);
    expect(nz.size_designation).toBe('4" SCH40 CL150');
    expect(nz.reinforcement_pad).toBe(true);
    expect(nz.reinforcement_pad_od).toBeCloseTo(2 * pipe.od, 6);
    expect(nz.reinforcement_pad_thickness).toBe(12);
    expect(nz.rating_class).toBe("CL150");

    const m = st().addPipeNozzle({
      host_component_id: "HEAD-R", nozzle_type: "manway", nps: "20", schedule: "STD",
      rating_class: "CL150", axial_position: 0, circumferential_angle: 0,
    });
    expect(m).toBe("M1");
    expect(st().project.nozzles.find((n) => n.tag === "M1")!.outside_projection).toBe(200);
  });

  it("addCoupling: outside_projection = katalog boyu; weldolet → null", () => {
    const tag = st().addCoupling({
      host_component_id: "SHELL-01", nozzle_type: "coupling", nps: "1", rating_class: "3000#",
      coupling_form: "full", axial_position: 300, circumferential_angle: 0,
    });
    expect(tag).toBe("C1");
    const nz = st().project.nozzles.find((n) => n.tag === "C1")!;
    const row = catalogs.coupling("1", "3000#", "full")!;
    expect(nz.outside_projection).toBe(row.length);
    expect(nz.outside_diameter).toBe(row.body_od);
    expect(nz.inside_projection).toBe(0);
    expect(nz.neck_thickness).toBeCloseTo((nz.outside_diameter - nz.inside_diameter) / 2, 6);
    expect(nz.coupling_form).toBe("full");
    expect(nz.rating_class).toBe("3000#");

    expect(st().addCoupling({
      host_component_id: "SHELL-01", nozzle_type: "coupling", nps: "1", rating_class: "3000#",
      coupling_form: "weldolet", axial_position: 300, circumferential_angle: 0,
    })).toBeNull();
  });

  it("removeNozzle yeniden numaralandırmaz", () => {
    st().addNozzle();
    st().addNozzle();
    st().removeNozzle(0);
    expect(st().project.nozzles.map((n) => n.tag)).toEqual(["N2", "N3"]);
  });

  it("addSupport(type, host) ve eski onClick çağrısı", () => {
    expect(st().addSupport("leg")).toBe("SUP-01");
    expect(st().addSupport({ type: "click" } as object)).toBe("SUP-02");
    const [leg, saddle] = st().project.supports;
    expect(leg.type).toBe("leg");
    expect(leg.leg_count).toBe(4);
    expect(saddle.type).toBe("saddle");
    expect(saddle.host_component_id).toBe("SHELL-01");
  });

  it("loadProject alt adımı ve seçimi sıfırlar", () => {
    st().setGeoSubStep(3);
    st().setSelection({ kind: "shell", id: "SHELL-01" });
    st().loadProject("x", defaultProject());
    expect(st().geoSubStep).toBe(0);
    expect(st().selection).toBeNull();
  });
});
