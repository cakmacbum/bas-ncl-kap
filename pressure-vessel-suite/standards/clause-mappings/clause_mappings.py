"""Clause mappings — formül ↔ madde referans eşleştirmeleri.

Her hesap formülünün hangi standart maddesine karşılık geldiğini izler.
K5 kuralı: Her hesap denetlenebilir olmalı.
K6 kuralı: Standart telifli metni kopyalanmaz; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field


class ClauseMapping(BaseModel):
    """Formül ↔ madde referans eşleştirmesi."""

    formula_id: str = Field(
        ..., description="Formül tanımı (ör. 'UG-27-CIRC', 'EN-13445-5.4.2')."
    )
    code: str = Field(
        ..., description="Standart (ör. 'ASME VIII-1', 'EN 13445')."
    )
    edition: str = Field(
        ..., description="Standart sürümü."
    )
    clause_reference: str = Field(
        ..., description="Madde referansı (ör. 'UG-27(c)(1)')."
    )
    formula_reference: str = Field(
        ..., description="Formül referansı (ör. 'UG-27(c)(1) Eq. (1)')."
    )
    description: str = Field(
        default="",
        description="Formül açıklaması.",
    )
    unit: str = Field(
        default="mm",
        description="Sonuç birimi.",
    )


# ── ASME VIII-1 madde eşleştirmeleri ──────────────────────────────────────────

_ASME_MAPPINGS: Dict[str, ClauseMapping] = {
    "UG-27-CIRC": ClauseMapping(
        formula_id="UG-27-CIRC",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-27(c)(1)",
        formula_reference="UG-27(c)(1) Eq. (1)",
        description="Silindirik gövde, iç basınç, çevresel gerilme",
        unit="mm",
    ),
    "UG-27-LONG": ClauseMapping(
        formula_id="UG-27-LONG",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-27(c)(1)",
        formula_reference="UG-27(c)(1) Eq. (2)",
        description="Silindirik gövde, iç basınç, boyuna gerilme",
        unit="mm",
    ),
    "UG-32-ELLIP": ClauseMapping(
        formula_id="UG-32-ELLIP",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-32(d)",
        formula_reference="UG-32(d)",
        description="2:1 elipsoidal bombe",
        unit="mm",
    ),
    "UG-32-TORI": ClauseMapping(
        formula_id="UG-32-TORI",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-32(e)",
        formula_reference="UG-32(e)",
        description="Torisferik bombe",
        unit="mm",
    ),
    "UG-32-HEMI": ClauseMapping(
        formula_id="UG-32-HEMI",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-32(f)",
        formula_reference="UG-32(f)",
        description="Yarım küresel bombe",
        unit="mm",
    ),
    "UG-99-HYDRO": ClauseMapping(
        formula_id="UG-99-HYDRO",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-99(b)",
        formula_reference="UG-99(b)",
        description="Hidrostatik test basıncı",
        unit="MPa",
    ),
}

# ── EN 13445 madde eşleştirmeleri ─────────────────────────────────────────────

_EN13445_MAPPINGS: Dict[str, ClauseMapping] = {
    "EN-5.4.2-CIRC": ClauseMapping(
        formula_id="EN-5.4.2-CIRC",
        code="EN 13445",
        edition="2021+A1:2023",
        clause_reference="EN 13445-3, 5.4.2",
        formula_reference="5.4.2-1",
        description="Silindirik gövde, iç basınç, çevresel gerilme",
        unit="mm",
    ),
    "EN-5.4.2-LONG": ClauseMapping(
        formula_id="EN-5.4.2-LONG",
        code="EN 13445",
        edition="2021+A1:2023",
        clause_reference="EN 13445-3, 5.4.2",
        formula_reference="5.4.2-2",
        description="Silindirik gövde, iç basınç, boyuna gerilme",
        unit="mm",
    ),
    "EN-5.5.2-ELLIP": ClauseMapping(
        formula_id="EN-5.5.2-ELLIP",
        code="EN 13445",
        edition="2021+A1:2023",
        clause_reference="EN 13445-3, 5.5.2",
        formula_reference="5.5.2-1",
        description="Elipsoidal bombe",
        unit="mm",
    ),
    "EN-5.5.3-TORI": ClauseMapping(
        formula_id="EN-5.5.3-TORI",
        code="EN 13445",
        edition="2021+A1:2023",
        clause_reference="EN 13445-3, 5.5.3",
        formula_reference="5.5.3-1",
        description="Torisferik bombe (Korbbogen)",
        unit="mm",
    ),
    "EN-5.5.4-HEMI": ClauseMapping(
        formula_id="EN-5.5.4-HEMI",
        code="EN 13445",
        edition="2021+A1:2023",
        clause_reference="EN 13445-3, 5.5.4",
        formula_reference="5.5.4-1",
        description="Yarım küresel bombe",
        unit="mm",
    ),
    "EN-10.2-HYDRO": ClauseMapping(
        formula_id="EN-10.2-HYDRO",
        code="EN 13445",
        edition="2021+A1:2023",
        clause_reference="EN 13445-5, 10.2",
        formula_reference="10.2-1",
        description="PED test basıncı",
        unit="MPa",
    ),
}


def get_clause_mapping(formula_id: str, code: Optional[str] = None) -> Optional[ClauseMapping]:
    """Formül ID'sine göre madde referans eşleştirmesini getir.

    Args:
        formula_id: Formül tanımı.
        code: Standart (opsiyonel, filtreleme için).

    Returns:
        ClauseMapping veya None.
    """
    # ASME ara
    if formula_id in _ASME_MAPPINGS:
        mapping = _ASME_MAPPINGS[formula_id]
        if code is None or mapping.code == code:
            return mapping

    # EN 13445 ara
    if formula_id in _EN13445_MAPPINGS:
        mapping = _EN13445_MAPPINGS[formula_id]
        if code is None or mapping.code == code:
            return mapping

    return None


__all__ = ["ClauseMapping", "get_clause_mapping"]
