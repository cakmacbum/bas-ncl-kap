"""UG-36(c)(3)(-a) küçük açıklık muafiyeti testleri.

Kural özeti (kendi cümlelerimizle): hızlı basınç dalgalanmasına maruz olmayan
kapta, kaynaklı bağlantıda bitmiş açıklık; host gerekli kalınlığı ≤ 10 mm ise
≤ 89 mm, > 10 mm ise ≤ 60 mm olduğunda ek takviye gerekmez. Dalgalanma ve
komşu açıklık aralığı koşulları program tarafından doğrulanamaz → kullanıcı
beyanları (`no_rapid_pressure_fluctuation_confirmed`,
`opening_spacing_confirmed`, `welded_attachment_confirmed`)
olmadan muafiyet uygulanmaz.

Bitmiş açıklık muhafazakâr yorumla max(ID + 2·CA_nozul, OD) / cosα alınır
(standarttaki tanım programda doğrulanmadı); testlerdeki sınırlar bu değere göredir.
"""

from dataclasses import replace

import pytest

from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import (
    CalculationStatus,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    NozzleType,
    ShellSection,
)
from domain.enums import ProductForm
from nozzles.reinforcement import (
    NozzleReinforcementInput,
    build_reinforcement_calculation_result,
    calculate_reinforcement,
    evaluate_ug36c3_size,
)


def _inp(**over) -> NozzleReinforcementInput:
    """Alanı YETERSİZ küçük açıklık, muaf sınırında.

    ID 79 + 2·CA(0) = 79, OD 89 (= ID + 2·tn) → bitmiş açıklık max(79, 89) = 89 mm
    (tr = 10.0 mm, CA = 0 → sınır 89 mm).
    """
    base = dict(
        nozzle_tag="N-S",
        nozzle_inside_diameter=79.0,
        nozzle_outside_diameter=89.0,
        nozzle_neck_thickness=5.0,
        nozzle_corrosion_allowance=0.0,
        nozzle_projection_outside=100.0,
        nozzle_projection_inside=0.0,
        nozzle_allowable_stress=138.0,
        component_type="shell",
        component_inside_diameter=1000.0,
        component_nominal_thickness=12.0,
        component_corrosion_allowance=0.0,
        component_required_thickness=10.0,
        component_allowable_stress=138.0,
        design_pressure=1.2,
        design_temperature=200.0,
    )
    base.update(over)
    return NozzleReinforcementInput(**base)


def _confirmed(**over) -> dict:
    d = dict(
        no_rapid_pressure_fluctuation_confirmed=True,
        opening_spacing_confirmed=True,
        welded_attachment_confirmed=True,
    )
    d.update(over)
    return d


def _iv(res, name):
    return next(float(i["value"]) for i in res.intermediate_values if i.get("name") == name)


# ── Taban: fixture gerçekten alan-yetersiz mi ────────────────────────────────

def test_fixture_fails_area_replacement_without_declaration():
    r = calculate_reinforcement(_inp())
    assert r.status == CalculationStatus.FAIL
    assert r.total_available_area < r.required_area
    assert r.limits["neck_thickness_adequate"] is True


# ── A) Aday değil ────────────────────────────────────────────────────────────

def test_not_candidate_just_above_89_even_if_confirmed():
    # OD 89.1 yönetir (ID 79.1 + 2·5) → bitmiş açıklık 89.1 > 89
    inp = _inp(nozzle_inside_diameter=79.1, nozzle_outside_diameter=89.1,
               **_confirmed())
    r = calculate_reinforcement(inp)
    assert r.ug36c3_candidate is False
    assert r.ug36c3_applied is False
    assert r.status == CalculationStatus.FAIL
    assert r.clause_reference == "UG-37/UG-40"
    assert not r.assumptions
    # Beyan verildiği hâlde uygulanmadığı görünür olmalı.
    assert any("uygulanmadı" in n for n in r.notices)


