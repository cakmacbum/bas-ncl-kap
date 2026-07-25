"""Motor sarmalayıcıları — hesap paketlerini API için ince bir katmanla sarar.

K1/K7: Hesap mantığı paketlerde kalır; burada yalnızca çağrı/serileştirme yapılır.
"""

from __future__ import annotations

import math
import tempfile
from typing import Any, Dict, Optional

from domain import VesselProject  # type: ignore
from code_asme_viii_1 import ASMEVIII1DesignCode  # type: ignore
from calc_core.orchestrator import CalculationOrchestrator, OrchestratorResult  # type: ignore
from calc_core.volume_mass import calculate_vessel_volume_mass  # type: ignore
from report_engine.generator import ReportGenerator  # type: ignore

try:
    from cad_engine.vessel_builder import (  # type: ignore
        build_vessel,
        export_step,
        export_stl,
        CADQUERY_AVAILABLE,
    )
except Exception:  # pragma: no cover
    build_vessel = None  # type: ignore
    export_step = None  # type: ignore
    export_stl = None  # type: ignore
    CADQUERY_AVAILABLE = False


def _json_safe(obj: Any) -> Any:
    """Yanıtı JSON-güvenli hale getir: sonlu olmayan float'ları (inf/-inf/nan) None'a çevir.

    Starlette JSONResponse `allow_nan=False` ile serileştirdiği için, herhangi bir hesap
    sonucundaki inf/nan tüm yanıtı 500 ile çökertir. Bu temizleyici o hata sınıfını bitirir;
    UI bu değerleri "—" gösterir.
    """
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


def run_calculation(project: VesselProject) -> OrchestratorResult:
    """ASME VIII-1 hesap sırasını çalıştır."""
    code = ASMEVIII1DesignCode(edition=project.code_edition or "2025")
    return CalculationOrchestrator(code).run(project)


def calculation_payload(project: VesselProject) -> Dict[str, Any]:
    """Hesap sonucu + global MAWP + hacim/ağırlığı JSON'a çevir."""
    result = run_calculation(project)
    global_mawp = result.get_global_mawp()

    # Hacim/ağırlık korumasız aritmetik içerir; hata olursa 500 yerine null dön.
    try:
        vm = calculate_vessel_volume_mass(project)
        volume_mass = {
            "inner_volume_liters": round(vm.total_inner_volume_liters, 2),
            "inner_volume_m3": round(vm.total_inner_volume_m3, 4),
            "metal_mass_kg": round(vm.total_metal_mass_kg, 1),
        }
    except Exception as e:  # pragma: no cover
        volume_mass = {"inner_volume_liters": None, "inner_volume_m3": None, "metal_mass_kg": None}
        result.add_error(f"Volume/mass calc error: {e}")

    payload = {
        "project_number": result.project_number,
        "project_name": result.project_name,
        "code": result.code,
        "edition": result.edition,
        "global_mawp_mpa": global_mawp,
        "results": [r.to_dict() for r in result.results],
        "errors": result.errors,
        "volume_mass": volume_mass,
    }
    return _json_safe(payload)


def generate_report_html(project: VesselProject) -> str:
    """Tam HTML rapor üret (izlenebilirlik bloğuyla)."""
    result = run_calculation(project)
    vm = calculate_vessel_volume_mass(project)
    rep = ReportGenerator().generate(project, result, vm)
    return rep.html_content


def generate_step(project: VesselProject) -> Optional[str]:
    """STEP dosyası üret; CadQuery yoksa None döner. Geçici dosya yolu döndürür."""
    if not CADQUERY_AVAILABLE or build_vessel is None:
        return None
    cad = build_vessel(project)
    if not cad.success:
        return None
    tmp = tempfile.NamedTemporaryFile(suffix=".step", delete=False)
    tmp.close()
    return export_step(cad.shape, tmp.name)


def generate_stl(project: VesselProject) -> Optional[str]:
    """STL mesh üret (web 3D görüntüleyici için); CadQuery yoksa None döner."""
    if not CADQUERY_AVAILABLE or build_vessel is None or export_stl is None:
        return None
    cad = build_vessel(project)
    if not cad.success:
        return None
    tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
    tmp.close()
    return export_stl(cad.shape, tmp.name)
