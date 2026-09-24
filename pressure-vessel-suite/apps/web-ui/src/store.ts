import { create } from "zustand";
import type { VesselProject, CalcPayload } from "./types";

export function defaultProject(): VesselProject {
  return {
    project_number: "PRJ-001",
    project_name: "Yeni Basınçlı Kap",
    customer: "",
    revision: "A",
    calculation_code: "ASME VIII-1",
    code_edition: "2025",
    unit_system: "SI",
    orientation: "horizontal",
    diameter_relation: "linked",
    pressure_relief: {
      enabled: false,
      protected_mawp_mpa: null,
      accumulation_limit_percent: 10,
      devices: [],
    },
    design_conditions: {
      operating_pressure: 1.0,
      design_pressure: 1.2,
      maximum_allowable_pressure_ps: 1.5,
      operating_temperature: 120,
      design_temperature: 150,
      minimum_design_temperature: -10,
      external_pressure: 0,
      vacuum_condition: false,
      hydrotest_temperature: 20,
      corrosion_allowance_internal: 2.0,
      corrosion_allowance_external: 0,
      fluid_density_kg_m3: 0,
      impact_test_temperature_C: null,
    },
    materials: [
      {
        material_id: "MAT-01",
        standard_pack: "ASME II-D 2025",
        material_designation: "SA-516 Gr.70",
        product_form: "plate",
        thickness_min: 0,
        thickness_max: 1000,
        temperature: 150,
        allowable_stress: 138,
        yield_strength: 260,
        tensile_strength: 485,
        source_reference: "ASME II-D Table 1A",
        source_revision: "2025",
        density: 7850,
        // K4: UCS-66 eğri grubu tahmin edilmez — kullanıcı malzeme
        // belgesinden girer. Boşken MDMT kontrolü bloke olur.
        ucs66_curve_group: null,
      },
    ],
    supports: [],
    welds: [
      {
        joint_id: "WJ-01",
        joint_type: "longitudinal",
        weld_category: "A",
        joint_efficiency: 1.0,
        nde_method: "RT-1",
        nde_extent: "100%",
        full_penetration: true,
        wps_number: null,
        pqr_number: null,
        welder_qualification: null,
        pwht_required: false,
      },
    ],
    shell_sections: [
      {
        section_id: "SHELL-01",
        inside_diameter: 1000,
        outside_diameter: null,
        tangent_length: 2000,
        nominal_thickness: 12,
        material_id: "MAT-01",
        weld_joint_id: "WJ-01",
        internal_corrosion_allowance: 2.0,
        external_corrosion_allowance: 0,
        mill_tolerance: 12.5,
        forming_thinning: 0,
        ug28_strain_factor_a: null,
        ug28_allowable_stress_b: null,
      },
    ],
    heads: [
      makeHead("HEAD-L"),
      makeHead("HEAD-R"),
    ],
    cones: [],
    junctions: [],
    component_sequence: [
      { component_type: "head", component_id: "HEAD-L" },
      { component_type: "shell", component_id: "SHELL-01" },
      { component_type: "head", component_id: "HEAD-R" },
    ],
    nozzles: [
      {
        tag: "N1",
        nozzle_type: "flanged",
        host_component_id: "SHELL-01",
        axial_position: 800,
        circumferential_angle: 90,
        inclination_angle: 0,
        head_position_diameter: null,
        outside_diameter: 168.3,
        inside_diameter: 154.1,
        neck_thickness: 7.1,
        inside_projection: 0,
        outside_projection: 150,
        size_designation: null,
        material_id: "MAT-01",
        corrosion_allowance: 2.0,
        reinforcement_pad: true,
        reinforcement_pad_thickness: 10,
        reinforcement_pad_od: 300,
      },
    ],
  };
}

function makeHead(id: string) {
  return {
    head_id: id,
    type: "elliptical" as const,
    inside_diameter: 1000,
    crown_radius: null,
    knuckle_radius: null,
    straight_flange_length: 40,
    nominal_thickness: 12,
    material_id: "MAT-01",
    weld_joint_id: "WJ-01",
    internal_corrosion_allowance: 2.0,
    mill_tolerance: 12.5,
    forming_thinning: 0,
    flat_attachment_factor: null,
    ug28_strain_factor_a: null,
    ug28_allowable_stress_b: null,
  };
}

