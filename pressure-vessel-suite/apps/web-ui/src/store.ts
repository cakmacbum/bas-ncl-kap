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
      },
    ],
    heads: [
      makeHead("HEAD-L"),
      makeHead("HEAD-R"),
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
  };
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

  setProject: (updater: (p: VesselProject) => VesselProject) => void;
  patchConditions: (patch: Partial<VesselProject["design_conditions"]>) => void;
  setProjectId: (id: string, hash: string) => void;
  setCalc: (c: CalcPayload | null) => void;
  setStep: (s: number) => void;
  setDirty: (d: boolean) => void;
  toggleTheme: () => void;
  addNozzle: () => void;
  removeNozzle: (index: number) => void;
  updateNozzle: (index: number, patch: Partial<VesselProject["nozzles"][0]>) => void;
}

export const useStore = create<AppState>((set) => ({
  project: defaultProject(),
  projectId: null,
  inputHash: null,
  calc: null,
  step: 0,
  theme: "dark",
  dirty: true,

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
  setCalc: (c) => set({ calc: c }),
  setStep: (step) => set({ step }),
  setDirty: (dirty) => set({ dirty }),
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
}));
