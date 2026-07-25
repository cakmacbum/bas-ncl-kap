"""FEAdapter — FEA iskelet + adapter.

Parametrik CAD → basitleştirilmiş geometri → Gmsh mesh → CalculiX/Code_Aster
→ stress linearization → code acceptance.

Çözücü kurulu değilse modülü "REVIEW REQUIRED / mesh ve sınır şartları mühendis
onayı gerektirir" ile iskelet bırakır; sahte "PASS" ÜRETMEZ.

K5 kuralı: Her hesap denetlenebilir (CalculationResult).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

import shutil
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from calc_core.result import CalculationResult


@dataclass
class FEAConfig:
    """FEA yapılandırması."""
    solver: str = "calculix"  # "calculix" | "code_aster"
    mesh_size: float = 10.0   # mm
    element_type: str = "C3D10"  # Tetrahedral 10-node
    linear_elastic: bool = True
    pressure_load: float = 0.0  # MPa
    temperature_load: float = 0.0  # °C
    boundary_conditions: str = "fixed_base"  # "fixed_base" | "pinned" | "custom"


@dataclass
class MeshQuality:
    """Mesh kalite metrikleri."""
    total_elements: int = 0
    total_nodes: int = 0
    min_jacobian: float = 0.0
    max_aspect_ratio: float = 0.0
    quality_pass: bool = False
    warnings: List[str] = field(default_factory=list)


@dataclass
class StressLinearizationResult:
    """Stress linearization sonuçları."""
    membrane_stress: float = 0.0      # MPa
    bending_stress: float = 0.0       # MPa
    peak_stress: float = 0.0          # MPa
    total_stress: float = 0.0         # MPa
    classification: str = ""          # "primary", "secondary", "peak"
    path_id: str = ""


class FEAdapter:
    """FEA adaptörü — iskelet modül.

    Bu modül FEA pipeline'ının tüm aşamalarını tanımlar ancak:
    - Çözücü (CalculiX / Code_Aster) kurulu değilse → REVIEW REQUIRED
    - Mesh ve sınır şartları mühendis onayı gerektirir → REVIEW REQUIRED
    - Sahte "PASS" ÜRETMEZ

    Kullanım:
        adapter = FEAdapter()
        results = adapter.run_analysis(input_data)
    """

    def __init__(self, config: Optional[FEAConfig] = None):
        self.config = config or FEAConfig()

    def check_solver_availability(self) -> bool:
        """Çözücü kurulu mu?"""
        solver = self.config.solver.lower()
        if solver == "calculix":
            return shutil.which("ccx") is not None
        elif solver in ("code_aster", "code-aster"):
            return shutil.which("as_run") is not None
        return False

    def run_analysis(self, input_data: dict) -> CalculationResult:
        """FEA analizi çalıştır (iskelet).

        Args:
            input_data: {
                "project": VesselProject,
                "shell": ShellSection,
                "head": Head (optional),
                "mesh_config": dict (optional),
                "load_cases": List[dict] (optional),
                "stress_paths": List[dict] (optional),
            }

        Returns:
            CalculationResult — REVIEW_REQUIRED / NOT_CALCULATED.
            Sahte "PASS" ÜRETMEZ.
        """
        shell = input_data["shell"]
        project = input_data.get("project")

        result = CalculationResult(
            component_id=shell.section_id,
            component_type="system",
            calculation_type="fea_analysis",
            code="FEA",
            edition="Iskelet v0.1",
            clause_reference="ASME VIII-2 Part 5",
            formula_reference="Stress Linearization",
        )

        # Çözücü kontrolü
        solver_available = self.check_solver_availability()

        result.input_snapshot = {
            "solver": self.config.solver,
            "solver_available": solver_available,
            "mesh_size_mm": self.config.mesh_size,
            "element_type": self.config.element_type,
            "linear_elastic": self.config.linear_elastic,
        }

        if not solver_available:
            result.set_review_required(
                f"FEA solver '{self.config.solver}' is not installed or not found in PATH. "
                "This analysis requires a valid FEA solver (CalculiX or Code_Aster). "
                "Mesh and boundary conditions require engineer approval. "
                "This result must not be used for fabrication."
            )
            result.add_assumption(
                "FEA iskelet modülü: Çözücü kurulu değil. "
                "Mesh kalitesi, sınır şartları ve gerilme sınıflandırması "
                "mühendis onayı gerektirir."
            )
        else:
            # Çözücü varsa bile mesh ve BC onayı gerekir
            result.set_review_required(
                "FEA analysis results require engineer review. "
                "Mesh quality, boundary conditions, and stress classification "
                "must be validated by a qualified engineer before use. "
                "This result must not be used for fabrication."
            )
            result.add_assumption(
                "FEA iskelet modülü: Analiz sonuçları mühendis incelemesi gerektirir. "
                "Mesh kalitesi, sınır şartları ve gerilme sınıflandırması "
                "onaylanmadan kullanılamaz."
            )

        self._add_skeleton_intermediates(result, shell)

        # Stress linearization iskeleti (her iki durumda da eklenir)
        sl = StressLinearizationResult(
            membrane_stress=0.0,
            bending_stress=0.0,
            peak_stress=0.0,
            total_stress=0.0,
            classification="NOT_EVALUATED",
            path_id="PATH-01",
        )

        result.add_intermediate(
            "stress_linearization_membrane", sl.membrane_stress, "MPa",
            "Membrane stress (NOT EVALUATED — requires FEA run)"
        )
        result.add_intermediate(
            "stress_linearization_bending", sl.bending_stress, "MPa",
            "Bending stress (NOT EVALUATED — requires FEA run)"
        )
        result.add_intermediate(
            "stress_linearization_peak", sl.peak_stress, "MPa",
            "Peak stress (NOT EVALUATED — requires FEA run)"
        )

        # Code acceptance iskeleti
        result.add_intermediate(
            "code_acceptance_status", "NOT_EVALUATED", "-",
            "ASME VIII-2 Part 5 acceptance check — not evaluated in skeleton mode"
        )

        return result

    def _add_skeleton_intermediates(self, result: CalculationResult, shell) -> None:
        """İskelet ara değerleri ekle."""
        D = shell.inside_diameter or (shell.outside_diameter - 2 * shell.nominal_thickness)
        R_m = D / 2.0 + shell.nominal_thickness / 2.0
        t = shell.nominal_thickness

        result.add_intermediate("D_inside", D, "mm", "Inside diameter")
        result.add_intermediate("R_mean", R_m, "mm", "Mean radius")
        result.add_intermediate("t_nominal", t, "mm", "Nominal thickness")
        result.add_intermediate(
            "mesh_size", self.config.mesh_size, "mm",
            "Target mesh size (engineer approval required)"
        )
        result.add_intermediate(
            "element_type", self.config.element_type, "-",
            "Element type (engineer approval required)"
        )
        result.add_intermediate(
            "solver", self.config.solver, "-",
            "FEA solver"
        )

    def get_mesh_quality_report(self) -> MeshQuality:
        """Mesh kalite raporu (iskelet — gerçek mesh yok)."""
        return MeshQuality(
            total_elements=0,
            total_nodes=0,
            min_jacobian=0.0,
            max_aspect_ratio=0.0,
            quality_pass=False,
            warnings=[
                "Mesh not generated — skeleton mode. "
                "Mesh quality requires engineer validation.",
            ],
        )

    def classify_stress(
        self,
        membrane: float,
        bending: float,
        peak: float,
        S_allow: float,
    ) -> Dict[str, Any]:
        """ASME VIII-2 Part 5 gerilme sınıflandırması (iskelet).

        Bu fonksiyon gerilme sınıflandırma kurallarını tanımlar ancak
        gerçek FEA sonuçları olmadan değerlendirme yapmaz.

        Returns:
            {"status": "NOT_EVALUATED", "reason": str}
        """
        return {
            "status": "NOT_EVALUATED",
            "reason": (
                "Stress classification requires FEA results. "
                "This is a skeleton module — run actual FEA analysis first."
            ),
            "membrane_MPa": membrane,
            "bending_MPa": bending,
            "peak_MPa": peak,
            "S_allow_MPa": S_allow,
        }


__all__ = ["FEAdapter", "FEAConfig", "MeshQuality", "StressLinearizationResult"]
