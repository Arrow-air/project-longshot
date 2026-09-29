"""ruthex RX-M4x8.1 M4 heat-set insert (purchased).

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "EN-INSERT-002-ruthex_RX-M4x8_1"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
