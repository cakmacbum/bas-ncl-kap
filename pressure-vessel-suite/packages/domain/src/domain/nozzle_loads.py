"""Nozul dış yükleri — WRC 537 / WRC 297 lokal gerilme girdisi (P07).

K7: standarttan bağımsız veri modeli; hesap `nozzles.nozzle_loads` modülündedir.
K6: WRC bülten eğrileri teliflidir ve repoda yoktur. Kullanıcı lisanslı bültenden
okuduğu boyutsuz eğri değerlerini `coefficients` sözlüğüne girer; girilmeyen ve
programda doğrulanmış tablosu olmayan değer sıfır SAYILMAZ → BLOCKED_CODE_DATA.

Yük işaret kabulü (bülten eksenleri, nozul ekseni radyal):
  Fr  radyal kuvvet, + = dışa çekme (nozulda çekme)            [N]
  Vc  çevresel kesme kuvveti                                    [N]
  VL  boyuna (kap ekseni yönü) kesme kuvveti                    [N]
  Mc  çevresel moment (çevre doğrultusunda eğen)                [N·mm]
  ML  boyuna moment (kap ekseni doğrultusunda eğen)             [N·mm]
  Mt  burulma momenti (nozul ekseni etrafında)                  [N·mm]
"""

from __future__ import annotations

import re
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# WRC 537 (silindirik kabuk, dairesel bağlantı) eğri anahtarları:
#   "<yük>.<bileşke>.<nokta grubu>"
#   yük ∈ P (radyal), MC, ML; bileşke ∈ Nphi, Nx, Mphi, Mx
#   grup: P → AB (boyuna eksen) ve CD (çevresel eksen); MC → CD; ML → AB
WRC537_COEFFICIENT_KEYS = tuple(
    [f"P.{c}.{g}" for g in ("AB", "CD") for c in ("Nphi", "Nx", "Mphi", "Mx")]
    + [f"MC.{c}.CD" for c in ("Nphi", "Nx", "Mphi", "Mx")]
    + [f"ML.{c}.AB" for c in ("Nphi", "Nx", "Mphi", "Mx")]
)
_WRC297_KEY = re.compile(r"^(shell|nozzle)\.(P|MC|ML)\.(Nphi|Nx|Mphi|Mx)$")


class NozzleLoadEntry(BaseModel):
    """Bir nozulun dış yük takımı ve (isteğe bağlı) kullanıcı eğri okumaları."""

    nozzle_tag: str = Field(..., min_length=1, description="Yük uygulanan nozul etiketi (Nozzle.tag).")
    method: Literal["WRC537", "WRC297"] = Field(
        default="WRC537",
        description="WRC 537 (=WRC 107 eğrileri, kabuk tarafı) veya WRC 297 (kabuk + nozul tarafı).",
    )
    Fr_N: float = Field(default=0.0, description="Radyal kuvvet P (N), + = dışa çekme.")
    Vc_N: float = Field(default=0.0, description="Çevresel kesme kuvveti Vc (N).")
    VL_N: float = Field(default=0.0, description="Boyuna kesme kuvveti VL (N).")
    Mc_Nmm: float = Field(default=0.0, description="Çevresel moment Mc (N·mm).")
    ML_Nmm: float = Field(default=0.0, description="Boyuna moment ML (N·mm).")
    Mt_Nmm: float = Field(default=0.0, description="Burulma momenti Mt (N·mm).")
    coefficients: Optional[Dict[str, Optional[float]]] = Field(
        default=None,
        description="Lisanslı bültenden okunan boyutsuz eğri değerleri; anahtar 'P.Nphi.AB' biçimi "
                    "(WRC 297 için 'shell.P.Nphi'). Boş/None = okunmadı → BLOCKED_CODE_DATA.",
    )
    Kn: float = Field(default=1.0, ge=1.0, description="Membran gerilme yığılma katsayısı (WRC 107 Kn).")
    Kb: float = Field(default=1.0, ge=1.0, description="Eğilme gerilme yığılma katsayısı (WRC 107 Kb).")
    include_pressure: bool = Field(
        default=True, description="Basınç genel membran gerilmesi lokal gerilmeyle birleştirilsin mi?"
    )

    @model_validator(mode="after")
    def _check_coefficient_keys(self) -> "NozzleLoadEntry":
        for key in (self.coefficients or {}):
            ok = key in WRC537_COEFFICIENT_KEYS if self.method == "WRC537" else bool(_WRC297_KEY.match(key))
            if not ok:
                raise ValueError(f"{self.method} için geçersiz katsayı anahtarı: {key!r}")
        return self


class NozzleLoadAnalysis(BaseModel):
    """Proje genelinde nozul dış yük analizi girdisi."""

    entries: List[NozzleLoadEntry] = Field(default_factory=list, description="Nozul başına yük takımları.")
    stress_criterion: Literal["tresca", "von_mises"] = Field(
        default="tresca",
        description="Eşdeğer gerilme: tresca (WRC 107/537 gerilme şiddeti) veya von_mises (VIII-2 2007+).",
    )

    @field_validator("entries")
    @classmethod
    def _unique_tags(cls, entries: List[NozzleLoadEntry]) -> List[NozzleLoadEntry]:
        seen = set()
        for e in entries:
            if e.nozzle_tag in seen:
                raise ValueError(f"Aynı nozul için birden fazla yük takımı: {e.nozzle_tag!r}")
            seen.add(e.nozzle_tag)
        return entries


__all__ = ["NozzleLoadEntry", "NozzleLoadAnalysis", "WRC537_COEFFICIENT_KEYS"]