def test_not_candidate_unconfirmed_is_silent_legacy_behaviour():
    r = calculate_reinforcement(_inp(nozzle_inside_diameter=79.1, nozzle_outside_diameter=89.1))
    assert r.ug36c3_candidate is False
    assert r.notices == [] and r.assumptions == [] and r.validity_checks == []
    assert r.status == CalculationStatus.FAIL


# ── B) Aday ama beyan yok ────────────────────────────────────────────────────

def test_candidate_without_declaration_keeps_area_result_and_adds_notice():
    r = calculate_reinforcement(_inp())
    # Karşılaştırma tabanı: adaylığın tümüyle kapatıldığı (eski davranış) koşu.
    legacy = calculate_reinforcement(_inp(ug36c3_not_applicable_reason="test"))

    assert r.ug36c3_candidate is True
    assert r.ug36c3_applied is False
    assert r.status == legacy.status == CalculationStatus.FAIL
    assert r.utilization_ratio == legacy.utilization_ratio
    assert r.required_area == legacy.required_area
    assert r.total_available_area == legacy.total_available_area
    assert r.warnings == legacy.warnings
    assert r.clause_reference == "UG-37/UG-40"
    assert r.assumptions == []
    assert len(r.notices) == 1
    assert "UG-36(c)(3)" in r.notices[0] and "UYGULANMADI" in r.notices[0]
    assert legacy.notices == []


def test_default_declaration_is_false():
    inp = NozzleReinforcementInput()
    assert inp.no_rapid_pressure_fluctuation_confirmed is False
    assert inp.opening_spacing_confirmed is False
    assert inp.welded_attachment_confirmed is False


# ── C) Muafiyet uygulanır ────────────────────────────────────────────────────

def test_exemption_applied_gives_pass_despite_area_deficit():
    plain = calculate_reinforcement(_inp())
    r = calculate_reinforcement(_inp(**_confirmed()))

    assert r.ug36c3_candidate is True and r.ug36c3_applied is True
    assert r.status == CalculationStatus.PASS
    assert "UG-36(c)(3)" in r.clause_reference
    assert "UG-37/UG-40" in r.clause_reference
    # Alan hesabı aynen raporlanır (bilgi amaçlı).
    assert r.required_area == plain.required_area
    assert r.total_available_area == plain.total_available_area
    assert r.utilization_ratio == plain.utilization_ratio < 1.0
    assert [a.name for a in r.available_areas] == ["A1", "A2", "A3", "A4", "A5"]
    # Her beyan ayrı varsayım: dalgalanma, aralık, kaynaklı bağlantı, eşik yorumu.
    assert len(r.assumptions) == 5
    assert all("UG-36(c)(3)" in a for a in r.assumptions)
    assert any("dalgalanma" in a for a in r.assumptions)
    assert any("(-c)/(-d)" in a for a in r.assumptions)
    assert any("kaynaklı" in a for a in r.assumptions)
    assert any("tr + host korozyon" in a for a in r.assumptions)
    assert any("Bitmiş açıklık" in a and "iç çap ile nozul dış çapının büyüğü" in a
               and "89.00 mm" in a and "doğrulanmadı" in a for a in r.assumptions)
    # Alan yetersizliği uyarı/FAIL üretmez, bilgi notuna döner.
    assert not any("yetersiz" in w for w in r.warnings)
    assert any("BİLGİ" in n for n in r.notices)
    assert any("FAIL üretmedi" in n for n in r.notices)
    assert len(r.validity_checks) == 3 and all(v["passed"] for v in r.validity_checks)


