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
from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from domain import VesselProject, compute_input_hash  # type: ignore

from apps.api import services
from apps.api.geometry_agent import (
    AgentNotConfiguredError,
    AgentProviderError,
    GeometryAgentRequest,
    GeometryAgentResponse,
    interpret_geometry_command,
)
from apps.api.store import store

logger = logging.getLogger("basincli-kap.api")

app = FastAPI(
    title="Basınçlı Kap Tasarım Suite API",
    description="ASME VIII-1 hesap, CAD/STEP ve rapor motorunu saran REST katmanı.",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Beklenmeyen sunucu hatalarında jenerik 'Internal Server Error' yerine
    gerçek hata tipini/mesajını döndür — böylece frontend'de teşhis edilebilir."""
    logger.exception("Beklenmeyen hata (%s %s): %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Sunucu hatası: {type(exc).__name__}: {exc}"},
    )

# Vite geliştirme sunucusuna CORS izni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "cad_available": services.CADQUERY_AVAILABLE}


@app.post("/api/agent/geometry/interpret", response_model=GeometryAgentResponse)
def geometry_agent_interpret(payload: GeometryAgentRequest) -> GeometryAgentResponse:
    """Interpret a sentence as a safe, review-only basic geometry patch."""
    try:
        return interpret_geometry_command(payload)
    except AgentNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AgentProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/projects")
def list_projects() -> list:
    return store.summaries()


@app.post("/api/projects", status_code=201)
def create_project(project: VesselProject) -> dict:
    project_id = store.create(project)
    return {"id": project_id, "input_file_hash": compute_input_hash(project)}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> VesselProject:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return project


@app.put("/api/projects/{project_id}")
def update_project(project_id: str, project: VesselProject) -> dict:
    if not store.update(project_id, project):
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return {"id": project_id, "input_file_hash": compute_input_hash(project)}


@app.post("/api/projects/{project_id}/calculate")
def calculate(project_id: str) -> dict:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return services.calculation_payload(project)


@app.get("/api/projects/{project_id}/report.html", response_class=HTMLResponse)
def report_html(project_id: str) -> HTMLResponse:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    return HTMLResponse(content=services.generate_report_html(project))


@app.get("/api/projects/{project_id}/model.step")
def model_step(project_id: str) -> FileResponse:
    project = store.get(project_id)
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
def model_stl(project_id: str) -> FileResponse:
    project = store.get(project_id)
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


@app.post("/api/import/step")
async def import_step(request: Request) -> dict:
    """Ham STEP baytlarını al, tanıyıcıya ver, ölçü önerilerini döndür."""
    if services.recognize_step is None:
        raise HTTPException(status_code=503, detail="STEP tanıyıcı kullanılamıyor (CAD motoru yok).")

    # Content-Length'e güvenme: okurken say.
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > STEP_MAX_BYTES:
            raise HTTPException(status_code=413, detail="Dosya 20 MB sınırını aşıyor.")

    if b"ISO-10303-21" not in bytes(data[:4096]):
        raise HTTPException(status_code=415, detail="Geçerli bir STEP dosyası değil (ISO-10303-21 başlığı yok).")

    filename = _safe_filename(request.headers.get("x-filename"))
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        recognition = services.recognize_step(tmp_path, filename=filename)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    result = recognition.to_dict()
    if result.get("status") == "BLOCKED":
        raise HTTPException(status_code=503, detail="CAD motoru (CadQuery) kurulu değil.")
    return services._json_safe(result)
