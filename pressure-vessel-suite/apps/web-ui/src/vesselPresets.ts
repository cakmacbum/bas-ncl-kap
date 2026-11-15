// Başlangıç şablonları (Adım 01). Yalnız geometri ve tasarım koşulu girdisi taşır.
// K3/K6: izin verilen gerilme (S), akma/çekme dayanımı, UCS-66 eğrisi ve UG-28 A/B
// faktörleri GÖMÜLMEZ — "girilmedi" (0 / null) bırakılır, kullanıcı lisanslı kaynağından girer.
// K4: şablonun seçtiği her değer `notes` ile kullanıcıya gösterilir.

import { defaultProject, normalizeProject } from "./store";
import type { HeadTypeT, VesselProject } from "./types";

export interface VesselPreset {
  id: string;
  name: string;
  description: string;
  /** Kullanıcının girmesi / doğrulaması gereken değerler (uygulandıktan sonra görünür kalır). */
  notes: string[];
  build(): VesselProject;
}

/** `MaterialProperty.allowable_stress` vb. alanlar `number`'dır; projedeki "girilmedi" temsili 0'dır. */
export const NOT_ENTERED = 0;

interface PresetSpec {
  projectNumber: string;
  projectName: string;
  orientation: "horizontal" | "vertical";
  insideDiameter: number;
  tangentLength: number;
  nominalThickness: number;
  headType: HeadTypeT;
  operatingPressure: number;
  designPressure: number;
  operatingTemperature: number;
  designTemperature: number;
  externalPressure: number;
  vacuum: boolean;
  corrosionAllowance: number;
  materialDesignation: string;
  density: number;
}

function buildProject(s: PresetSpec): VesselProject {
  const base = defaultProject();
  const material = {
    ...base.materials[0],
    material_designation: s.materialDesignation,
    temperature: s.designTemperature,
    allowable_stress: NOT_ENTERED,
    allowable_stress_test_temp: null,
    yield_strength: NOT_ENTERED,
    tensile_strength: NOT_ENTERED,
    source_reference: "Girilmedi — kullanıcı lisanslı kaynağından girer",
    source_revision: "",
    density: s.density,
    ucs66_curve_group: null,
  };
  const shell = {
    ...base.shell_sections[0],
    inside_diameter: s.insideDiameter,
    outside_diameter: null,
    tangent_length: s.tangentLength,
    nominal_thickness: s.nominalThickness,
    material_id: material.material_id,
    internal_corrosion_allowance: s.corrosionAllowance,
    external_corrosion_allowance: 0,
    ug28_strain_factor_a: null,
    ug28_allowable_stress_b: null,
  };
  const heads = base.heads.map((h) => ({
    ...h,
    type: s.headType,
    inside_diameter: s.insideDiameter,
    crown_radius: null,
    knuckle_radius: null,
    nominal_thickness: s.nominalThickness,
    material_id: material.material_id,
    internal_corrosion_allowance: s.corrosionAllowance,
    ug28_strain_factor_a: null,
    ug28_allowable_stress_b: null,
  }));
  // Varsayılan projedeki tek nozul (N1) korunur: gövde ortasına alınır, takviye pedi kapalı.
  const nozzles = base.nozzles.slice(0, 1).map((n) => ({
    ...n,
    host_component_id: shell.section_id,
    axial_position: Math.round(s.tangentLength / 2),
    material_id: material.material_id,
    corrosion_allowance: s.corrosionAllowance,
    reinforcement_pad: false,
    reinforcement_pad_thickness: null,
    reinforcement_pad_od: null,
  }));
  return normalizeProject({
    ...base,
    project_number: s.projectNumber,
    project_name: s.projectName,
    calculation_code: "ASME VIII-1",
    orientation: s.orientation,
    diameter_relation: "linked",
    design_conditions: {
      ...base.design_conditions,
      operating_pressure: s.operatingPressure,
      design_pressure: s.designPressure,
      maximum_allowable_pressure_ps: s.designPressure,
      operating_temperature: s.operatingTemperature,
      design_temperature: s.designTemperature,
      external_pressure: s.externalPressure,
      vacuum_condition: s.vacuum,
      corrosion_allowance_internal: s.corrosionAllowance,
      corrosion_allowance_external: 0,
      fluid_density_kg_m3: 0,
      liquid_level_mm: null,
    },
    materials: [material],
    shell_sections: [shell],
    heads,
    cones: [],
    junctions: [],
    supports: [],
    flanges: [],
    component_sequence: [
      { component_type: "head", component_id: heads[0].head_id },
      { component_type: "shell", component_id: shell.section_id },
      { component_type: "head", component_id: heads[1].head_id },
    ],
    nozzles,
  });
}

const MATERIAL_NOTE =
  "Malzeme: izin verilen gerilme (S), test sıcaklığındaki S, akma ve çekme dayanımı girilmedi (0). " +
  "Bu değerleri kendi lisanslı kaynağınızdan Malzeme adımında girin. Girilene kadar proje kaydedilemez ve hesaplanamaz (sunucu 0 değerlerini reddeder); " +
  "3B model, rapor ve STEP çıktısı da bu nedenle kullanılamaz.";
