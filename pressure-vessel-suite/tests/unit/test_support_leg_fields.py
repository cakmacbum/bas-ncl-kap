"""E01 — ayak geometri alanları (facing / ped taşma / başlangıç açısı) Support şemasında."""
import pytest
from pydantic import ValidationError

from domain.geometry import Support

BASE = dict(support_id="LEG-01", type="leg", width_mm=100, height_mm=800, material_id="M")


def test_new_leg_fields_default_none():
    s = Support(**BASE)
    assert s.leg_channel_facing is None
    assert s.leg_pad_top_extension_mm is None
    assert s.leg_start_angle_deg is None


def test_new_leg_fields_accepted():
    s = Support(**BASE, leg_channel_facing="flanges", leg_pad_top_extension_mm=0, leg_start_angle_deg=30)
    assert s.leg_channel_facing == "flanges"
    assert s.leg_pad_top_extension_mm == 0
    assert s.leg_start_angle_deg == 30
    assert Support(**BASE, leg_channel_facing="web").leg_channel_facing == "web"


@pytest.mark.parametrize("bad", [{"leg_channel_facing": "side"}, {"leg_pad_top_extension_mm": -5}])
def test_invalid_leg_fields_rejected(bad):
    with pytest.raises(ValidationError):
        Support(**BASE, **bad)
