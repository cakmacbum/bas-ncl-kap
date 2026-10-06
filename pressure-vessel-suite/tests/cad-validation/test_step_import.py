"""STEP tanıyıcı testleri (M1 / P01) — `cad_engine.step_import.recognize_step`.

K2: tanınan değerler yalnız öneridir. K4: tanınmayan her şey açıkça raporlanır.
Round-trip: suite'in kendi `build_vessel` + `export_step` çıktısı geri tanınır.
"""

import json
import math

import pytest

cq = pytest.importorskip("cadquery", reason="CadQuery kurulu değil — STEP tanıma testleri atlandı")

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    ProductForm,
    ShellSection,
    VesselProject,
)

from cad_engine import recognize_step
from cad_engine import step_import
from cad_engine.vessel_builder import build_vessel, export_step

NOT_IN_FILE = {"material", "design_pressure", "design_temperature", "joint_efficiency", "corrosion_allowance"}


def _project(head_type=HeadType.ELLIPTICAL, nozzles=(), crown=None, knuckle=None):
    """sample_project ile aynı ölçüler: ID 1000, t 12, L 2000, sf 25."""
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0, design_temperature=200.0, minimum_design_temperature=-10.0,
        corrosion_allowance_internal=2.0,
    )
    shell = ShellSection(
        section_id="SHELL-01", inside_diameter=1000.0, tangent_length=2000.0,
        nominal_thickness=12.0, material_id="MAT-01", internal_corrosion_allowance=2.0,
    )
    kw = {}
    if head_type == HeadType.TORISPHERICAL:
        kw = dict(crown_radius=crown or 1000.0, knuckle_radius=knuckle or 100.0)
    heads = [
        Head(head_id=hid, type=head_type, inside_diameter=1000.0, nominal_thickness=12.0,
             material_id="MAT-01", internal_corrosion_allowance=2.0,
             straight_flange_length=25.0, **kw)
        for hid in ("HEAD-L", "HEAD-R")
    ]
    mat = MaterialProperty(
        material_id="MAT-01", standard_pack="x", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )
    return VesselProject(
        project_number="P", project_name="t", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell], heads=heads,
        nozzles=list(nozzles), materials=[mat],
    )


def _export(project, path):
    r = build_vessel(project)
    assert r.success, r.error
    return export_step(r.shape, path)


def _close(actual, expected, rel):
    return math.isclose(actual, expected, rel_tol=rel)


def _assert_contract(d):
    """S-3 şeması: anahtarlar, Field yapısı, not_in_file her zaman dolu, JSON'lanabilir."""
    json.dumps(d)
    assert set(d) == {"status", "source", "shell", "heads", "nozzles", "unrecognized", "warnings", "not_in_file"}
    assert d["status"] in {"RECOGNIZED", "PARTIAL", "REJECTED", "BLOCKED"}
    assert set(d["source"]) == {"filename", "unit", "unit_scale", "solid_count"}
    assert set(d["not_in_file"]) == NOT_IN_FILE
    assert len(d["heads"]) in (0, 2)

    def field(f):
        assert set(f) == {"value", "confidence", "note"}
        assert f["confidence"] in {"high", "medium", "low"}

    if d["shell"] is not None:
        for k in ("inside_diameter", "nominal_thickness", "tangent_length"):
            field(d["shell"][k])
    for h in d["heads"]:
        assert h["side"] in {"left", "right"}
        for k in ("type", "inside_diameter", "nominal_thickness"):
            field(h[k])
        for k in ("straight_flange_length", "crown_radius", "knuckle_radius"):
            if h[k] is not None:
                field(h[k])
    for n in d["nozzles"]:
        for k in ("outside_diameter", "inside_diameter", "neck_thickness", "axial_position",
                  "circumferential_angle", "outside_projection"):
            field(n[k])
    for u in d["unrecognized"]:
        assert set(u) == {"feature", "reason"} and u["reason"]
    if d["status"] == "RECOGNIZED":
        assert d["shell"] and len(d["heads"]) == 2 and not d["unrecognized"]
    if d["status"] == "REJECTED":
        assert d["unrecognized"], "REJECTED sebepsiz olamaz"


# ── Round-trip: gövde + bombe tipleri ────────────────────────────────────────


@pytest.fixture(scope="module")
def stepdir(tmp_path_factory):
    return tmp_path_factory.mktemp("step_import")


