// Domain modellerinin TypeScript karşılıkları (backend Pydantic ile uyumlu).

export interface DesignConditions {
  operating_pressure: number;
  design_pressure: number;
  maximum_allowable_pressure_ps: number;
  operating_temperature: number;
  design_temperature: number;
  minimum_design_temperature: number;
  external_pressure: number;
  vacuum_condition: boolean;
  hydrotest_temperature: number;
  corrosion_allowance_internal: number;
  corrosion_allowance_external: number;
  fluid_density_kg_m3: number;
  impact_test_temperature_C: number | null;
}

export interface ShellSection {
  section_id: string;
  inside_diameter: number | null;
  outside_diameter: number | null;
  tangent_length: number;
  nominal_thickness: number;
  material_id: string;
  weld_joint_id: string | null;
  internal_corrosion_allowance: number;
  external_corrosion_allowance: number;
  mill_tolerance: number;
  forming_thinning: number;
  ug28_strain_factor_a: number | null;
  ug28_allowable_stress_b: number | null;
}

export type HeadTypeT = "elliptical" | "torispherical" | "hemispherical" | "flat";

export type RecognitionConfidence = "high" | "medium" | "low";
export interface RecognizedField<T = number> { value: T; confidence: RecognitionConfidence; note: string | null; }
export interface StepRecognition {
  status: "RECOGNIZED" | "PARTIAL" | "REJECTED" | "BLOCKED";
  source: { filename: string; unit: string; unit_scale: number; solid_count: number };
  shell: null | { inside_diameter: RecognizedField; nominal_thickness: RecognizedField; tangent_length: RecognizedField };
  heads: Array<{ side: "left" | "right"; type: RecognizedField<HeadTypeT>; inside_diameter: RecognizedField; nominal_thickness: RecognizedField; straight_flange_length: RecognizedField | null; crown_radius: RecognizedField | null; knuckle_radius: RecognizedField | null }>;
  nozzles: Array<{ tag: string; outside_diameter: RecognizedField; inside_diameter: RecognizedField; neck_thickness: RecognizedField; axial_position: RecognizedField; circumferential_angle: RecognizedField; outside_projection: RecognizedField }>;
  unrecognized: Array<{ feature: string; reason: string }>;
  warnings: string[];
  not_in_file: string[];
}

export interface Head {
  head_id: string;
  type: HeadTypeT;
  inside_diameter: number;
  crown_radius: number | null;
  knuckle_radius: number | null;
  outside_diameter?: number | null;
  crown_depth?: number | null;
  torispherical_geometry?: "standard_asme_fd" | "custom";
  straight_flange_length: number;
  nominal_thickness: number;
  material_id: string;
  weld_joint_id: string | null;
  internal_corrosion_allowance: number;
  mill_tolerance: number;
  forming_thinning: number;
  flat_attachment_factor: number | null;
  flat_z_factor?: number | null;
  ug28_strain_factor_a: number | null;
  ug28_allowable_stress_b: number | null;
}

export interface Cone {
  cone_id: string;
  large_diameter: number;
  small_diameter: number;
  half_apex_angle: number;
  length: number;
  nominal_thickness: number;
  material_id: string;
  weld_joint_id: string | null;
  internal_corrosion_allowance: number;
  mill_tolerance: number;
}

export interface Junction {
  junction_id: string;
  left_component_id: string;
  right_component_id: string;
  junction_type: "cone_to_shell" | "cone_to_head" | "shell_to_shell";
  cone_end: "large" | "small" | null;
  weld_joint_id: string | null;
  weld_efficiency: number | null;
  large_end_diameter: number | null;
  small_end_diameter: number | null;
  knuckle_radius_mm: number | null;
  analysis_status: "INPUT_ONLY" | "REVIEW_REQUIRED" | "SUPPORTED";
}

export type ComponentType = "head" | "shell" | "cone";

export interface ComponentReference {
  component_type: ComponentType;
  component_id: string;
}

export interface Nozzle {
  tag: string;
  nozzle_type: string;
  host_component_id: string;
  axial_position: number;
  circumferential_angle: number;
  inclination_angle: number;
  /** Bombe host'ta: merkez ekseninden ölçülen yerleşim çapı (mm). */
  head_position_diameter: number | null;
  outside_diameter: number;
  inside_diameter: number;
  neck_thickness: number;
  inside_projection: number;
  outside_projection: number;
  /** Katalogdan seçilen anma ölçüsü (ör. '1½" SCH40') — K5 izlenebilirlik. */
  size_designation: string | null;
  material_id: string;
  corrosion_allowance: number;
  reinforcement_pad: boolean;
  reinforcement_pad_thickness: number | null;
  reinforcement_pad_od: number | null;
}