@pytest.mark.parametrize(
    "confirmations, missing_field",
    [
        (
            dict(opening_spacing_confirmed=True, welded_attachment_confirmed=True),
            "no_rapid_pressure_fluctuation_confirmed",
        ),
        (
            dict(no_rapid_pressure_fluctuation_confirmed=True, welded_attachment_confirmed=True),
            "opening_spacing_confirmed",
        ),
        (
            dict(no_rapid_pressure_fluctuation_confirmed=True, opening_spacing_confirmed=True),
            "welded_attachment_confirmed",
        ),
    ],
)
def test_partial_confirmation_blocks_exemption_and_names_missing_field(confirmations, missing_field):
    inp = _inp(**confirmations)
    r = calculate_reinforcement(inp)
    assert r.ug36c3_candidate is True
    assert r.ug36c3_applied is False
    assert r.status == CalculationStatus.FAIL
    assert r.clause_reference == "UG-37/UG-40"
    assert len(r.notices) == 1
    assert "UYGULANMADI" in r.notices[0]
    assert missing_field in r.notices[0]
    for other in confirmations:
        assert other not in r.notices[0]


@pytest.mark.parametrize(
    "confirmations, missing_fields",
    [
        (
            _confirmed(
                opening_spacing_confirmed=False,
                welded_attachment_confirmed=False,
            ),
            ["opening_spacing_confirmed", "welded_attachment_confirmed"],
        ),
        (
            _confirmed(
                no_rapid_pressure_fluctuation_confirmed=False,
                welded_attachment_confirmed=False,
            ),
            ["no_rapid_pressure_fluctuation_confirmed", "welded_attachment_confirmed"],
        ),
        (
            _confirmed(
                no_rapid_pressure_fluctuation_confirmed=False,
                opening_spacing_confirmed=False,
            ),
            ["no_rapid_pressure_fluctuation_confirmed", "opening_spacing_confirmed"],
        ),
    ],
)
def test_two_missing_confirmations_block_exemption(confirmations, missing_fields):
    inp = _inp(**confirmations)
    r = calculate_reinforcement(inp)
    assert r.ug36c3_candidate is True
    assert r.ug36c3_applied is False
    assert r.status == CalculationStatus.FAIL
    assert r.clause_reference == "UG-37/UG-40"
    assert len(r.notices) == 1
    assert "UYGULANMADI" in r.notices[0]
    for field in missing_fields:
        assert field in r.notices[0]


def test_all_confirmations_false_blocks_exemption():
    inp = _inp(
        **_confirmed(
            no_rapid_pressure_fluctuation_confirmed=False,
            opening_spacing_confirmed=False,
            welded_attachment_confirmed=False,
        )
    )
    r = calculate_reinforcement(inp)
    assert r.ug36c3_candidate is True
    assert r.ug36c3_applied is False
    assert r.status == CalculationStatus.FAIL
    assert r.clause_reference == "UG-37/UG-40"
    assert len(r.notices) == 1
    assert "UYGULANMADI" in r.notices[0]
    assert "no_rapid_pressure_fluctuation_confirmed" in r.notices[0]
    assert "opening_spacing_confirmed" in r.notices[0]
    assert "welded_attachment_confirmed" in r.notices[0]


# ── Sınırlar ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "d, tr, ca, limit, candidate",
    [
        (89.0, 10.0, 0.0, 89.0, True),    # iki sınır birden dahil
        (89.0, 8.0, 2.0, 89.0, True),     # tr + CA = 10.0 → hâlâ ≤ 10
        (60.0, 10.01, 0.0, 60.0, True),   # kalın sınıf, d sınırda
        (60.1, 10.01, 0.0, 60.0, False),  # kalın sınıf, d sınırın üstünde
        (89.0, 9.0, 2.0, 60.0, False),    # CA eşiği 10'un üstüne itiyor (11 mm)
        (89.1, 10.0, 0.0, 89.0, False),
    ],
)
def test_size_boundaries(d, tr, ca, limit, candidate):
    # d = BİTMİŞ açıklık: OD = d yönetir (ID = d − 2·tn, tn = 5) → max(ID, OD) = d.
    inp = _inp(
        nozzle_inside_diameter=d - 10.0,
        nozzle_outside_diameter=d,
        component_required_thickness=tr,
        component_corrosion_allowance=ca,
        component_nominal_thickness=14.0,
        **_confirmed(),
    )
    size = evaluate_ug36c3_size(inp)
    assert size.diameter_limit == limit
    assert size.threshold_thickness == pytest.approx(tr + ca)
    assert size.candidate is candidate

    r = calculate_reinforcement(inp)
    assert r.ug36c3_candidate is candidate
    assert r.ug36c3_applied is candidate
    assert ("UG-36(c)(3)" in r.clause_reference) is candidate


