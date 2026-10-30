"""zick_tables: ara değerleme ve aralık/boş tablo davranışı (sentetik tablo; gerçek K verisi değil)."""

import pytest

from supports import zick_tables as zt

SYN = {
    "KX": {"source": "sentetik", "verified": False, "theta": [120.0, 180.0],
           "a_over_r": [0.5, 1.0], "values": [[1.0, 2.0], [3.0, 4.0]]},
    "KY": {"source": "sentetik", "theta": [120.0, 150.0, 180.0], "a_over_r": None,
           "values": [[0.0], [10.0], [30.0]]},
}


def test_bilinear_ve_kaynak():
    hit = zt.lookup("KX", 150.0, 0.75, SYN)
    assert hit["value"] == pytest.approx(2.5)
    assert hit["verified"] is False and hit["source"] == "sentetik"


def test_tek_boyutlu_dilim_araligi():
    assert zt.lookup("KY", 165.0, None, SYN)["value"] == pytest.approx(20.0)


@pytest.mark.parametrize("theta,ar", [(119.0, 0.7), (181.0, 0.7), (150.0, 0.4), (150.0, 1.1)])
def test_aralik_disi_hata(theta, ar):
    with pytest.raises(zt.ZickTableError):
        zt.lookup("KX", theta, ar, SYN)


def test_ar_gerekli_ve_tablo_yok():
    with pytest.raises(zt.ZickTableError):
        zt.lookup("KX", 150.0, None, SYN)
    with pytest.raises(zt.ZickTableError):
        zt.lookup("K1", 150.0, 0.5, {})
