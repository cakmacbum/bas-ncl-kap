"""Vercel Python sunucusuz fonksiyon girişi (ASGI).

/api/* istekleri vercel.json rewrite'ı ile buraya gelir; FastAPI uygulaması
apps/api/main.py içindeki `app`tır. Kök dizin sys.path'e eklenir ki
`apps.api` ve (bootstrap ile) packages/*/src içe aktarılabilsin.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from apps.api.main import app  # noqa: E402,F401
