"""HTML kaçış yardımcısı (report_engine.generator._esc ile aynı davranış)."""

from __future__ import annotations

import html as _html
from enum import Enum
from typing import Any


def esc(value: Any) -> str:
    """Kullanıcı kaynaklı metni HTML için kaçır. Enum için .value kullanılır."""
    if isinstance(value, Enum):
        value = value.value
    return _html.escape(str(value), quote=True)