export interface MaterialProperty {
  material_id: string;
  standard_pack: string;
  material_designation: string;
  product_form: string;
  thickness_min: number;
  thickness_max: number;
  temperature: number;
  allowable_stress: number;
  /** Test sıcaklığındaki S (UG-99(b)/UG-100 LSR). Boşsa ve sıcaklıklar farklıysa test basıncı REVIEW_REQUIRED. */
  allowable_stress_test_temp: number | null;
  yield_strength: number;
  tensile_strength: number;
  source_reference: string;
  source_revision: string;
  density: number;
  /** UCS-66 eğri grubu (A/B/C/D). Boşsa MDMT kontrolü bloke olur — tahmin edilmez. */
  ucs66_curve_group: string | null;
}

export interface Support {
  support_id: string;
  host_component_id: string | null;
  type: "saddle" | "skirt" | "leg";
  location_mm: number;
  width_mm: number;
  height_mm: number;
  diameter_mm: number | null;
  thickness_mm: number | null;
  skirt_allowable_compressive_MPa: number | null;
  skirt_weld_efficiency: number | null;
  material_id: string;
  contact_angle_deg: number | null;
  /** Eyer düzleminde halka var mı; null = girilmedi (Zick bloke). */
  saddle_stiffened: boolean | null;
  /** Zick K katsayıları — kullanıcı tablodan okur (K6: program tabloyu içermez). null = girilmedi. */
  zick_K1: number | null;
  zick_K2: number | null;
  zick_K3: number | null;
  zick_K6: number | null;
  zick_K7: number | null;
  leg_count: number | null;
  leg_diameter_mm: number | null;
  leg_thickness_mm: number | null;
  support_radius_mm: number | null;
  leg_pad_length_mm: number | null;
  leg_pad_width_mm: number | null;
  leg_pad_thickness_mm: number | null;
  base_plate_area_mm2: number | null;
  /** Ayak alt kontrol alanları (Ayak-A backend). null = girilmedi. K6: profil katalogu/AWS tablosu/WRC katsayısı programda yok. */
  leg_attachment: "shell" | "bottom_head" | null;
  leg_section_type: "pipe" | "channel" | "box" | "angle" | null;
  leg_profile_height_mm: number | null;
  leg_profile_width_mm: number | null;
  leg_web_thickness_mm: number | null;
  leg_flange_thickness_mm: number | null;
  leg_unbraced_length_mm: number | null;
  leg_eccentricity_mm: number | null;
  leg_effective_length_factor_K: number | null;
  leg_pad_contact_ratio: number | null;
  base_plate_length_mm: number | null;
  base_plate_width_mm: number | null;
  base_plate_thickness_mm: number | null;
  base_plate_yield_MPa: number | null;
  foundation_bearing_allowable_MPa: number | null;
  pad_to_shell_weld_leg_mm: number | null;
  leg_to_pad_weld_leg_mm: number | null;
  leg_to_base_plate_weld_leg_mm: number | null;
  weld_electrode_strength_MPa: number | null;
  weld_min_leg_mm: number | null;
  /** WRC 107/537 katsayıları: nokta (A/B/C/D) → yük (P/ML/MC/VL/VC) → dört katsayı. null = okunmadı. */
  wrc_coefficients: Record<string, Record<string, WrcCoefficientEntry>> | null;
  anchor_bolt_count: number | null;
  anchor_bolt_diameter_mm: number | null;
  anchor_tension_allowable_N: number | null;
  anchor_shear_allowable_N: number | null;
  lateral_load_N: number;
  overturning_moment_Nmm: number;
}

export interface WrcCoefficientEntry {
  Nx: number | null;
  Ny: number | null;
  Mx: number | null;
  My: number | null;
}

export interface WeldJoint {
  joint_id: string;
  joint_type: string;
  weld_category: string | null;
  joint_efficiency: number;
  nde_method: string | null;
  nde_extent: string | null;
  full_penetration: boolean;
  wps_number: string | null;
  pqr_number: string | null;
  welder_qualification: string | null;
  pwht_required: boolean;
}

