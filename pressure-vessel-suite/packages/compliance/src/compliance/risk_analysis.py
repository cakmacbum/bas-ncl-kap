"""Risk ve tehlike analizi formu — PED Ek I, Bölüm 3.

PED 2014/68/EU Ek I, Bölüm 3'e uygun risk analizi yapısı.
Ekipmanın kullanım ömrü boyunca karşılaşabileceği tehlikelerin
belirlenmesi ve azaltılması için.

K6 kuralı: Standart telifli metni kopyalanmaz.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    """Tehlike ciddiyeti."""
    NEGLIGIBLE = "Negligible"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class RiskProbability(str, Enum):
    """Tehlike olasılığı."""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class RiskLevel(str, Enum):
    """Risk seviyesi (ciddiyet × olasılık)."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class RiskItem(BaseModel):
    """Tek bir risk kaydı."""

    hazard_id: str = Field(..., description="Tehlike tanımı (ör. 'H-001').")
    hazard_description: str = Field(..., description="Tehlike açıklaması.")
    hazard_source: str = Field(
        default="",
        description="Tehlike kaynağı (basınç, sıcaklık, korozyon vb.).",
    )
    severity: RiskSeverity = Field(..., description="Ciddiyet.")
    probability: RiskProbability = Field(..., description="Olasılık.")
    risk_level: RiskLevel = Field(..., description="Risk seviyesi.")
    mitigation_measures: List[str] = Field(
        default_factory=list,
        description="Azaltma önlemleri.",
    )
    residual_risk: RiskLevel = Field(
        default=RiskLevel.LOW,
        description="Kalan risk (azaltma sonrası).",
    )
    standard_reference: str = Field(
        default="",
        description="İlgili standart maddesi.",
    )
    notes: Optional[str] = Field(default=None, description="Ek notlar.")


class RiskAnalysis(BaseModel):
    """Risk ve tehlike analizi formu.

    PED Ek I, Bölüm 3'e uygun risk analizi yapısı.

    Kullanım:
        analysis = RiskAnalysis.default_for_pressure_vessel()
        analysis.add_risk(RiskItem(...))
    """

    project_number: str = Field(default="", description="Proje numarası.")
    equipment_description: str = Field(default="", description="Ekipman tanımı.")
    items: List[RiskItem] = Field(
        default_factory=list,
        description="Risk kalemleri.",
    )

    @classmethod
    def default_for_pressure_vessel(cls) -> "RiskAnalysis":
        """Basınçlı kap için varsayılan risk analizi oluştur."""
        items = [
            RiskItem(
                hazard_id="H-001",
                hazard_description="Aşırı basınç — izin verilen basınç sınırının aşılması",
                hazard_source="Basınç",
                severity=RiskSeverity.VERY_HIGH,
                probability=RiskProbability.LOW,
                risk_level=RiskLevel.HIGH,
                mitigation_measures=[
                    "Emniyet ventili montajı",
                    "Basınç şalteri",
                    "Tasarım basıncında konservatif marj",
                ],
                residual_risk=RiskLevel.LOW,
                standard_reference="PED Ek I, 4.8",
            ),
            RiskItem(
                hazard_id="H-002",
                hazard_description="Yüksek sıcaklık — malzeme dayanımının düşmesi",
                hazard_source="Sıcaklık",
                severity=RiskSeverity.HIGH,
                probability=RiskProbability.LOW,
                risk_level=RiskLevel.MEDIUM,
                mitigation_measures=[
                    "Sıcaklığa göre malzeme seçimi",
                    "İzin verilen gerilme sıcaklık düzeltmesi",
                    "Sıcaklık izleme sistemi",
                ],
                residual_risk=RiskLevel.LOW,
                standard_reference="PED Ek I, 5.1",
            ),
            RiskItem(
                hazard_id="H-003",
                hazard_description="Korozyon — duvar kalınlığının azalması",
                hazard_source="Kimyasal",
                severity=RiskSeverity.HIGH,
                probability=RiskProbability.MEDIUM,
                risk_level=RiskLevel.HIGH,
                mitigation_measures=[
                    "Korozyon payı eklenmesi",
                    "Korozyona dayanıklı malzeme seçimi",
                    "Düzenli muayene programı",
                ],
                residual_risk=RiskLevel.LOW,
                standard_reference="PED Ek I, 4.5",
            ),
            RiskItem(
                hazard_id="H-004",
                hazard_description="Kaynak hataları — yapısal bütünlüğün kaybı",
                hazard_source="İmalat",
                severity=RiskSeverity.VERY_HIGH,
                probability=RiskProbability.LOW,
                risk_level=RiskLevel.HIGH,
                mitigation_measures=[
                    "Onaylanmış WPS/PQR",
                    "Kaynakçı yeterliliği",
                    "NDT (RT, UT, MT, VT)",
                    "PWHT (gerekliyse)",
                ],
                residual_risk=RiskLevel.LOW,
                standard_reference="PED Ek I, 7.1-7.3",
            ),
            RiskItem(
                hazard_id="H-005",
                hazard_description="Dış etki — darbe, deprem, rüzgar",
                hazard_source="Dış etkenler",
                severity=RiskSeverity.MEDIUM,
                probability=RiskProbability.LOW,
                risk_level=RiskLevel.LOW,
                mitigation_measures=[
                    "Destek tasarımı",
                    "Çevresel etki değerlendirmesi",
                ],
                residual_risk=RiskLevel.LOW,
                standard_reference="PED Ek I, 4.2",
            ),
        ]
        return cls(items=items)

    def add_risk(self, item: RiskItem) -> None:
        """Yeni risk kalemi ekle."""
        self.items.append(item)

    def get_high_risks(self) -> List[RiskItem]:
        """Yüksek ve çok yüksek risk kalemlerini getir."""
        return [
            i for i in self.items
            if i.risk_level in (RiskLevel.HIGH, RiskLevel.VERY_HIGH)
        ]

    def get_residual_high_risks(self) -> List[RiskItem]:
        """Kalan yüksek risk kalemlerini getir."""
        return [
            i for i in self.items
            if i.residual_risk in (RiskLevel.HIGH, RiskLevel.VERY_HIGH)
        ]

    def to_html(self) -> str:
        """Risk analizini HTML tablosu olarak üret."""
        rows = ""
        for item in self.items:
            rows += (
                f'<tr>'
                f'<td>{item.hazard_id}</td>'
                f'<td>{item.hazard_description}</td>'
                f'<td>{item.severity.value}</td>'
                f'<td>{item.probability.value}</td>'
                f'<td>{item.risk_level.value}</td>'
                f'<td>{"; ".join(item.mitigation_measures)}</td>'
                f'<td>{item.residual_risk.value}</td>'
                f'</tr>\n'
            )
        return f"""
<table>
<tr><th>ID</th><th>Tehlike</th><th>Ciddiyet</th><th>Olasılık</th>
<th>Risk</th><th>Azaltma Önlemleri</th><th>Kalan Risk</th></tr>
{rows}
</table>
"""


__all__ = [
    "RiskAnalysis",
    "RiskItem",
    "RiskSeverity",
    "RiskProbability",
    "RiskLevel",
]