/** Eski tek silindirli JSON'larını güncel zincir sözleşmesine taşır. */
export function normalizeProject(project: VesselProject): VesselProject {
  const cones = project.cones ?? [];
  const sequence = project.component_sequence ?? [];
  if (sequence.length > 0) return { ...project, cones };
  if (project.shell_sections.length === 1 && project.heads.length === 2 && cones.length === 0) {
    return {
      ...project,
      cones,
      component_sequence: [
        { component_type: "head", component_id: project.heads[0].head_id },
        { component_type: "shell", component_id: project.shell_sections[0].section_id },
        { component_type: "head", component_id: project.heads[1].head_id },
      ],
    };
  }
  return { ...project, cones, component_sequence: sequence };
}

type Theme = "dark" | "light";

interface AppState {
  project: VesselProject;
  projectId: string | null;
  inputHash: string | null;
  calc: CalcPayload | null;
  step: number;
  theme: Theme;
  dirty: boolean;
  activeShellId: string;

  setProject: (updater: (p: VesselProject) => VesselProject) => void;
  patchConditions: (patch: Partial<VesselProject["design_conditions"]>) => void;
  setProjectId: (id: string, hash: string) => void;
  loadProject: (id: string, project: VesselProject) => void;
  setCalc: (c: CalcPayload | null) => void;
  setStep: (s: number) => void;
  setDirty: (d: boolean) => void;
  setActiveShellId: (id: string) => void;
  toggleTheme: () => void;
  addNozzle: () => void;
  removeNozzle: (index: number) => void;
  updateNozzle: (index: number, patch: Partial<VesselProject["nozzles"][0]>) => void;
  addSupport: () => void;
  removeSupport: (index: number) => void;
  updateSupport: (index: number, patch: Partial<VesselProject["supports"][0]>) => void;
  updateShell: (sectionId: string, patch: Partial<VesselProject["shell_sections"][0]>) => void;
  updateHead: (headId: string, patch: Partial<VesselProject["heads"][0]>) => void;
  updateCone: (coneId: string, patch: Partial<VesselProject["cones"][0]>) => void;
  updateMaterial: (materialId: string, patch: Partial<VesselProject["materials"][0]>) => void;
  updateWeld: (jointId: string, patch: Partial<VesselProject["welds"][0]>) => void;
  addMaterial: () => void;
  removeMaterial: (materialId: string) => void;
  addWeld: () => void;
  removeWeld: (jointId: string) => void;
  duplicateComponent: (ref: VesselProject["component_sequence"][0]) => void;
  removeComponent: (ref: VesselProject["component_sequence"][0]) => void;
  moveComponent: (index: number, direction: -1 | 1) => void;
}

