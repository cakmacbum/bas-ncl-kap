import pytest

from domain import calculate_seismic_load, calculate_wind_load


def test_wind_resultant_and_base_moment_are_deterministic():
    result = calculate_wind_load(
        wind_speed_m_s=40.0,
        projected_width_m=2.0,
        exposed_height_m=10.0,
        drag_coefficient=1.0,
        gust_factor=1.0,
        directionality_factor=1.0,
    )
    assert result.projected_area_m2 == pytest.approx(20.0)
    assert result.dynamic_pressure_pa == pytest.approx(980.0)
    assert result.force_n == pytest.approx(19_600.0)
    assert result.moment_n_m == pytest.approx(98_000.0)
    assert "Code/site gust and exposure verification required" in result.assumptions


def test_seismic_equivalent_static_shear_and_moment():
    result = calculate_seismic_load(
        weight_n=100_000.0,
        seismic_acceleration_g=0.3,
        center_of_mass_elevation_m=5.0,
        importance_factor=1.5,
        response_reduction_factor=3.0,
    )
    assert result.seismic_coefficient == pytest.approx(0.15)
    assert result.base_shear_n == pytest.approx(15_000.0)
    assert result.moment_n_m == pytest.approx(75_000.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"wind_speed_m_s": 0, "projected_width_m": 1, "exposed_height_m": 1},
        {"wind_speed_m_s": 1, "projected_width_m": 0, "exposed_height_m": 1},
    ],
)
def test_wind_rejects_non_physical_inputs(kwargs):
    with pytest.raises(ValueError):
        calculate_wind_load(**kwargs)


def test_seismic_rejects_zero_response_factor():
    with pytest.raises(ValueError):
        calculate_seismic_load(
            weight_n=1_000,
            seismic_acceleration_g=0.2,
            center_of_mass_elevation_m=1,
            response_reduction_factor=0,
        )
