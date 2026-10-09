# Basınçlı Kap Suite API — CadQuery pip wheel'leri (cadquery-ocp) ile slim imajda çalışır.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# OCP (OpenCASCADE) için gereken paylaşımlı kütüphaneler
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglu1-mesa libxrender1 libxext6 libsm6 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY apps/__init__.py apps/__init__.py
COPY apps/api apps/api
COPY packages packages

RUN useradd --create-home appuser
USER appuser

# Render $PORT verir; yerelde 8000
CMD ["sh", "-c", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
