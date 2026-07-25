"""Proje kaydetme/yükleme yardımcıları — JSON + SHA-256 hash.

K5 kuralı: Her hesap denetlenebilir olmalı → input_file_hash izlenebilirlik için.
Round-trip güvencesi: kaydet → yükle → aynı veri + hash tutarlı.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from domain.project import VesselProject


def _canonical_bytes(data: Dict[str, Any]) -> bytes:
    """Dict'in kanonik JSON baytlarını üret.

    Sıralı anahtarlar + kompakt ayırıcı → deterministik.
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def compute_input_hash(project: VesselProject) -> str:
    """Projenin SHA-256 hash'ini üret.

    Hash, input_file_hash alanı None iken hesaplanır — böylece
    kaydetme/yükleme döngüsünde tutarlı kalır.

    Returns:
        Hex-digest: örn. "a1b2c3..."
    """
    data = project.model_dump(mode="json")
    data["input_file_hash"] = None
    return hashlib.sha256(_canonical_bytes(data)).hexdigest()


def save_project_json(project: VesselProject, path: str | Path) -> VesselProject:
    """Projeyi JSON dosyasına kaydet ve input_file_hash'i doldur.

    Args:
        project: Kaydedilecek proje.
        path: Çıktı dosya yolu.

    Returns:
        Hash'i güncellenmiş proje kopyası.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    project_hash = compute_input_hash(project)

    project_dict = project.model_dump(mode="json")
    project_dict["input_file_hash"] = project_hash

    path.write_text(
        json.dumps(project_dict, indent=2, ensure_ascii=False, sort_keys=False),
        encoding="utf-8",
    )

    return project.model_copy(update={"input_file_hash": project_hash})


def load_project_json(path: str | Path) -> VesselProject:
    """JSON dosyasından proje yükle.

    Hash doğrulaması yapar: dosyadaki input_file_hash ile hesaplanan hash eşleşmeli.

    Args:
        path: Kaynak dosya yolu.

    Returns:
        Yüklenmiş VesselProject.

    Raises:
        FileNotFoundError: Dosya yoksa.
        ValueError: JSON geçersizse, model doğrulaması başarısızsa veya hash eşleşmiyorsa.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Proje dosyası bulunamadı: {path}")

    raw = path.read_text(encoding="utf-8")
    try:
        data: Dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Geçersiz JSON: {e}") from e

    # Hash doğrulama (varsa)
    stored_hash = data.get("input_file_hash")
    if stored_hash:
        check_dict = data.copy()
        check_dict["input_file_hash"] = None
        computed = hashlib.sha256(_canonical_bytes(check_dict)).hexdigest()
        if computed != stored_hash:
            raise ValueError(
                f"Hash doğrulama başarısız! Dosyadaki: {stored_hash}, "
                f"Hesaplanan: {computed}. Dosya bozulmuş veya değiştirilmiş olabilir."
            )

    try:
        project = VesselProject.model_validate(data)
    except Exception as e:
        raise ValueError(f"Proje doğrulama hatası: {e}") from e

    return project


__all__ = ["save_project_json", "load_project_json", "compute_input_hash"]
