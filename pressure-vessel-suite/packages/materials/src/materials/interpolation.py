"""Malzeme özellik interpolasyonu.

Sıcaklığa bağlı malzeme özelliklerinin interpolasyonu.
Lineer interpolasyon kullanılır; ekstrapolasyon yapılmaz (son bilinen değer kullanılır).
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np


def linear_interpolate(
    x: float,
    x_points: List[float],
    y_points: List[float],
    allow_extrapolation: bool = False,
) -> float:
    """Lineer interpolasyon.

    Args:
        x: İnterpolasyon yapılacak nokta.
        x_points: X değerleri (artan sırada olmalı).
        y_points: Y değerleri.
        allow_extrapolation: Ekstrapolasyona izin verilsin mi?

    Returns:
        İnterpolasyon sonucu.

    Raises:
        ValueError: x_points ve y_points uzunlukları farklıysa veya boşsa.
    """
    if len(x_points) != len(y_points):
        raise ValueError("x_points ve y_points uzunlukları aynı olmalı")
    if len(x_points) == 0:
        raise ValueError("Boş veri seti ile interpolasyon yapılamaz")

    x_arr = np.array(x_points)
    y_arr = np.array(y_points)

    if len(x_points) == 1:
        return float(y_arr[0])

    # Ekstrapolasyon kontrolü
    if x < x_arr[0]:
        if not allow_extrapolation:
            return float(y_arr[0])  # En düşük sıcaklık değeri kullanılır
        # Lineer ekstrapolasyon (ilk iki nokta)
        slope = (y_arr[1] - y_arr[0]) / (x_arr[1] - x_arr[0])
        return float(y_arr[0] + slope * (x - x_arr[0]))

    if x > x_arr[-1]:
        if not allow_extrapolation:
            return float(y_arr[-1])  # En yüksek sıcaklık değeri kullanılır
        # Lineer ekstrapolasyon (son iki nokta)
        slope = (y_arr[-1] - y_arr[-2]) / (x_arr[-1] - x_arr[-2])
        return float(y_arr[-1] + slope * (x - x_arr[-1]))

    return float(np.interp(x, x_arr, y_arr))


def interpolate_material_property(
    temperature: float,
    data_points: List[Tuple[float, float]],
    property_name: str = "allowable_stress",
) -> float:
    """Malzeme özelliği interpolasyonu.

    Args:
        temperature: Tasarım sıcaklığı (°C).
        data_points: (sıcaklık, değer) çiftleri listesi.
        property_name: Özellik adı (hata mesajları için).

    Returns:
        İnterpolasyon sonucu.

    Raises:
        ValueError: Boş veri seti.
    """
    if not data_points:
        raise ValueError(f"'{property_name}' için veri noktası yok")

    # Sıcaklığa göre sırala
    sorted_points = sorted(data_points, key=lambda p: p[0])
    temps = [p[0] for p in sorted_points]
    values = [p[1] for p in sorted_points]

    return linear_interpolate(temperature, temps, values)


__all__ = ["linear_interpolate", "interpolate_material_property"]