@pytest.mark.parametrize(
    "head_type, expected",
    [
        (HeadType.ELLIPTICAL, "elliptical"),
        (HeadType.HEMISPHERICAL, "hemispherical"),
        (HeadType.FLAT, "flat"),
    ],
)
def test_roundtrip_shell_and_heads(stepdir, head_type, expected):
    p = _export(_project(head_type), stepdir / f"rt_{expected}.step")
    rec = recognize_step(p, filename="kap.step")
    d = rec.to_dict()
    _assert_contract(d)

    assert d["status"] == "RECOGNIZED", d["unrecognized"]
    assert d["source"] == {"filename": "kap.step", "unit": "mm", "unit_scale": 1.0, "solid_count": 1}
    sh = d["shell"]
    assert _close(sh["inside_diameter"]["value"], 1000.0, 1e-3)
    assert _close(sh["nominal_thickness"]["value"], 12.0, 1e-3)
    assert _close(sh["tangent_length"]["value"], 2000.0, 1e-3)

    assert [h["side"] for h in d["heads"]] == ["left", "right"]
    for h in d["heads"]:
        assert h["type"]["value"] == expected
        assert _close(h["inside_diameter"]["value"], 1000.0, 1e-3)
        assert _close(h["nominal_thickness"]["value"], 12.0, 1e-3)
        assert h["crown_radius"] is None and h["knuckle_radius"] is None


def test_builder_straight_flange_is_not_in_geometry(stepdir):
    """Dürüstlük: builder bombe eteğini gövde silindirinin içine bindiriyor → sf=25 dosyada
    ayırt edilemez. Uydurma değer önerilmez: güven 'low' + açıklayıcı not (UI'da varsayılan
    işaretsiz)."""
    p = _export(_project(HeadType.ELLIPTICAL), stepdir / "rt_sf.step")
    d = recognize_step(p).to_dict()
    assert d["heads"]
    for h in d["heads"]:
        assert h["straight_flange_length"] is None
    assert any("ayırt edilemez" in w for w in d["warnings"])


