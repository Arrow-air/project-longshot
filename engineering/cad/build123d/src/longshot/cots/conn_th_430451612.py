"""Through-hole connector 430451612 (CAD model name) on the SL_PCB (purchased).

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "CONN-TH_430451612"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
