"""Paket yolu bootstrap'ı.

Monorepo paketleri editable install edilmeden çalıştırılabilsin diye
packages/*/src dizinlerini sys.path'e ekler (conftest.py ile aynı mantık).
API'nin herhangi bir modülünü import etmeden ÖNCE bu modül import edilmelidir.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SUITE_ROOT = Path(__file__).resolve().parents[2]  # .../pressure-vessel-suite


def bootstrap_packages() -> None:
    packages = _SUITE_ROOT / "packages"
    if not packages.is_dir():
        return
    for pkg_dir in packages.iterdir():
        src = pkg_dir / "src"
        if src.is_dir():
            s = str(src)
            if s not in sys.path:
                sys.path.insert(0, s)


bootstrap_packages()
