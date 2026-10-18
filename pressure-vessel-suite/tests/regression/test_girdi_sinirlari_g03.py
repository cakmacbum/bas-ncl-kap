"""G-03: anlamsız tasarım koşulu girdileri 422 ile reddedilir (200 PASS/FAIL dönmez)."""
import pytest
from pydantic import ValidationError

from domain.conditions import DesignConditions

_OK = dict(operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.2,
           operating_temperature=20, design_temperature=100, minimum_design_temperature=-10)


def test_makul_girdi_kabul_edilir():
    assert DesignConditions(**_OK).design_pressure == 1.2


@pytest.mark.parametrize("alan,deger", [
    ("design_pressure", 1e9), ("operating_pressure", 1e9), ("maximum_allowable_pressure_ps", 1e9),
    ("design_pressure", float("inf")), ("design_pressure", float("nan")),
    ("design_temperature", 1e6), ("design_temperature", float("nan")),
    ("minimum_design_temperature", -1000.0),
    ("external_pressure", 1e9), ("corrosion_allowance_internal", 1e9),
    ("corrosion_allowance_external", 1e9), ("fluid_density_kg_m3", 1e12),
    ("liquid_level_mm", 1e12),
])
def test_anlamsiz_girdi_reddedilir(alan, deger):
    with pytest.raises(ValidationError):
        DesignConditions(**{**_OK, alan: deger})
