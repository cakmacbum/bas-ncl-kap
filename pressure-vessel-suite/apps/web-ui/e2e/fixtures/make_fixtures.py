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

def ui_consistent(project: dict) -> dict:
    """Kampanya tabanları API için geçerli ama UI geometri doğrulaması (bloklayıcı) iki şeyi reddeder:
    HEAD-R iç çapı gövdeyle eşleşmiyor (800 != 1000) ve ayak boyu kap altına ulaşmıyor (600 < 802).
    UI'dan ilerleyebilmek için yalnız bu iki değeri düzeltiriz."""
    shell_di = project["shell_sections"][0]["inside_diameter"]
    for head in project["heads"]:
        head["inside_diameter"] = shell_di
    for support in project["supports"]:
        if support["type"] == "leg":
            support["height_mm"] = 1000
    return project


for name, factory in (
    ("vertical-leg", vertical_leg_tank),
    ("horizontal-saddle", horizontal_saddle_tank),
    ("skirt-column", skirt_column),
):
    (OUT / f"{name}.json").write_text(
        json.dumps(ui_consistent(factory()), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
