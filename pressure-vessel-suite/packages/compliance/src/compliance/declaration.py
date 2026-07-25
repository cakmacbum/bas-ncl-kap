"""EU Declaration of Conformity ve isim plakası bilgileri.

PED 2014/68/EU Madde 14 ve 16'ya uygun DoC taslağı ve isim plakası üretimi.

K6 kuralı: Standart telifli metni kopyalanmaz.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class NameplateInfo(BaseModel):
    """İsim plakası bilgileri (PED Madde 16(2)).

    PED Ek II, Section 9'a uygun isim plakası bilgileri.
    """

    manufacturer_name: str = Field(
        ..., description="İmalatçı adı."
    )
    manufacturer_address: str = Field(
        default="", description="İmalatçı adresi."
    )
    year_of_manufacture: int = Field(
        ..., description="İmalat yılı."
    )
    equipment_type: str = Field(
        ..., description="Ekipman türü (ör. 'Pressure Vessel')."
    )
    serial_number: str = Field(
        ..., description="Seri numarası."
    )
    maximum_allowable_pressure_ps: float = Field(
        ..., description="Azami izin verilen basınç PS (MPa)."
    )
    maximum_allowable_temperature_ts_max: float = Field(
        ..., description="Azami çalışma sıcaklığı TS max (°C)."
    )
    minimum_allowable_temperature_ts_min: float = Field(
        ..., description="Asgari çalışma sıcaklığı TS min (°C)."
    )
    volume_liters: float = Field(
        ..., description="Hacim (litre)."
    )
    test_pressure: float = Field(
        ..., description="Test basıncı (MPa)."
    )
    test_date: Optional[date] = Field(
        default=None, description="Test tarihi."
    )
    test_type: str = Field(
        default="Hydrostatic", description="Test tipi (hidrostatik/pnömatik)."
    )
    design_code: str = Field(
        ..., description="Tasarım standardı (ör. 'EN 13445', 'ASME VIII-1')."
    )
    design_code_edition: str = Field(
        ..., description="Standart sürümü."
    )
    ce_marking: bool = Field(
        default=True, description="CE işareti uygulanacak mı?"
    )
    notify_body_number: Optional[str] = Field(
        default=None,
        description="Onaylanmış kuruluş numarası (ör. '0044')."
    )
    ped_category: str = Field(
        ..., description="PED kategorisi (ör. 'Category III')."
    )
    fluid_group: str = Field(
        ..., description="Akışkan grubu ('Group 1' veya 'Group 2')."
    )
    conformity_module: str = Field(
        ..., description="Uygunluk modülü (ör. 'B+D', 'G')."
    )

    def to_markdown(self) -> str:
        """İsim plakası bilgilerini markdown olarak üret."""
        ce_line = f"CE {self.notify_body_number}" if self.ce_marking and self.notify_body_number else "CE" if self.ce_marking else "—"
        return f"""
## İsim Plakası Bilgileri

| Alan | Değer |
|------|-------|
| İmalatçı | {self.manufacturer_name} |
| Adres | {self.manufacturer_address} |
| İmalat Yılı | {self.year_of_manufacture} |
| Ekipman Türü | {self.equipment_type} |
| Seri No | {self.serial_number} |
| PS | {self.maximum_allowable_pressure_ps} MPa |
| TS max | {self.maximum_allowable_temperature_ts_max} °C |
| TS min | {self.minimum_allowable_temperature_ts_min} °C |
| Hacim | {self.volume_liters} L |
| Test Basıncı | {self.test_pressure} MPa ({self.test_type}) |
| Tasarım Standardı | {self.design_code} {self.design_code_edition} |
| PED Kategorisi | {self.ped_category} |
| Akışkan Grubu | {self.fluid_group} |
| Uygunluk Modülü | {self.conformity_module} |
| CE | {ce_line} |
"""

    def to_html(self) -> str:
        """İsim plakası bilgilerini HTML tablosu olarak üret."""
        ce_line = f"CE {self.notify_body_number}" if self.ce_marking and self.notify_body_number else "CE" if self.ce_marking else "—"
        return f"""
