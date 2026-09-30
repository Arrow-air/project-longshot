"""EN-STRAP-001 Metal piece - 0.5 mm metal band inside the rubber pack strap.

Dimensions probed from the Fusion reference solid (bbox 200 x 0.5 x 17.4 mm,
volume 1 597.6 mm^3). Component frame (unchanged from the STEP): band
length along X centred on x = 0, width along Z centred on z = 0, thickness
y = 0..0.5.

Flat strip whose short ends are convex R25.98 arcs (arc apex at x = +/-100),
with one 5.5 mm wide, 25.5 mm long slot near each end (slot end-circle
centres at |x| = 73 and 93). The same slot pattern and end-arc style are
used by the rubber part EN-STRAP-002.
"""

from __future__ import annotations

from build123d import Box, Cylinder, Part, Pos, Rot

PART_NUMBER = "EN-STRAP-001-Metal_piece"

LENGTH = 200.0
WIDTH = 17.4
THICKNESS = 0.5
END_RADIUS = 25.98  # convex end arcs, apex at x = +/-LENGTH/2

SLOT_WIDTH = 5.5
SLOT_X_INNER = 73.0  # centre of the inner slot end circle
SLOT_X_OUTER = 93.0  # centre of the outer slot end circle


def slot(x0: float, x1: float, width: float, depth: float, y_mid: float) -> Part:
    """Straight slot along X (end-circle centres x0 < x1), through Y."""
    r = width / 2
    body = Pos((x0 + x1) / 2, y_mid, 0) * Box(x1 - x0, depth, width)
    for x in (x0, x1):
        body += Pos(x, y_mid, 0) * Rot(90, 0, 0) * Cylinder(r, depth)
    return body


def arc_ended_plate(length: float, width: float, thickness: float, end_radius: float, y_mid: float) -> Part:
    """Plate in XZ (centred), thickness along Y, short ends convex arcs."""
    cx = length / 2 - end_radius
    body = Pos(0, y_mid, 0) * Box(2 * cx, thickness, width)
    for s in (1, -1):
        body += Pos(s * cx, y_mid, 0) * Rot(90, 0, 0) * Cylinder(end_radius, thickness)
    return body & (Pos(0, y_mid, 0) * Box(length, thickness, width))


def build() -> Part:
    y_mid = THICKNESS / 2
    part = arc_ended_plate(LENGTH, WIDTH, THICKNESS, END_RADIUS, y_mid)
    for s in (1, -1):
        part -= Pos(s * (SLOT_X_INNER + SLOT_X_OUTER) / 2, 0, 0) * slot(
            -(SLOT_X_OUTER - SLOT_X_INNER) / 2, (SLOT_X_OUTER - SLOT_X_INNER) / 2, SLOT_WIDTH, 3 * THICKNESS, y_mid
        )
    part.label = PART_NUMBER
    return part
