"""MaterialProvider — malzeme veri sağlayıcısı.

V1'de manuel giriş desteklenir (K4: program otomatik seçmez).
İleride lisanslı paket import edilebilir.

Sürümlü yapı: her proje kendi StandardPack'ine kilitlenir (K3).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from domain.materials import MaterialProperty


class MaterialProvider:
    """Malzeme veri sağlayıcısı.

    V1'de kullanıcı malzeme özelliklerini manuel girer.
    Bu sınıf, girilen malzemeleri yönetir ve sorgular.

    Kullanım:
        provider = MaterialProvider()
        provider.add_material(material_property)
        mat = provider.get("MAT-01")
    """

    def __init__(self) -> None:
        self._materials: Dict[str, MaterialProperty] = {}

    def add_material(self, material: MaterialProperty) -> None:
        """Malzeme ekle (veya güncelle)."""
        self._materials[material.material_id] = material

    def get(self, material_id: str) -> Optional[MaterialProperty]:
        """ID ile malzeme getir."""
        return self._materials.get(material_id)

    def get_required(self, material_id: str) -> MaterialProperty:
        """ID ile malzeme getir (yoksa hata fırlat)."""
        mat = self._materials.get(material_id)
        if mat is None:
            raise ValueError(f"Malzeme bulunamadı: {material_id}")
        return mat

    def list_materials(self) -> List[MaterialProperty]:
        """Tüm malzemeleri listele."""
        return list(self._materials.values())

    def remove(self, material_id: str) -> bool:
        """Malzeme sil. Başarılı ise True döner."""
        if material_id in self._materials:
            del self._materials[material_id]
            return True
        return False

    def clear(self) -> None:
        """Tüm malzemeleri temizle."""
        self._materials.clear()

    @property
    def count(self) -> int:
        """Malzeme sayısı."""
        return len(self._materials)

    def validate_against_project(self, project_materials: List[MaterialProperty]) -> List[str]:
        """Proje malzemelerinin provider'da olup olmadığını kontrol et.

        Returns:
            Eksik malzeme ID'lerinin listesi (boş ise tümü mevcut).
        """
        missing = []
        for mat in project_materials:
            if mat.material_id not in self._materials:
                missing.append(mat.material_id)
        return missing


__all__ = ["MaterialProvider"]
