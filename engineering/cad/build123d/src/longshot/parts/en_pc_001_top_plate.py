"""EN-PC-001 Top Plate - 3 mm polycarbonate plate over the upper cell holder.

Dimensions probed from the Fusion reference solid. Component frame: plate
centred on XY, bottom face on z = 0, countersinks open towards +Z.
"""

from __future__ import annotations

import math

from build123d import Align, Axis, Box, Cone, Cylinder, Part, Plane, Pos, fillet, mirror

PART_NUMBER = "EN-PC-001-Top_Plate"

LENGTH_X = 234.6
LENGTH_Y = 285.6
THICKNESS = 3.0
CORNER_RADIUS = 1.8  # vertical corner rounds

# 12 countersunk holes, alternating between the two long sides.
HOLE_DIAMETER = 3.3
COUNTERSINK_DIAMETER = 8.3  # at the countersunk face
COUNTERSINK_ANGLE = 90.0  # included angle
HOLE_X = 103.875  # +/- X of the two hole columns
HOLE_Y_FIRST = 106.52284  # first hole, on the +X column
HOLE_PITCH_Y = 23.0 * math.sin(math.radians(60))  # 19.9186: one cell row
HOLE_COUNT = 12

CENTERED = (Align.CENTER, Align.CENTER, Align.MIN)


def hole_positions() -> list[tuple[float, float]]:
    """Hole centres, alternating +X / -X, stepping towards -Y."""
    return [
        (HOLE_X if i % 2 == 0 else -HOLE_X, HOLE_Y_FIRST - i * HOLE_PITCH_Y)
        for i in range(HOLE_COUNT)
    ]


def build_plate(countersink_up: bool = True) -> Part:
    """Plate on z = 0..THICKNESS with countersinks on +Z.

    With ``countersink_up=False`` the plate is mirrored about XY
    (z = -THICKNESS..0, countersinks on -Z), which is the bottom plate.
    """
    plate = Box(LENGTH_X, LENGTH_Y, THICKNESS, align=CENTERED)
    plate = fillet(plate.edges().filter_by(Axis.Z), CORNER_RADIUS)

    sink_depth = (COUNTERSINK_DIAMETER - HOLE_DIAMETER) / 2 / math.tan(math.radians(COUNTERSINK_ANGLE / 2))
    for x, y in hole_positions():
        plate -= Pos(x, y, 0) * Cylinder(HOLE_DIAMETER / 2, THICKNESS, align=CENTERED)
        plate -= Pos(x, y, THICKNESS - sink_depth) * Cone(
            HOLE_DIAMETER / 2, COUNTERSINK_DIAMETER / 2, sink_depth, align=CENTERED
        )
    if not countersink_up:
        plate = mirror(plate, Plane.XY)
    return plate


def build() -> Part:
    part = build_plate(countersink_up=True)
    part.label = PART_NUMBER
    return part
