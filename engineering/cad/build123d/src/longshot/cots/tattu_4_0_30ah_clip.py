"""Tattu 4.0 30Ah clip (purchased; vendor model from the Fusion export).

Geometry is loaded from the reference STEP extracted from the Fusion export;
it is not recreated here.
"""

from __future__ import annotations

from . import ReferencePart

PART_NUMBER = "Tattu_4_0_30Ah_Clip"

_PART = ReferencePart(PART_NUMBER)
REFERENCE_KEYS = _PART.keys
build = _PART.build
