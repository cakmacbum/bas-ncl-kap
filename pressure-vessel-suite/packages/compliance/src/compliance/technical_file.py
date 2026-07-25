"""Teknik dosya indeksi — PED Madde 14(3).

PED 2014/68/EU Madde 14(3)'e göre teknik dosya içeriğinin takibi.
Teknik dosya, ekipmanın tasarım ve imalat bilgilerini içerir
ve 10 yıl süreyle saklanmalıdır.

K6 kuralı: Standart telifli metni kopyalanmaz.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TechnicalFileItemType(str, Enum):
    """Teknik dosya kalemi türü."""
    GENERAL_DESCRIPTION = "General Description"
    DESIGN_DRAWINGS = "Design Drawings"
    CALCULATION_NOTES = "Calculation Notes"
    MANUFACTURING_PROCEDURES = "Manufacturing Procedures"
    MATERIAL_CERTIFICATES = "Material Certificates"
    WELDING_RECORDS = "Welding Records"
    NDT_REPORTS = "NDT Reports"
    HEAT_TREATMENT_RECORDS = "Heat Treatment Records"
    HYDROTEST_CERTIFICATE = "Hydrotest Certificate"
    ESR_COMPLIANCE_MATRIX = "ESR Compliance Matrix"
    RISK_ANALYSIS = "Risk Analysis"
    EU_DECLARATION = "EU Declaration of Conformity"
    NAMEPLATE_PHOTO = "Nameplate Photo"
    OTHER = "Other"


class TechnicalFileItem(BaseModel):
    """Teknik dosya kalemi."""

    item_id: str = Field(..., description="Kalem tanımı (ör. 'TF-001').")
    item_type: TechnicalFileItemType = Field(..., description="Kalem türü.")
    description: str = Field(..., description="Kalem açıklaması.")
    document_reference: str = Field(
        default="",
        description="Doküman referansı (dosya adı, revizyon vb.).",
    )
    revision: str = Field(default="", description="Revizyon.")
    date: Optional[str] = Field(default=None, description="Tarih.")
    status: str = Field(
        default="Planned",
        description="Durum (Planned, In Progress, Completed, N/A).",
    )
    notes: Optional[str] = Field(default=None, description="Ek notlar.")


class TechnicalFileIndex(BaseModel):
    """Teknik dosya indeksi.

    PED Madde 14(3)'e göre teknik dosya içeriğini izler.

    Kullanım:
        index = TechnicalFileIndex.default_for_vessel()
        index.add_item(TechnicalFileItem(...))
    """

    project_number: str = Field(default="", description="Proje numarası.")
    equipment_description: str = Field(default="", description="Ekipman tanımı.")
    retention_years: int = Field(
        default=10,
        description="Saklama süresi (yıl). PED Madde 14(3): en az 10 yıl.",
    )
    items: List[TechnicalFileItem] = Field(
        default_factory=list,
        description="Teknik dosya kalemleri.",
    )

    @classmethod
    def default_for_vessel(cls) -> "TechnicalFileIndex":
        """Basınçlı kap için varsayılan teknik dosya indeksi oluştur."""
        items = [
            TechnicalFileItem(
                item_id="TF-001",
                item_type=TechnicalFileItemType.GENERAL_DESCRIPTION,
                description="Genel tanımlama ve teknik özellikler",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-002",
                item_type=TechnicalFileItemType.DESIGN_DRAWINGS,
                description="Tasarım çizimleri (genel görünüş, detaylar)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-003",
                item_type=TechnicalFileItemType.CALCULATION_NOTES,
                description="Hesap notları (et kalınlığı, MAWP, test basıncı)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-004",
                item_type=TechnicalFileItemType.MANUFACTURING_PROCEDURES,
                description="İmalat prosedürleri (kesme, bükme, kaynak)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-005",
                item_type=TechnicalFileItemType.MATERIAL_CERTIFICATES,
                description="Malzeme sertifikaları (EN 10204 3.1/3.2)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-006",
                item_type=TechnicalFileItemType.WELDING_RECORDS,
                description="Kaynak kayıtları (WPS, PQR, kaynakçı yeterliliği)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-007",
                item_type=TechnicalFileItemType.NDT_REPORTS,
                description="NDT raporları (RT, UT, MT, VT sonuçları)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-008",
                item_type=TechnicalFileItemType.HEAT_TREATMENT_RECORDS,
                description="Isıl işlem kayıtları (PWHT, normalize vb.)",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-009",
                item_type=TechnicalFileItemType.HYDROTEST_CERTIFICATE,
                description="Hidrostatik test sertifikası",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-010",
                item_type=TechnicalFileItemType.ESR_COMPLIANCE_MATRIX,
                description="ESR uygunluk matrisi",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-011",
                item_type=TechnicalFileItemType.RISK_ANALYSIS,
                description="Risk ve tehlike analizi",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-012",
                item_type=TechnicalFileItemType.EU_DECLARATION,
                description="EU Declaration of Conformity",
                status="Planned",
            ),
            TechnicalFileItem(
                item_id="TF-013",
                item_type=TechnicalFileItemType.NAMEPLATE_PHOTO,
                description="İsim plakası fotoğrafı",
                status="Planned",
            ),
        ]
        return cls(items=items)

    def add_item(self, item: TechnicalFileItem) -> None:
        """Yeni teknik dosya kalemi ekle."""
        self.items.append(item)

    def get_completed_count(self) -> int:
        """Tamamlanan kalem sayısı."""
        return sum(1 for i in self.items if i.status == "Completed")

    def get_completion_percentage(self) -> float:
        """Tamamlanma yüzdesi."""
        if not self.items:
            return 0.0
        return (self.get_completed_count() / len(self.items)) * 100.0

    def to_html(self) -> str:
        """Teknik dosya indeksini HTML tablosu olarak üret."""
        rows = ""
        for item in self.items:
            status_class = {
                "Completed": "status-pass",
                "In Progress": "status-nc",
                "Planned": "status-fail",
                "N/A": "status-na",
            }.get(item.status, "")

            rows += (
                f'<tr>'
                f'<td>{item.item_id}</td>'
                f'<td>{item.item_type.value}</td>'
                f'<td>{item.description}</td>'
                f'<td>{item.document_reference or "—"}</td>'
                f'<td class="{status_class}">{item.status}</td>'
                f'</tr>\n'
            )
        return f"""
<table>
<tr><th>ID</th><th>Tür</th><th>Açıklama</th><th>Doküman Ref.</th><th>Durum</th></tr>
{rows}
</table>
<p><em>Saklama süresi: {self.retention_years} yıl (PED Madde 14(3)).</em></p>
"""


__all__ = ["TechnicalFileIndex", "TechnicalFileItem", "TechnicalFileItemType"]
