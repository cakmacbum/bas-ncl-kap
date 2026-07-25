"""Project / Revision Service — tutarlılık mekanizması (kaynak §16).

Nominal kalınlık değişirse otomatik:
  1. MAWP yeniden hesaplanır
  2. Nozul takviyesi yeniden hesaplanır (Faz 3)
  3. Ağırlık/hacim güncellenir
  4. STEP yeniden üretilir (CadQuery varsa)
  5. Eski PDF rapor "OUTDATED" işaretlenir
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from domain.project import VesselProject
from calc_core.code_interface import DesignCode
from calc_core.orchestrator import CalculationOrchestrator, OrchestratorResult
from calc_core.volume_mass import VesselVolumeMassReport, calculate_vessel_volume_mass


@dataclass
class RevisionRecord:
    """Tek bir revizyon kaydı."""

    revision_id: str
    timestamp: str
    changes: Dict[str, Any]
    calc_result_summary: Dict[str, Any]
    report_hash: str = ""
    report_status: str = "CURRENT"  # "CURRENT" veya "OUTDATED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "revision_id": self.revision_id,
            "timestamp": self.timestamp,
            "changes": self.changes,
            "calc_result_summary": self.calc_result_summary,
            "report_hash": self.report_hash,
            "report_status": self.report_status,
        }


@dataclass
class RevisionUpdateResult:
    """Revizyon güncelleme sonucu."""

    project: VesselProject
    calc_result: OrchestratorResult
    volume_mass: VesselVolumeMassReport
    changes_detected: List[str]
    previous_report_outdated: bool = False
    step_regenerated: bool = False
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "changes_detected": self.changes_detected,
            "previous_report_outdated": self.previous_report_outdated,
            "step_regenerated": self.step_regenerated,
            "global_mawp": self.calc_result.get_global_mawp(),
            "total_mass_kg": self.volume_mass.total_metal_mass_kg,
            "total_volume_liters": self.volume_mass.total_inner_volume_liters,
        }


class ProjectRevisionService:
    """Proje revizyon yönetimi servisi.

    Kullanım:
        service = ProjectRevisionService(design_code)
        service.set_project(project)
        # Kalınlık değişikliği
        result = service.update_thickness("SHELL-01", 16.0)
    """

    def __init__(self, design_code: DesignCode):
        self.design_code = design_code
        self._project: Optional[VesselProject] = None
        self._revisions: List[RevisionRecord] = []
        self._current_report_hash: str = ""

    @property
    def project(self) -> Optional[VesselProject]:
        return self._project

    @property
    def revisions(self) -> List[RevisionRecord]:
        return list(self._revisions)

    def set_project(self, project: VesselProject) -> None:
        """Projeyi ayarla (ilk yükleme)."""
        self._project = project
        self._revisions.clear()
        self._current_report_hash = ""

    def update_thickness(
        self,
        component_id: str,
        new_thickness: float,
        regenerate_step: bool = True,
    ) -> RevisionUpdateResult:
        """Bileşen nominal kalınlığını güncelle ve her şeyi yeniden hesapla.

        Args:
            component_id: Güncellenecek bileşen ID'si (ör. "SHELL-01", "HEAD-L").
            new_thickness: Yeni nominal kalınlık (mm).
            regenerate_step: STEP dosyası yeniden üretilsin mi?

        Returns:
            RevisionUpdateResult.
        """
        if self._project is None:
            return RevisionUpdateResult(
                project=self._project,
                calc_result=OrchestratorResult(),
                volume_mass=VesselVolumeMassReport([], []),
                changes_detected=[],
                error="Proje ayarlanmamış. Önce set_project() çağırın.",
            )

        changes = []
        old_project = self._project

        # Gövde kesitlerinde ara
        new_shells = list(self._project.shell_sections)
        shell_found = False
        for i, shell in enumerate(new_shells):
            if shell.section_id == component_id:
                old_thickness = shell.nominal_thickness
                if old_thickness == new_thickness:
                    return RevisionUpdateResult(
                        project=self._project,
                        calc_result=OrchestratorResult(),
                        volume_mass=VesselVolumeMassReport([], []),
                        changes_detected=[],
                        error="Kalınlık değişmedi.",
                    )
                new_shells[i] = shell.model_copy(update={"nominal_thickness": new_thickness})
                changes.append(
                    f"{component_id}: nominal_thickness {old_thickness} → {new_thickness} mm"
                )
                shell_found = True
                break

        # Bombelerde ara
        new_heads = list(self._project.heads)
        head_found = False
        if not shell_found:
            for i, head in enumerate(new_heads):
                if head.head_id == component_id:
                    old_thickness = head.nominal_thickness
                    if old_thickness == new_thickness:
                        return RevisionUpdateResult(
                            project=self._project,
                            calc_result=OrchestratorResult(),
                            volume_mass=VesselVolumeMassReport([], []),
                            changes_detected=[],
                            error="Kalınlık değişmedi.",
                        )
                    new_heads[i] = head.model_copy(update={"nominal_thickness": new_thickness})
                    changes.append(
                        f"{component_id}: nominal_thickness {old_thickness} → {new_thickness} mm"
                    )
                    head_found = True
                    break

        if not shell_found and not head_found:
            return RevisionUpdateResult(
                project=self._project,
                calc_result=OrchestratorResult(),
                volume_mass=VesselVolumeMassReport([], []),
                changes_detected=[],
                error=f"Bileşen bulunamadı: {component_id}",
            )

        # Revizyon numarasını artır
        old_rev = self._project.revision
        new_rev = self._increment_revision(old_rev)

        # Güncellenmiş proje
        updated_project = self._project.model_copy(
            update={
                "shell_sections": new_shells,
                "heads": new_heads,
                "revision": new_rev,
            }
        )

        # 1. MAWP ve tüm hesapları yeniden çalıştır
        orch = CalculationOrchestrator(self.design_code)
        calc_result = orch.run(updated_project)

        # 2. Ağırlık/hacim güncelle
        volume_mass = calculate_vessel_volume_mass(updated_project)

        # 3. STEP yeniden üretim (opsiyonel — CadQuery varsa)
        step_regenerated = False
        if regenerate_step:
            try:
                from cad_engine.vessel_builder import build_vessel, export_step
                cad_result = build_vessel(updated_project)
                if cad_result.success:
                    step_regenerated = True
            except ImportError:
                pass  # CadQuery yok, STEP yeniden üretilmez

        # 4. Eski rapor OUTDATED
        previous_outdated = False
        if self._current_report_hash:
            previous_outdated = True
            self._mark_previous_report_outdated()

        # Revizyon kaydı
        record = RevisionRecord(
            revision_id=new_rev,
            timestamp=datetime.now(timezone.utc).isoformat(),
            changes=changes,
            calc_result_summary={
                "global_mawp": calc_result.get_global_mawp(),
                "total_mass_kg": volume_mass.total_metal_mass_kg,
                "all_passed": calc_result.all_passed,
            },
        )
        self._revisions.append(record)

        # Projeyi güncelle
        self._project = updated_project

        return RevisionUpdateResult(
            project=updated_project,
            calc_result=calc_result,
            volume_mass=volume_mass,
            changes_detected=changes,
            previous_report_outdated=previous_outdated,
            step_regenerated=step_regenerated,
        )

    def register_report(self, report_hash: str) -> None:
        """Rapor hash'ini kaydet (sonraki revizyonda OUTDATED işaretlemek için)."""
        self._current_report_hash = report_hash

    def _mark_previous_report_outdated(self) -> None:
        """Eski raporu OUTDATED işaretle."""
        for record in reversed(self._revisions):
            if record.report_hash == self._current_report_hash:
                record.report_status = "OUTDATED"
                break

    @staticmethod
    def _increment_revision(revision: str) -> str:
        """Revizyon numarasını artır: A → B → C ... Z → AA → AB ..."""
        if not revision:
            return "A"

        # Son harfi al ve artır
        last_char = revision[-1]
        prefix = revision[:-1]

        if last_char == "Z":
            return prefix + "AA" if prefix else "AA"
        else:
            return prefix + chr(ord(last_char) + 1)

    def get_history(self) -> List[Dict[str, Any]]:
        """Revizyon geçmişini getir."""
        return [r.to_dict() for r in self._revisions]

    def get_current_status(self) -> Dict[str, Any]:
        """Mevcut durum bilgisini getir."""
        if self._project is None:
            return {"error": "Proje ayarlanmamış."}

        return {
            "project_number": self._project.project_number,
            "revision": self._project.revision,
            "revision_count": len(self._revisions),
            "current_report_hash": self._current_report_hash,
        }


__all__ = ["ProjectRevisionService", "RevisionRecord", "RevisionUpdateResult"]
