import { create } from "zustand";
import type {
  VesselProject, CalcPayload, Flange, ComponentReference, Cone, Nozzle, ShellSection, Support,
} from "./types";
import type { CouplingForm, CouplingRating, FlangeClass, Selection } from "./geometryContract";
import { componentFrames, tangentDatum } from "./vesselModel";
import { catalogs, contractSchedule, couplingNozzleDims } from "./data/catalogAdapter";

export const PIPE_NOZZLE_TYPES = ["flanged", "slip_on", "pad_reinforced", "manway"] as const;
export const COUPLING_TYPES = ["coupling", "socket_welded"] as const;

export type ChainSide = "left" | "right";
export type GeoSubStep = 0 | 1 | 2 | 3 | 4;

/** `prefix-pad2(max+1)` — HEAD-L/HEAD-R gibi sayısız kimlikler dikkate alınmaz. */
export function nextId(prefix: string, ids: string[]): string {
  const re = new RegExp(`^${prefix}-(\\d+)$`);
  const max = ids.reduce((m, id) => {
    const hit = re.exec(id);
    return hit ? Math.max(m, Number(hit[1])) : m;
  }, 0);
  return `${prefix}-${String(max + 1).padStart(2, "0")}`;
}

/** Nozul etiketi: boru N, manway M, manşon C. Etiket = kimlik; yeniden numaralandırılmaz. */
export function nextTag(prefix: "N" | "M" | "C", tags: string[]): string {
  const re = new RegExp(`^${prefix}(\\d+)$`);
  const max = tags.reduce((m, t) => {
    const hit = re.exec(t);
    return hit ? Math.max(m, Number(hit[1])) : m;
  }, 0);
  return `${prefix}${max + 1}`;
}

/** Uç bombelerin iç çapını komşu zincir ucuna eşitler (diameter_relation="linked" için). */
export function syncTerminalHeads(p: VesselProject): VesselProject {
  const f = componentFrames(p);
  const n = f.length;
  if (n < 2) return p;
  const targets = new Map<string, number>();
  if (f[0].head?.side === "left") targets.set(f[0].id, 2 * f[1].rInStart);
  if (f[n - 1].head?.side === "right") targets.set(f[n - 1].id, 2 * f[n - 2].rInEnd);
  let changed = false;
  const heads = p.heads.map((h) => {
    const d = targets.get(h.head_id);
    if (d == null || !(d > 0) || Math.abs(d - h.inside_diameter) < 1e-9) return h;
    changed = true;
    return { ...h, inside_diameter: d };
  });
  return changed ? { ...p, heads } : p;
}

function isLinked(p: VesselProject): boolean {
  return (p.diameter_relation ?? "linked") === "linked";
}

/** Zincir mutasyonu sonrası ortak adım: linked ise bombe senkronu. */
function chainCommit(p: VesselProject) {
  return { project: isLinked(p) ? syncTerminalHeads(p) : p, dirty: true, calc: null };
}

function halfApexAngle(large: number, small: number, length: number): number {
  return +((Math.atan((large - small) / 2 / Math.max(length, 1e-9)) * 180) / Math.PI).toFixed(4);
}

type ChainItem = ShellSection | Cone | VesselProject["heads"][0];

function findChainItem(p: VesselProject, ref: ComponentReference | undefined): ChainItem | undefined {
  if (!ref) return undefined;
  if (ref.component_type === "shell") return p.shell_sections.find((x) => x.section_id === ref.component_id);
  if (ref.component_type === "cone") return p.cones.find((x) => x.cone_id === ref.component_id);
  return p.heads.find((x) => x.head_id === ref.component_id);
}

/** Ekleme ucundaki bilgiler: sequence indeksi, komşu eleman, uçtaki zincir iç çapı. */
function chainEnd(p: VesselProject, side: ChainSide) {
  const seq = p.component_sequence ?? [];
  const frames = componentFrames(p);
  const n = frames.length;
  if (seq.length < 2 || n < 2) return null;
  const insertAt = side === "right" ? seq.length - 1 : 1;
  const neighborRef = side === "right" ? seq[seq.length - 2] : seq[1];
  const neighbor = findChainItem(p, neighborRef);
  if (!neighbor) return null;
  const endD = 2 * (side === "right" ? frames[n - 2].rInEnd : frames[1].rInStart);
  return { seq, insertAt, neighborRef, neighbor, endD };
}

