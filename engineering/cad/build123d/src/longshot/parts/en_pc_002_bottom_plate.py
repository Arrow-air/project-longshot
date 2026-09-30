"""EN-PC-002 Bottom Plate - 3 mm polycarbonate plate under the bottom cell holder.

The reference solid is the top plate mirrored about the XY plane: same
outline and hole pattern, countersinks open towards -Z, body on z = -3..0.
"""

from __future__ import annotations

from build123d import Part

from .en_pc_001_top_plate import build_plate

PART_NUMBER = "EN-PC-002-Bottom_Plate"


def build() -> Part:
    part = build_plate(countersink_up=False)
    part.label = PART_NUMBER
    return part
