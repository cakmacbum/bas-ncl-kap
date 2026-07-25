"""Birim dönüşümleri — birim testleri."""

import pytest

from units import (
    AreaUnit,
    LengthUnit,
    PressureUnit,
    TemperatureUnit,
    VolumeUnit,
    convert_area,
    convert_length,
    convert_pressure,
    convert_temperature,
    convert_volume,
    relative_tolerance,
    round_down_to_nearest,
    round_to,
    round_up_to_nearest,
    within_tolerance,
)


# ── Basınç dönüşümleri ────────────────────────────────────────────────────────

class TestPressureConversion:
    """Basınç birimi dönüşüm testleri."""

    def test_bar_to_mpa(self):
        assert relative_tolerance(convert_pressure(1.0, PressureUnit.BAR, PressureUnit.MPA), 0.1)

    def test_mpa_to_bar(self):
        assert relative_tolerance(convert_pressure(1.0, PressureUnit.MPA, PressureUnit.BAR), 10.0)

    def test_psi_to_mpa(self):
        # 14.6959 psi ≈ 0.101325 MPa (1 atm)
        result = convert_pressure(14.6959, PressureUnit.PSI, PressureUnit.MPA)
        assert relative_tolerance(result, 0.101325, 0.01)

    def test_mpa_to_psi(self):
        result = convert_pressure(1.0, PressureUnit.MPA, PressureUnit.PSI)
        assert relative_tolerance(result, 145.038, 0.001)

    def test_bar_to_psi(self):
        result = convert_pressure(1.0, PressureUnit.BAR, PressureUnit.PSI)
        assert relative_tolerance(result, 14.5038, 0.001)

    def test_kpa_to_mpa(self):
        assert relative_tolerance(convert_pressure(1000.0, PressureUnit.KPA, PressureUnit.MPA), 1.0)

    def test_atm_to_mpa(self):
        result = convert_pressure(1.0, PressureUnit.ATM, PressureUnit.MPA)
        assert relative_tolerance(result, 0.101325)

    def test_pa_to_mpa(self):
        assert relative_tolerance(convert_pressure(1_000_000.0, PressureUnit.PA, PressureUnit.MPA), 1.0)

    def test_roundtrip_bar_mpa_bar(self):
        original = 2.5
        result = convert_pressure(
            convert_pressure(original, PressureUnit.BAR, PressureUnit.MPA),
            PressureUnit.MPA,
            PressureUnit.BAR,
        )
        assert relative_tolerance(result, original)

    def test_roundtrip_psi_mpa_psi(self):
        original = 3000.0
        result = convert_pressure(
            convert_pressure(original, PressureUnit.PSI, PressureUnit.MPA),
            PressureUnit.MPA,
            PressureUnit.PSI,
        )
        assert relative_tolerance(result, original)

    def test_same_unit(self):
        assert convert_pressure(5.0, PressureUnit.MPA, PressureUnit.MPA) == 5.0


# ── Sıcaklık dönüşümleri ──────────────────────────────────────────────────────

class TestTemperatureConversion:
    """Sıcaklık birimi dönüşüm testleri."""

    def test_celsius_to_kelvin(self):
        assert relative_tolerance(convert_temperature(0.0, TemperatureUnit.C, TemperatureUnit.K), 273.15)

    def test_kelvin_to_celsius(self):
        assert relative_tolerance(convert_temperature(273.15, TemperatureUnit.K, TemperatureUnit.C), 0.0)

    def test_celsius_to_fahrenheit(self):
        assert relative_tolerance(convert_temperature(100.0, TemperatureUnit.C, TemperatureUnit.F), 212.0)

    def test_fahrenheit_to_celsius(self):
        assert relative_tolerance(convert_temperature(32.0, TemperatureUnit.F, TemperatureUnit.C), 0.0)

    def test_fahrenheit_to_kelvin(self):
        result = convert_temperature(32.0, TemperatureUnit.F, TemperatureUnit.K)
        assert relative_tolerance(result, 273.15)

    def test_roundtrip_c_f_c(self):
        original = 150.0
        result = convert_temperature(
            convert_temperature(original, TemperatureUnit.C, TemperatureUnit.F),
            TemperatureUnit.F,
            TemperatureUnit.C,
        )
        assert relative_tolerance(result, original)

    def test_same_unit(self):
        assert convert_temperature(100.0, TemperatureUnit.C, TemperatureUnit.C) == 100.0