export interface VesselProject {
  project_number: string;
  project_name: string;
  customer: string | null;
  revision: string;
  calculation_code: string;
  code_edition: string;
  unit_system: string;
  orientation: string;
  /** Gövde ve bombe çaplarının varsayılan ilişkisi. */
  diameter_relation?: "linked" | "independent";
  design_conditions: DesignConditions;
  shell_sections: ShellSection[];
  heads: Head[];
  cones: Cone[];
  junctions: Junction[];
  component_sequence: ComponentReference[];
  flanges?: Flange[];
  nozzles: Nozzle[];
  materials: MaterialProperty[];
  supports: Support[];
  welds: WeldJoint[];
  pressure_relief?: PressureReliefSystem | null;
}

export type GeometryAgentTarget = "shell" | "head" | "vessel";
export type GeometryAgentField =
  | "inside_diameter"
  | "tangent_length"
  | "nominal_thickness"
  | "type"
  | "straight_flange_length"
  | "orientation";

export interface GeometryAgentChange {
  target_type: GeometryAgentTarget;
  target_id: string;
  field: GeometryAgentField;
  value: number | string;
}

export interface GeometryAgentSuggestion {
  summary: string;
  changes: GeometryAgentChange[];
  warnings: string[];
}

export interface GeometryAgentInterpretRequest {
  instruction: string;
  context: {
    active_shell_id: string;
    shell_ids: string[];
    heads: { head_id: string; side: "left" | "right" | "other" }[];
    diameter_relation: "linked" | "independent";
  };
}

export interface ProjectSummary {
  id: string;
  project_number: string;
  project_name: string;
  customer: string | null;
  revision: string;
  calculation_code: string;
}

export interface Flange {
  flange_id: string;
  type: "integral" | "loose";
  inside_diameter: number;
  outside_diameter: number;
  thickness: number;
  hub_small_thickness: number;
  hub_length: number;
  material_id: string;
  gasket_m: number | null;
  gasket_y: number | null;
  bolt_count: number | null;
  bolt_area: number | null;
  bolt_allowable_stress: number | null;
  // K6: lisanslı ASME Appendix 2 çizelgesinden kullanıcı okur; null = girilmedi (hesap bloke).
  flange_factor_Y: number | null;
  flange_factor_f: number | null;
  // K6: Şekil 2-7.1 faktörleri F, V, T, U — kullanıcı okur; null = girilmedi (hesap bloke).
  flange_factor_F: number | null;
  flange_factor_V: number | null;
  flange_factor_T: number | null;
  flange_factor_U: number | null;
  // Appendix 2 g1: hub büyük uç kalınlığı (hub_small_thickness = g0); null = girilmedi (bloke).
  hub_large_thickness: number | null;
  // K6: W (N) ve M (N·mm) kullanıcının Appendix 2 çalışma sayfasından gelir; null = girilmedi (hesap bloke).
  bolt_load_W_N: number | null;
  moment_M_Nmm: number | null;
  rating_standard: string | null;
}

export interface PressureReliefDevice {
  device_id: string;
  device_type: "safety_valve" | "rupture_disk";
  protected_component_id?: string | null;
  set_pressure_mpa?: number | null;
  burst_pressure_mpa?: number | null;
  accumulation_percent?: number | null;
  blowdown_percent?: number | null;
  certified_capacity_kg_s?: number | null;
  fluid_orifice_area_mm2?: number | null;
  certification_reference?: string | null;
}

export interface PressureReliefSystem {
  enabled: boolean;
  protected_mawp_mpa?: number | null;
  accumulation_limit_percent: number;
  devices: PressureReliefDevice[];
  notes?: string;
}

export interface IntermediateValue {
  name: string;
  value: number | string;
  unit: string;
  description: string;
}

export interface CalcResult {
  component_id: string | null;
  component_type: string;
  calculation_type: string;
  code: string;
  edition: string;
  clause_reference: string;
  final_result: number | null;
  final_result_unit: string;
  allowable_limit: number | null;
  allowable_limit_unit: string;
  utilization_ratio: number | null;
  status: string;
  warnings: string[];
  notices?: string[];
  assumptions: string[];
  intermediate_values: IntermediateValue[];
  governing?: boolean;
  reference_elevation_mm?: number;
}

/** Publication validation summary; informative and does not change calculations. */
export interface CalcVerification {
  case_name: string;
  passed: boolean;
  checks: { calculation_id: string; passed: boolean }[];
  errors: string[];
}

export interface CalcPayload {
  project_number: string;
  code: string;
  edition: string;
  global_mawp_mpa: number | null;
  results: CalcResult[];
  errors: string[];
  volume_mass: {
    inner_volume_liters: number;
    inner_volume_m3: number;
    metal_mass_kg: number;
  };
  verification?: CalcVerification;
}
