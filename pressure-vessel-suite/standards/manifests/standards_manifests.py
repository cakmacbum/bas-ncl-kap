"""StandardPack modeli — sürümlü standart paketi tanımı.

K3 kuralı: Standart ve malzeme sürümlerini koda gömme.
Her proje kendi StandardPack'ine kilitlenir; harmonize liste değişse bile eski proje değişmez.

Referans: Kaynak §2
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class StandardPack(BaseModel):
    """Sürümlü standart paketi tanımı.

    Bir projenin kullandığı tüm standartların sürüm bilgisini içerir.
    Proje başında seçilip kilitlenir.
    """

    pack_id: str = Field(
        ..., description="Standart paketi tanımı (ör. 'ASME-2025', 'EN-13445-2021')."
    )
    code_family: str = Field(
        ..., description="Standart ailesi (ör. 'ASME VIII-1', 'EN 13445')."
    )
    base_edition: str = Field(
        ..., description="Temel sürüm (ör. '2025', '2021')."
    )
    amendments: List[str] = Field(
        default_factory=list,
        description="Düzeltmeler (ör. ['A1:2023', 'A2:2024'])."
    )
    ped_directive: str = Field(
        default="2014/68/EU",
        description="PED direktif numarası.",
    )
    harmonised_list_date: Optional[str] = Field(
        default=None,
        description="Harmonize liste tarihi (ör. '2024-01-15').",
    )
    material_standard: str = Field(
        default="",
        description="Malzeme standardı (ör. 'ASME II-D', 'EN 10028')."
    )
    material_edition: str = Field(
        default="",
        description="Malzeme standardı sürümü.",
    )
    welding_standard: str = Field(
        default="",
        description="Kaynak standardı (ör. 'ASME IX', 'EN ISO 15614')."
    )
    welding_edition: str = Field(
        default="",
        description="Kaynak standardı sürümü.",
    )
    nde_standard: str = Field(
        default="",
        description="NDE standardı (ör. 'ASME V', 'EN ISO 17637')."
    )
    nde_edition: str = Field(
        default="",
        description="NDE standardı sürümü.",
    )
    notes: Optional[str] = Field(
        default=None, description="Ek notlar."
    )

    @property
    def full_edition(self) -> str:
        """Tam sürüm bilgisi (temel + düzeltmeler)."""
        if self.amendments:
            return f"{self.base_edition}+{'+'.join(self.amendments)}"
        return self.base_edition

    @property
    def display_name(self) -> str:
        """Görüntüleme adı."""
        return f"{self.code_family} {self.full_edition}"


def load_standard_pack(pack_id: str, manifests_dir: Optional[str] = None) -> StandardPack:
    """Standart paketini manifest dosyasından yükle.

    Args:
        pack_id: Paket tanımı.
        manifests_dir: Manifest dizini (varsayılan: bu dosyanın dizini).

    Returns:
        StandardPack.

    Raises:
        FileNotFoundError: Manifest dosyası bulunamazsa.
    """
    if manifests_dir is None:
        manifests_dir = str(Path(__file__).parent)

    manifest_path = Path(manifests_dir) / f"{pack_id}.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Standart paketi manifest dosyası bulunamadı: {manifest_path}")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return StandardPack.model_validate(data)


# ── Hazır standart paketleri ────────────────────────────────────────────────────

ASME_VIII_1_2025 = StandardPack(
    pack_id="asme-viii-1-2025",
    code_family="ASME VIII-1",
    base_edition="2025",
    ped_directive="2014/68/EU",
    material_standard="ASME II-D",
    material_edition="2025",
    welding_standard="ASME IX",
    welding_edition="2025",
    nde_standard="ASME V",
    nde_edition="2025",
)

EN_13445_2021 = StandardPack(
    pack_id="en-13445-2021",
    code_family="EN 13445",
    base_edition="2021",
    amendments=["A1:2023"],
    ped_directive="2014/68/EU",
    material_standard="EN 10028",
    material_edition="2017",
    welding_standard="EN ISO 15614",
    welding_edition="2017",
    nde_standard="EN ISO 17637",
    nde_edition="2016",
)


__all__ = [
    "StandardPack",
    "load_standard_pack",
    "ASME_VIII_1_2025",
    "EN_13445_2021",
]
