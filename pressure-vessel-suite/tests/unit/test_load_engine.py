import pytest

from calc_core import aggregate_load_case, combine_load_cases, governing_state
from domain import ExternalLoad, LoadCase, LoadCombination, LoadType


def test_aggregate_transfers_moment_to_base_and_preserves_components():
    case = LoadCase(
        load_case_id="W-1", name="wind", load_type=LoadType.WIND,
        external_loads=[ExternalLoad(
            load_id="L1", fx_n=1000, fy_n=2000, fz_n=-5000,
            mx_nmm=10, my_nmm=20, elevation_mm=3000,
        )],
    )
    state = aggregate_load_case(case)
    assert state.axial_force_n == -5000
    assert state.shear_x_n == 1000
    assert state.shear_y_n == 2000
    assert state.overturning_moment_x_nmm == -5_999_990
    assert state.overturning_moment_y_nmm == 3_000_020
    assert state.assumptions


def test_combination_rejects_missing_case_and_unknown_factor():
    case = LoadCase(load_case_id="A", name="A", load_type=LoadType.DEAD_WEIGHT)
    with pytest.raises(ValueError, match="missing cases"):
        combine_load_cases({}, LoadCombination(combination_id="C", name="C", load_case_ids=["A"]))
    with pytest.raises(ValueError, match="unknown cases"):
        combine_load_cases({"A": case}, LoadCombination(
            combination_id="C", name="C", load_case_ids=["A"], load_factors={"B": 1.0}
        ))


def test_combination_applies_factors_and_governing_state():
    a = LoadCase(load_case_id="A", name="A", load_type=LoadType.DEAD_WEIGHT,
                 external_loads=[ExternalLoad(load_id="a", fx_n=10)])
    b = LoadCase(load_case_id="B", name="B", load_type=LoadType.WIND,
                 external_loads=[ExternalLoad(load_id="b", fx_n=30)])
    state = combine_load_cases(
        {"A": a, "B": b},
        LoadCombination(combination_id="C", name="C", load_case_ids=["A", "B"], load_factors={"A": 1.5, "B": 2.0}),
    )
    assert state.shear_x_n == 75
    assert governing_state([state]) is state


def test_combination_rejects_non_concurrent_test_and_wind():
    hydro = LoadCase(load_case_id="H", name="hydro", load_type=LoadType.HYDROTEST)
    wind = LoadCase(load_case_id="W", name="wind", load_type=LoadType.WIND)
    with pytest.raises(ValueError, match="Non-concurrent"):
        combine_load_cases(
            {"H": hydro, "W": wind},
            LoadCombination(combination_id="bad", name="bad", load_case_ids=["H", "W"]),
        )
