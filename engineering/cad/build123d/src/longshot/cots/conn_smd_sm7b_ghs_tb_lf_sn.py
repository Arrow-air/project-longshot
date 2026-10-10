"""JST SM7B-GHS-TB 7-pin SMD connector, used on the SL_PCB and the four
voltage-sense PCBs (purchased).

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "CONN-SMD_SM7B-GHS-TB-LF-SN"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
