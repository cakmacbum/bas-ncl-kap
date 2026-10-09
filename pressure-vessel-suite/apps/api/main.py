"""Basınçlı Kap Suite — FastAPI uygulama servisi.

Python hesap paketlerini saran ince REST katmanı (BASINCLI-KAP §4).
Çalıştırma:  uvicorn apps.api.main:app --reload  (pressure-vessel-suite kökünden)
"""

from __future__ import annotations

# Paket yollarını her şeyden ÖNCE ayarla
from apps.api import _bootstrap  # noqa: F401

import logging
import os
import tempfile
import threading
from pathlib import Path
from urllib.parse import unquote

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from domain import VesselProject, compute_input_hash  # type: ignore

from apps.api import services
from apps.api.auth import auth_mode, require_owner
from apps.api.geometry_agent import (
    AgentNotConfiguredError,
    AgentProviderError,
    GeometryAgentRequest,
    GeometryAgentResponse,
    interpret_geometry_command,
)
from apps.api.store import ProjectLimitReached, store

logger = logging.getLogger("basincli-kap.api")

app = FastAPI(
    title="Basınçlı Kap Tasarım Suite API",
    description="ASME VIII-1 hesap, CAD/STEP ve rapor motorunu saran REST katmanı.",
    version="0.1.0",
)


