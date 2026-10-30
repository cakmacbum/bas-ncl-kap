"""Zick K katsayıları için tablo arama + lineer ara değerleme (P05).

Yapı: `ZICK_TABLES[ad]` = {"source": str, "verified": bool, "theta": [...],
"a_over_r": [...] | None, "values": [[...]]}  (values[satır=θ][sütun=A/R]; a_over_r yoksa
tek sütun).

ÖNEMLİ: Sayısal içerik Moss PVDM Prosedür 3-10 / Zick 1951 çizelgesinden DOĞRULANMIŞ
biçimde okunmadan buraya yazılmaz (K4: uydurma değer yok; repodaki kaynak incelemesi
K1'/Moss-Megyesy eşlemesini "doğrulanmadı" diye işaretler). Tablo boşken `lookup`
ZickTableError verir; çağıran taraf sonucu BLOCKED_CODE_DATA bırakır. Kapalı formül
bu aşamada kullanılmadı: Zick'in K1/K2/K7 integral ifadelerini bağımsız doğrulayamadım.
Tablo eklerken her girdiye `source` satırı yaz ve `verified: False` bırak.
"""

from __future__ import annotations

from bisect import bisect_right
from typing import Dict, Optional, Sequence

THETA_MIN, THETA_MAX = 120.0, 180.0

# Doldurulacak: "K1", "K2", "K3", "K6", "K7" (bkz. modül açıklaması).
ZICK_TABLES: Dict[str, dict] = {}


class ZickTableError(ValueError):
    """Tablo yok / girdi tablo aralığı dışında (kırpma yapılmaz)."""


def _interp(xs: Sequence[float], ys: Sequence[float], x: float, label: str) -> float:
    if len(xs) != len(ys) or not xs:
        raise ZickTableError(f"{label}: tablo bozuk")
    if x < xs[0] - 1e-9 or x > xs[-1] + 1e-9:
        raise ZickTableError(f"{label}={x:g} tablo aralığı dışında [{xs[0]:g}, {xs[-1]:g}]")
    if len(xs) == 1:
        return ys[0]
    i = min(max(bisect_right(xs, x) - 1, 0), len(xs) - 2)
    w = (x - xs[i]) / (xs[i + 1] - xs[i])
    return ys[i] + w * (ys[i + 1] - ys[i])


def lookup(name: str, theta_deg: float, a_over_r: Optional[float] = None,
           tables: Optional[Dict[str, dict]] = None) -> dict:
    """K değerini döndürür: {"value", "source", "verified"}. Aralık dışı/tablo yok -> ZickTableError."""
    tbl = (ZICK_TABLES if tables is None else tables).get(name)
    if not tbl:
        raise ZickTableError(f"{name}: doğrulanmış tablo programda yok")
    if not (THETA_MIN <= theta_deg <= THETA_MAX):
        raise ZickTableError(f"θ={theta_deg:g}° tablo aralığı dışında [{THETA_MIN:g}, {THETA_MAX:g}]")
    thetas, cols, rows = tbl["theta"], tbl.get("a_over_r"), tbl["values"]
    if cols:
        if a_over_r is None:
            raise ZickTableError(f"{name}: A/R gerekli")
        per_theta = [_interp(cols, row, a_over_r, "A/R") for row in rows]
    else:
        per_theta = [row[0] for row in rows]
    value = _interp(thetas, per_theta, theta_deg, "θ")
    return {"value": value, "source": tbl["source"], "verified": bool(tbl.get("verified", False))}
