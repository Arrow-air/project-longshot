"""EN-SHEET-001 Reinfocement Right - 1 mm bent aluminium side reinforcement.

"Reinfocement" (sic) is the spelling of the Fusion/CAD part number and is
kept verbatim in PART_NUMBER.

All dimensions probed from the Fusion reference solid (bbox 64 x 316 x
77.7 mm, volume 28 401.7 mm^3). Component frame (unchanged from the STEP):
the part runs along +Y (y = 0..316), is symmetric about z = 0 and sits at
x = -118.5..-54.5.

Cross-section (XZ, constant along Y) is a joggled hat made of 1 mm sheet
with inside bend radius 1 mm (outside 2 mm):

* outer web ("web A", x = -118.5..-117.5): two 19 mm strips at
    |z| = 19.85..38.85, each with one 4.5 mm hole near the far end;
* two 5 mm flanges (|z| = 17.85..18.85) stepping inwards by 8 mm;
* inner web ("web B", x = -110.5..-109.5, |z| <= 16.85): carries the
    alternating 3.8 mm cell-row hole pattern, continues past the hat to
    y = 316 as a tongue with R5 corners and two 3.5 mm holes;
* at y = 0 web B is bent 90 deg outward (+X) into a 20 mm wide foot tab
    (y = 0..1, x = -108.5..-54.5, R5 corners) with four 3.8 mm holes.

The left-hand twin (EN-SHEET-002) is NOT a mirror image: it is the same
blank with the web-B hole pattern shifted one cell row (+19.92 mm in Y,
z signs swapped) and the foot-tab holes shifted -11.5 mm in X. Both are
built by :func:`build_reinforcement`.
"""

from __future__ import annotations

import math

from build123d import Axis, Box, Cylinder, Part, Pos, Rot, fillet

PART_NUMBER = "EN-SHEET-001-Reinfocement_Right"

THICKNESS = 1.0
BEND_RADIUS = 1.0  # inside; outside = BEND_RADIUS + THICKNESS

# Cross-section (x of the outer faces of each web, z of the flange outer faces)
WEB_A_X = -118.5  # outer face of the outer web
WEB_B_X = -110.5  # -X face of the inner web
FLANGE_Z = 17.85  # |z| of the flange face nearest the centre
HALF_HEIGHT = 38.85  # |z| of the outer web edges
WEB_B_HALF = FLANGE_Z - THICKNESS  # 16.85, flat part of web B

# Lengths along Y
HAT_Y0 = 2.0  # start of hat (end of foot-tab bend)
HAT_Y1 = 295.942  # end of web A / flanges
LENGTH = 316.0  # end of web-B tongue
WEB_A_CORNER_R = 1.0
TONGUE_CORNER_R = 5.0
TONGUE_HOLE_D = 3.5
TONGUE_HOLE_Y = 310.0
TONGUE_HOLE_Z = 8.85

WEB_A_HOLE_D = 4.5
WEB_A_HOLE_Y = 289.942
WEB_A_HOLE_Z = 27.363

# Foot tab at y = 0..1
TAB_X_END = -54.5
TAB_HALF_WIDTH = 10.0
TAB_CORNER_R = 5.0

# Cell-pattern holes
CELL_HOLE_D = 3.8
CELL_HOLE_Z = 6.2
CELL_PITCH_Y = 2 * 23.0 * math.sin(math.radians(60))  # 39.837: two cell rows
WEB_B_HOLE_COUNT = 6
WEB_B_HOLE_Y_FIRST = 32.419
WEB_B_HOLE_Z_FIRST = -CELL_HOLE_Z  # sign alternates along Y
TAB_HOLE_X = (-63.25, -86.25)  # 23 mm cell pitch, each at z = +/-CELL_HOLE_Z


def _quarter_tube(center, r_in, r_out, length, quadrant, axis, y_mid=0.0):
    """Quarter-annulus bend.

    ``axis`` 'Y': center=(x, z), quadrant=(sx, sz), centred on y = y_mid.
    ``axis`` 'Z': center=(x, y), quadrant=(sx, sy), centred on z = 0.
    """
    ring = Cylinder(r_out, length) - Cylinder(r_in, length)
    quad = Pos(quadrant[0] * r_out, quadrant[1] * r_out, 0) * Box(2 * r_out, 2 * r_out, length)
    q = ring & quad
    if axis == "Y":
        # local (x, y, z) -> global (x, -z, y)
        return Pos(center[0], y_mid, center[1]) * Rot(90, 0, 0) * q
    return Pos(center[0], center[1], 0) * q