@app.on_event("startup")
def _log_auth_mode() -> None:
    logger.info("AUTH_MODE=%s", auth_mode())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Beklenmeyen hatayı sunucuda logla; istemciye ayrıntı verme."""
    logger.exception("Beklenmeyen hata (%s %s)", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def _cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-Filename", "X-Client-Id"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "cad_available": services.CADQUERY_AVAILABLE}


@app.post("/api/agent/geometry/interpret", response_model=GeometryAgentResponse, dependencies=[Depends(require_owner)])
def geometry_agent_interpret(payload: GeometryAgentRequest) -> GeometryAgentResponse:
    """Interpret a sentence as a safe, review-only basic geometry patch."""
    if os.environ.get("GEOMETRY_AGENT_ENABLED", "").strip().lower() not in {"1", "true", "yes"}:
        raise HTTPException(status_code=503, detail="AI assistant is not available yet")
    try:
        return interpret_geometry_command(payload)
    except AgentNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AgentProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/projects")
def list_projects(owner: str = Depends(require_owner)) -> list:
    return store.summaries(owner)


@app.post("/api/projects", status_code=201)
def create_project(project: VesselProject, owner: str = Depends(require_owner)) -> dict:
    try:
        project_id = store.create(owner, project)
    except ProjectLimitReached:
        raise HTTPException(status_code=429, detail="Project limit reached") from None
    return {"id": project_id, "input_file_hash": compute_input_hash(project)}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str, owner: str = Depends(require_owner)) -> VesselProject:
    project = store.get(owner, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return project


@app.put("/api/projects/{project_id}")
def update_project(project_id: str, project: VesselProject, owner: str = Depends(require_owner)) -> dict:
    if not store.update(owner, project_id, project):
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return {"id": project_id, "input_file_hash": compute_input_hash(project)}


@app.post("/api/projects/{project_id}/calculate")
def calculate(project_id: str, owner: str = Depends(require_owner)) -> dict:
    project = store.get(owner, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return services.calculation_payload(project)


@app.get("/api/projects/{project_id}/report.html", response_class=HTMLResponse)
def report_html(project_id: str, owner: str = Depends(require_owner)) -> HTMLResponse:
    project = store.get(owner, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return HTMLResponse(content=services.generate_report_html(project))


@app.get("/api/projects/{project_id}/model.step")
def model_step(project_id: str, owner: str = Depends(require_owner)) -> FileResponse:
    project = store.get(owner, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    path = services.generate_step(project)
    if path is None:
        raise HTTPException(
            status_code=503,
            detail="STEP üretilemedi (CadQuery kurulu değil veya model hatası).",
        )
    filename = f"{project.project_number or 'vessel'}.step"
    return FileResponse(path, filename=filename, media_type="application/step")


@app.get("/api/projects/{project_id}/model.stl")
def model_stl(project_id: str, owner: str = Depends(require_owner)) -> FileResponse:
    project = store.get(owner, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    path = services.generate_stl(project)
    if path is None:
        raise HTTPException(
            status_code=503,
            detail="STL üretilemedi (CadQuery kurulu değil veya model hatası).",
        )
    filename = f"{project.project_number or 'vessel'}.stl"
    return FileResponse(path, filename=filename, media_type="model/stl")


# --- STEP içe aktarma (proje deposuna dokunmaz) ---
STEP_MAX_BYTES = 20 * 1024 * 1024


def _safe_filename(raw: str | None) -> str | None:
    """X-Filename başlığından yalnız dosya adını al (URL-decode, yol bileşenlerini at)."""
    if not raw:
        return None
    name = unquote(raw).replace("\\", "/").split("/")[-1].strip()
    name = "".join(ch for ch in name if ch.isprintable())[:200]
    return name or None


STEP_HEADER_PROBE = 4096
STEP_MAX_CONCURRENT = 2
# Eşzamanlı tanıma sınırı (her biri ayrı süreç + OCC belleği). Dolu → 429, kuyruk yok.
_step_slots = threading.BoundedSemaphore(STEP_MAX_CONCURRENT)


def _check_step_header(head: bytes) -> None:
    if b"ISO-10303-21" not in head[:STEP_HEADER_PROBE]:
        raise HTTPException(status_code=415, detail="Geçerli bir STEP dosyası değil (ISO-10303-21 başlığı yok).")


async def _receive_step(request: Request, dest: str) -> None:
    """Gövdeyi akışta `dest`'e yaz: boyutu okurken say, başlığı ilk 4 KB'ta denetle."""
    size = 0
    head = b""
    checked = False
    try:
        with open(dest, "wb") as fh:
            async for chunk in request.stream():
                if not chunk:
                    continue
                size += len(chunk)
                if size > STEP_MAX_BYTES:
                    raise HTTPException(status_code=413, detail="Dosya 20 MB sınırını aşıyor.")
                if not checked:
                    head += chunk[: STEP_HEADER_PROBE - len(head)]
                    if len(head) >= STEP_HEADER_PROBE:
                        _check_step_header(head)
                        checked = True
                fh.write(chunk)
    except OSError:
        logger.exception("STEP yüklemesi geçici dosyaya yazılamadı")
        raise HTTPException(status_code=500, detail="Yüklenen dosya geçici alana yazılamadı.")
    if not checked:
        _check_step_header(head)


@app.post("/api/import/step", dependencies=[Depends(require_owner)])
async def import_step(request: Request) -> dict:
    """Ham STEP baytlarını al, tanıyıcıya (ayrı süreçte) ver, ölçü önerilerini döndür."""
    if services.recognize_step is None:
        raise HTTPException(status_code=503, detail="STEP tanıyıcı kullanılamıyor (CAD motoru yok).")

    filename = _safe_filename(request.headers.get("x-filename"))
    # Windows'ta kilitli dosya silinemezse temizlik hatası asıl yanıtı ezmesin.
    with tempfile.TemporaryDirectory(prefix="step-import-", ignore_cleanup_errors=True) as tmp_dir:
        tmp_path = os.path.join(tmp_dir, "upload.step")
        await _receive_step(request, tmp_path)

        if not _step_slots.acquire(blocking=False):
            raise HTTPException(
                status_code=429,
                detail="Şu anda çok fazla STEP içe aktarma işleniyor; biraz sonra tekrar deneyin.",
                headers={"Retry-After": "10"},
            )
        try:
            result = await run_in_threadpool(services.recognize_step_isolated, tmp_path, filename)
        except services.StepRecognitionTimeout:
            logger.warning("STEP tanıma zaman aşımı (%s)", filename)
            raise HTTPException(
                status_code=504,
                detail="STEP tanıma zaman aşımına uğradı — model çok karmaşık olabilir.",
            )
        except services.StepRecognitionFailed as exc:
            logger.error("STEP tanıma süreci başarısız (%s): %s", filename, exc)
            raise HTTPException(status_code=500, detail="STEP tanıma beklenmedik şekilde sonlandı.")
        finally:
            _step_slots.release()

    if result.get("status") == "BLOCKED":
        raise HTTPException(status_code=503, detail="CAD motoru (CadQuery) kurulu değil.")
    return services._json_safe(result)
