"""WRC 537 / WRC 297 boyutsuz eğri tabloları — arama + ara değerleme (P07).

Yapı (her iki aile için aynı):
    CURVES[anahtar] = {
        "source": str,          # bülten + şekil numarası, okuma yöntemi
        "verified": bool,       # bağımsız ikinci okuma ile doğrulandı mı
        "x1": [...],            # WRC 537: γ = Rm/T   | WRC 297: λ (bkz. nozzle_loads)
        "x2": [...],            # WRC 537: β          | WRC 297: T/t
        "values": [[...]],      # values[i(x1)][j(x2)]
    }

ÖNEMLİ (K4/K6): WRC 107/537/297 eğrileri teliflidir ve bellekten güvenle
yazılamaz. Tablolar BİLEREK boştur; boşken `lookup` WrcCurveError verir ve hesap
BLOCKED_CODE_DATA kalır. Tablo eklenirken her girdiye `source` yazılır, ikinci
bağımsız okuma yapılmadan `verified: False` bırakılır. Kırpma/extrapolasyon yok:
tablo ekseni dışı girdi hata verir (P05 Zick deseni).

Ara değerleme: her iki eksende doğrusal (bilineer). Bültenler γ eksenini
logaritmik çizer; logaritmik ara değerleme gerekiyorsa tablo eklenirken eksen
`log10` dönüştürülmüş girilip `"x1_log": True` işaretlenir.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from typing import Dict, Optional, Sequence

# Doldurulacak: anahtarlar domain.nozzle_loads.WRC537_COEFFICIENT_KEYS ile aynı.
WRC537_CURVES: Dict[str, dict] = {}
# Doldurulacak: "shell.P.Nphi", "nozzle.ML.Mx" ... (bkz. nozzle_loads.WRC297_KEYS).
WRC297_CURVES: Dict[str, dict] = {}


class WrcCurveError(ValueError):
    """Tablo yok / bozuk / girdi tablo aralığı dışında (kırpma yapılmaz)."""


def _interp(xs: Sequence[float], ys: Sequence[float], x: float, label: str) -> float:
    if len(xs) != len(ys) or not xs:
        raise WrcCurveError(f"{label}: tablo bozuk")
    if any(b <= a for a, b in zip(xs, xs[1:])):
        raise WrcCurveError(f"{label}: eksen artan sırada değil")
    if x < xs[0] - 1e-9 or x > xs[-1] + 1e-9:
        raise WrcCurveError(f"{label}={x:g} tablo aralığı dışında [{xs[0]:g}, {xs[-1]:g}]")
    if len(xs) == 1:
        return ys[0]
    i = min(max(bisect_right(xs, x) - 1, 0), len(xs) - 2)
    w = (x - xs[i]) / (xs[i + 1] - xs[i])
    return ys[i] + w * (ys[i + 1] - ys[i])


def lookup(key: str, x1: float, x2: float, tables: Dict[str, dict]) -> dict:
    """Eğri değeri: {"value", "source", "verified"}. Tablo yok/aralık dışı → WrcCurveError."""
    tbl = tables.get(key)
    if not tbl:
        raise WrcCurveError(f"{key}: doğrulanmış eğri tablosu programda yok")
    xs1, xs2, rows = tbl["x1"], tbl["x2"], tbl["values"]
    if len(rows) != len(xs1):
        raise WrcCurveError(f"{key}: satır sayısı x1 eksenine eşit değil")
    q1 = math.log10(x1) if tbl.get("x1_log") else x1
    per_x1 = [_interp(xs2, row, x2, f"{key} x2") for row in rows]
    value = _interp(xs1, per_x1, q1, f"{key} x1")
    return {"value": value, "source": tbl["source"], "verified": bool(tbl.get("verified", False))}


def resolve(key: str, user: Optional[Dict[str, Optional[float]]], x1: float, x2: float,
            tables: Dict[str, dict]) -> dict:
    """Öncelik: kullanıcı okuması > programdaki tablo > hata (BLOCKED).

    Dönüş: {"value", "source", "verified"}; kullanıcı okuması `verified: False`
    (program bağımsız doğrulayamaz) ve source="user".
    """
    if user is not None and user.get(key) is not None:
        v = float(user[key])
        if not math.isfinite(v):
            raise WrcCurveError(f"{key}: sonlu olmayan kullanıcı değeri")
        return {"value": v, "source": "user", "verified": False}
    return lookup(key, x1, x2, tables)


__all__ = ["WRC537_CURVES", "WRC297_CURVES", "WrcCurveError", "lookup", "resolve"]