<table>
<tr><th>Alan</th><th>Değer</th></tr>
<tr><td>İmalatçı</td><td>{self.manufacturer_name}</td></tr>
<tr><td>Adres</td><td>{self.manufacturer_address}</td></tr>
<tr><td>İmalat Yılı</td><td>{self.year_of_manufacture}</td></tr>
<tr><td>Ekipman Türü</td><td>{self.equipment_type}</td></tr>
<tr><td>Seri No</td><td>{self.serial_number}</td></tr>
<tr><td>PS</td><td>{self.maximum_allowable_pressure_ps} MPa</td></tr>
<tr><td>TS max</td><td>{self.maximum_allowable_temperature_ts_max} °C</td></tr>
<tr><td>TS min</td><td>{self.minimum_allowable_temperature_ts_min} °C</td></tr>
<tr><td>Hacim</td><td>{self.volume_liters} L</td></tr>
<tr><td>Test Basıncı</td><td>{self.test_pressure} MPa ({self.test_type})</td></tr>
<tr><td>Tasarım Standardı</td><td>{self.design_code} {self.design_code_edition}</td></tr>
<tr><td>PED Kategorisi</td><td>{self.ped_category}</td></tr>
<tr><td>Akışkan Grubu</td><td>{self.fluid_group}</td></tr>
<tr><td>Uygunluk Modülü</td><td>{self.conformity_module}</td></tr>
<tr><td>CE</td><td>{ce_line}</td></tr>
</table>
"""


class DeclarationOfConformity(BaseModel):
    """EU Declaration of Conformity (Uygunluk Beyanı) taslağı.

    PED 2014/68/EU Madde 14(2)'ye uygun DoC yapısı.

    Not: Bu bir taslaktır; nihai DoC imzalanmadan önce hukuki inceleme gerekir.
    """

    declaration_number: str = Field(
        default="", description="Beyan numarası."
    )
    issue_date: Optional[date] = Field(
        default=None, description="Düzenlenme tarihi."
    )
    manufacturer_name: str = Field(
        ..., description="İmalatçı adı."
    )
    manufacturer_address: str = Field(
        default="", description="İmalatçı adresı."
    )
    equipment_description: str = Field(
        ..., description="Ekipman tanımı."
    )
    equipment_type: str = Field(
        ..., description="Ekipman türü."
    )
    serial_number: str = Field(
        ..., description="Seri numarası."
    )
    ped_category: str = Field(
        ..., description="PED kategorisi."
    )
    conformity_module: str = Field(
        ..., description="Uygulanan uygunluk modülü."
    )
    harmonised_standards: List[str] = Field(
        default_factory=list,
        description="Uygulanan harmonize standartlar listesi."
    )
    notify_body_name: Optional[str] = Field(
        default=None, description="Onaylanmış kuruluş adı."
    )
    notify_body_number: Optional[str] = Field(
        default=None, description="Onaylanmış kuruluş numarası."
    )
    notify_body_certificate: Optional[str] = Field(
        default=None, description="Onaylanmış kuruluş sertifika numarası."
    )
    additional_information: str = Field(
        default="",
        description="Ek bilgiler."
    )

    def to_markdown(self) -> str:
        """DoC taslağını markdown olarak üret."""
        standards_str = "\n".join(f"  - {s}" for s in self.harmonised_standards) if self.harmonised_standards else "  —"
        nb_str = f"{self.notify_body_name} (No: {self.notify_body_number})" if self.notify_body_name else "—"
        cert_str = f"Sertifika No: {self.notify_body_certificate}" if self.notify_body_certificate else ""

        return f"""
# EU DECLARATION OF CONFORMITY

(EU Declaration of Conformity pursuant to Article 14(2) of Directive 2014/68/EU)

**Declaration Number:** {self.declaration_number or '—'}
**Date:** {self.issue_date or '—'}

## 1. Manufacturer
{self.manufacturer_name}
{self.manufacturer_address}

## 2. Equipment Description
{self.equipment_description}

**Type:** {self.equipment_type}
**Serial Number:** {self.serial_number}

## 3. PED Classification
**Category:** {self.ped_category}
**Conformity Module:** {self.conformity_module}

## 4. Harmonised Standards Applied
{standards_str}

## 5. Notified Body
{nb_str}
{cert_str}

## 6. Additional Information
{self.additional_information or '—'}

---
*Bu belge bir taslaktır. Nihai EU Declaration of Conformity, onaylanmış kuruluş
incelemesi ve hukuki değerlendirme sonrasında imzalanmalıdır.*

**Referans:** Directive 2014/68/EU, Article 14(2)
"""

    def to_html(self) -> str:
        """DoC taslağını HTML olarak üret."""
        standards_str = "<br>".join(self.harmonised_standards) if self.harmonised_standards else "—"
        nb_str = f"{self.notify_body_name} (No: {self.notify_body_number})" if self.notify_body_name else "—"

        return f"""
<div class="doc-declaration">
<h2>EU DECLARATION OF CONFORMITY</h2>
<p><em>Pursuant to Article 14(2) of Directive 2014/68/EU</em></p>
<table>
<tr><th>Alan</th><th>Değer</th></tr>
<tr><td>Beyan No</td><td>{self.declaration_number or '—'}</td></tr>
<tr><td>Tarih</td><td>{self.issue_date or '—'}</td></tr>
<tr><td>İmalatçı</td><td>{self.manufacturer_name}</td></tr>
<tr><td>Adres</td><td>{self.manufacturer_address}</td></tr>
<tr><td>Ekipman Tanımı</td><td>{self.equipment_description}</td></tr>
<tr><td>Ekipman Türü</td><td>{self.equipment_type}</td></tr>
<tr><td>Seri No</td><td>{self.serial_number}</td></tr>
<tr><td>PED Kategorisi</td><td>{self.ped_category}</td></tr>
<tr><td>Uygunluk Modülü</td><td>{self.conformity_module}</td></tr>
<tr><td>Harmonize Standartlar</td><td>{standards_str}</td></tr>
<tr><td>Onaylanmış Kuruluş</td><td>{nb_str}</td></tr>
</table>
<p><em>Bu belge bir taslaktır. Nihai DoC, onaylanmış kuruluş incelemesi sonrası imzalanmalıdır.</em></p>
</div>
"""


__all__ = ["DeclarationOfConformity", "NameplateInfo"]
