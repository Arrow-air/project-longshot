"""Parametric build123d models of Longshot's custom parts.

One module per part number. Every module exposes:

* ``PART_NUMBER`` - the Fusion component name / part number.
* module-level parameters (mm) probed from Julius's reference solid.
* ``build() -> Part`` - the part in its Fusion component frame, so it can be
    placed with the matrices in ``placements.json``.
* optional ``VALIDATION_NOTE`` - known, measured differences to the reference.
"""

from __future__ import annotations

import importlib
from types import ModuleType

PART_NUMBERS = [
    "PW-CELL-001-21700",
    "PW-BUS-001-N_Terminal",
    "PW-BUS-002-P_Terminal",
    "PW-BUS-003-Bridge_1",
    "PW-BUS-003-Bridge_1_Mirror",
    "PW-BUS-004-Bridge_2",
    "PW-BUS-005-Screw_Terminal_Negative",
    "PW-BUS-006-Screw_Terminal_Positive",
    "EN-CELL-001-Upper_Cell_Holder",
    "EN-CELL-001-Bottom_Cell_Holder",
    "EN-SHEET-001-Reinfocement_Right",
    "EN-SHEET-002-Reinfocement_Left",
    "EN-PC-001-Top_Plate",
    "EN-PC-002-Bottom_Plate",
    "EN-PRINT-001-3D-Printable_Battery_Base",
    "EN-PRINT-002-3D-Printable_Battery_Top_Cover",
    "EN-STRAP-001-Metal_piece",
    "EN-STRAP-002-Rubber_Part",
    "EN-STRAP-003-Metal_End",
]


def module_name(part_number: str) -> str:
    """``PW-BUS-003-Bridge_1`` -> ``pw_bus_003_bridge_1``."""
    return part_number.lower().replace("-", "_")


def load(part_number: str) -> ModuleType:
    return importlib.import_module(f"{__name__}.{module_name(part_number)}")
