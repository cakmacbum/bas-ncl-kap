"""Bombe nozul konumu — K4: sessiz kırpma yok, kapsam dışı konum OUT_OF_HOST."""

import pytest

from domain import Head, Nozzle
from domain.enums import HeadType
from nozzles import calculate_nozzle_position_on_head

HEAD = Head(
    head_id="HEAD-L", type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
    nominal_thickness=12.0, material_id="MAT-01", weld_joint_id="WJ-02",
)  # b = 250


def _nz(**kw):
    d = dict(tag="NH", host_component_id="HEAD-L", axial_position=0.0,
             outside_diameter=100.0, inside_diameter=80.0, neck_thickness=10.0,
             material_id="MAT-01")
    d.update(kw)
    return Nozzle(**d)


@pytest.mark.parametrize("ax", [0.0, 100.0, 250.0])
def test_axial_within_bounds_ok(ax):
    pos = calculate_nozzle_position_on_head(_nz(axial_position=ax), HEAD)
    assert pos.host_type == "head"


@pytest.mark.parametrize("ax", [-0.1, -50.0])
def test_negative_axial_out_of_host_raises(ax):
    # Model negatif axial'ı zaten reddeder; fonksiyon savunması model_construct ile sınanır.
    nz = Nozzle.model_construct(**{**_nz().model_dump(), "axial_position": ax})
    with pytest.raises(ValueError, match="OUT_OF_HOST"):
        calculate_nozzle_position_on_head(nz, HEAD)


@pytest.mark.parametrize("ax", [250.1, 400.0])
def test_axial_out_of_host_raises(ax):
    with pytest.raises(ValueError, match="OUT_OF_HOST"):
        calculate_nozzle_position_on_head(_nz(axial_position=ax), HEAD)


def test_diameter_over_di_raises():
    with pytest.raises(ValueError, match="OUT_OF_HOST"):
        calculate_nozzle_position_on_head(_nz(head_position_diameter=1200.0), HEAD)


def test_diameter_equal_di_ok():
    calculate_nozzle_position_on_head(_nz(head_position_diameter=1000.0), HEAD)
