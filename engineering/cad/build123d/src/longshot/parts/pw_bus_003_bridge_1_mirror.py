"""PW-BUS-003 Bridge 1 Mirror - handed twin of the 0.2 mm copper Bridge 1.

Dimensions probed from the Fusion reference solid. Component frame identical
to PW-BUS-003-Bridge_1 (top face z = 0.2, first cell at the origin, rows
towards +Y).

The reference is *not* a true mirror image of Bridge 1: the cell pads,
outline and all weld tongues are identical (the tongues keep the same point
symmetric orientation), only the locating ear moves from the -X end
(x = -10.3 .. -15.3) to the +X end (x = 102.3 .. 107.3) of the first row.
Mirroring Bridge 1 about x = 46 would flip the tongue handedness and differ
by ~7.5 % of the volume, so the part is built from the shared Bridge 1
builder with the ear on the other side.
"""

from __future__ import annotations

from build123d import Part

from .pw_bus_003_bridge_1 import bridge_1_busbar, build_busbar

PART_NUMBER = "PW-BUS-003-Bridge_1_Mirror"

EAR_SIDE = +1  # locating ear on the +X end of the first row


def build() -> Part:
    part = build_busbar(bridge_1_busbar(ear_side=EAR_SIDE))
    part.label = PART_NUMBER
    return part
