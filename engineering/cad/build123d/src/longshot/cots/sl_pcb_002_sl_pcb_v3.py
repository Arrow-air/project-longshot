"""SL_PCB V3 main battery PCB - bare board layers (board, soldermask).

The copper and silkscreen artwork layers of the Fusion export are not
committed (copper alone is about 18 MB as STEP); populated components have
their own wrapper modules.

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "SL_PCB-002-SL_PCB_V3"

_PART = ReferencePart(PART_NUMBER, prefix="SL_PCB-002-SL_PCB_V3:")
REFERENCE_KEYS = _PART.keys
build = _PART.build
