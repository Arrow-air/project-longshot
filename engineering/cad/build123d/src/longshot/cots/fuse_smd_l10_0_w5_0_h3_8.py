"""SMD fuse, 10.0 x 5.0 x 3.8 mm package (per CAD model name), on the SL_PCB.

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "FUSE-SMD_L10_0-W5_0-H3_8"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