export const useStore = create<AppState>((set) => ({
  project: defaultProject(),
  projectId: null,
  inputHash: null,
  calc: null,
  step: 0,
  theme: "light",
  dirty: true,
  activeShellId: "SHELL-01",

  setProject: (updater) =>
    set((s) => ({ project: updater(s.project), dirty: true, calc: null })),
  patchConditions: (patch) =>
    set((s) => ({
      project: {
        ...s.project,
        design_conditions: { ...s.project.design_conditions, ...patch },
      },
      dirty: true,
      calc: null,
    })),
  setProjectId: (id, hash) => set({ projectId: id, inputHash: hash, dirty: false }),
  loadProject: (id, project) => set({
    project: normalizeProject(project), projectId: id, inputHash: null,
    calc: null, dirty: false, step: 0,
    activeShellId: project.shell_sections[0]?.section_id ?? "",
  }),
  setCalc: (c) => set({ calc: c }),
  setStep: (step) => set({ step }),
  setDirty: (dirty) => set({ dirty }),
  setActiveShellId: (activeShellId) => set({ activeShellId }),
  toggleTheme: () =>
    set((s) => {
      const theme = s.theme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", theme);
      return { theme };
    }),
  addNozzle: () =>
    set((s) => {
      const n = s.project.nozzles.length + 1;
      const shell = s.project.shell_sections[0];
      const newNozzle = {
        tag: `N${n}`,
        nozzle_type: "flanged",
        host_component_id: "SHELL-01",
        axial_position: Math.round((shell.tangent_length ?? 2000) / 2),
        circumferential_angle: 90,
        inclination_angle: 0,
        head_position_diameter: null,
        outside_diameter: 168.3,
        inside_diameter: 154.1,
        neck_thickness: 7.1,
        inside_projection: 0,
        outside_projection: 150,
        size_designation: null,
        material_id: "MAT-01",
        corrosion_allowance: 2.0,
        reinforcement_pad: false,
        reinforcement_pad_thickness: null,
        reinforcement_pad_od: null,
      };
      return {
        project: { ...s.project, nozzles: [...s.project.nozzles, newNozzle] },
        dirty: true,
        calc: null,
      };
    }),
  removeNozzle: (index) =>
    set((s) => {
      const nozzles = s.project.nozzles.filter((_, i) => i !== index);
      // Etiketleri yeniden numaralandır
      const reTagged = nozzles.map((nz, i) => ({ ...nz, tag: `N${i + 1}` }));
      return {
        project: { ...s.project, nozzles: reTagged },
        dirty: true,
        calc: null,
      };
    }),
  updateNozzle: (index, patch) =>
    set((s) => {
      const nozzles = s.project.nozzles.map((nz, i) =>
        i === index ? { ...nz, ...patch } : nz
      );
      return {
        project: { ...s.project, nozzles },
        dirty: true,
        calc: null,
      };
    }),
  addSupport: () =>
    set((s) => {
      const n = s.project.supports.length + 1;
      const shell = s.project.shell_sections[0];
      const newSupport = {
        support_id: `SUP-${n}`,
        type: "saddle" as const,
        location_mm: Math.round((shell.tangent_length ?? 2000) * 0.2),
        width_mm: 200,
        height_mm: 500,
        diameter_mm: null,
        thickness_mm: null,
        material_id: "MAT-01",
        contact_angle_deg: 120,
        leg_count: null,
        leg_diameter_mm: null,
        leg_thickness_mm: null,
        support_radius_mm: null,
        base_plate_area_mm2: null,
        anchor_bolt_count: null,
        anchor_bolt_diameter_mm: null,
        anchor_tension_allowable_N: null,
        anchor_shear_allowable_N: null,
        lateral_load_N: 0,
        overturning_moment_Nmm: 0,
      };
      return {
        project: { ...s.project, supports: [...s.project.supports, newSupport] },
        dirty: true,
        calc: null,
      };
    }),
  removeSupport: (index) =>
    set((s) => {
      const supports = s.project.supports.filter((_, i) => i !== index);
      return {
        project: { ...s.project, supports },
        dirty: true,
        calc: null,
      };
    }),
  updateSupport: (index, patch) =>
    set((s) => {
      const supports = s.project.supports.map((sup, i) =>
        i === index ? { ...sup, ...patch } : sup
      );
      return {
        project: { ...s.project, supports },
        dirty: true,
        calc: null,
      };
    }),
  updateShell: (sectionId, patch) =>
    set((s) => ({
      project: {
        ...s.project,
        shell_sections: s.project.shell_sections.map((section) =>
          section.section_id === sectionId ? { ...section, ...patch } : section
        ),
      },
      dirty: true,
      calc: null,
    })),
  updateHead: (headId, patch) =>
    set((s) => ({
      project: {
        ...s.project,
        heads: s.project.heads.map((head) =>
          head.head_id === headId ? { ...head, ...patch } : head
        ),
      },
      dirty: true,
      calc: null,
    })),
  updateCone: (coneId, patch) =>
    set((s) => ({
      project: {
        ...s.project,
        cones: s.project.cones.map((cone) =>
          cone.cone_id === coneId ? { ...cone, ...patch } : cone
        ),
      },
      dirty: true,
      calc: null,
    })),
  updateMaterial: (materialId, patch) =>
    set((s) => ({
      project: {
        ...s.project,
        materials: s.project.materials.map((material) =>
          material.material_id === materialId ? { ...material, ...patch } : material
        ),
      },
      dirty: true,
      calc: null,
    })),
  updateWeld: (jointId, patch) =>
    set((s) => ({
      project: {
        ...s.project,
        welds: s.project.welds.map((weld) =>
          weld.joint_id === jointId ? { ...weld, ...patch } : weld
        ),
      },
      dirty: true,
      calc: null,
    })),
  addMaterial: () => set((s) => {
    const n = s.project.materials.length + 1;
    const source = s.project.materials[0];
    const material = { ...source, material_id: `MAT-${String(n).padStart(2, "0")}`, material_designation: `${source.material_designation} (kopya)` };
    return { project: { ...s.project, materials: [...s.project.materials, material] }, dirty: true, calc: null };
  }),
  removeMaterial: (materialId) => set((s) => {
    if (s.project.materials.length <= 1) return s;
    const remaining = s.project.materials.filter((m) => m.material_id !== materialId);
    const fallback = remaining[0].material_id;
    const replace = (id: string) => id === materialId ? fallback : id;
    return { project: { ...s.project,
      materials: remaining,
      shell_sections: s.project.shell_sections.map((x) => ({ ...x, material_id: replace(x.material_id) })),
      heads: s.project.heads.map((x) => ({ ...x, material_id: replace(x.material_id) })),
      cones: s.project.cones.map((x) => ({ ...x, material_id: replace(x.material_id) })),
      nozzles: s.project.nozzles.map((x) => ({ ...x, material_id: replace(x.material_id) })),
      supports: s.project.supports.map((x) => ({ ...x, material_id: replace(x.material_id) })),
    }, dirty: true, calc: null };
  }),
  addWeld: () => set((s) => {
    const n = s.project.welds.length + 1;
    const source = s.project.welds[0];
    const weld = { ...source, joint_id: `WJ-${String(n).padStart(2, "0")}`, joint_type: "circumferential" };
    return { project: { ...s.project, welds: [...s.project.welds, weld] }, dirty: true, calc: null };
  }),
  removeWeld: (jointId) => set((s) => {
    if (s.project.welds.length <= 1) return s;
    const remaining = s.project.welds.filter((w) => w.joint_id !== jointId);
    const fallback = remaining[0].joint_id;
    const replace = (id: string | null) => id === jointId ? fallback : id;
    return { project: { ...s.project,
      welds: remaining,
      shell_sections: s.project.shell_sections.map((x) => ({ ...x, weld_joint_id: replace(x.weld_joint_id) })),
      heads: s.project.heads.map((x) => ({ ...x, weld_joint_id: replace(x.weld_joint_id) })),
      cones: s.project.cones.map((x) => ({ ...x, weld_joint_id: replace(x.weld_joint_id) })),
    }, dirty: true, calc: null };
  }),
  duplicateComponent: (ref) => set((s) => {
    const suffix = Date.now().toString(36).slice(-4).toUpperCase();
    const nextId = `${ref.component_type === "shell" ? "SHELL" : ref.component_type === "head" ? "HEAD" : "CONE"}-${suffix}`;
    let project = s.project;
    if (ref.component_type === "shell") {
      const item = s.project.shell_sections.find((x) => x.section_id === ref.component_id);
      if (item) project = { ...project, shell_sections: [...project.shell_sections, { ...item, section_id: nextId }] };
    } else if (ref.component_type === "head") {
      const item = s.project.heads.find((x) => x.head_id === ref.component_id);
      if (item) project = { ...project, heads: [...project.heads, { ...item, head_id: nextId }] };
    } else {
      const item = s.project.cones.find((x) => x.cone_id === ref.component_id);
      if (item) project = { ...project, cones: [...project.cones, { ...item, cone_id: nextId }] };
    }
    const index = s.project.component_sequence.findIndex((x) => x.component_id === ref.component_id);
    const sequence = [...s.project.component_sequence];
    sequence.splice(index + 1, 0, { component_type: ref.component_type, component_id: nextId });
    return { project: { ...project, component_sequence: sequence }, dirty: true, calc: null };
  }),
  removeComponent: (ref) => set((s) => {
    const sequence = s.project.component_sequence.filter((x) => x.component_id !== ref.component_id);
    const project = ref.component_type === "shell"
      ? { ...s.project, shell_sections: s.project.shell_sections.filter((x) => x.section_id !== ref.component_id) }
      : ref.component_type === "head"
        ? { ...s.project, heads: s.project.heads.filter((x) => x.head_id !== ref.component_id) }
        : { ...s.project, cones: s.project.cones.filter((x) => x.cone_id !== ref.component_id) };
    return { project: { ...project, component_sequence: sequence, nozzles: project.nozzles.filter((x) => x.host_component_id !== ref.component_id) }, dirty: true, calc: null };
  }),
  moveComponent: (index, direction) => set((s) => {
    const next = index + direction;
    if (next < 0 || next >= s.project.component_sequence.length) return s;
    const sequence = [...s.project.component_sequence];
    [sequence[index], sequence[next]] = [sequence[next], sequence[index]];
    return { project: { ...s.project, component_sequence: sequence }, dirty: true, calc: null };
  }),
}));
