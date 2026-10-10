"""EN-STRAP-003 Metal End - pressed 1.3 mm sheet-metal end cap of the pack strap.

Dimensions probed from the Fusion reference solid (bbox 47.5 x 30 x 13.6 mm,
volume 3 179.1 mm^3). Two instances in the strap assembly (the second is
rotated 180 deg). Component frame (unchanged from the STEP): symmetric about
y = 0; top face of the cap at z = 1.3 (underside z = 0); the cap is open
towards -Z and at the +X end.

Construction (sheet 1.3 mm, outside bend radii 1 mm, sharp inside corners):

* flat top plate z = 0..1.3 from the bend line x = -14 to x = 14, with
    1.5 x 1.5 mm chamfers on the rear corners (width 24 mm at x = 14);
* a 9 deg downward-sloping plate from x = -14 to the front wall (vertical
    offset of its faces = sheet thickness);
* front wall x = -33.5..-32.2 down to z = -9.7 with a V-shaped centre tab
    (4 mm wide at the root, R0.5 tip at z = -12.3);
* side walls |y| = 13.7..15 from the front to x = 12.5, down to z = -9.7,
    R0.5 at the rear-bottom corner; outer R2 / inner R0.7 front corners;
* a formed countersink at (-6.25, 0): 5.6 mm hole, conical top face
    (34.14 deg to horizontal) and conical underside (20 deg), bottom z = -1.2;
* a pressed rib at x = 8: 2 x 14 mm groove 2 mm deep on top, 4.6 x 16.6 mm
    boss 2 mm below the underside.

The small R0.5 edge rounds on the countersink and rib cross-sections are
omitted (plan-view R0.5 corners are modelled); effect < 0.1 % volume.
"""

from __future__ import annotations

import math

from build123d import (
    Align,
    Axis,
    Box,
    BuildSketch,
    Cone,
    Cylinder,
    Part,
    Plane,
    Polygon,
    Pos,
    extrude,
    fillet,
)

PART_NUMBER = "EN-STRAP-003-Metal_End"

THICKNESS = 1.3
OUTER_BEND_RADIUS = 1.0  # inside bends are sharp

X_FRONT = -33.5  # outer face of the front wall
X_BEND = -14.0  # top plate / slope bend line (inside corner)
X_REAR = 14.0  # end of the top plate
X_SIDE_REAR = 12.5  # end of the side walls
REAR_HALF_WIDTH = 12.0  # top plate at x = 14
REAR_CHAMFER = 1.5  # top-plate rear corners (x = 12.5..14, |y| 13.5 -> 12)
SLOPE_DEG = 9.0
HALF_WIDTH = 15.0
Z_BOTTOM = -9.7  # lower edge of the side / front walls
SIDE_REAR_CORNER_R = 0.5
FRONT_CORNER_R_OUT = 2.0
FRONT_CORNER_R_IN = 0.7

TAB_ROOT_HALF_WIDTH = 2.0
TAB_APEX_Z = -12.7  # sharp apex of the V before the tip radius
TAB_TIP_R = 0.5

CSK_X = -6.25
CSK_HOLE_D = 5.6
CSK_BOTTOM_Z = -1.2  # underside of the formed countersink at the hole
CSK_TOP_ANGLE = 34.136  # top cone, deg to horizontal
CSK_UNDER_ANGLE = 20.0  # underside cone, deg to horizontal

RIB_X = 8.0
RIB_GROOVE = (2.0, 14.0)  # x, y
RIB_GROOVE_BOTTOM_Z = -0.7
RIB_BOSS = (4.6, 16.6)
RIB_BOSS_BOTTOM_Z = -2.0
RIB_CORNER_R = 0.5

AMIN = (Align.CENTER, Align.CENTER, Align.MIN)


def _xz_prism(points, half_y: float) -> Part:
    with BuildSketch(Plane.XZ) as sk:
        Polygon(*points, align=None)
    return extrude(sk.sketch, amount=half_y, both=True)


