"""Nozul Schedule üretimi — rapora girer (kaynak §6)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from domain.geometry import Nozzle
from domain.project import VesselProject


@dataclass
class NozzleScheduleEntry:
    """Nozul schedule kalemi."""

    tag: str
    nozzle_type: str
    host_component: str
    axial_position_mm: float
    circumferential_angle_deg: float
    outside_diameter_mm: float
    inside_diameter_mm: float
    neck_thickness_mm: float
    inside_projection_mm: float
    outside_projection_mm: float
    has_reinforcement_pad: bool
    material_id: str

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "nozzle_type": self.nozzle_type,
            "host_component": self.host_component,
            "axial_position_mm": self.axial_position_mm,
            "circumferential_angle_deg": self.circumferential_angle_deg,
            "outside_diameter_mm": self.outside_diameter_mm,
            "inside_diameter_mm": self.inside_diameter_mm,
            "neck_thickness_mm": self.neck_thickness_mm,
            "inside_projection_mm": self.inside_projection_mm,
            "outside_projection_mm": self.outside_projection_mm,
            "has_reinforcement_pad": self.has_reinforcement_pad,
            "material_id": self.material_id,
        }

    def to_html_row(self) -> str:
        return f"""
<tr>
<td>{self.tag}</td>
<td>{self.nozzle_type}</td>
<td>{self.host_component}</td>
<td>{self.axial_position_mm:.0f}</td>
<td>{self.circumferential_angle_deg:.0f}°</td>
<td>{self.outside_diameter_mm:.1f}</td>
<td>{self.inside_diameter_mm:.1f}</td>
<td>{self.neck_thickness_mm:.1f}</td>
<td>{'Evet' if self.has_reinforcement_pad else 'Hayır'}</td>
<td>{self.material_id}</td>
</tr>"""


def generate_nozzle_schedule(project: VesselProject) -> List[NozzleScheduleEntry]:
    """Projeden nozul schedule üret.

    Args:
        project: VesselProject.

    Returns:
        NozzleScheduleEntry listesi.
    """
    entries = []
    for n in project.nozzles:
        entry = NozzleScheduleEntry(
            tag=n.tag,
            nozzle_type=n.nozzle_type.value,
            host_component=n.host_component_id,
            axial_position_mm=n.axial_position,
            circumferential_angle_deg=n.circumferential_angle,
            outside_diameter_mm=n.outside_diameter,
            inside_diameter_mm=n.inside_diameter,
            neck_thickness_mm=n.neck_thickness,
            inside_projection_mm=n.inside_projection,
            outside_projection_mm=n.outside_projection,
            has_reinforcement_pad=n.reinforcement_pad,
            material_id=n.material_id,
        )
        entries.append(entry)
    return entries


__all__ = ["NozzleScheduleEntry", "generate_nozzle_schedule"]
