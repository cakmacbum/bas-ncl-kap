"""Root conftest — Pressure Vessel Suite test configuration."""

import sys
from pathlib import Path

# Paketlerin src dizinlerini sys.path'e ekle (editable install gerektirmeden test çalıştırabilmek için)
_SUITE_ROOT = Path(__file__).resolve().parent.parent
for pkg_dir in (_SUITE_ROOT / "packages").iterdir():
    src = pkg_dir / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))

# apps/ (FastAPI) import edilebilsin diye suite kökünü de ekle
if str(_SUITE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SUITE_ROOT))
