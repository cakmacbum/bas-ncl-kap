import { beforeEach, describe, expect, it } from "vitest";
import { defaultProject, normalizeProject, useStore } from "../store";
import { geometryIssues } from "../geometryValidation";
import { computeIssues } from "../geometrySteps/IssuesPanel";
import { chainIssues, componentFrames } from "../vesselModel";
import { VESSEL_PRESETS } from "../vesselPresets";

const st = () => useStore.getState();
const preset = (id: string) => VESSEL_PRESETS.find((p) => p.id === id)!;

const EXPECTED: Record<string, { name: string; orientation: string; id: number; tt: number; p: number; t: number; ca: number; mat: string }> = {
  "horizontal-air-receiver": { name: "Yatay Hava Tankı", orientation: "horizontal", id: 1200, tt: 3000, p: 1.0, t: 65, ca: 1.5, mat: "SA-516 Gr.70" },
  "vacuum-process-tank": { name: "Vakumlu Proses Tankı", orientation: "vertical", id: 1600, tt: 2400, p: 0.35, t: 100, ca: 0, mat: "SA-240 304" },
  "vertical-separator": { name: "Dikey Seperatör", orientation: "vertical", id: 1000, tt: 3000, p: 1.6, t: 120, ca: 3, mat: "SA-516 Gr.70" },
};

beforeEach(() => {
  useStore.setState({
    project: defaultProject(), projectId: null, inputHash: null, calc: null,
    dirty: false, selection: null, geoSubStep: 0, activeShellId: "SHELL-01",
  });
});

