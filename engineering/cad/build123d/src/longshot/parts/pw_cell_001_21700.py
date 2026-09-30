"""PW-CELL-001 21700 cell - simplified parametric 21700 cylindrical cell.

The Fusion assembly uses a vendor model named "Molicel 21700 P45B" as a
placeholder; the PT1 build uses BAK 21700 65E cells (see
engineering/builds/PT1/BOM.md). This module replaces the vendor model with a
light revolved can, the insulator ring and a stamped positive cap, using
dimensions probed from the reference solid.

Component frame: cell axis on Z, positive cap towards +Z, overall
z = -35.175..34.975.

Simplifications: the crimp groove near the top of the can and the vent slots
in the positive cap are not modelled.
"""

from __future__ import annotations

import math

from build123d import (
    Align,
    Axis,
    BuildLine,
    BuildSketch,
    Compound,
    Cylinder,
    Line,
    Part,
    Plane,
    Pos,
    ThreePointArc,
    make_face,
    revolve,
)

PART_NUMBER = "PW-CELL-001-21700"

DIAMETER = 21.55
Z_BOTTOM = -35.175  # outer bottom rim (negative terminal)
CAN_TOP = 34.725  # top of the crimped can shoulder
EDGE_RADIUS = 1.5  # top and bottom can rounds

BOTTOM_RECESS_RADIUS = 7.5  # centre of the can bottom sits BOTTOM_RECESS_DEPTH higher
BOTTOM_RECESS_DEPTH = 0.2
TOP_RECESS_RADIUS = 7.5  # opening in the can top that holds ring and cap
TOP_RECESS_DEPTH = 2.0

RING_INNER_RADIUS = 6.0  # insulator ring in the top recess
RING_Z = (33.225, 34.175)

CAP_SHEET = 0.5  # stamped positive cap sheet thickness
CAP_FLANGE_RADIUS = 6.935
CAP_FLANGE_Z = 33.452  # underside of the cap flange
CAP_HAT_RADIUS = 5.0
CAP_TOP = 34.975  # overall cell top


_C45 = math.cos(math.radians(45))


def _can() -> Part:
    r = DIAMETER / 2
    e = EDGE_RADIUS
    z0, z1 = Z_BOTTOM, CAN_TOP
    with BuildSketch(Plane.XZ) as profile:
        with BuildLine():
            Line((0, z0 + BOTTOM_RECESS_DEPTH), (BOTTOM_RECESS_RADIUS, z0 + BOTTOM_RECESS_DEPTH))
            Line((BOTTOM_RECESS_RADIUS, z0 + BOTTOM_RECESS_DEPTH), (BOTTOM_RECESS_RADIUS, z0))
            Line((BOTTOM_RECESS_RADIUS, z0), (r - e, z0))
            ThreePointArc((r - e, z0), (r - e + e * _C45, z0 + e - e * _C45), (r, z0 + e))
            Line((r, z0 + e), (r, z1 - e))
            ThreePointArc((r, z1 - e), (r - e + e * _C45, z1 - e + e * _C45), (r - e, z1))
            Line((r - e, z1), (TOP_RECESS_RADIUS, z1))
            Line((TOP_RECESS_RADIUS, z1), (TOP_RECESS_RADIUS, z1 - TOP_RECESS_DEPTH))
            Line((TOP_RECESS_RADIUS, z1 - TOP_RECESS_DEPTH), (0, z1 - TOP_RECESS_DEPTH))
            Line((0, z1 - TOP_RECESS_DEPTH), (0, z0 + BOTTOM_RECESS_DEPTH))
        make_face()
    return revolve(profile.sketch, Axis.Z)


def _ring() -> Part:
    height = RING_Z[1] - RING_Z[0]
    base = (Align.CENTER, Align.CENTER, Align.MIN)
    outer = Cylinder(TOP_RECESS_RADIUS, height, align=base)
    inner = Cylinder(RING_INNER_RADIUS, height, align=base)
    return Pos(0, 0, RING_Z[0]) * (outer - inner)


def _cap() -> Part:
    base = (Align.CENTER, Align.CENTER, Align.MIN)
    flange = Pos(0, 0, CAP_FLANGE_Z) * (
        Cylinder(CAP_FLANGE_RADIUS, CAP_SHEET, align=base)
        - Cylinder(CAP_HAT_RADIUS - CAP_SHEET, CAP_SHEET, align=base)
    )
    wall_z = CAP_FLANGE_Z + CAP_SHEET
    wall_h = CAP_TOP - CAP_SHEET - wall_z
    wall = Pos(0, 0, wall_z) * (
        Cylinder(CAP_HAT_RADIUS, wall_h, align=base) - Cylinder(CAP_HAT_RADIUS - CAP_SHEET, wall_h, align=base)
    )
    top = Pos(0, 0, CAP_TOP - CAP_SHEET) * Cylinder(CAP_HAT_RADIUS, CAP_SHEET, align=base)
    return flange + wall + top


def build() -> Compound:
    """Can, insulator ring and positive cap as three solids (as in the reference)."""
    part = Compound([_can().solid(), _ring().solid(), _cap().solid()])
    part.label = PART_NUMBER
    return part
