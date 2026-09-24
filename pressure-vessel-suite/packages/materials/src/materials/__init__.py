"""Materials paketi — sürümlü malzeme veri sağlayıcısı.

V1'de manuel giriş (K4: program otomatik seçmez, kullanıcıya gösterip onay ister).
K3: Her proje kendi StandardPack'ine kilitlenir.
"""

from materials.interpolation import interpolate_material_property, linear_interpolate
from materials.provider import MaterialProvider
from materials.data_pack import MaterialDataPack, interpolate_pack_property

__all__ = [
    "MaterialProvider",
    "linear_interpolate",
    "interpolate_material_property",
    "MaterialDataPack",
    "interpolate_pack_property",
]
