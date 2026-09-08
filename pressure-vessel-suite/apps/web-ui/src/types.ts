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

export interface Head {
  head_id: string;
  type: HeadTypeT;
  inside_diameter: number;
  crown_radius: number | null;
  knuckle_radius: number | null;
  straight_flange_length: number;
  nominal_thickness: number;
  material_id: string;
  weld_joint_id: string | null;
  internal_corrosion_allowance: number;
  mill_tolerance: number;
  forming_thinning: number;
  flat_attachment_factor: number | null;
  ug28_strain_factor_a: number | null;
  ug28_allowable_stress_b: number | null;
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
  type: "saddle" | "skirt" | "leg";
  location_mm: number;
  width_mm: number;
  height_mm: number;
  material_id: string;
  contact_angle_deg: number | null;
  leg_count: number | null;
  overturning_moment_Nmm: number;
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
  design_conditions: DesignConditions;
  shell_sections: ShellSection[];
  heads: Head[];
  nozzles: Nozzle[];
  materials: MaterialProperty[];
  supports: Support[];
  welds: WeldJoint[];
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
  assumptions: string[];
  intermediate_values: IntermediateValue[];
  governing?: boolean;
  reference_elevation_mm?: number;
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
}
