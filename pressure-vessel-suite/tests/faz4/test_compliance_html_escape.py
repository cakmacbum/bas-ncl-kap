"""B-12b: compliance to_html() kullanıcı kaynaklı metinleri kaçırmalı."""

from compliance.declaration import DeclarationOfConformity, NameplateInfo
from compliance.esr_matrix import ESRComplianceStatus, ESRItem, ESRMatrix
from compliance.risk_analysis import (
    RiskAnalysis, RiskItem, RiskLevel, RiskProbability, RiskSeverity,
)

XSS = "<script>alert(1)</script>"
ATTR = '"onmouseover="x'


def _assert_escaped(html: str):
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert '"onmouseover="x' not in html
    assert "&quot;onmouseover=&quot;x" in html


def test_esr_to_html_kacirir():
    m = ESRMatrix(items=[ESRItem(
        clause=ATTR, title=XSS, status=ESRComplianceStatus.APPLIED,
        evidence=XSS, standard_reference=ATTR)])
    _assert_escaped(m.to_html())


def test_esr_to_html_normal_ayni():
    m = ESRMatrix(items=[ESRItem(
        clause="4.1", title="Tasarim", status=ESRComplianceStatus.APPLIED,
        evidence="Hesap", standard_reference="EN 13445")])
    assert ('<tr><td>4.1</td><td>Tasarim</td><td class="status-pass">'
            + ESRComplianceStatus.APPLIED.value
            + '</td><td>Hesap</td><td>EN 13445</td></tr>') in m.to_html()


def test_risk_to_html_kacirir():
    a = RiskAnalysis(items=[RiskItem(
        hazard_id=ATTR, hazard_description=XSS, severity=RiskSeverity.HIGH,
        probability=RiskProbability.MEDIUM, risk_level=RiskLevel.HIGH,
        mitigation_measures=[XSS, "ok"], residual_risk=RiskLevel.LOW)])
    h = a.to_html()
    _assert_escaped(h)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;; ok" in h


def test_nameplate_to_html_kacirir():
    n = NameplateInfo(
        manufacturer_name=XSS, manufacturer_address=ATTR, year_of_manufacture=2026,
        equipment_type=XSS, serial_number=ATTR, maximum_allowable_pressure_ps=1.5,
        maximum_allowable_temperature_ts_max=100, minimum_allowable_temperature_ts_min=-10,
        volume_liters=100, test_pressure=2.0, test_type=XSS,
        design_code=ATTR, design_code_edition=XSS, ped_category="II", fluid_group="1",
        conformity_module="B+D")
    _assert_escaped(n.to_html())


def test_doc_to_html_kacirir_ve_normal():
    d = DeclarationOfConformity(
        manufacturer_name=XSS, manufacturer_address=ATTR, equipment_description=XSS,
        equipment_type="vessel", serial_number=ATTR,
        harmonised_standards=[XSS, "EN 13445"], notify_body_name=XSS, notify_body_number="0123",
        ped_category="II", conformity_module="B+D")
    h = d.to_html()
    _assert_escaped(h)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>EN 13445" in h
    d2 = DeclarationOfConformity(manufacturer_name="ACME", equipment_description="d", equipment_type="v", serial_number="s", ped_category="II", conformity_module="B+D", harmonised_standards=["A", "B"])
    assert "<td>ACME</td>" in d2.to_html() and "A<br>B" in d2.to_html()
