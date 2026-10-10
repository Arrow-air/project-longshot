"""ET60S-D06 power/signal connector on the SL_PCB (purchased; vendor model
with power terminals, guide posts and pins as sub-bodies).

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "ET60S-D06-0-00-D06-L-V1-S"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
