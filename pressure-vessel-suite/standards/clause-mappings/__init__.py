"""Clause mappings — formül ↔ madde referans eşleştirmeleri.

Bu modül, her hesap formülünün hangi standart maddesine karşılık geldiğini izler.
K5 kuralı: Her hesap denetlenebilir olmalı → madde referansı saklanır.
K6 kuralı: Standart telifli metni kopyalanmaz.
"""

from clause_mappings import ClauseMapping, get_clause_mapping

__all__ = ["ClauseMapping", "get_clause_mapping"]
