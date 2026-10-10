"""Voltage-sense PCB, bottom right - bare board layers (board, pads,
soldermask). Silkscreen artwork is not committed.

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "VS_PCB_COMPLETE_BOTTOM_RIGHT"

_PART = ReferencePart(PART_NUMBER, prefix="VS_PCB_COMPLETE_BOTTOM_RIGHT:")
REFERENCE_KEYS = _PART.keys
build = _PART.build