# ── Uzunluk dönüşümleri ───────────────────────────────────────────────────────

class TestLengthConversion:
    """Uzunluk birimi dönüşüm testleri."""

    def test_mm_to_in(self):
        assert relative_tolerance(convert_length(25.4, LengthUnit.MM, LengthUnit.IN), 1.0)

    def test_in_to_mm(self):
        assert relative_tolerance(convert_length(1.0, LengthUnit.IN, LengthUnit.MM), 25.4)

    def test_m_to_mm(self):
        assert relative_tolerance(convert_length(1.0, LengthUnit.M, LengthUnit.MM), 1000.0)

    def test_mm_to_m(self):
        assert relative_tolerance(convert_length(1000.0, LengthUnit.MM, LengthUnit.M), 1.0)

    def test_ft_to_mm(self):
        result = convert_length(1.0, LengthUnit.FT, LengthUnit.MM)
        assert relative_tolerance(result, 304.8)

    def test_same_unit(self):
        assert convert_length(100.0, LengthUnit.MM, LengthUnit.MM) == 100.0


# ── Alan dönüşümleri ──────────────────────────────────────────────────────────

class TestAreaConversion:
    """Alan birimi dönüşüm testleri."""

    def test_mm2_to_in2(self):
        result = convert_area(645.16, AreaUnit.MM2, AreaUnit.IN2)
        assert relative_tolerance(result, 1.0)

    def test_in2_to_mm2(self):
        result = convert_area(1.0, AreaUnit.IN2, AreaUnit.MM2)
        assert relative_tolerance(result, 645.16)

    def test_m2_to_mm2(self):
        assert relative_tolerance(convert_area(1.0, AreaUnit.M2, AreaUnit.MM2), 1e6)


# ── Hacim dönüşümleri ─────────────────────────────────────────────────────────

class TestVolumeConversion:
    """Hacim birimi dönüşüm testleri."""

    def test_l_to_mm3(self):
        assert relative_tolerance(convert_volume(1.0, VolumeUnit.L, VolumeUnit.MM3), 1e6)

    def test_mm3_to_l(self):
        assert relative_tolerance(convert_volume(1e6, VolumeUnit.MM3, VolumeUnit.L), 1.0)

    def test_m3_to_l(self):
        assert relative_tolerance(convert_volume(1.0, VolumeUnit.M3, VolumeUnit.L), 1000.0)

    def test_in3_to_mm3(self):
        result = convert_volume(1.0, VolumeUnit.IN3, VolumeUnit.MM3)
        assert relative_tolerance(result, 16387.064, 0.001)


# ── Yuvarlama ─────────────────────────────────────────────────────────────────

class TestRounding:
    """Yuvarlama yardımcı testleri."""

    def test_round_to_decimals(self):
        assert round_to(3.456, 2) == 3.46
        assert round_to(3.454, 2) == 3.45
        assert round_to(3.456, 0) == 3.0

    def test_round_up_to_nearest_half(self):
        assert round_up_to_nearest(7.01, 0.5) == 7.5
        assert round_up_to_nearest(7.5, 0.5) == 7.5
        assert round_up_to_nearest(7.51, 0.5) == 8.0

    def test_round_up_to_nearest_1(self):
        assert round_up_to_nearest(7.1, 1.0) == 8.0
        assert round_up_to_nearest(8.0, 1.0) == 8.0

    def test_round_down_to_nearest(self):
        assert round_down_to_nearest(7.9, 1.0) == 7.0
        assert round_down_to_nearest(7.0, 1.0) == 7.0

    def test_round_up_invalid_step(self):
        with pytest.raises(ValueError):
            round_up_to_nearest(5.0, 0.0)


# ── Tolerans ──────────────────────────────────────────────────────────────────

class TestTolerance:
    """Tolerans kontrol testleri."""

    def test_within_tolerance_pass(self):
        assert within_tolerance(10.0, 10.0, 0.1) is True

    def test_within_tolerance_fail(self):
        assert within_tolerance(10.2, 10.0, 0.1) is False

    def test_relative_tolerance_pass(self):
        assert relative_tolerance(100.0, 100.0, 0.01) is True

    def test_relative_tolerance_fail(self):
        assert relative_tolerance(102.0, 100.0, 0.01) is False

    def test_relative_tolerance_zero_expected(self):
        assert relative_tolerance(0.001, 0.0, 0.01) is True
        assert relative_tolerance(0.02, 0.0, 0.01) is False