describe("başlangıç şablonları", () => {
  it("üç şablon, benzersiz kimlik, dolu ad/açıklama/not", () => {
    expect(VESSEL_PRESETS.map((p) => p.id).sort()).toEqual(Object.keys(EXPECTED).sort());
    for (const p of VESSEL_PRESETS) {
      expect(p.name).toBe(EXPECTED[p.id].name);
      expect(p.description.length).toBeGreaterThan(0);
      expect(p.notes.length).toBeGreaterThan(0);
      expect(p.notes.some((n) => /lisanslı kaynağınızdan/.test(n))).toBe(true);
    }
  });

  for (const p of VESSEL_PRESETS) {
    describe(p.name, () => {
      const e = EXPECTED[p.id];

      it("normalizeProject idempotent", () => {
        const built = p.build();
        expect(normalizeProject(built)).toEqual(built);
      });

      it("hesap standardı, yönelim ve tasarım koşulları", () => {
        const b = p.build();
        expect(b.calculation_code).toBe("ASME VIII-1");
        expect(b.orientation).toBe(e.orientation);
        expect(b.design_conditions.design_pressure).toBe(e.p);
        expect(b.design_conditions.design_temperature).toBe(e.t);
        expect(b.design_conditions.operating_pressure).toBeLessThanOrEqual(e.p);
        expect(b.design_conditions.corrosion_allowance_internal).toBe(e.ca);
      });

      it("zincir: bombe-gövde-bombe, tüm kimlikler mevcut", () => {
        const b = p.build();
        expect(b.component_sequence.map((c) => c.component_type)).toEqual(["head", "shell", "head"]);
        for (const ref of b.component_sequence) {
          const known = ref.component_type === "head"
            ? b.heads.some((h) => h.head_id === ref.component_id)
            : b.shell_sections.some((s) => s.section_id === ref.component_id);
          expect(known).toBe(true);
        }
        expect(b.cones).toEqual([]);
        expect(b.supports).toEqual([]);
      });

      it("gövde ve bombe çapı / kalınlığı / korozyon payı tutarlı", () => {
        const b = p.build();
        const shell = b.shell_sections[0];
        expect(b.shell_sections).toHaveLength(1);
        expect(b.heads).toHaveLength(2);
        expect(shell.inside_diameter).toBe(e.id);
        expect(shell.tangent_length).toBe(e.tt);
        expect(shell.internal_corrosion_allowance).toBe(e.ca);
        for (const h of b.heads) {
          expect(h.type).toBe("elliptical");
          expect(h.inside_diameter).toBe(shell.inside_diameter);
          expect(h.nominal_thickness).toBe(shell.nominal_thickness);
          expect(h.internal_corrosion_allowance).toBe(e.ca);
        }
      });

      it("malzeme / kaynak / nozul başvuruları geçerli", () => {
        const b = p.build();
        const mats = new Set(b.materials.map((m) => m.material_id));
        const welds = new Set(b.welds.map((w) => w.joint_id));
        const hosts = new Set([...b.shell_sections.map((s) => s.section_id), ...b.heads.map((h) => h.head_id)]);
        for (const c of [...b.shell_sections, ...b.heads]) {
          expect(mats.has(c.material_id)).toBe(true);
          expect(welds.has(c.weld_joint_id!)).toBe(true);
        }
        for (const n of b.nozzles) {
          expect(hosts.has(n.host_component_id)).toBe(true);
          expect(mats.has(n.material_id)).toBe(true);
          expect(n.corrosion_allowance).toBe(e.ca);
          expect(n.axial_position).toBeGreaterThan(0);
          expect(n.axial_position).toBeLessThan(e.tt);
        }
      });

      it("gömülü S / akma / çekme / UCS-66 / UG-28 değeri yok", () => {
        const b = p.build();
        expect(b.materials).toHaveLength(1);
        const m = b.materials[0];
        expect(m.material_designation).toBe(e.mat);
        expect(m.allowable_stress).toBe(0);
        expect(m.allowable_stress_test_temp).toBeNull();
        expect(m.yield_strength).toBe(0);
        expect(m.tensile_strength).toBe(0);
        expect(m.ucs66_curve_group).toBeNull();
        expect(m.elastic_modulus ?? null).toBeNull();
        expect(m.source_reference).not.toMatch(/Table/i);
        expect(m.density).toBeGreaterThan(0);
        for (const c of [...b.shell_sections, ...b.heads]) {
          expect(c.ug28_strain_factor_a).toBeNull();
          expect(c.ug28_allowable_stress_b).toBeNull();
        }
        // defaultProject'in 138/260/485 varsayılanları hiçbir yere sızmamalı.
        const d = defaultProject().materials[0];
        const json = JSON.stringify(b.materials);
        for (const v of [d.allowable_stress, d.yield_strength, d.tensile_strength]) {
          expect(v).toBeGreaterThan(0);
          expect(json).not.toContain(`:${v}`);
        }
      });

      it("istemci geometri doğrulamasından hatasız geçer", () => {
        const b = p.build();
        expect(geometryIssues(b)).toEqual([]);
        expect(chainIssues(b, componentFrames(b))).toEqual([]);
        expect(computeIssues(b).filter((i) => i.blocking)).toEqual([]);
      });

      it("build() her çağrıda bağımsız nesne döndürür", () => {
        const a = p.build();
        const snapshot = JSON.stringify(a);
        a.shell_sections[0].inside_diameter = 1;
        a.heads[0].nominal_thickness = 1;
        a.materials[0].allowable_stress = 999;
        a.design_conditions.design_pressure = 99;
        a.nozzles.length = 0;
        a.component_sequence.pop();
        const fresh = p.build();
        expect(JSON.stringify(fresh)).toBe(snapshot);
        expect(fresh).not.toBe(a);
        expect(fresh.materials[0]).not.toBe(p.build().materials[0]);
      });

      it("applyPreset: kaydedilmemiş yeni proje olarak yüklenir", () => {
        useStore.setState({
          projectId: "eski-id", inputHash: "eski-hash", dirty: false, geoSubStep: 3,
          calc: {} as never, selection: { kind: "nozzle", id: "N1" } as never, activeShellId: "SHELL-99",
        });
        const built = p.build();
        st().applyPreset(built);
        expect(st().project).toEqual(built);
        expect(st().projectId).toBeNull();
        expect(st().inputHash).toBeNull();
        expect(st().calc).toBeNull();
        expect(st().dirty).toBe(true);
        expect(st().selection).toBeNull();
        expect(st().geoSubStep).toBe(0);
        expect(st().activeShellId).toBe(built.shell_sections[0].section_id);
      });
    });
  }

  it("vakum şablonu: vacuum_condition açık, dış basınç > 0; diğerlerinde kapalı", () => {
    const vac = preset("vacuum-process-tank").build().design_conditions;
    expect(vac.vacuum_condition).toBe(true);
    expect(vac.external_pressure).toBeGreaterThan(0);
    expect(preset("vacuum-process-tank").notes.some((n) => /UG-28/.test(n))).toBe(true);
    for (const id of ["horizontal-air-receiver", "vertical-separator"]) {
      const dc = preset(id).build().design_conditions;
      expect(dc.vacuum_condition).toBe(false);
      expect(dc.external_pressure).toBe(0);
    }
  });

  it("notlar: devralınan varsayılan seçimler defaultProject ile tutarlı ve görünür", () => {
    const d = defaultProject();
    const tr = (n: number) => String(n).replace(".", ",");
    const sh = d.shell_sections[0];
    const hd = d.heads[0];
    const nz = d.nozzles[0];
    for (const p of VESSEL_PRESETS) {
      const text = p.notes.join("\n");
      const b = p.build();
      // Notta yazan sayılar gerçekten projeye uygulanan değerlerle aynı olmalı.
      expect(b.shell_sections[0].mill_tolerance).toBe(sh.mill_tolerance);
      expect(b.shell_sections[0].forming_thinning).toBe(sh.forming_thinning);
      for (const h of b.heads) {
        expect(h.mill_tolerance).toBe(hd.mill_tolerance);
        expect(h.forming_thinning).toBe(hd.forming_thinning);
        expect(h.straight_flange_length).toBe(hd.straight_flange_length);
      }
      expect(text).toContain(`%${tr(sh.mill_tolerance)}`);
      expect(text).toMatch(/şekillendirme incelmesi 0\b/);
      expect(sh.forming_thinning).toBe(0);
      expect(text).toContain(`${tr(hd.straight_flange_length)} mm`);
      expect(b.design_conditions.maximum_allowable_pressure_ps).toBe(b.design_conditions.design_pressure);
      expect(text).toMatch(/Ps\) tasarım basıncına eşitlendi/);
      const n = b.nozzles[0];
      expect(n.outside_diameter).toBe(nz.outside_diameter);
      expect(n.inside_diameter).toBe(nz.inside_diameter);
      expect(n.neck_thickness).toBe(nz.neck_thickness);
      expect(n.outside_projection).toBe(nz.outside_projection);
      expect(n.inside_projection).toBe(nz.inside_projection);
      expect(n.corrosion_allowance).toBe(b.design_conditions.corrosion_allowance_internal);
      expect(text).toContain(`dış çap ${tr(nz.outside_diameter)} mm`);
      expect(text).toContain(`iç çap ${tr(nz.inside_diameter)} mm`);
      expect(text).toContain(`boyun kalınlığı ${tr(nz.neck_thickness)} mm`);
      expect(text).toContain(`dış çıkıntı ${tr(nz.outside_projection)} mm`);
      expect(nz.inside_projection).toBe(0);
      expect(text).toMatch(/korozyon payı kap korozyon payına eşitlendi/);
    }
  });

  it("notlar: malzeme değerleri girilmeden kaydet/hesap/3B/rapor/STEP yok uyarısı", () => {
    for (const p of VESSEL_PRESETS) {
      const text = p.notes.join("\n");
      expect(text).toMatch(/kaydedilemez ve hesaplanamaz/);
      expect(text).toMatch(/3B model, rapor ve STEP/);
    }
  });

  it("vakum notu: tam vakum (1 atm) varsayımı ve E gerekmediği", () => {
    const vac = preset("vacuum-process-tank");
    const text = vac.notes.join("\n");
    expect(vac.build().design_conditions.external_pressure).toBe(0.1013);
    expect(text).toMatch(/0,1013 MPa tam vakum \(1 atm\)/);
    expect(text).toMatch(/Elastisite modülü \(E\) boş/);
    expect(vac.build().materials[0].elastic_modulus ?? null).toBeNull();
  });

  it("applyPreset eksik zincirli projeyi normalize eder", () => {
    const built = preset("vertical-separator").build();
    st().applyPreset({ ...built, component_sequence: [] });
    expect(st().project.component_sequence).toEqual(built.component_sequence);
  });
});