def test_nozzle_corrosion_allowance_enlarges_finished_opening():
    # OD 89 sabit; ID 88 + 2×0.5 = 89.0 → aday; ID 88 + 2×0.6 = 89.2 (> OD, ID yönetir) → değil.
    base = dict(nozzle_inside_diameter=88.0, nozzle_outside_diameter=89.0,
                nozzle_neck_thickness=0.5)
    assert evaluate_ug36c3_size(_inp(nozzle_corrosion_allowance=0.5, **base)).candidate is True
    assert evaluate_ug36c3_size(_inp(nozzle_corrosion_allowance=0.6, **base)).candidate is False


def test_threshold_uses_required_not_actual_thickness():
    # Gerçek et 30 mm olsa da tr = 6 mm → ince sınıf (89 mm).
    size = evaluate_ug36c3_size(
        _inp(component_nominal_thickness=30.0, component_required_thickness=6.0))
    assert size.diameter_limit == 89.0 and size.candidate is True


# ── C') Boyun yetersiz → muafiyet yok ────────────────────────────────────────

def test_inadequate_neck_blocks_exemption_even_if_confirmed():
    inp = _inp(nozzle_neck_thickness=0.3, **_confirmed())
    r = calculate_reinforcement(inp)
    assert r.limits["neck_thickness_adequate"] is False
    assert r.ug36c3_candidate is True
    assert r.ug36c3_applied is False
    assert r.status == CalculationStatus.FAIL
    assert r.clause_reference == "UG-37/UG-40"
    assert r.assumptions == []
    assert any("UYGULANMADI" in n and "boynu" in n for n in r.notices)
    assert any(v["passed"] is False for v in r.validity_checks)
    assert any("Nozul boynu kalınlığı" in w for w in r.warnings)


def test_unverifiable_neck_blocks_exemption():
    # Basınç 0 → trn hesaplanamaz; boyun kontrolü yapılmadan muafiyet verilmez.
    r = calculate_reinforcement(_inp(design_pressure=0.0, **_confirmed()))
    assert r.ug36c3_applied is False
    assert r.status != CalculationStatus.PASS or r.total_available_area >= r.required_area
    assert any("UYGULANMADI" in n for n in r.notices)


def test_opening_through_weld_seam_blocks_exemption():
    r = calculate_reinforcement(
        _inp(opening_weld_joint_efficiency=0.85, **_confirmed()))
    assert r.ug36c3_applied is False
    assert r.status == CalculationStatus.FAIL
    assert any("UW-14" in n for n in r.notices)


# ── Bitmiş açıklık = max(korozyonlu ID, OD) ──────────────────────────────────

def test_od_governs_over_id():
    # ID 80, OD 90 → 90 > 89 → aday değil (ID tek başına 80 ile aday sayılırdı).
    inp = _inp(nozzle_inside_diameter=80.0, nozzle_outside_diameter=90.0,
               **_confirmed())
    size = evaluate_ug36c3_size(inp)
    assert size.finished_diameter == pytest.approx(90.0)
    assert size.candidate is False
    assert "muhafazakâr" in size.reason
    r = calculate_reinforcement(inp)
    assert r.ug36c3_applied is False and r.status == CalculationStatus.FAIL
    assert r.assumptions == []


def test_missing_od_falls_back_to_id_plus_two_neck_thickness():
    # OD = 0 → ID + 2·tn = 80 + 2·5 = 90 > 89 → aday değil; tn = 4.5 → 89.0 → aday.
    size = evaluate_ug36c3_size(_inp(nozzle_inside_diameter=80.0, nozzle_outside_diameter=0.0))
    assert size.finished_diameter == pytest.approx(90.0) and size.candidate is False
    size = evaluate_ug36c3_size(_inp(nozzle_inside_diameter=80.0, nozzle_outside_diameter=0.0,
                                     nozzle_neck_thickness=4.5))
    assert size.finished_diameter == pytest.approx(89.0) and size.candidate is True