/** Komşudan kalınlık/malzeme/kaynak/CA devralan ortak alanlar. */
function inherited(n: ChainItem) {
  return {
    nominal_thickness: n.nominal_thickness,
    material_id: n.material_id,
    weld_joint_id: n.weld_joint_id,
    internal_corrosion_allowance: n.internal_corrosion_allowance,
    mill_tolerance: n.mill_tolerance,
  };
}

function buildShell(p: VesselProject, neighbor: ChainItem, diameter: number, params?: Partial<ShellSection>): ShellSection {
  const base = "section_id" in neighbor ? neighbor : (p.shell_sections[0] ?? defaultProject().shell_sections[0]);
  return {
    ...base,
    ...inherited(neighbor),
    section_id: nextId("SHELL", p.shell_sections.map((s) => s.section_id)),
    inside_diameter: diameter,
    outside_diameter: null,
    ...params,
  };
}

function buildCone(
  p: VesselProject, neighbor: ChainItem, startD: number, endD: number, length: number, thickness?: number,
): Cone {
  const large = Math.max(startD, endD);
  const small = Math.min(startD, endD);
  return {
    cone_id: nextId("CONE", p.cones.map((c) => c.cone_id)),
    large_diameter: large,
    small_diameter: small,
    half_apex_angle: halfApexAngle(large, small, length),
    length,
    ...inherited(neighbor),
    ...(thickness != null ? { nominal_thickness: thickness } : {}),
  };
}

function insertRefs(seq: ComponentReference[], at: number, refs: ComponentReference[]): ComponentReference[] {
  const next = [...seq];
  next.splice(at, 0, ...refs);
  return next;
}

/** Sol uca koni eklenirken linked ise sol bombe yeni uç çapına alınır (koni yönü komşudan çıkar). */
function withLeftHeadDiameter(p: VesselProject, side: ChainSide, d: number): VesselProject {
  if (side !== "left" || !isLinked(p)) return p;
  const leftId = p.component_sequence[0]?.component_id;
  return { ...p, heads: p.heads.map((h) => (h.head_id === leftId ? { ...h, inside_diameter: d } : h)) };
}

function hostOf(p: VesselProject, id: string): ChainItem | undefined {
  return p.shell_sections.find((x) => x.section_id === id)
    ?? p.cones.find((x) => x.cone_id === id)
    ?? p.heads.find((x) => x.head_id === id);
}

function nozzleBase(p: VesselProject, host: string) {
  const h = hostOf(p, host);
  return {
    host_component_id: host,
    inclination_angle: 0,
    inside_projection: 0,
    material_id: h?.material_id ?? p.materials[0]?.material_id ?? "MAT-01",
    corrosion_allowance: h?.internal_corrosion_allowance ?? p.design_conditions.corrosion_allowance_internal,
    hostThickness: h?.nominal_thickness ?? 10,
  };
}

const npsText = (nps: string) => `${nps}"`;

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
      liquid_level_mm: null,
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
        allowable_stress_test_temp: null,
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
    flanges: [],
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
    en_flat_end_factor_c: null,
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
  geoSubStep: GeoSubStep;
  selection: Selection | null;

  setGeoSubStep: (n: GeoSubStep) => void;
  setSelection: (sel: Selection | null) => void;
  appendShell: (side: ChainSide, params?: Partial<ShellSection>) => string | null;
  appendCone: (side: ChainSide, params: { endDiameter: number; length: number; nominal_thickness?: number }) => string | null;
  appendStepped: (side: ChainSide, params: { endDiameter: number; coneLength: number; shellLength: number }) => [string, string] | null;
  addPipeNozzle: (p: {
    host_component_id: string; nozzle_type: (typeof PIPE_NOZZLE_TYPES)[number];
    nps: string; schedule: string; rating_class: FlangeClass; axial_position: number; circumferential_angle: number;
    head_position_diameter?: number | null;
  }) => string;
  addCoupling: (p: {
    host_component_id: string; nozzle_type: (typeof COUPLING_TYPES)[number];
    nps: string; rating_class: CouplingRating; coupling_form: CouplingForm; axial_position: number;
    circumferential_angle: number; head_position_diameter?: number | null;
  }) => string | null;

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
  addFlange: () => void;
  removeFlange: (index: number) => void;
  updateFlange: (index: number, patch: Partial<Flange>) => void;
  /** Varsayılan "saddle". Eski `onClick={addSupport}` çağrısı (event argümanı) güvenle yok sayılır. */
  // `| object`: geçiş — pages.tsx `onClick={addSupport}` (D05 kaldırınca daraltılabilir).
  addSupport: (type?: Support["type"] | object, host?: string) => string;
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

