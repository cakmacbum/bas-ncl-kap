"""ESR (Essential Safety Requirements) Matrisi — PED Ek I.

PED 2014/68/EU Ek I'deki temel güvenlik gerekliliklerinin takibi.
Her gereklilik için uygulanma durumu, kanıt ve referans izlenir.

K6 kuralı: Standart telifli metni kopyalanmaz; yalnızca madde numaraları kullanılır.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ESRComplianceStatus(str, Enum):
    """ESR uygunluk durumu."""
    APPLIED = "Applied"           # Tam uygulandı
    PARTIALLY_APPLIED = "Partially Applied"  # Kısmen uygulandı
    NOT_APPLIED = "Not Applied"   # Uygulanmadı
    NOT_APPLICABLE = "Not Applicable"  # Bu ekipman için geçerli değil


class ESRItem(BaseModel):
    """Tek bir ESR gerekliliğinin uygunluk kaydı."""

    clause: str = Field(
        ..., description="PED Ek I madde numarası (ör. '4.1', '4.2', '5.1')."
    )
    title: str = Field(
        ..., description="Gereklilik başlığı."
    )
    description: str = Field(
        default="",
        description="Gereklilik açıklaması.",
    )
    status: ESRComplianceStatus = Field(
        ..., description="Uygulanma durumu."
    )
    evidence: str = Field(
        default="",
        description="Kanıt / referans (hesap raporu, test sonucu vb.)."
    )
    standard_reference: str = Field(
        default="",
        description="Uygulanan harmonize standart referansı."
    )
    notes: Optional[str] = Field(
        default=None, description="Ek notlar."
    )


class ESRMatrix(BaseModel):
    """PED Ek I Temel Güvenlik Gereklilikleri Matrisi.

    PED 2014/68/EU Ek I'deki tüm gerekliliklerin uygulanma durumunu izler.
    Bu matris, teknik dosyanın bir parçasıdır ve CE işaretleme için zorunludur.

    Kullanım:
        matrix = ESRMatrix.default_for_vessel()
        matrix.update_status("4.1", ESRComplianceStatus.APPLIED, evidence="ASME VIII-1 raporu")
    """

    project_number: str = Field(default="", description="Proje numarası.")
    equipment_type: str = Field(default="vessel", description="Ekipman türü.")
    items: List[ESRItem] = Field(
        default_factory=list,
        description="ESR gereklilik listesi.",
    )

    @classmethod
    def default_for_vessel(cls) -> "ESRMatrix":
        """Basınçlı kap için varsayılan ESR matrisi oluştur.

        PED Ek I, Bölüm 4-5'teki temel gereklilikleri dahil eder.
        """
        items = [
            ESRItem(
                clause="4.1",
                title="Design for adequate strength",
                description=(
                    "Ekipman, tüm çalışma koşullarında yeterli dayanıma sahip olacak "
                    "şekilde tasarlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.2",
                title="Design for safe handling and operation",
                description=(
                    "Ekipman, güvenli kullanım ve bakım için tasarlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.3",
                title="Means of access and inspection",
                description=(
                    "İç muayene ve temizlik için erişim imkanları sağlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.4",
                title="Means of draining and venting",
                description=(
                    "Boşaltma ve havalandırma imkanları sağlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.5",
                title="Corrosion or other chemical attack",
                description=(
                    "Korozyon veya kimyasal aşınma göz önüne alınmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.6",
                title="Wear",
                description=(
                    "Aşınma göz önüne alınmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.7",
                title="Provisions for filling and discharge",
                description=(
                    "Doldurma ve boşaltma için düzenlemeler yapılmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.8",
                title="Protection against exceeding allowable limits",
                description=(
                    "İzin verilen basınç ve sıcaklık sınırlarının aşılmasına karşı "
                    "koruma sağlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.9",
                title="Safety accessories",
                description=(
                    "Güvenlik aksesuarları (emniyet ventili, basınç şalteri vb.) "
                    "uygun şekilde seçilmeli ve monte edilmelidir."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="4.10",
                title="External fire",
                description=(
                    "Dış yangın durumu göz önüne alınmalıdır (gerekliyse)."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="5.1",
                title="Material properties",
                description=(
                    "Malzeme özellikleri (akma, çekme, darbe, kimyasal bileşim) "
                    "uygun standartlara uygun olmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="5.2",
                title="Material inspection",
                description=(
                    "Malzeme muayenesi ve testleri yapılmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="5.3",
                title="Welding and heat treatment",
                description=(
                    "Kaynak ve ısıl işlem prosedürleri onaylanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="7.1",
                title="Permanent joining",
                description=(
                    "Kalıcı birleştirme (kaynak) yöntemleri ve kaynakçı yeterliliği "
                    "doğrulanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="7.2",
                title="Non-destructive testing",
                description=(
                    "Tahribatsız muayene (NDT) yöntemleri uygulanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="7.3",
                title="Heat treatment",
                description=(
                    "Kaynak sonrası ısıl işlem (PWHT) gerekliyse uygulanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="7.4",
                title="Traceability of materials",
                description=(
                    "Malzeme izlenebilirliği sağlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="8.1",
                title="Hydrostatic test",
                description=(
                    "Hidrostatik test yapılmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="8.2",
                title="Non-destructive testing of permanent joints",
                description=(
                    "Kalıcı birleştirmelerin NDT'si yapılmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="9",
                title="Marking and labelling",
                description=(
                    "İsim plakası ve işaretleme gereklilikleri karşılanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
            ESRItem(
                clause="10",
                title="Operating instructions",
                description=(
                    "Kullanım talimatları sağlanmalıdır."
                ),
                status=ESRComplianceStatus.NOT_APPLICABLE,
            ),
        ]
        return cls(items=items)

    def update_status(
        self,
        clause: str,
        status: ESRComplianceStatus,
        evidence: str = "",
        notes: Optional[str] = None,
    ) -> bool:
        """Belirli bir gerekliliğin durumunu güncelle.

        Args:
            clause: Madde numarası.
            status: Yeni durum.
            evidence: Kanıt referansı.
            notes: Ek not.

        Returns:
            True ise güncellendi, False ise madde bulunamadı.
        """
        for item in self.items:
            if item.clause == clause:
                item.status = status
                if evidence:
                    item.evidence = evidence
                if notes:
                    item.notes = notes
                return True
        return False

    def get_applied_count(self) -> int:
        """Uygulanan gereklilik sayısı."""
        return sum(1 for i in self.items if i.status == ESRComplianceStatus.APPLIED)

    def get_not_applied_count(self) -> int:
        """Uygulanmayan gereklilik sayısı."""
        return sum(1 for i in self.items if i.status == ESRComplianceStatus.NOT_APPLIED)

    def get_applicable_count(self) -> int:
        """Geçerli gereklilik sayısı (Not Applicable hariç)."""
        return sum(1 for i in self.items if i.status != ESRComplianceStatus.NOT_APPLICABLE)

    def to_html(self) -> str:
        """ESR matrisini HTML tablosu olarak üret."""
        rows = ""
        for item in self.items:
            status_class = {
                ESRComplianceStatus.APPLIED: "status-pass",
                ESRComplianceStatus.PARTIALLY_APPLIED: "status-nc",
                ESRComplianceStatus.NOT_APPLIED: "status-fail",
                ESRComplianceStatus.NOT_APPLICABLE: "status-na",
            }.get(item.status, "")

            rows += (
                f'<tr>'
                f'<td>{item.clause}</td>'
                f'<td>{item.title}</td>'
                f'<td class="{status_class}">{item.status.value}</td>'
                f'<td>{item.evidence or "—"}</td>'
                f'<td>{item.standard_reference or "—"}</td>'
                f'</tr>\n'
            )

        return f"""
<table>
<tr><th>Madde</th><th>Gereklilik</th><th>Durum</th><th>Kanıt</th><th>Standart</th></tr>
{rows}
</table>
"""


__all__ = ["ESRMatrix", "ESRItem", "ESRComplianceStatus"]
