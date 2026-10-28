"""Nozzle.rating_class / coupling_form — opsiyonel geometri alanları (D00 §2).

Hesaba girmezler; amaç PUT/GET roundtrip'te sessizce silinmemeleri
(Pydantic `extra="ignore"`) ve eski dosyaların bozulmaması.
"""

import pytest
from pydantic import ValidationError

from domain import Nozzle


def _nozzle(**kwargs) -> Nozzle:
    data = dict(
        tag="C1",
        nozzle_type="coupling",
        host_component_id="SHELL-01",
        axial_position=500.0,
        outside_diameter=44.0,
        inside_diameter=26.6,
        neck_thickness=8.7,
        material_id="MAT-01",
    )
    data.update(kwargs)
    return Nozzle(**data)


def test_defaults_none_for_old_files():
    nz = _nozzle()
    assert nz.rating_class is None
    assert nz.coupling_form is None


@pytest.mark.parametrize(
    "rating, form",
    [("3000#", "full"), ("6000#", "half"), ("3000#", "weldolet"), ("CL150", None), ("CL2500", None)],
)
def test_roundtrip_preserves_fields(rating, form):
    nz = _nozzle(rating_class=rating, coupling_form=form)
    dumped = nz.model_dump(mode="json")
    assert dumped["rating_class"] == rating
    assert dumped["coupling_form"] == form
    again = Nozzle.model_validate_json(nz.model_dump_json())
    assert again.rating_class == rating
    assert again.coupling_form == form
    assert again == nz


@pytest.mark.parametrize("bad", ["150", "CL400", "cl150", "3000", "PN16", ""])
def test_rating_class_regex_rejects(bad):
    with pytest.raises(ValidationError):
        _nozzle(rating_class=bad)


def test_coupling_form_literal_rejects():
    with pytest.raises(ValidationError):
        _nozzle(coupling_form="quarter")
