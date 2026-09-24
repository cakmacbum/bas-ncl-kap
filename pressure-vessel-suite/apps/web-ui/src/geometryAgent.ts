import type {
  GeometryAgentChange,
  GeometryAgentField,
  Head,
  HeadTypeT,
  ShellSection,
  VesselProject,
} from "./types";

const HEAD_TYPES = new Set<HeadTypeT>(["elliptical", "torispherical", "hemispherical", "flat"]);

export function expandGeometryAgentChanges(
  project: VesselProject,
  changes: GeometryAgentChange[]
): GeometryAgentChange[] {
  const expanded = [...changes];
  if ((project.diameter_relation ?? "linked") === "linked") {
    const shellDiameter = changes.find(
      (change) => change.target_type === "shell" && change.field === "inside_diameter"
    );
    if (shellDiameter && typeof shellDiameter.value === "number") {
      project.heads.forEach((head) => {
        if (!changes.some((change) => change.target_type === "head" && change.target_id === head.head_id && change.field === "inside_diameter")) {
          expanded.push({
            target_type: "head",
            target_id: head.head_id,
            field: "inside_diameter",
            value: shellDiameter.value,
          });
        }
      });
    }
  }
  return expanded;
}

function safeNumber(value: number | string, allowZero = false): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  if (allowZero ? value < 0 : value <= 0) return null;
  return value;
}

export function applyGeometryAgentChanges(
  project: VesselProject,
  rawChanges: GeometryAgentChange[]
): VesselProject {
  let next = project;
  const changes = expandGeometryAgentChanges(project, rawChanges);
  for (const change of changes) {
    if (change.target_type === "vessel") {
      if (change.target_id === "project" && change.field === "orientation" && (change.value === "horizontal" || change.value === "vertical")) {
        next = { ...next, orientation: change.value };
      }
      continue;
    }
    if (change.target_type === "shell") {
      const allowed: GeometryAgentField[] = ["inside_diameter", "tangent_length", "nominal_thickness"];
      if (!allowed.includes(change.field)) continue;
      const value = safeNumber(change.value);
      if (value == null || !next.shell_sections.some((item) => item.section_id === change.target_id)) continue;
      next = {
        ...next,
        shell_sections: next.shell_sections.map((item) =>
          item.section_id === change.target_id
            ? { ...item, [change.field]: value } as ShellSection
            : item
        ),
      };
      continue;
    }
    const targetExists = next.heads.some((item) => item.head_id === change.target_id);
    if (!targetExists) continue;
    if (change.field === "type") {
      if (typeof change.value !== "string" || !HEAD_TYPES.has(change.value as HeadTypeT)) continue;
      next = {
        ...next,
        heads: next.heads.map((item) => item.head_id === change.target_id ? { ...item, type: change.value as HeadTypeT } : item),
      };
      continue;
    }
    const allowed: GeometryAgentField[] = ["inside_diameter", "nominal_thickness", "straight_flange_length"];
    if (!allowed.includes(change.field)) continue;
    const value = safeNumber(change.value, change.field === "straight_flange_length");
    if (value == null) continue;
    next = {
      ...next,
      heads: next.heads.map((item) =>
        item.head_id === change.target_id
          ? { ...item, [change.field]: value } as Head
          : item
      ),
    };
  }
  return next;
}

export function geometryAgentCurrentValue(
  project: VesselProject,
  change: GeometryAgentChange
): number | string | null {
  if (change.target_type === "vessel") return change.field === "orientation" ? project.orientation : null;
  const item = change.target_type === "shell"
    ? project.shell_sections.find((shell) => shell.section_id === change.target_id)
    : project.heads.find((head) => head.head_id === change.target_id);
  if (!item || !(change.field in item)) return null;
  const value = (item as unknown as Record<string, unknown>)[change.field];
  return typeof value === "number" || typeof value === "string" ? value : null;
}
