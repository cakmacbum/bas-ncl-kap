"""İzlenebilirlik bloğu — her raporda bulunması gereken bilgiler (kaynak §11).

Her raporda şu bilgiler bulunmalıdır:
  - Software version
  - Calculation engine version
  - Standard pack version
  - Material database version
  - Project revision
  - Calculation date
  - Input file hash
  - Report hash (rapor üretildikten sonra hesaplanır)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ── Sabit sürüm bilgileri ─────────────────────────────────────────────────────

SOFTWARE_VERSION = "0.1.0"
CALCULATION_ENGINE_VERSION = "0.1.0"
STANDARD_PACK_VERSION = "ASME VIII-1 2025"
MATERIAL_DB_VERSION = "manual-v1"


@dataclass
class TraceabilityBlock:
    """Rapor izlenebilirlik bloğu."""

    software_version: str = SOFTWARE_VERSION
    calculation_engine_version: str = CALCULATION_ENGINE_VERSION
    standard_pack_version: str = STANDARD_PACK_VERSION
    material_database_version: str = MATERIAL_DB_VERSION
    project_revision: str = ""
    calculation_date: str = ""
    input_file_hash: str = ""
    report_hash: str = ""  # Rapor üretildikten sonra doldurulur

    def to_dict(self) -> Dict[str, Any]:
        return {
            "software_version": self.software_version,
            "calculation_engine_version": self.calculation_engine_version,
            "standard_pack_version": self.standard_pack_version,
            "material_database_version": self.material_database_version,
            "project_revision": self.project_revision,
            "calculation_date": self.calculation_date,
            "input_file_hash": self.input_file_hash,
            "report_hash": self.report_hash,
        }

    def to_html(self) -> str:
        """İzlenebilirlik bloğunu HTML olarak üret."""
        rows = [
            ("Yazılım Sürümü", self.software_version),
            ("Hesap Motoru Sürümü", self.calculation_engine_version),
            ("Standart Paket Sürümü", self.standard_pack_version),
            ("Malzeme Veritabanı Sürümü", self.material_database_version),
            ("Proje Revizyonu", self.project_revision),
            ("Hesap Tarihi", self.calculation_date),
            ("Girdi Dosyası Hash", self.input_file_hash[:16] + "..." if len(self.input_file_hash) > 16 else self.input_file_hash),
            ("Rapor Hash", self.report_hash[:16] + "..." if len(self.report_hash) > 16 else self.report_hash),
        ]
        html = '<table class="traceability">\n'
        html += '<tr><th colspan="2">İzlenebilirlik Bilgileri</th></tr>\n'
        for label, value in rows:
            html += f'<tr><td><strong>{label}</strong></td><td>{value}</td></tr>\n'
        html += '</table>\n'
        return html


def build_traceability(
    project_revision: str = "",
    input_file_hash: str = "",
    calculation_date: Optional[str] = None,
) -> TraceabilityBlock:
    """İzlenebilirlik bloğu oluştur.

    Args:
        project_revision: Proje revizyonu.
        input_file_hash: Girdi dosyası SHA-256 hash'i.
        calculation_date: Hesap tarihi (None = şimdi).

    Returns:
        TraceabilityBlock.
    """
    return TraceabilityBlock(
        project_revision=project_revision,
        calculation_date=calculation_date or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        input_file_hash=input_file_hash,
    )


def compute_report_hash(html_content: str) -> str:
    """Rapor HTML'inin SHA-256 hash'ini üret.

    Args:
        html_content: Rapor HTML içeriği.

    Returns:
        Hex-digest.
    """
    return hashlib.sha256(html_content.encode("utf-8")).hexdigest()


__all__ = [
    "TraceabilityBlock",
    "build_traceability",
    "compute_report_hash",
    "SOFTWARE_VERSION",
    "CALCULATION_ENGINE_VERSION",
    "STANDARD_PACK_VERSION",
    "MATERIAL_DB_VERSION",
]