const COMMON_NOTES = [
  "Başlangıç değeri olarak bırakılanlar: gövde ve bombe imalat eksi toleransı %12,5, şekillendirme incelmesi 0, bombe düz kenar uzunluğu 40 mm; izin verilen azami basınç (Ps) tasarım basıncına eşitlendi. Projenize göre doğrulayın.",
  "Nozul N1 varsayılan ölçüleriyle geldi: dış çap 168,3 mm, iç çap 154,1 mm, boyun kalınlığı 7,1 mm, dış çıkıntı 150 mm, iç çıkıntı 0; korozyon payı kap korozyon payına eşitlendi.",
  "Malzeme adı yalnızca etikettir; UCS-66 eğri grubu boş bırakıldı (MDMT kontrolü siz girene kadar yapılmaz).",
  "Nominal kalınlık, kaynak verimi (1,0 — tam radyografi kabulü), en düşük tasarım sıcaklığı (−10 °C) ve hidrotest sıcaklığı (20 °C) başlangıç değeridir; projenize göre doğrulayın.",
  "Akışkan yoğunluğu 0 ve sıvı seviyesi boş: statik sıvı basıncı hesaba girmez. Sıvı varsa Tasarım Koşulları adımında girin.",
  "Tek nozul (N1, gövde ortası, takviye pedsiz) örnek olarak eklendi; destek tanımlı değil. Nozul ve destekleri kendi tasarımınıza göre düzenleyin.",
];

export const VESSEL_PRESETS: readonly VesselPreset[] = [
  {
    id: "horizontal-air-receiver",
    name: "Yatay Hava Tankı",
    description: "ASME VIII-1 · yatay · iç çap 1200 mm · teğet boyu 3000 mm · 1,0 MPa · 65 °C · 2:1 eliptik bombe · SA-516 Gr.70 · korozyon payı 1,5 mm",
    notes: [
      MATERIAL_NOTE,
      "Şablonun seçtikleri: çalışma basıncı 0,8 MPa, çalışma sıcaklığı 50 °C, nominal kalınlık 10 mm, çelik yoğunluğu 7850 kg/m³.",
      ...COMMON_NOTES,
    ],
    build: () => buildProject({
      projectNumber: "PRJ-HAVA-01",
      projectName: "Yatay Hava Tankı",
      orientation: "horizontal",
      insideDiameter: 1200,
      tangentLength: 3000,
      nominalThickness: 10,
      headType: "elliptical",
      operatingPressure: 0.8,
      designPressure: 1.0,
      operatingTemperature: 50,
      designTemperature: 65,
      externalPressure: 0,
      vacuum: false,
      corrosionAllowance: 1.5,
      materialDesignation: "SA-516 Gr.70",
      density: 7850,
    }),
  },
  {
    id: "vacuum-process-tank",
    name: "Vakumlu Proses Tankı",
    description: "ASME VIII-1 · dikey · iç çap 1600 mm · teğet boyu 2400 mm · iç 0,35 MPa · dış 0,1013 MPa (tam vakum) · 2:1 eliptik bombe · SA-240 304 · korozyon payı 0",
    notes: [
      MATERIAL_NOTE,
      "Dış basınç 0,1013 MPa tam vakum (1 atm) varsayımıdır; gerçek çalışma vakumunuza göre değiştirin.",
      "Elastisite modülü (E) boş bırakıldı: ASME VIII-1 dış basınç kontrolü (UG-28) E yerine A/B faktörlerini kullanır; E yalnız EN 13445 ve FEA laboratuvarı için gerekir.",
      "Dış basınç: gövde ve bombelerin UG-28 A/B faktörleri boş bırakıldı. Kendi lisanslı eğrilerinizden okuyup Kap Geometrisi adımında girin; girilmeden dış basınç kontrolü sonuç vermez.",
      "Şablonun seçtikleri: çalışma basıncı 0,25 MPa, tasarım sıcaklığı 100 °C, çalışma sıcaklığı 80 °C, nominal kalınlık 10 mm, paslanmaz çelik yoğunluğu 8000 kg/m³ (malzeme belgenizden doğrulayın).",
      ...COMMON_NOTES,
    ],
    build: () => buildProject({
      projectNumber: "PRJ-VAKUM-01",
      projectName: "Vakumlu Proses Tankı",
      orientation: "vertical",
      insideDiameter: 1600,
      tangentLength: 2400,
      nominalThickness: 10,
      headType: "elliptical",
      operatingPressure: 0.25,
      designPressure: 0.35,
      operatingTemperature: 80,
      designTemperature: 100,
      externalPressure: 0.1013,
      vacuum: true,
      corrosionAllowance: 0,
      materialDesignation: "SA-240 304",
      density: 8000,
    }),
  },
  {
    id: "vertical-separator",
    name: "Dikey Seperatör",
    description: "ASME VIII-1 · dikey · iç çap 1000 mm · teğet boyu 3000 mm · 1,6 MPa · 120 °C · 2:1 eliptik bombe · SA-516 Gr.70 · korozyon payı 3 mm",
    notes: [
      MATERIAL_NOTE,
      "Şablonun seçtikleri: çalışma basıncı 1,4 MPa, çalışma sıcaklığı 100 °C, nominal kalınlık 12 mm, çelik yoğunluğu 7850 kg/m³.",
      ...COMMON_NOTES,
    ],
    build: () => buildProject({
      projectNumber: "PRJ-SEP-01",
      projectName: "Dikey Seperatör",
      orientation: "vertical",
      insideDiameter: 1000,
      tangentLength: 3000,
      nominalThickness: 12,
      headType: "elliptical",
      operatingPressure: 1.4,
      designPressure: 1.6,
      operatingTemperature: 100,
      designTemperature: 120,
      externalPressure: 0,
      vacuum: false,
      corrosionAllowance: 3,
      materialDesignation: "SA-516 Gr.70",
      density: 7850,
    }),
  },
];
