"""Generate UI E2E projects from the canonical campaign tank definitions."""
from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.campaign.bases import (  # noqa: E402
    horizontal_saddle_tank,
    skirt_column,
    vertical_leg_tank,
)

OUT = Path(__file__).resolve().parent

for name, factory in (
    ("vertical-leg", vertical_leg_tank),
    ("horizontal-saddle", horizontal_saddle_tank),
    ("skirt-column", skirt_column),
):
    (OUT / f"{name}.json").write_text(
        json.dumps(factory(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