def build_reinforcement(
    web_b_hole_y_first: float = WEB_B_HOLE_Y_FIRST,
    web_b_hole_z_first: float = WEB_B_HOLE_Z_FIRST,
    tab_hole_x: tuple[float, ...] = TAB_HOLE_X,
) -> Part:
    t, ri, ro = THICKNESS, BEND_RADIUS, BEND_RADIUS + THICKNESS
    hat_len = HAT_Y1 - HAT_Y0
    y_mid = (HAT_Y0 + HAT_Y1) / 2
    bend_a_x = WEB_A_X + ro  # -116.5
    bend_b_x = WEB_B_X - ri  # -111.5
    bend_a_z = FLANGE_Z + ro  # 19.85
    web_a_h = HALF_HEIGHT - bend_a_z

    parts = []
    for s in (1, -1):
        web_a = Pos(WEB_A_X + t / 2, y_mid, s * (bend_a_z + web_a_h / 2)) * Box(t, hat_len, web_a_h)
        web_a = fillet(
            web_a.edges().filter_by(Axis.X).filter_by(lambda e, s=s: s * e.center().Z > HALF_HEIGHT - 0.01),
            WEB_A_CORNER_R,
        )
        for hz in (s * WEB_A_HOLE_Z,):
            web_a -= Pos(WEB_A_X + t / 2, WEB_A_HOLE_Y, hz) * Rot(0, 90, 0) * Cylinder(WEB_A_HOLE_D / 2, 3 * t)
        parts.append(web_a)
        flange_len = bend_b_x - bend_a_x
        parts.append(
            Pos((bend_a_x + bend_b_x) / 2, y_mid, s * (FLANGE_Z + t / 2)) * Box(flange_len, hat_len, t)
        )
        parts.append(_quarter_tube((bend_a_x, s * bend_a_z), ri, ro, hat_len, (-1, -s), "Y", y_mid))
        parts.append(_quarter_tube((bend_b_x, s * WEB_B_HALF), ri, ro, hat_len, (1, s), "Y", y_mid))
    hat = Part() + parts

    # Web B with tongue
    web_b_len = LENGTH - HAT_Y0
    web_b = Pos(WEB_B_X + t / 2, HAT_Y0 + web_b_len / 2, 0) * Box(t, web_b_len, 2 * WEB_B_HALF)
    web_b = fillet(
        web_b.edges().filter_by(Axis.X).filter_by(lambda e: e.center().Y > LENGTH - 0.01), TONGUE_CORNER_R
    )
    for i in range(WEB_B_HOLE_COUNT):
        z = web_b_hole_z_first * (1 if i % 2 == 0 else -1)
        web_b -= Pos(WEB_B_X + t / 2, web_b_hole_y_first + i * CELL_PITCH_Y, z) * Rot(0, 90, 0) * Cylinder(
            CELL_HOLE_D / 2, 3 * t
        )
    for z in (TONGUE_HOLE_Z, -TONGUE_HOLE_Z):
        web_b -= Pos(WEB_B_X + t / 2, TONGUE_HOLE_Y, z) * Rot(0, 90, 0) * Cylinder(TONGUE_HOLE_D / 2, 3 * t)

    # Foot tab and its bend (axis Z)
    tab_x0 = WEB_B_X + ro  # -108.5
    bend = _quarter_tube((tab_x0, HAT_Y0), ri, ro, 2 * TAB_HALF_WIDTH, (-1, -1), "Z")
    tab_len = TAB_X_END - tab_x0
    tab = Pos(tab_x0 + tab_len / 2, t / 2, 0) * Box(tab_len, t, 2 * TAB_HALF_WIDTH)
    tab = fillet(tab.edges().filter_by(Axis.Y).filter_by(lambda e: e.center().X > TAB_X_END - 0.01), TAB_CORNER_R)
    for x in tab_hole_x:
        for z in (CELL_HOLE_Z, -CELL_HOLE_Z):
            tab -= Pos(x, t / 2, z) * Rot(90, 0, 0) * Cylinder(CELL_HOLE_D / 2, 3 * t)

    part = hat + web_b + bend + tab
    return part


def build() -> Part:
    part = build_reinforcement()
    part.label = PART_NUMBER
    return part
