"""EN-CELL-001 Upper Cell Holder - 3D-printed holder for the upper cell ends.

Companion of the bottom cell holder (126 x 21700 cells, 14S9P, 23 mm hex
pitch). Dimensions probed from the Fusion reference solid:
234.6 x 299.842 x 37.675 mm, 392 820 mm^3.

Component frame (same as the reference STEP): the outer floor face lies on
z = 0 and the part grows towards -Z (it is the bottom holder's construction
mirrored about XY); cell (row 0, column 0) is at the origin, same grid as the
bottom holder (confirmed from ``placements.json``).

Shared with the bottom holder (``build_cell_holder``): envelope, flanges,
+Y ledge, cell windows/seats, R11/R2 scalloped cavity, floor-face wire
channel, floor holes, +Y face holes, flange end holes. Differences:

* steeper seat lead-in: the 21.5 mm seat ends 2 mm from the floor face and
    opens to 22.9 mm at the web tops (4 mm), leaving knife-edge webs;
* wire channels run further towards +Y (to y 265.44 / 262.44);
* insert stack for M3 screws from the far face: 8.25 mm bore 28.55 deep,
    45 deg step to a 6 mm counterbore 3 mm long, then a 3.5 mm clearance hole
    through a 8 mm x 2 mm boss (0.5 mm chamfer) standing proud of the far face
    - this is what makes the part 2 mm taller than the bottom holder;
* cross holes at the other three insert positions per side;
* one -Y lug in the middle (x 97.75) near the far face instead of two;
* a 2.25 mm recess in the -Y face (two bays, 14.8 mm tall, R5 corners) with
    four 4 mm holes, instead of the bottom holder's +Y busbar notch.
"""

from __future__ import annotations

from build123d import Align, Circle, Cylinder, Part, Plane, Polygon, Pos, Rot, extrude, mirror

from .en_cell_001_bottom_cell_holder import (
    GRID_CENTRE_X,
    HEIGHT,
    INSERT_BORE_DIAMETER,
    Y_MIN,
    build_cell_holder,
    cone_z,
    hole_z,
    insert_positions,
)

PART_NUMBER = "EN-CELL-001-Upper_Cell_Holder"

SEAT_CONE_START = 2.0
SEAT_CONE_TOP_DIAMETER = 22.9
CHANNEL_Y_END_MINUS_X = 265.4416
CHANNEL_Y_END_PLUS_X = 262.4416
CROSS_HOLE_INDICES = (0, 2, 4)
LUGS = ((GRID_CENTRE_X, 28.275),)  # (x, depth from the floor face)

# insert / screw stack (depths from the floor face)
INSERT_BORE_DEPTH = 28.55
SCREW_CBORE_DIAMETER = 6.0
SCREW_CBORE_BOTTOM = 32.675
SCREW_HOLE_DIAMETER = 3.5
BOSS_DIAMETER = 8.0
BOSS_HEIGHT = 2.0  # proud of the far face -> total 37.675
BOSS_CHAMFER = 0.5
TOTAL_HEIGHT = HEIGHT + BOSS_HEIGHT

# -Y face recess
RECESS_BAYS_X = ((1.1, 102.4), (104.6, 194.4))
RECESS_DEPTH = 2.25  # y -20 -> -17.75
RECESS_HEIGHT = 14.8
RECESS_CORNER_RADIUS = 5.0
RECESS_HOLES_X = (5.2, 98.3, 108.7, 190.3)
RECESS_HOLES_Z = 4.0
RECESS_HOLE_DIAMETER = 4.0
RECESS_HOLE_DEPTH = 6.5


def insert_stack(x: float, y: float) -> list:
    step = (INSERT_BORE_DIAMETER - SCREW_CBORE_DIAMETER) / 2
    return [
        hole_z(x, y, INSERT_BORE_DIAMETER, -1, INSERT_BORE_DEPTH),
        cone_z(x, y, INSERT_BORE_DIAMETER, SCREW_CBORE_DIAMETER, INSERT_BORE_DEPTH, INSERT_BORE_DEPTH + step),
        hole_z(x, y, SCREW_CBORE_DIAMETER, INSERT_BORE_DEPTH + step, SCREW_CBORE_BOTTOM),
        hole_z(x, y, SCREW_HOLE_DIAMETER, SCREW_CBORE_BOTTOM - 0.1, TOTAL_HEIGHT + 1),
    ]


def bosses() -> list:
    out = []
    for side in (-1, 1):
        for x, y in insert_positions(side):
            out.append(hole_z(x, y, BOSS_DIAMETER, HEIGHT - 0.1, TOTAL_HEIGHT - BOSS_CHAMFER))
            out.append(cone_z(x, y, BOSS_DIAMETER, BOSS_DIAMETER - 2 * BOSS_CHAMFER, TOTAL_HEIGHT - BOSS_CHAMFER, TOTAL_HEIGHT))
    return out


def recess_tools() -> list:
    rc = RECESS_CORNER_RADIUS
    out = []
    for x0, x1 in RECESS_BAYS_X:
        prof = Polygon((x0, -1), (x1, -1), (x1, RECESS_HEIGHT), (x0, RECESS_HEIGHT), align=None)
        for xc, sx in ((x0 + rc, -1), (x1 - rc, 1)):
            corner = Polygon((xc, RECESS_HEIGHT - rc), (xc + sx * rc, RECESS_HEIGHT - rc), (xc + sx * rc, RECESS_HEIGHT),
                                (xc, RECESS_HEIGHT), align=None) - Pos(xc, RECESS_HEIGHT - rc) * Circle(rc)
            prof -= corner
        # Plane.XZ faces -Y; start at the recess floor and extrude 1 mm past the -Y face
        out.append(extrude(Plane.XZ.offset(-(Y_MIN + RECESS_DEPTH)) * prof, RECESS_DEPTH + 1))
    for x in RECESS_HOLES_X:
        out.append(Pos(x, Y_MIN + RECESS_DEPTH - 0.1, RECESS_HOLES_Z) * Rot(-90, 0, 0)
                    * Cylinder(RECESS_HOLE_DIAMETER / 2, RECESS_HOLE_DEPTH + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return out


def build() -> Part:
    part = build_cell_holder(
        cone_start=SEAT_CONE_START,
        cone_top_diameter=SEAT_CONE_TOP_DIAMETER,
        channel_y_end=(CHANNEL_Y_END_MINUS_X, CHANNEL_Y_END_PLUS_X),
        insert_holes=insert_stack,
        cross_hole_indices=CROSS_HOLE_INDICES,
        lugs=LUGS,
        extra_cuts=recess_tools(),
        extra_adds=bosses(),
    )
    part = mirror(part, Plane.XY)
    part.label = PART_NUMBER
    return part