def build() -> Part:
    t = THICKNESS
    tan_s = math.tan(math.radians(SLOPE_DEG))
    z_out_front = (X_FRONT - X_BEND) * tan_s + t  # outer slope face at the front wall
    x_in_front = X_FRONT + t
    z_in_front = (x_in_front - X_BEND) * tan_s

    outer = _xz_prism(
        [
            (X_FRONT, Z_BOTTOM),
            (X_SIDE_REAR, Z_BOTTOM),
            (X_SIDE_REAR, 0),
            (X_REAR, 0),
            (X_REAR, t),
            (X_BEND, t),
            (X_FRONT, z_out_front),
        ],
        HALF_WIDTH,
    )
    # rear of the top plate: narrower, chamfered
    y_c = REAR_HALF_WIDTH + REAR_CHAMFER  # 13.5
    for s in (1, -1):
        with BuildSketch(Plane.XY.offset(-1)) as sk:
            Polygon(
                (X_SIDE_REAR, s * y_c),
                (X_REAR, s * (y_c - REAR_CHAMFER)),
                (X_REAR + 1, s * (y_c - REAR_CHAMFER)),
                (X_REAR + 1, s * (HALF_WIDTH + 1)),
                (X_SIDE_REAR, s * (HALF_WIDTH + 1)),
                align=None,
            )
        outer -= extrude(sk.sketch, 3)

    outer = fillet(
        outer.edges().filter_by(Axis.Z).filter_by(lambda e: e.center().X < X_FRONT + 0.01), FRONT_CORNER_R_OUT
    )
    r1_edges = [
        e
        for e in outer.edges()
        if e.bounding_box().min.Z > z_out_front - 1.5
        and e.center().X < X_SIDE_REAR - 0.1
        and (
            abs(abs(e.center().Y) - HALF_WIDTH) < 0.01  # top/slope to side walls
            or (e.geom_type.name == "LINE" and abs(e.bounding_box().size.Y) > 20)  # the two bends
        )
    ]
    outer = fillet(r1_edges, OUTER_BEND_RADIUS)

    cavity = _xz_prism(
        [(x_in_front, Z_BOTTOM - 5), (X_REAR + 5, Z_BOTTOM - 5), (X_REAR + 5, 0), (X_BEND, 0), (x_in_front, z_in_front)],
        HALF_WIDTH - t,
    )
    cavity = fillet(
        cavity.edges().filter_by(Axis.Z).filter_by(lambda e: e.center().X < x_in_front + 0.01), FRONT_CORNER_R_IN
    )
    part = outer - cavity
    part = fillet(
        part.edges()
        .filter_by(Axis.Y)
        .filter_by(lambda e: abs(e.center().X - X_SIDE_REAR) < 0.01 and abs(e.center().Z - Z_BOTTOM) < 0.01),
        SIDE_REAR_CORNER_R,
    )

    # V tab on the front wall
    with BuildSketch(Plane.YZ.offset(X_FRONT)) as sk:
        Polygon((-TAB_ROOT_HALF_WIDTH, Z_BOTTOM), (TAB_ROOT_HALF_WIDTH, Z_BOTTOM), (0, TAB_APEX_Z), align=None)
    tab = extrude(sk.sketch, t)
    tab = fillet(tab.edges().filter_by(Axis.X).sort_by(Axis.Z)[0:1], TAB_TIP_R)
    part += tab

    # formed countersink
    r_h = CSK_HOLE_D / 2
    under_h = -CSK_BOTTOM_Z
    r_under = r_h + under_h / math.tan(math.radians(CSK_UNDER_ANGLE))
    part += Pos(CSK_X, 0, CSK_BOTTOM_Z) * Cone(r_h, r_under, under_h, align=AMIN)
    top_bottom_z = CSK_BOTTOM_Z + 0.5
    top_h = t - top_bottom_z + 1
    r_top = r_h + top_h / math.tan(math.radians(CSK_TOP_ANGLE))
    part -= Pos(CSK_X, 0, top_bottom_z) * Cone(r_h, r_top, top_h, align=AMIN)
    part -= Pos(CSK_X, 0, 0) * Cylinder(r_h, 10)

    # pressed rib
    boss = Pos(RIB_X, 0, RIB_BOSS_BOTTOM_Z) * Box(*RIB_BOSS, -RIB_BOSS_BOTTOM_Z, align=AMIN)
    boss = fillet(boss.edges().filter_by(Axis.Z), RIB_CORNER_R)
    part += boss
    groove = Pos(RIB_X, 0, RIB_GROOVE_BOTTOM_Z) * Box(*RIB_GROOVE, 5, align=AMIN)
    groove = fillet(groove.edges().filter_by(Axis.Z), RIB_CORNER_R)
    part -= groove

    part.label = PART_NUMBER
    return part