def test_seam_path_adds_no_passed_validity_checks():
    r = calculate_reinforcement(
        _inp(opening_weld_joint_efficiency=0.85, **_confirmed()))
    assert r.ug36c3_applied is False
    assert not any(v["passed"] is True for v in r.validity_checks)
    assert r.validity_checks == []


# ── tr yok → adaylık yok ─────────────────────────────────────────────────────

@pytest.mark.parametrize("tr", [0.0, -1.0])
def test_no_candidacy_without_required_thickness(tr):
    inp = _inp(component_required_thickness=tr, **_confirmed())
    assert evaluate_ug36c3_size(inp).candidate is False
    r = calculate_reinforcement(inp)
    assert r.ug36c3_candidate is False and r.ug36c3_applied is False
    assert r.status != CalculationStatus.PASS
    assert r.clause_reference == "UG-37/UG-40"


# ── Eğimli nozul: d/cosα ─────────────────────────────────────────────────────

def test_inclined_nozzle_uses_projected_diameter():
    # Bitmiş açıklık 60 mm (OD 60 yönetir).
    radial = _inp(nozzle_inside_diameter=50.0, nozzle_outside_diameter=60.0,
                  component_required_thickness=10.01)
    inclined = replace(radial, nozzle_inclination_angle=30.0)
    assert evaluate_ug36c3_size(radial).candidate is True
    size = evaluate_ug36c3_size(inclined)
    assert size.finished_diameter == pytest.approx(60.0 / 0.8660254, rel=1e-6)
    assert size.candidate is False  # 69.28 mm > 60 mm

    r = calculate_reinforcement(replace(inclined, **_confirmed()))
    assert r.ug36c3_applied is False


def test_inclined_candidate_stays_review_required_when_exempt():
    inp = _inp(nozzle_inside_diameter=50.0, nozzle_outside_diameter=60.0,
               nozzle_inclination_angle=30.0, **_confirmed())  # 69.28 mm ≤ 89 mm (tr = 10)
    r = calculate_reinforcement(inp)
    assert r.ug36c3_applied is True
    assert r.status == CalculationStatus.REVIEW_REQUIRED
    assert any("Eğik nozul" in w for w in r.warnings)


# ── CalculationResult taşıma ─────────────────────────────────────────────────

def test_calculation_result_carries_notices_assumptions_validity_checks():
    reinp = calculate_reinforcement(_inp(**_confirmed()))
    res = build_reinforcement_calculation_result(_inp(**_confirmed()))

    assert res.status == CalculationStatus.PASS
    assert res.clause_reference == "UG-36(c)(3); UG-37/UG-40"
    assert "UG-36(c)(3)" in res.formula_reference
    assert res.notices == reinp.notices and len(res.notices) >= 2
    assert res.assumptions == reinp.assumptions and len(res.assumptions) == 5
    assert [v["name"] for v in res.validity_checks] == [v["name"] for v in reinp.validity_checks]
    assert len(res.validity_checks) == 3
    # Tüketicilerin bağlı olduğu ara değerler aynen duruyor.
    for name in ("d", "A_required", "A1", "A2", "A3", "A4", "A5", "A_total"):
        _iv(res, name)
    assert res.final_result == reinp.total_available_area
    assert res.allowable_limit == reinp.required_area
    assert res.utilization_ratio == reinp.utilization_ratio
    assert res.input_snapshot["ug36c3_applied"] is True
    d = res.to_dict()
    assert d["notices"] and d["assumptions"] and d["validity_checks"]


