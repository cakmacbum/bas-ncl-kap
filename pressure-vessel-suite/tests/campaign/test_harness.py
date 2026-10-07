import json

import pytest
from domain import VesselProject

from tools.campaign.aggregate import aggregate
from tools.campaign.bases import horizontal_saddle_tank, skirt_column, vertical_leg_tank, with_code
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of


@pytest.mark.parametrize("factory", [vertical_leg_tank, horizontal_saddle_tank, skirt_column])
def test_base_tanks_validate_and_calculate(factory):
    project = factory()
    VesselProject.model_validate(project)
    result = run_case(project)
    assert result["ok"], result["error"]


def test_ug27_lookup_and_published_v01():
    project = vertical_leg_tank(design_conditions={"design_pressure": 125 * 0.006894757293168361,
                                "corrosion_allowance_internal": 0},
                                shell_sections=[{"section_id": "SHELL-01", "inside_diameter": 812.8,
                                  "tangent_length": 2000, "nominal_thickness": 12, "material_id": "M1",
                                  "weld_joint_id": "WJ-01", "internal_corrosion_allowance": 0,
                                  "mill_tolerance": 0}])
    project["materials"][0]["allowable_stress"] = 20000 * 0.006894757293168361
    result = run_case(project)
    assert result["ok"], result["error"]
    rows = find_results(result["payload"], component_id="SHELL-01", clause_prefix="UG-27")
    assert rows
    thickness = value_of(rows[0], "t_circ")
    assert thickness is not None
    expected = 0.1004 * 25.4
    assert abs(thickness - expected) / expected <= 0.01


def test_compare_and_aggregate(tmp_path):
    diff, verdict = judge(10.05, 10, rel_tol=.01)
    assert verdict == "DOĞRULANDI" and diff == pytest.approx(.5)
    assert judge(None, None)[1] == "KAYNAK_BEKLİYOR"
    assert judge(1, 1, suite_status="REVIEW")[1] == "KAPSAM_DIŞI"
    source = tmp_path / "families"; (source / "f01").mkdir(parents=True); (source / "f02").mkdir()
    item = CaseResult("C1", "F01", {}, "t", "mm", 1, 1, "oracle", 0, "DOĞRULANDI")
    write_results(source / "f01", "F01", [item], {})
    write_results(source / "f02", "F02", [item], {})
    md, csv = aggregate(source, tmp_path / "out")
    assert md.exists() and csv.exists()
    assert "Toplam vaka: 2" in md.read_text(encoding="utf-8")
