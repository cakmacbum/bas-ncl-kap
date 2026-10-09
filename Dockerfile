# Render (repo kökünden build) — Pressure Vessel Suite API (FastAPI + CadQuery)
# Asıl kaynak pressure-vessel-suite/ altında; bu dosya yalnız yolları kökten verir.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AUTH_MODE=anonymous \
    CORS_ORIGINS=https://pv-suite-app.vercel.app \
    GEOMETRY_AGENT_ENABLED=false

# OCP (OpenCASCADE) için gereken paylaşımlı kütüphaneler
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglu1-mesa libxrender1 libxext6 libsm6 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pressure-vessel-suite/requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY pressure-vessel-suite/apps/__init__.py apps/__init__.py
COPY pressure-vessel-suite/apps/api apps/api
COPY pressure-vessel-suite/packages packages

RUN useradd --create-home appuser
USER appuser

CMD ["sh", "-c", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