def test_calculation_result_clause_unchanged_without_declaration():
    res = build_reinforcement_calculation_result(_inp())
    assert res.clause_reference == "UG-37/UG-40"
    assert res.formula_reference == "Area Replacement Method"
    assert res.status == CalculationStatus.FAIL
    assert res.assumptions == [] and res.validity_checks == []
    assert len(res.notices) == 1 and "UYGULANMADI" in res.notices[0]


# ── design_code.calculate_nozzle bağlantısı ──────────────────────────────────

def _dc():
    return DesignConditions(
        design_pressure=1.2, design_temperature=200.0, operating_pressure=1.0,
        maximum_allowable_pressure_ps=1.2, operating_temperature=150.0,
        minimum_design_temperature=-10.0)


def _mat():
    return MaterialProperty(
        material_id="M", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=138.0,
        yield_strength=260.0, tensile_strength=485.0, source_reference="t")


def _nozzle(host, **over):
    kw = dict(tag="N1", nozzle_type=NozzleType.FLANGED, host_component_id=host,
              axial_position=500.0, outside_diameter=88.9, inside_diameter=80.0,
              neck_thickness=4.45, material_id="M")
    kw.update(over)
    return Nozzle(**kw)


def _run_shell(**over):
    shell = ShellSection(section_id="S", inside_diameter=1000.0, tangent_length=2000.0,
                         nominal_thickness=12.0, internal_corrosion_allowance=2.0, material_id="M")
    return ASMEVIII1DesignCode().calculate_nozzle({
        "nozzle": _nozzle("S", **over), "design_conditions": _dc(), "materials": [_mat()],
        "shell_sections": [shell], "heads": []})


def test_domain_nozzle_field_defaults_false():
    noz = _nozzle("S")
    assert noz.no_rapid_pressure_fluctuation_confirmed is False
    assert noz.opening_spacing_confirmed is False
    assert noz.welded_attachment_confirmed is False


def test_design_code_wiring_without_declaration():
    res = _run_shell()
    assert res.clause_reference == "UG-37/UG-40"
    assert res.input_snapshot["ug36c3_candidate"] is True
    assert res.input_snapshot["ug36c3_applied"] is False
    assert any("UG-36(c)(3)" in n for n in res.notices)


def test_design_code_wiring_with_declaration():
    plain = _run_shell()
    res = _run_shell(**_confirmed())
    assert res.input_snapshot["ug36c3_applied"] is True
    assert res.clause_reference == "UG-36(c)(3); UG-37/UG-40"
    assert len(res.assumptions) == 5
    assert _iv(res, "A_required") == pytest.approx(_iv(plain, "A_required"))
    assert _iv(res, "A_total") == pytest.approx(_iv(plain, "A_total"))


def test_design_code_flat_head_host_disables_candidacy():
    head = Head(head_id="H", type=HeadType.FLAT, inside_diameter=1000.0,
                nominal_thickness=60.0, material_id="M", flat_attachment_factor=0.33)
    res = ASMEVIII1DesignCode().calculate_nozzle({
        "nozzle": _nozzle("H", **_confirmed()),
        "design_conditions": _dc(), "materials": [_mat()],
        "shell_sections": [], "heads": [head]})
    assert res.input_snapshot["ug36c3_candidate"] is False
    assert res.input_snapshot["ug36c3_applied"] is False
    assert res.clause_reference == "UG-37/UG-40"
    assert res.assumptions == []
    assert any("UG-39" in n for n in res.notices)


def test_design_code_uses_nozzle_outside_diameter():
    # _nozzle: ID 80, OD 88.9 → 88.9 ≤ 89 aday (beyanlı → uygulanır).
    ok = _run_shell(**_confirmed())
    assert ok.input_snapshot["ug36c3_candidate"] is True
    # OD 90 yönetir → 90 > 89 → aday değil, muafiyet yok.
    big = _run_shell(outside_diameter=90.0, **_confirmed())
    assert big.input_snapshot["ug36c3_candidate"] is False
    assert big.input_snapshot["ug36c3_applied"] is False
    assert big.clause_reference == "UG-37/UG-40"
    assert big.assumptions == []
