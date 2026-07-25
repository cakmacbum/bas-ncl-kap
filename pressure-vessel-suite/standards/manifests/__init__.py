"""Standards manifests — StandardPack sürüm tanımları.

Her proje kendi StandardPack'ine kilitlenir (K3 kuralı).
Harmonize liste değişse bile eski proje değişmez.
"""

from standards_manifests import StandardPack, load_standard_pack

__all__ = ["StandardPack", "load_standard_pack"]
