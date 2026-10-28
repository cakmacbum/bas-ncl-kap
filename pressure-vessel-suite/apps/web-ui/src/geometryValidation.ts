import type { ComponentReference, VesselProject } from "./types";

export interface GeometryIssue {
  code: string;
  message: string;
  blocking: boolean;
}

function sequenceFor(project: VesselProject): ComponentReference[] {
  if (project.component_sequence?.length) return project.component_sequence;
  if (project.shell_sections.length === 1 && project.heads.length >= 2 && project.cones.length === 0) {
    return [
      { component_type: "head", component_id: project.heads[0].head_id },
      { component_type: "shell", component_id: project.shell_sections[0].section_id },
      { component_type: "head", component_id: project.heads[1].head_id },
    ];
  }
  return [];
}

function knownComponent(project: VesselProject, ref: ComponentReference): boolean {
  return ref.component_type === "head"
    ? project.heads.some((x) => x.head_id === ref.component_id)
    : ref.component_type === "shell"
      ? project.shell_sections.some((x) => x.section_id === ref.component_id)
      : project.cones.some((x) => x.cone_id === ref.component_id);
}

export function geometryIssues(project: VesselProject): GeometryIssue[] {
  const issues: GeometryIssue[] = [];
  const sequence = sequenceFor(project);

  if (sequence.length === 0) {
    issues.push({ code: "sequence-missing", message: "Basınç taşıyan eleman zinciri tanımlanmamış.", blocking: true });
  }
  const seen = new Set<string>();
  sequence.forEach((ref, index) => {
    const key = `${ref.component_type}:${ref.component_id}`;
    if (seen.has(key)) issues.push({ code: `sequence-duplicate-${index}`, message: `${key} zincirde birden fazla kullanılamaz.`, blocking: true });
    seen.add(key);
    if (!knownComponent(project, ref)) issues.push({ code: `sequence-missing-${index}`, message: `${key} gerçek bileşen dizisinde bulunamadı.`, blocking: true });
  });
  if (sequence.length >= 2 && (sequence[0].component_type !== "head" || sequence[sequence.length - 1].component_type !== "head")) {
    issues.push({ code: "sequence-terminals", message: "Zincirin iki terminalinde bombe bulunmalıdır.", blocking: true });
  }

  project.shell_sections.forEach((shell) => {
    if ((shell.inside_diameter ?? 0) <= 0) issues.push({ code: `shell-${shell.section_id}-diameter`, message: `${shell.section_id} iç çapı 0'dan büyük olmalıdır.`, blocking: true });
    if (shell.tangent_length <= 0) issues.push({ code: `shell-${shell.section_id}-length`, message: `${shell.section_id} teğet uzunluğu 0'dan büyük olmalıdır.`, blocking: true });
    if (shell.nominal_thickness <= 0) issues.push({ code: `shell-${shell.section_id}-thickness`, message: `${shell.section_id} nominal kalınlığı 0'dan büyük olmalıdır.`, blocking: true });
  });
  project.heads.forEach((head) => {
    if (head.inside_diameter <= 0 || head.nominal_thickness <= 0) issues.push({ code: `head-${head.head_id}-dimensions`, message: `${head.head_id} çapı ve nominal kalınlığı pozitif olmalıdır.`, blocking: true });
  });
  project.cones.forEach((cone) => {
    if (cone.large_diameter <= cone.small_diameter) issues.push({ code: `cone-${cone.cone_id}-diameter-order`, message: `${cone.cone_id} büyük çapı küçük çapından büyük olmalıdır.`, blocking: true });
    if (cone.half_apex_angle > 30) issues.push({ code: `cone-${cone.cone_id}-knuckle-review`, message: `${cone.cone_id}: α > 30° için torikonik/knuckle veya özel analiz gerekir.`, blocking: true });
    if (cone.half_apex_angle > 60) issues.push({ code: `cone-${cone.cone_id}-appendix-1-8-scope`, message: `${cone.cone_id}: α > 60° için Appendix 1-8 dış basınç birleşim hesabı uygulanamaz.`, blocking: true });
  });

  project.nozzles.forEach((nozzle, index) => {
    if (nozzle.inside_diameter >= nozzle.outside_diameter) issues.push({ code: `nozzle-${index}-diameter`, message: `${nozzle.tag || `N${index + 1}`} iç çapı dış çaptan küçük olmalıdır.`, blocking: true });
  });
  return issues;
}

export function geometrySignature(project: VesselProject): string {
  return JSON.stringify({
    relation: project.diameter_relation ?? "linked",
    sequence: sequenceFor(project),
    shells: project.shell_sections.map((x) => [x.section_id, x.inside_diameter, x.tangent_length, x.nominal_thickness]),
    heads: project.heads.map((x) => [x.head_id, x.inside_diameter, x.nominal_thickness, x.type]),
    cones: project.cones.map((x) => [x.cone_id, x.large_diameter, x.small_diameter, x.length, x.half_apex_angle]),
    nozzles: project.nozzles.map((x) => [x.tag, x.host_component_id, x.axial_position, x.head_position_diameter, x.inside_diameter, x.outside_diameter]),
  });
}
