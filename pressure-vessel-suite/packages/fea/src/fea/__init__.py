"""FEA paketi — iskelet + adapter.

Parametrik CAD → basitleştirilmiş geometri → Gmsh mesh → CalculiX/Code_Aster
→ stress linearization → code acceptance. Çözücü kurulu değilse modülü
"REVIEW REQUIRED / mesh ve sınır şartları mühendis onayı gerektirir" ile
iskelet bırakır; sahte "PASS" ÜRETMEZ.

Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K1 kuralı: Formüller yalnızca bu pakette.
K5 kuralı: Her hesap denetlenebilir (CalculationResult).
"""

from fea.fea_adapter import FEAdapter
from fea.face_tags import (
    ALL_KNOWN_TAGS,
    PRESSURE_TAGS,
    SYMMETRY_TAGS,
    FaceTaggingResult,
    TaggedFace,
    tag_vessel_faces,
)
from fea.geometry_prep import (
    EighthSymmetryResult,
    build_eighth_symmetry_geometry,
    check_material_elastic_properties,
    check_symmetry_preconditions,
)

__all__ = [
    "FEAdapter",
    # face_tags (2.3)
    "ALL_KNOWN_TAGS",
    "PRESSURE_TAGS",
    "SYMMETRY_TAGS",
    "FaceTaggingResult",
    "TaggedFace",
    "tag_vessel_faces",
    # geometry_prep (2.2)
    "EighthSymmetryResult",
    "build_eighth_symmetry_geometry",
    "check_symmetry_preconditions",
    "check_material_elastic_properties",
]
