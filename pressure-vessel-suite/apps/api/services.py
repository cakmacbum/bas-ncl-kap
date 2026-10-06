"""Motor sarmalayıcıları — hesap paketlerini API için ince bir katmanla sarar.

K1/K7: Hesap mantığı paketlerde kalır; burada yalnızca çağrı/serileştirme yapılır.
"""

from __future__ import annotations

import logging
import math
import multiprocessing
import tempfile
from typing import Any, Dict, Optional

from domain import CalculationCode, VesselProject  # type: ignore
from code_asme_viii_1 import ASMEVIII1DesignCode  # type: ignore
from code_en_13445 import EN13445DesignCode  # type: ignore
from calc_core.orchestrator import CalculationOrchestrator, OrchestratorResult  # type: ignore
from calc_core.verification import validate_suite  # type: ignore
from calc_core.volume_mass import calculate_vessel_volume_mass  # type: ignore
from report_engine.generator import ReportGenerator  # type: ignore
from compliance import ESRMatrix  # type: ignore
from ped_2014_68_eu import (  # type: ignore
    ClassificationInput,
    FluidClassification,
    PEDClassificationEngine,
    EquipmentType,
    FluidPhasePED,
    GHSClassification,
)

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

# STEP tanıyıcı (P01) — yoksa uç 503 döner, uygulama yine de açılır.
try:
    from cad_engine.step_import import recognize_step  # type: ignore
except Exception:  # pragma: no cover
    recognize_step = None  # type: ignore

logger = logging.getLogger("basincli-kap.api")

# Tanıma ayrı süreçte koşar (OCC olay döngüsünü/sunucuyu kilitlemesin, takılırsa
# öldürülebilsin). Süre, çocuk sürecin OCP import'unu (~4-5 sn) da kapsar.
STEP_RECOGNITION_TIMEOUT_S = 30.0


class StepRecognitionTimeout(Exception):
    """Tanıma süresi aşıldı; süreç öldürüldü."""


class StepRecognitionFailed(Exception):
    """Tanıma süreci sonuç vermeden öldü/çöktü ya da hata fırlattı."""


def _step_worker(fn, path: str, filename: Optional[str], conn) -> None:
    """Çocuk süreç girişi (spawn; modül seviyesinde olmalı)."""
    try:
        conn.send(("ok", fn(path, filename=filename).to_dict()))
    except BaseException as exc:  # sonuç yerine yalnız hata tipi döner
        conn.send(("error", type(exc).__name__))
    finally:
        conn.close()


def recognize_step_isolated(
    path: str, filename: Optional[str] = None, timeout: Optional[float] = None
) -> Dict[str, Any]:
    """`recognize_step`'i ayrı bir süreçte çalıştır, `to_dict()` sonucunu döndür.

    Bloklayıcıdır — async uçtan threadpool ile çağrılmalı.
    Raises: StepRecognitionTimeout, StepRecognitionFailed.
    """
    if timeout is None:
        timeout = STEP_RECOGNITION_TIMEOUT_S
    ctx = multiprocessing.get_context("spawn")
    recv_conn, send_conn = ctx.Pipe(duplex=False)
    proc = ctx.Process(
        target=_step_worker,
        args=(recognize_step, str(path), filename, send_conn),
        daemon=True,
    )
    try:
        proc.start()
        send_conn.close()  # çocuk ölürse recv EOFError versin
        if not recv_conn.poll(timeout):
            raise StepRecognitionTimeout()
        try:
            kind, payload = recv_conn.recv()
        except (EOFError, OSError):
            proc.join(5)
            raise StepRecognitionFailed(f"süreç sonuç vermeden sonlandı (exitcode={proc.exitcode})")
        if kind != "ok":
            raise StepRecognitionFailed(f"tanıyıcı hata fırlattı: {payload}")
        proc.join(5)
        return payload
    finally:
        recv_conn.close()
        send_conn.close()
        if proc.is_alive():
            proc.kill()
        if proc.pid is not None:
            proc.join(5)


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


def _build_design_code(project: VesselProject):
    """Projede seçilen standardın motorunu açıkça oluşturur.

    Standart seçimi hiçbir durumda sessizce başka bir motora düşmez.
    """
    if project.calculation_code == CalculationCode.ASME_VIII_1:
        return ASMEVIII1DesignCode(edition=project.code_edition or "2025")
    if project.calculation_code == CalculationCode.EN_13445:
        return EN13445DesignCode(edition=project.code_edition or "2021+A1:2023")
    raise ValueError(f"Unsupported calculation code: {project.calculation_code}")


def run_calculation(project: VesselProject) -> OrchestratorResult:
    """Projede seçilen hesap standardının hesap sırasını çalıştır."""
    code = _build_design_code(project)
    return CalculationOrchestrator(code).run(project)


def _verification_section(results) -> Dict[str, Any]:
    """Yayın-öncesi doğrulama kapısı (bilgilendirici; hesabı değiştirmez/engellemez)."""
    try:
        return validate_suite(results).to_dict()
    except Exception as e:  # pragma: no cover - kapı hatası hesabı düşürmemeli
        return {"case_name": "calculation-run", "passed": False, "checks": [],
                "errors": [f"Doğrulama kapısı çalıştırılamadı: {e}"]}


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
        "verification": _verification_section(result.results),
    }
    return _json_safe(payload)


def generate_report_html(project: VesselProject) -> str:
    """Tam HTML rapor üret (PED/ESR verisi EN raporuna bağlanır)."""
    result = run_calculation(project)
    vm = calculate_vessel_volume_mass(project)
    ped_result = None
    compliance = None
    if project.fluid is not None:
        try:
            expected_components = {
                ("shell", item.section_id) for item in project.shell_sections
            } | {
                ("head", item.head_id) for item in project.heads
            } | {
                ("cone", item.cone_id) for item in project.cones
            }
            reported_components = [
                (item.component_type, item.component_id) for item in vm.volume_results
            ]
            if (
                not expected_components
                or
                len(reported_components) != len(expected_components)
                or set(reported_components) != expected_components
            ):
                raise ValueError(
                    "PED classification blocked: vessel volume does not cover each "
                    "pressure-bearing component exactly once."
                )
            phase = FluidPhasePED.GAS if project.fluid.phase.lower() in {"gas", "steam", "vapor"} else FluidPhasePED.LIQUID
            hazard_classes = []
            for value in project.fluid.hazard_classes:
                try:
                    hazard_classes.append(GHSClassification(value))
                except ValueError:
                    # Bilinmeyen sınıflandırma güvenli tarafta Group 2'ye
                    # düşürülür; kullanıcı girdisi rapora yine yazılır.
                    continue
            ped_input = ClassificationInput(
                equipment_type=EquipmentType.VESSEL,
                ps_mpa=project.design_conditions.maximum_allowable_pressure_ps,
                volume_liters=vm.total_inner_volume_liters,
                ts_min_c=project.design_conditions.minimum_design_temperature,
                ts_max_c=project.design_conditions.design_temperature,
                fluids=[FluidClassification(
                    fluid_name=project.fluid.name,
                    phase=phase,
                    ghs_classifications=hazard_classes,
                )],
            )
            ped_result = PEDClassificationEngine().classify(ped_input)
            compliance = ESRMatrix.default_for_vessel()
            compliance.project_number = project.project_number
        except Exception as exc:
            # Rapor üretimi hesap sonucunu kaybetmemeli; başarısız PED yolu
            # raporda "çalıştırılmadı" olarak kalır.
            result.add_error(f"PED classification error: {exc}")
    rep = ReportGenerator().generate(
        project, result, vm, ped_result=ped_result, compliance=compliance
    )
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
