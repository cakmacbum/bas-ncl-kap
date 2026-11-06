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
        ..., description="Formül tanımı (ör. 'UG-27-CIRC', 'EN-7.4.2-CYL')."
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

# E04: numaralar hesapların gerçek maddesine çekildi (iç basınç kabukları EN 13445-3
# Madde 7'dedir). Numaralar bellekten; lisanslı metinle doğrulanmadı (verified=False).
# Eski "EN-5.x" kimlikleri geriye dönük takma ad olarak _EN13445_ALIASES'te kalır.
_EN_ED = "2021+A1:2023"


def _en(formula_id: str, clause: str, formula: str, description: str, unit: str) -> ClauseMapping:
    return ClauseMapping(formula_id=formula_id, code="EN 13445", edition=_EN_ED,
                         clause_reference=clause, formula_reference=formula,
                         description=description, unit=unit)


_EN13445_MAPPINGS: Dict[str, ClauseMapping] = {m.formula_id: m for m in (
    _en("EN-7.4.2-CYL", "EN 13445-3, 7.4.2", "e = P·Di/(2fz − P)",
        "Silindirik gövde, iç basınç", "mm"),
    _en("EN-7.5.2-HEMI", "EN 13445-3, 7.5.2", "e = P·R/(2fz − 0,5P)",
        "Yarım küresel bombe", "mm"),
    _en("EN-7.5.3-TORI", "EN 13445-3, 7.5.3", "es/ey/eb, β (7.5.3.5)",
        "Torisferik bombe tam prosedürü", "mm"),
    _en("EN-7.5.4-ELLIP", "EN 13445-3, 7.5.4",
        "K = Di/(2hi); R = Di(0,44K+0,02), r = Di(0,5/K−0,08) → 7.5.3 es/ey/eb",
        "Elipsoidal bombe — eşdeğer torisferik (1,7 < K < 2,2; katsayılar bellekten)", "mm"),
    _en("EN-7.6.4-CONE", "EN 13445-3, 7.6.4", "e = P·Di/(2fz − P)·1/cos α", "Konik gövde", "mm"),
    _en("EN-10.4-FLAT", "EN 13445-3, 10.4", "e = C·D·√(P/f)", "Desteksiz düz kapak", "mm"),
    _en("EN-6-FD", "EN 13445-3, 6", "f_d / f_test bölenleri (malzeme grubuna göre)",
        "Azami nominal tasarım gerilmesi (alt madde no doğrulanmadı)", "MPa"),
    _en("EN-5.6-Z", "EN 13445-3, 5.6", "test grubu 1·2 → 1; 3 → 0,85; 4 → 0,7",
        "Birimleştirme katsayısı z ↔ EN 13445-5 test grubu", "-"),
    _en("EN-10.2.3.3.1-HYDRO", "EN 13445-5, 10.2.3.3.1", "Pt = max(1,25·Pd·fa/fT ; 1,43·PS)",
        "Hidrostatik test basıncı", "MPa"),
    _en("EN-PNEU", "EN 13445-5, 10.2.3.3 (alt madde no doğrulanmadı)", "Pt = k·Pd·fa/fT (k kullanıcı)",
        "Pnömatik test basıncı", "MPa"),
)}

# Eski kimlikler (yanlış madde numarası taşıyordu) → yeni kayıt.
_EN13445_ALIASES: Dict[str, str] = {
    "EN-5.4.2-CIRC": "EN-7.4.2-CYL",
    "EN-5.4.2-LONG": "EN-7.4.2-CYL",
    "EN-5.5.2-ELLIP": "EN-7.5.4-ELLIP",
    "EN-5.5.3-TORI": "EN-7.5.3-TORI",
    "EN-5.5.4-HEMI": "EN-7.5.2-HEMI",
    "EN-10.2-HYDRO": "EN-10.2.3.3.1-HYDRO",
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
    formula_id = _EN13445_ALIASES.get(formula_id, formula_id)
    if formula_id in _EN13445_MAPPINGS:
        mapping = _EN13445_MAPPINGS[formula_id]
        if code is None or mapping.code == code:
            return mapping

    return None


__all__ = ["ClauseMapping", "get_clause_mapping"]