def test_builder_torispherical_reported_as_unsupported_ellipse(stepdir):
    """Bilinen tuzak: vessel_builder torisferiği gerçek küre+torus değil, derinliği Rc/rk'den
    hesaplanmış ELİPS olarak çiziyor (h/D ≈ 0.194). Tanıyıcı bunu torisferik diye
    UYDURMAMALI — 'eliptik, desteklenmeyen h/D oranı' olarak raporlamalı."""
    p = _export(_project(HeadType.TORISPHERICAL), stepdir / "rt_tori_builder.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "PARTIAL"
    assert d["heads"] == []
    assert _close(d["shell"]["inside_diameter"]["value"], 1000.0, 1e-3)
    reasons = [u["reason"] for u in d["unrecognized"] if u["feature"] == "head"]
    assert len(reasons) == 2
    assert all("eliptik" in r and "desteklenmeyen h/D" in r and "0.194" in r for r in reasons)


# ── Gerçek torisferik (küre + torus) ─────────────────────────────────────────


def _arc_mid(c, p, q, R):
    ux, uy = (p[0] - c[0]) + (q[0] - c[0]), (p[1] - c[1]) + (q[1] - c[1])
    n = math.hypot(ux, uy)
    return (c[0] + R * ux / n, c[1] + R * uy / n)


def _true_tori_vessel(a=500.0, t=12.0, L=2000.0, Rc=1000.0, rk=100.0):
    """Gerçek torisferik kap: taç küresi + hamut torusu profilinin revolve'u (XZ, eksen Z).

    Yerel profil (r, z): sağ bombe tanjantı z=L, sol bombe tanjantı z=0.
    """
    zc = -math.sqrt((Rc - rk) ** 2 - (a - rk) ** 2)  # taç merkezi, tanjant düzlemine göre

    def head(z_t, s):
        kc = (a - rk, z_t)
        cc = (0.0, z_t + s * zc)
        dx, dy = kc[0] - cc[0], kc[1] - cc[1]
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        out = {}
        for tag, rr_k, rr_c in (("i", rk, Rc), ("o", rk + t, Rc + t)):
            out[tag] = dict(
                eq=(kc[0] + rr_k, z_t),
                tan=(kc[0] + rr_k * ux, kc[1] + rr_k * uy),
                top=(0.0, cc[1] + s * rr_c),
                kc=kc, cc=cc, rk=rr_k, rc=rr_c,
            )
        return out

    R_, L_ = head(L, +1.0), head(0.0, -1.0)
    wp = cq.Workplane("XZ").moveTo(*R_["i"]["top"])

    def arc(wp, c, p, q, r):
        return wp.threePointArc(_arc_mid(c, p, q, r), q)

    # sağ iç: taç → hamut → gövde iç → sol iç hamut → taç
    ri_, li_ = R_["i"], L_["i"]
    wp = arc(wp, ri_["cc"], ri_["top"], ri_["tan"], ri_["rc"])
    wp = arc(wp, ri_["kc"], ri_["tan"], ri_["eq"], ri_["rk"])
    wp = wp.lineTo(*li_["eq"])
    wp = arc(wp, li_["kc"], li_["eq"], li_["tan"], li_["rk"])
    wp = arc(wp, li_["cc"], li_["tan"], li_["top"], li_["rc"])
    # eksen boyunca dışa, sol dış → gövde dış → sağ dış
    lo, ro_ = L_["o"], R_["o"]
    wp = wp.lineTo(*lo["top"])
    wp = arc(wp, lo["cc"], lo["top"], lo["tan"], lo["rc"])
    wp = arc(wp, lo["kc"], lo["tan"], lo["eq"], lo["rk"])
    wp = wp.lineTo(*ro_["eq"])
    wp = arc(wp, ro_["kc"], ro_["eq"], ro_["tan"], ro_["rk"])
    wp = arc(wp, ro_["cc"], ro_["tan"], ro_["top"], ro_["rc"])
    return wp.close().revolve(360, (0, 0, 0), (0, 1, 0))


def test_true_torispherical_crown_and_knuckle(stepdir):
    shape = _true_tori_vessel()
    assert len(shape.solids().vals()) == 1
    p = export_step(shape, stepdir / "true_tori.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "RECOGNIZED", d["unrecognized"]
    assert _close(d["shell"]["inside_diameter"]["value"], 1000.0, 1e-3)
    assert _close(d["shell"]["tangent_length"]["value"], 2000.0, 1e-3)
    for h in d["heads"]:
        assert h["type"]["value"] == "torispherical"
        assert _close(h["crown_radius"]["value"], 1000.0, 5e-3)
        assert _close(h["knuckle_radius"]["value"], 100.0, 5e-3)
        assert _close(h["nominal_thickness"]["value"], 12.0, 1e-3)
        assert _close(h["inside_diameter"]["value"], 1000.0, 1e-3)


# ── Nozullar ─────────────────────────────────────────────────────────────────


def test_radial_shell_nozzles(stepdir):
    """test_cad_nozzle_integration fixture'ı (pedli, flanşlı) + ikinci bir nozul."""
    n1 = Nozzle(
        tag="N1", host_component_id="SHELL-01", axial_position=800,
        circumferential_angle=90, outside_diameter=168.3, inside_diameter=154.1,
        neck_thickness=7.1, material_id="MAT-01", outside_projection=150,
        reinforcement_pad=True, reinforcement_pad_od=300, reinforcement_pad_thickness=10,
    )
    n2 = Nozzle(
        tag="N2", host_component_id="SHELL-01", axial_position=1500,
        circumferential_angle=210, outside_diameter=114.3, inside_diameter=102.3,
        neck_thickness=6.0, material_id="MAT-01", outside_projection=200,
    )
    p = _export(_project(nozzles=[n2, n1]), stepdir / "nozzles.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "RECOGNIZED", d["unrecognized"]
    noz = d["nozzles"]
    assert [n["tag"] for n in noz] == ["N1", "N2"]  # eksenel konuma göre sıralı
    for got, src in zip(noz, (n1, n2)):
        assert _close(got["outside_diameter"]["value"], src.outside_diameter, 1e-3)
        assert _close(got["inside_diameter"]["value"], src.inside_diameter, 1e-3)
        assert got["neck_thickness"]["value"] == pytest.approx(
            (src.outside_diameter - src.inside_diameter) / 2, abs=0.02
        )
        assert got["axial_position"]["value"] == pytest.approx(src.axial_position, abs=0.5)
        assert got["circumferential_angle"]["value"] == pytest.approx(src.circumferential_angle, abs=0.1)
        assert got["circumferential_angle"]["confidence"] == "high"
        # Flanş yüzüne kadar ölçülür → girdi değerinden biraz büyük olabilir
        assert src.outside_projection - 0.5 <= got["outside_projection"]["value"] <= src.outside_projection + 15
    # Pedli/flanşlı nozulda ek silindirler not edilir
    assert noz[0]["outside_diameter"]["note"]


def test_head_nozzle_is_unrecognized_not_silently_dropped(stepdir):
    noz = Nozzle(
        tag="NH", host_component_id="HEAD-L", axial_position=0,
        outside_diameter=100, inside_diameter=90, neck_thickness=5,
        material_id="MAT-01", outside_projection=120,
    )
    p = _export(_project(nozzles=[noz]), stepdir / "head_nozzle.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "PARTIAL"
    assert any(u["feature"] == "head_nozzle" for u in d["unrecognized"])
    assert d["nozzles"] == []
    assert _close(d["shell"]["inside_diameter"]["value"], 1000.0, 1e-3)


# ── Ret / kısmi vakalar ──────────────────────────────────────────────────────


def test_reject_box(stepdir):
    p = export_step(cq.Workplane("XY").box(500, 500, 500), stepdir / "box.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "REJECTED"
    assert d["shell"] is None
    assert "Silindirik gövde bulunamadı" in d["unrecognized"][0]["reason"]


def test_reject_two_solids(stepdir):
    a = cq.Workplane("XY").circle(500).circle(488).extrude(1000).val()
    b = cq.Workplane("XY").workplane(offset=2000).circle(500).circle(488).extrude(1000).val()
    p = export_step(cq.Compound.makeCompound([a, b]), stepdir / "two.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "REJECTED"
    assert d["source"]["solid_count"] == 2
    assert "2 ayrı katı" in d["unrecognized"][0]["reason"]


def test_reject_thickless_surface(stepdir):
    """Kalınlıksız kabuk: yalnız silindir yüzeyi (katı yok)."""
    side = cq.Workplane("XY").circle(500).extrude(2000).val().Faces()
    surf = cq.Shell.makeShell([f for f in side if f.geomType() == "CYLINDER"])
    p = export_step(surf, stepdir / "surface.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "REJECTED"
    assert d["source"]["solid_count"] == 0
    assert "kalınlıksız" in d["unrecognized"][0]["reason"]


def test_reject_corrupt_and_non_step(tmp_path):
    bad = tmp_path / "bozuk.step"
    bad.write_text("ISO-10303-21;\nHEADER;\nbu bir STEP değil @@@\n", encoding="utf-8")
    d = recognize_step(bad).to_dict()
    _assert_contract(d)
    assert d["status"] == "REJECTED"

    txt = tmp_path / "not.step"
    txt.write_text("merhaba", encoding="utf-8")
    d2 = recognize_step(txt).to_dict()
    _assert_contract(d2)
    assert d2["status"] == "REJECTED"
    assert "ISO-10303-21" in d2["unrecognized"][0]["reason"]

    d3 = recognize_step(tmp_path / "yok.step").to_dict()
    _assert_contract(d3)
    assert d3["status"] == "REJECTED"


def test_conical_heads_are_partial(stepdir):
    """Koni V1 dışı → gövde tanınır, koni `unrecognized` (PARTIAL)."""
    a, t, L, h = 500.0, 12.0, 2000.0, 300.0
    prof = (
        cq.Workplane("XZ")
        .polyline([(0, L + h), (a, L), (a, 0), (0, -h), (0, -h - t * 1.2),
                   (a + t, 0), (a + t, L), (0, L + h + t * 1.2)])
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    p = export_step(prof, stepdir / "cone.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert d["status"] == "PARTIAL"
    assert d["heads"] == []
    assert any(u["feature"] == "cone" for u in d["unrecognized"])
    assert _close(d["shell"]["inside_diameter"]["value"], 1000.0, 1e-3)


# ── Birim, eksen, BLOCKED ────────────────────────────────────────────────────


def test_unit_read_from_file(stepdir, tmp_path):
    """Birim dosyadan okunur: aynı sayılar METRE ile yazılırsa değerler ×1000 mm olur."""
    p = _export(_project(), stepdir / "unit_mm.step")
    text = open(p, encoding="latin-1").read()
    assert "SI_UNIT(.MILLI.,.METRE.)" in text
    pm = tmp_path / "unit_m.step"
    pm.write_text(text.replace("SI_UNIT(.MILLI.,.METRE.)", "SI_UNIT($,.METRE.)"), encoding="latin-1")
    d = recognize_step(pm).to_dict()
    _assert_contract(d)
    assert d["source"]["unit"] == "m" and d["source"]["unit_scale"] == 1000.0
    assert _close(d["shell"]["inside_diameter"]["value"], 1000.0 * 1000.0, 1e-3)


def test_non_z_axis_lowers_theta_confidence(stepdir):
    noz = Nozzle(
        tag="N1", host_component_id="SHELL-01", axial_position=800,
        circumferential_angle=90, outside_diameter=168.3, inside_diameter=154.1,
        neck_thickness=7.1, material_id="MAT-01", outside_projection=150,
    )
    r = build_vessel(_project(nozzles=[noz]))
    rotated = r.shape.rotate((0, 0, 0), (0, 1, 0), 90)  # eksen → X
    p = export_step(rotated, stepdir / "axis_x.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert _close(d["shell"]["tangent_length"]["value"], 2000.0, 1e-3)
    assert d["nozzles"][0]["circumferential_angle"]["confidence"] == "low"
    assert any("θ" in w for w in d["warnings"])


def test_blocked_without_cad_kernel(monkeypatch, tmp_path):
    monkeypatch.setattr(step_import, "CAD_KERNEL_AVAILABLE", False)
    d = recognize_step(tmp_path / "x.step", filename="x.step").to_dict()
    _assert_contract(d)
    assert d["status"] == "BLOCKED"
    assert d["source"]["filename"] == "x.step"


# ── Düz flanş üst sınırı (course dikişi) ve hata metni sızıntısı (P05) ──────


def _hemi_vessel_with_seams(seams, a=500.0, t=12.0, L=6000.0):
    """Yarım küre bombeli kap; iç gövde silindiri verilen z'lerde dikişle bölünür
    (çok parçalı/course gövde). clean=False → dikişler birleştirilmez."""
    s2 = math.sqrt(0.5)
    wp = cq.Workplane("XZ").moveTo(0.0, L + a)
    wp = wp.threePointArc((a * s2, L + a * s2), (a, L))
    for z in sorted(seams, reverse=True):
        wp = wp.lineTo(a, z)
    wp = wp.lineTo(a, 0.0)
    wp = wp.threePointArc((a * s2, -a * s2), (0.0, -a))
    b = a + t
    wp = wp.lineTo(0.0, -b)
    wp = wp.threePointArc((b * s2, -b * s2), (b, 0.0))
    wp = wp.lineTo(b, L)
    wp = wp.threePointArc((b * s2, L + b * s2), (0.0, L + b))
    return wp.close().revolve(360, (0, 0, 0), (0, 1, 0), clean=False)


def test_course_seam_is_not_straight_flange(stepdir):
    """Sol uçtan 1000 mm'deki course dikişi (eski kural: ≤0.25·L → sf=1000 önerirdi) düz
    flanş SAYILMAZ: alan null + sebep uyarıda. Sağdaki 40 mm dikiş sf olarak önerilir."""
    L = 6000.0
    shape = _hemi_vessel_with_seams([1000.0, L - 40.0], L=L)
    p = export_step(shape, stepdir / "courses.step")
    d = recognize_step(p).to_dict()
    _assert_contract(d)
    assert _close(d["shell"]["tangent_length"]["value"], L, 1e-3)
    heads = {h["side"]: h for h in d["heads"]}
    assert set(heads) == {"left", "right"}, d["unrecognized"]
    assert heads["left"]["straight_flange_length"] is None
    assert any("course" in w and "Sol" in w for w in d["warnings"])
    sf_r = heads["right"]["straight_flange_length"]
    assert sf_r is not None and _close(sf_r["value"], 40.0, 1e-3)
    assert sf_r["confidence"] == "medium"


def test_unexpected_error_reason_has_no_path_or_exception(monkeypatch, tmp_path):
    secret = tmp_path / "gizli-klasor" / "x.step"

    def _boom(path, source):
        raise RuntimeError(f"OCC patladı: {secret}")

    monkeypatch.setattr(step_import, "_recognize", _boom)
    d = recognize_step(secret, filename="x.step").to_dict()
    assert d["status"] == "REJECTED"
    reason = d["unrecognized"][0]["reason"]
    assert "gizli-klasor" not in reason and "RuntimeError" not in reason and "patladı" not in reason


def test_read_error_reason_has_no_path(monkeypatch, tmp_path):
    f = tmp_path / "gizli-klasor" / "x.step"
    f.parent.mkdir()
    f.write_bytes(b"ISO-10303-21;\n")

    def _deny(self):
        raise PermissionError(13, "Erişim engellendi", str(self))

    monkeypatch.setattr(step_import.Path, "read_bytes", _deny)
    d = recognize_step(f, filename="x.step").to_dict()
    assert d["status"] == "REJECTED"
    reason = d["unrecognized"][0]["reason"]
    assert reason == "Dosya okunamadı."
    assert "gizli-klasor" not in json.dumps(d)
