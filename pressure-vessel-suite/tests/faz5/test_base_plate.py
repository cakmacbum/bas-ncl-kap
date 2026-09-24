"""Ayak taban plakası — supports/formulas.py (Moss Procedure 4-12 deseni)."""

import math

import pytest

from supports.formulas import (
    base_plate_bearing_pressure,
    base_plate_cantilevers,
    base_plate_required_thickness,
)


def test_bearing_pressure():
    assert base_plate_bearing_pressure(100_000, 250, 200) == pytest.approx(2.0)


def test_cantilevers_channel_hand_calc():
    # m = (250 − 0,95·100)/2 = 77,5 ; n = (200 − 0,80·50)/2 = 80
    m, n = base_plate_cantilevers(250, 200, 100, 50)
    assert (m, n) == (pytest.approx(77.5), pytest.approx(80.0))


def test_cantilevers_reject_profile_larger_than_plate():
    with pytest.raises(ValueError, match="büyük olamaz"):
        base_plate_cantilevers(90, 200, 100, 50)


def test_required_thickness_hand_calc():
    # t = 80·√(3·2/(0,75·235)) = 14,76 mm  (≡ 2c·√(q/Fy))
    t = base_plate_required_thickness(2.0, 80.0, 235.0)
    assert t == pytest.approx(14.76, rel=1e-3)
    assert t == pytest.approx(2 * 80 * math.sqrt(2.0 / 235.0))


def test_required_thickness_stresses_strip_to_allowable():
    # Formülden bağımsız kabul: 1 mm şeritte konsol momenti M = q·c²/2,
    # kesit modülü t²/6 → gerilme tam olarak 0,75·Fy olmalı.
    q, c, Fy = 1.6, 65.0, 250.0
    t = base_plate_required_thickness(q, c, Fy)
    sigma = (q * c**2 / 2) / (t**2 / 6)
    assert sigma == pytest.approx(0.75 * Fy)


@pytest.mark.parametrize("args", [(-1, 50, 235), (1, -5, 235), (1, 50, 0)])
def test_required_thickness_rejects_invalid(args):
    with pytest.raises(ValueError):
        base_plate_required_thickness(*args)
