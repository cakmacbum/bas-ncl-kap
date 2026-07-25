"""Faz 4 test fixtures."""

import sys
from pathlib import Path

# Paketlerin src dizinlerini sys.path'e ekle
_SUITE_ROOT = Path(__file__).resolve().parent.parent.parent
for pkg_dir in (_SUITE_ROOT / "packages").iterdir():
    src = pkg_dir / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))

# Standards dizinini de ekle
standards_dir = _SUITE_ROOT / "standards"
if standards_dir.is_dir():
    for sub in ["manifests", "clause-mappings"]:
        sys.path.insert(0, str(standards_dir / sub))