export const useStore = create<AppState>((set, get) => ({
  project: defaultProject(),
  projectId: null,
  inputHash: null,
  calc: null,
  step: 0,
  theme: "light",
  dirty: true,
  activeShellId: "SHELL-01",
  geoSubStep: 0,
  selection: null,

  setGeoSubStep: (geoSubStep) => set({ geoSubStep }),
  setSelection: (selection) => set({ selection }),

  appendShell: (side, params) => {
    const p = get().project;
    const end = chainEnd(p, side);
    if (!end) return null;
    const shell = buildShell(p, end.neighbor, end.endD, params);
    set(chainCommit({
      ...p,
      shell_sections: [...p.shell_sections, shell],
      component_sequence: insertRefs(end.seq, end.insertAt, [{ component_type: "shell", component_id: shell.section_id }]),
    }));
    return shell.section_id;
  },

  appendCone: (side, { endDiameter, length, nominal_thickness }) => {
    const p = get().project;
    const end = chainEnd(p, side);
    if (!end || !(length > 0) || !(endDiameter > 0) || Math.abs(end.endD - endDiameter) < 1) return null;
    const cone = buildCone(p, end.neighbor, end.endD, endDiameter, length, nominal_thickness);
    const next = withLeftHeadDiameter(p, side, endDiameter);
    set(chainCommit({
      ...next,
      cones: [...next.cones, cone],
      component_sequence: insertRefs(end.seq, end.insertAt, [{ component_type: "cone", component_id: cone.cone_id }]),
    }));
    return cone.cone_id;
  },

  appendStepped: (side, { endDiameter, coneLength, shellLength }) => {
    const p = get().project;
    const end = chainEnd(p, side);
    if (!end || !(coneLength > 0) || !(shellLength > 0) || !(endDiameter > 0)
      || Math.abs(end.endD - endDiameter) < 1) return null;
    const cone = buildCone(p, end.neighbor, end.endD, endDiameter, coneLength);
    const shell = buildShell(p, end.neighbor, endDiameter, { tangent_length: shellLength });
    const coneRef: ComponentReference = { component_type: "cone", component_id: cone.cone_id };
    const shellRef: ComponentReference = { component_type: "shell", component_id: shell.section_id };
    // Sağda: …, koni, yeni gövde, HEAD-R. Solda: HEAD-L, yeni gövde, koni, …
    const refs = side === "right" ? [coneRef, shellRef] : [shellRef, coneRef];
    set(chainCommit({
      ...p,
      cones: [...p.cones, cone],
      shell_sections: [...p.shell_sections, shell],
      component_sequence: insertRefs(end.seq, end.insertAt, refs),
    }));
    return [cone.cone_id, shell.section_id];
  },

  addPipeNozzle: (a) => {
    const p = get().project;
    const pipe = catalogs.pipe(a.nps);
    const schedule = contractSchedule(a.schedule);
    const wall = pipe?.walls[schedule];
    if (!pipe || wall == null) return ""; // katalogda yok — mutasyon yok
    const base = nozzleBase(p, a.host_component_id);
    const isManway = a.nozzle_type === "manway";
    const tag = nextTag(isManway ? "M" : "N", p.nozzles.map((n) => n.tag));
    const od = pipe.od;
    const pad = a.nozzle_type === "pad_reinforced";
    const nozzle: Nozzle = {
      tag,
      nozzle_type: a.nozzle_type,
      host_component_id: base.host_component_id,
      axial_position: a.axial_position,
      circumferential_angle: a.circumferential_angle,
      inclination_angle: base.inclination_angle,
      head_position_diameter: a.head_position_diameter ?? null,
      outside_diameter: od,
      inside_diameter: +(od - 2 * wall).toFixed(2),
      neck_thickness: wall,
      inside_projection: base.inside_projection,
      outside_projection: isManway ? 200 : 150,
      size_designation: `${npsText(pipe.nps)} ${schedule} ${a.rating_class}`,
      material_id: base.material_id,
      corrosion_allowance: base.corrosion_allowance,
      reinforcement_pad: pad,
      reinforcement_pad_thickness: pad ? base.hostThickness : null,
      reinforcement_pad_od: pad ? +(2 * od).toFixed(2) : null,
      rating_class: a.rating_class,
      coupling_form: null,
    };
    set({ project: { ...p, nozzles: [...p.nozzles, nozzle] }, dirty: true, calc: null });
    return tag;
  },

  addCoupling: (a) => {
    const p = get().project;
    const end = a.nozzle_type === "socket_welded" ? "socket" : "threaded";
    const dims = couplingNozzleDims(a.nps, a.rating_class, a.coupling_form, end);
    if (!dims) return null;
    const base = nozzleBase(p, a.host_component_id);
    const tag = nextTag("C", p.nozzles.map((n) => n.tag));
    const nozzle: Nozzle = {
      tag,
      nozzle_type: a.nozzle_type,
      host_component_id: base.host_component_id,
      axial_position: a.axial_position,
      circumferential_angle: a.circumferential_angle,
      inclination_angle: base.inclination_angle,
      head_position_diameter: a.head_position_diameter ?? null,
      outside_diameter: dims.od,
      inside_diameter: dims.id,
      neck_thickness: +((dims.od - dims.id) / 2).toFixed(3),
      inside_projection: 0,
      outside_projection: dims.length,
      size_designation: `${npsText(dims.row.nps)} ${a.rating_class} ${a.coupling_form}`,
      material_id: base.material_id,
      corrosion_allowance: base.corrosion_allowance,
      reinforcement_pad: false,
      reinforcement_pad_thickness: null,
      reinforcement_pad_od: null,
      rating_class: a.rating_class,
      coupling_form: a.coupling_form,
    };
    set({ project: { ...p, nozzles: [...p.nozzles, nozzle] }, dirty: true, calc: null });
    return tag;
  },

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
    calc: null, dirty: false, step: 0, geoSubStep: 0, selection: null,
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
      const hostId = s.project.component_sequence.find((c) => c.component_type === "shell")?.component_id
        ?? s.project.shell_sections[0]?.section_id ?? "SHELL-01";
      const shell = s.project.shell_sections.find((x) => x.section_id === hostId) ?? s.project.shell_sections[0];
      const newNozzle: Nozzle = {
        tag: nextTag("N", s.project.nozzles.map((n) => n.tag)),
        nozzle_type: "flanged",
        host_component_id: hostId,
        axial_position: Math.round((shell?.tangent_length ?? 2000) / 2),
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
      // Etiket = kimlik: yeniden numaralandırma YOK.
      const removed = s.project.nozzles[index];
      if (!removed) return s;
      const nozzles = s.project.nozzles.filter((_, i) => i !== index);
      const selection = s.selection?.kind === "nozzle" && s.selection.id === removed.tag ? null : s.selection;
      return {
        project: { ...s.project, nozzles },
        selection,
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
  addFlange: () =>
    set((s) => {
      const flanges = s.project.flanges ?? [];
      const newFlange: Flange = {
        flange_id: `FL-${flanges.length + 1}`,
        type: "integral",
        inside_diameter: 500,
        outside_diameter: 700,
        thickness: 50,
        hub_small_thickness: 20,
        hub_length: 50,
        material_id: s.project.materials[0]?.material_id ?? "MAT-01",
        gasket_m: null,
        gasket_y: null,
        bolt_count: null,
        bolt_area: null,
        bolt_allowable_stress: null,
        flange_factor_Y: null,
        flange_factor_f: null,
        flange_factor_F: null,
        flange_factor_V: null,
        flange_factor_T: null,
        flange_factor_U: null,
        hub_large_thickness: null,
        bolt_load_W_N: null,
        moment_M_Nmm: null,
        rating_standard: null,
      };
      return { project: { ...s.project, flanges: [...flanges, newFlange] }, dirty: true, calc: null };
    }),
  removeFlange: (index) =>
    set((s) => ({
      project: { ...s.project, flanges: (s.project.flanges ?? []).filter((_, i) => i !== index) },
      dirty: true,
      calc: null,
    })),
  updateFlange: (index, patch) =>
    set((s) => ({
      project: {
        ...s.project,
        flanges: (s.project.flanges ?? []).map((f, i) => (i === index ? { ...f, ...patch } : f)),
      },
      dirty: true,
      calc: null,
    })),
  addSupport: (typeArg, hostArg) => {
    const type: Support["type"] = typeArg === "skirt" || typeArg === "leg" ? typeArg : "saddle";
    const p = get().project;
    const frames = componentFrames(p);
    const datum = tangentDatum(frames);
    const id = nextId("SUP", p.supports.map((x) => x.support_id));
    const newSupport: Support = {
        support_id: id,
        // Varsayılan host: zincirdeki ilk GÖVDE (eyer yalnız gövdeye oturur; etek/ayak da
        // varsayılan olarak gövdeye bağlanır). Gövde yoksa ilk eleman.
        host_component_id:
          (typeof hostArg === "string" ? hostArg : null)
          ?? p.component_sequence.find((c) => c.component_type === "shell")?.component_id
          ?? p.shell_sections[0]?.section_id
          ?? p.component_sequence[0]?.component_id
          ?? null,
        type,
        // location_mm sol teğet datumundan (Zick); etek kullanmaz.
        location_mm: type === "skirt" ? 0 : Math.round(Math.max(datum.right - datum.left, 0) * 0.2),
        width_mm: 200,
        height_mm: type === "skirt" ? 1500 : 500,
        diameter_mm: null,
        thickness_mm: null,
        skirt_allowable_compressive_MPa: null,
        skirt_weld_efficiency: null,
        material_id: p.materials[0]?.material_id ?? "MAT-01",
        contact_angle_deg: type === "saddle" ? 120 : null,
        saddle_stiffened: null,
        zick_K1: null,
        zick_K2: null,
        zick_K3: null,
        zick_K6: null,
        zick_K7: null,
        leg_count: type === "leg" ? 4 : null,
        leg_diameter_mm: null,
        leg_thickness_mm: null,
        support_radius_mm: null,
        leg_pad_length_mm: null,
        leg_pad_width_mm: null,
        leg_pad_thickness_mm: null,
        base_plate_area_mm2: null,
        leg_attachment: null,
        leg_section_type: null,
        leg_profile_height_mm: null,
        leg_profile_width_mm: null,
        leg_web_thickness_mm: null,
        leg_flange_thickness_mm: null,
        leg_channel_facing: null,
        leg_pad_top_extension_mm: null,
        leg_start_angle_deg: null,
        leg_unbraced_length_mm: null,
        leg_eccentricity_mm: null,
        leg_effective_length_factor_K: null,
        leg_pad_contact_ratio: null,
        base_plate_length_mm: null,
        base_plate_width_mm: null,
        base_plate_thickness_mm: null,
        base_plate_yield_MPa: null,
        foundation_bearing_allowable_MPa: null,
        pad_to_shell_weld_leg_mm: null,
        leg_to_pad_weld_leg_mm: null,
        leg_to_base_plate_weld_leg_mm: null,
        weld_electrode_strength_MPa: null,
        weld_min_leg_mm: null,
        wrc_coefficients: null,
        wrc_beta_ML: null,
        wrc_beta_MC: null,
        anchor_bolt_count: null,
        anchor_bolt_diameter_mm: null,
        anchor_tension_allowable_N: null,
        anchor_shear_allowable_N: null,
        lateral_load_N: 0,
        overturning_moment_Nmm: 0,
    };
    set({ project: { ...p, supports: [...p.supports, newSupport] }, dirty: true, calc: null });
    return id;
  },
  removeSupport: (index) =>
    set((s) => {
      const removedId = s.project.supports[index]?.support_id;
      const supports = s.project.supports.filter((_, i) => i !== index);
      return {
        project: { ...s.project, supports },
        selection: s.selection?.kind === "support" && s.selection.id === removedId ? null : s.selection,
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
    set((s) => chainCommit({
      ...s.project,
      shell_sections: s.project.shell_sections.map((section) =>
        section.section_id === sectionId ? { ...section, ...patch } : section
      ),
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
    set((s) => chainCommit({
      ...s.project,
      cones: s.project.cones.map((cone) => {
        if (cone.cone_id !== coneId) return cone;
        const next = { ...cone, ...patch };
        // large/small/length değişince yarı tepe açısı yeniden (patch'te açı açıkça verilse de).
        if (patch.large_diameter != null || patch.small_diameter != null || patch.length != null) {
          next.half_apex_angle = halfApexAngle(next.large_diameter, next.small_diameter, next.length);
        }
        return next;
      }),
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
      flanges: (s.project.flanges ?? []).map((x) => ({ ...x, material_id: replace(x.material_id) })),
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
    const p = s.project;
    const index = p.component_sequence.findIndex((x) => x.component_id === ref.component_id);
    // Bombe kopyası zincir ortasına bombe sokar (INTERNAL_HEAD) → yalnız gövde/koni.
    if (index < 0 || ref.component_type === "head") return s;
    let project = p;
    let id: string;
    if (ref.component_type === "shell") {
      const item = p.shell_sections.find((x) => x.section_id === ref.component_id);
      if (!item) return s;
      id = nextId("SHELL", p.shell_sections.map((x) => x.section_id));
      project = { ...project, shell_sections: [...project.shell_sections, { ...item, section_id: id }] };
    } else {
      const item = p.cones.find((x) => x.cone_id === ref.component_id);
      if (!item) return s;
      id = nextId("CONE", p.cones.map((x) => x.cone_id));
      project = { ...project, cones: [...project.cones, { ...item, cone_id: id }] };
    }
    const sequence = insertRefs(p.component_sequence, index + 1, [{ component_type: ref.component_type, component_id: id }]);
    return chainCommit({ ...project, component_sequence: sequence });
  }),
  removeComponent: (ref) => set((s) => {
    const seq = s.project.component_sequence;
    const index = seq.findIndex((x) => x.component_id === ref.component_id);
    // Terminal bombe ve tek kalan gövde elemanı silinmez.
    if (index <= 0 || index >= seq.length - 1 || seq.length <= 3) return s;
    const sequence = seq.filter((x) => x.component_id !== ref.component_id);
    const project = ref.component_type === "shell"
      ? { ...s.project, shell_sections: s.project.shell_sections.filter((x) => x.section_id !== ref.component_id) }
      : ref.component_type === "head"
        ? { ...s.project, heads: s.project.heads.filter((x) => x.head_id !== ref.component_id) }
        : { ...s.project, cones: s.project.cones.filter((x) => x.cone_id !== ref.component_id) };
    const removedTags = new Set(
      project.nozzles.filter((x) => x.host_component_id === ref.component_id).map((x) => x.tag),
    );
    const sel = s.selection;
    const selection = sel && (sel.id === ref.component_id || (sel.kind === "nozzle" && removedTags.has(sel.id)))
      ? null : sel;
    return {
      ...chainCommit({
        ...project,
        component_sequence: sequence,
        nozzles: project.nozzles.filter((x) => x.host_component_id !== ref.component_id),
        supports: project.supports.map((x) => x.host_component_id === ref.component_id ? { ...x, host_component_id: null } : x),
      }),
      selection,
    };
  }),
  moveComponent: (index, direction) => set((s) => {
    const next = index + direction;
    const n = s.project.component_sequence.length;
    // Yalnız iç elemanlar (1..n−2) yer değiştirir; uç bombeler sabit.
    if (index < 1 || index > n - 2 || next < 1 || next > n - 2) return s;
    const sequence = [...s.project.component_sequence];
    [sequence[index], sequence[next]] = [sequence[next], sequence[index]];
    return chainCommit({ ...s.project, component_sequence: sequence });
  }),
}));
