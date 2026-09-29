"""ruthex RX-M3x5.7 M3 heat-set insert (purchased).

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "EN-INSERT-001-ruthex_RX-M3x5_7"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
