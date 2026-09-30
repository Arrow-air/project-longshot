"""EN-CELL-001 Bottom Cell Holder - 3D-printed holder for the lower cell ends.

Holds the lower ends of the 126 21700 cells of the
14S9P pack (14 groups of 9 = a 5-cell row plus a 4-cell row each), hex packed
on a 23 mm pitch. Dimensions probed from the Fusion reference solid:
234.6 x 299.842 x 35.675 mm, 395 775 mm^3.

Component frame (same as the reference STEP): the outer floor face lies on
z = 0 and the part grows towards +Z. Cell (row 0, column 0) is at the origin;
cell centres are x = 23 i + 11.5 (j odd), y = 19.9186 j, i = 0..8, j = 0..13
(checked against ``placements.json``: every cell maps onto this grid in the
holder frame).

Construction (``build_cell_holder``, shared with the upper holder, which is
the same part mirrored about XY with a different pocket chamfer, hole stack
and side features):

* body = union of three prisms: the 8 mm side flanges (x -19.55..215.05,
    up to 16.825), the wall block with the 1 mm +Y ledge (up to 24.675) and the
    wall block (x -11.55..207.05, y -20..274.942, full height);
* per cell: a 15 mm window through the 0.6 mm floor, a 21.5 mm seat pocket
    and a conical lead-in up to the web tops at 4 mm;
* one open cavity above 4 mm whose wall is R11 arcs around the border cells
    joined by R2 fillets (the union of the border discs, the hull polygon of
    the border centres and the fillet patches);
* a 1.6 mm deep wire channel on the floor face along both flanges and round
    the -Y corners;
* 12 heat-set insert holes (EN-INSERT-001) in the long walls, 12 blind 4 mm
    holes in the floor face, side M4 cross holes with countersinks, 4 mm holes
    in the +Y face, 5.6 mm corner holes in the flanges, and the -Y lug(s).
"""

from __future__ import annotations

import math

from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Compound,
    Cone,
    Cylinder,
    Location,
    Part,
    Plane,
    Polygon,
    Pos,
    Rot,
    Solid,
    extrude,
    mirror,
    revolve,
)

PART_NUMBER = "EN-CELL-001-Bottom_Cell_Holder"

# --- cell grid (holder frame) ---------------------------------------------
CELL_PITCH_X = 23.0
CELL_PITCH_Y = 23.0 * math.sin(math.radians(60))  # 19.9186 row pitch
CELL_COLUMNS = 9
CELL_ROWS = 14  # 14 rows of 9 = 126 cells
ODD_ROW_OFFSET_X = 11.5
GRID_CENTRE_X = 97.75  # part is symmetric about x = 97.75

# --- overall envelope ------------------------------------------------------
FLANGE_X_MIN = -19.55
FLANGE_X_MAX = 215.05  # 234.6 overall
WALL_X_MIN = -11.55
WALL_X_MAX = 207.05
Y_MIN = -20.0
Y_MAX_LEDGE = 275.9416  # last row + 17
Y_MAX_WALL = 274.9416  # last row + 16
CHAMFER_MINUS_Y = 2.0  # vertical corner chamfers at -Y
CHAMFER_PLUS_Y_LEDGE = 3.0  # at +Y below the ledge top
CHAMFER_PLUS_Y_WALL = 2.0  # at +Y above the ledge top
HEIGHT = 35.675
FLANGE_HEIGHT = 16.825
LEDGE_HEIGHT = 24.675
FLANGE_FILLET = 1.3  # outer top edge of the flanges

# --- cell seats --------------------------------------------------------------
WINDOW_DIAMETER = 15.0
FLOOR_THICKNESS = 0.6  # floor under the seat, windows go through it
SEAT_DIAMETER = 21.5
WEB_HEIGHT = 4.0  # top of the webs between cells
SEAT_CONE_START = 3.0  # seat cylinder ends, conical lead-in starts
SEAT_CONE_TOP_DIAMETER = 21.9  # lead-in diameter at the web top
CAVITY_RADIUS = 11.0  # open cavity above the webs: R11 around border cells
CAVITY_FILLET = 2.0  # R2 fillets between neighbouring border arcs

# --- wire channel on the floor face -----------------------------------------
CHANNEL_DEPTH = 1.6
CHANNEL_X = (-18.75, -13.25)  # -X side; +X side mirrored about x = 97.75
CHANNEL_Y_END_MINUS_X = 243.4416  # channel end (incl. R1 end fillets)
CHANNEL_Y_END_PLUS_X = 225.4416
CHANNEL_CORNER_Y = -13.0  # corner branch: y < -13 ...
CHANNEL_CORNER_X_END = -3.25  # ... up to x = -3.25 (+X side mirrored)
CHANNEL_CORNER_RADIUS = 5.0

# --- insert holes (12, heat-set EN-INSERT-001) --------------------------------
INSERT_X = -6.125  # -X column; +X column at 201.625 (mirrored)
INSERT_Y_FIRST_MINUS_X = CELL_PITCH_Y - 3.5  # 16.4186, then every 2 rows
INSERT_Y_FIRST_PLUS_X = 2 * CELL_PITCH_Y - 3.5  # 36.3372
INSERT_PITCH_Y = 2 * CELL_PITCH_Y
INSERT_COUNT_PER_SIDE = 6
INSERT_BORE_DIAMETER = 8.25  # from the floor face
INSERT_BORE_DEPTH = 23.55
INSERT_HOLE_DIAMETER = 4.0  # after a 45 deg step
INSERT_CBORE_DIAMETER = 8.2  # at the top face
INSERT_CBORE_DEPTH = 2.0
INSERT_TOP_CHAMFER = 0.5

# 4 mm blind holes in the floor face, 8 mm towards +Y from each insert
FLOOR_HOLE_DIAMETER = 4.0
FLOOR_HOLE_DEPTH = 6.5
FLOOR_HOLE_OFFSET_Y = 8.0

# side cross holes (4 mm, 45 deg countersink) at insert y + 8
CROSS_HOLE_Z = 29.675
CROSS_HOLE_DIAMETER = 4.0
CROSS_HOLE_END_X = -3.25  # hole bottom (x = 198.75 on the +X side)
CROSS_HOLE_SINK_DIAMETER = 7.2
CROSS_HOLE_INDICES = (1, 3, 5)  # which insert positions (both sides)

# holes in the +Y face
PLUS_Y_HOLES_X = (0.0, 23.0, 161.0, 184.0)
PLUS_Y_HOLES_Z = 29.675
PLUS_Y_HOLES_DEPTH = 6.5  # from y = 274.942
PLUS_Y_LOW_HOLES_X = (5.25, 190.25)
PLUS_Y_LOW_HOLES_Z = 11.5
PLUS_Y_LOW_HOLES_DEPTH = 6.0  # from y = 275.942
PLUS_Y_HOLE_DIAMETER = 4.0

# 5.6 mm holes into the flange ends near -Y
FLANGE_HOLE_DIAMETER = 5.6
FLANGE_HOLE_Y = -14.0
FLANGE_HOLE_Z = 8.5125
FLANGE_HOLE_DEPTH = 8.8

# lugs on the -Y face: 8 mm boss, 3.9 mm proud, 4 mm hole 6.9 deep
LUG_DIAMETER = 8.0
LUG_LENGTH = 3.9
LUG_HOLE_DIAMETER = 4.0
LUG_HOLE_DEPTH = 6.9
LUGS = ((2.75, 6.0), (192.75, 6.0))  # (x, z)

# bottom-holder-only notch in the +Y face (for the busbar tabs)
NOTCH_X = (9.25, 186.25)
NOTCH_BACK_Y = 272.9416
NOTCH_TOP_Z = 20.0
NOTCH_CORNER_RADIUS = 5.0


def cell_centres() -> list[tuple[float, float]]:
    return [
        (i * CELL_PITCH_X + (ODD_ROW_OFFSET_X if j % 2 else 0.0), j * CELL_PITCH_Y)
        for j in range(CELL_ROWS)
        for i in range(CELL_COLUMNS)
    ]


def border_centres() -> list[tuple[float, float]]:
    """Border cells in counter-clockwise order, starting at cell (0, 0)."""
    last = CELL_ROWS - 1

    def x(i, j):
        return i * CELL_PITCH_X + (ODD_ROW_OFFSET_X if j % 2 else 0.0)

    pts = [(x(i, 0), 0.0) for i in range(CELL_COLUMNS)]  # row 0, +X
    pts += [(x(CELL_COLUMNS - 1, j), j * CELL_PITCH_Y) for j in range(1, last)]
    pts += [(x(i, last), last * CELL_PITCH_Y) for i in reversed(range(CELL_COLUMNS))]
    pts += [(x(0, j), j * CELL_PITCH_Y) for j in reversed(range(1, last))]
    return pts


def mirror_x(x: float) -> float:
    return 2 * GRID_CENTRE_X - x


def insert_positions(side: int) -> list[tuple[float, float]]:
    """side -1: -X column, +1: +X column."""
    if side < 0:
        return [(INSERT_X, INSERT_Y_FIRST_MINUS_X + k * INSERT_PITCH_Y) for k in range(INSERT_COUNT_PER_SIDE)]
    return [(mirror_x(INSERT_X), INSERT_Y_FIRST_PLUS_X + k * INSERT_PITCH_Y) for k in range(INSERT_COUNT_PER_SIDE)]


def chamfered_rect(x0, x1, y0, y1, c_lo, c_hi):
    return Polygon(
        (x0, y0 + c_lo), (x0 + c_lo, y0), (x1 - c_lo, y0), (x1, y0 + c_lo),
        (x1, y1 - c_hi), (x1 - c_hi, y1), (x0 + c_hi, y1), (x0, y1 - c_hi),
        align=None,
    )


def prism(face, z0, z1):
    return extrude(Pos(0, 0, z0) * face, z1 - z0)


def cavity_face():
    """Cavity outline: border discs R11 + hull polygon + R2 fillet patches."""
    pts = border_centres()
    shape = Polygon(*pts, align=None)
    d = CAVITY_RADIUS + CAVITY_FILLET
    for k, (x1, y1) in enumerate(pts):
        shape += Pos(x1, y1) * Circle(CAVITY_RADIUS)
        x2, y2 = pts[(k + 1) % len(pts)]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        h = math.sqrt(d * d - (L / 2) ** 2)
        nx, ny = dy / L, -dx / L  # outward (right-hand) normal, CCW order
        fx, fy = (x1 + x2) / 2 + h * nx, (y1 + y2) / 2 + h * ny
        patch = Polygon((x1, y1), (fx, fy), (x2, y2), align=None) - Pos(fx, fy) * Circle(CAVITY_FILLET)
        shape += patch
    return shape


def seat_tool(cone_start: float, cone_top_diameter: float) -> Solid:
    """Window + seat + lead-in for one cell, revolved about Z."""
    r_w, r_s, r_t = WINDOW_DIAMETER / 2, SEAT_DIAMETER / 2, cone_top_diameter / 2
    prof = Polygon(
        (0, -1), (r_w, -1), (r_w, FLOOR_THICKNESS), (r_s, FLOOR_THICKNESS),
        (r_s, cone_start), (r_t, WEB_HEIGHT), (0, WEB_HEIGHT),
        align=None,
    )
    return revolve(Plane.XZ * prof, Axis.Z)


def hole_z(x, y, d, z0, z1):
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def cone_z(x, y, d0, d1, z0, z1):
    return Pos(x, y, z0) * Cone(d0 / 2, d1 / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def build_cell_holder(
    *,
    cone_start: float = SEAT_CONE_START,
    cone_top_diameter: float = SEAT_CONE_TOP_DIAMETER,
    channel_y_end=(CHANNEL_Y_END_MINUS_X, CHANNEL_Y_END_PLUS_X),
    insert_holes=None,
    cross_hole_indices=CROSS_HOLE_INDICES,
    lugs=LUGS,
    extra_cuts=None,
    extra_adds=None,
) -> Part:
    """Holder with the floor face on z = 0 growing towards +Z."""
    # body
    body = prism(chamfered_rect(FLANGE_X_MIN, FLANGE_X_MAX, Y_MIN, Y_MAX_LEDGE, CHAMFER_MINUS_Y, CHAMFER_PLUS_Y_LEDGE), 0, FLANGE_HEIGHT)
    body += prism(chamfered_rect(WALL_X_MIN, WALL_X_MAX, Y_MIN, Y_MAX_LEDGE, CHAMFER_MINUS_Y, CHAMFER_PLUS_Y_LEDGE), 0, LEDGE_HEIGHT)
    body += prism(chamfered_rect(WALL_X_MIN, WALL_X_MAX, Y_MIN, Y_MAX_WALL, CHAMFER_MINUS_Y, CHAMFER_PLUS_Y_WALL), 0, HEIGHT)
    for x, z in lugs:
        body += Pos(x, Y_MIN, z) * Rot(90, 0, 0) * Cylinder(LUG_DIAMETER / 2, LUG_LENGTH, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if extra_adds:
        for a in extra_adds:
            body += a

    cuts = []
    # flange top outer fillets (R1.3 along Y)
    r = FLANGE_FILLET
    for xe, sx in ((FLANGE_X_MIN, 1), (FLANGE_X_MAX, -1)):
        tool = Pos(xe + sx * r, Y_MIN - 1, FLANGE_HEIGHT - r) * Rot(-90, 0, 0) * Cylinder(r, Y_MAX_LEDGE - Y_MIN + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        box = Pos(xe + sx * r / 2, (Y_MIN + Y_MAX_LEDGE) / 2, FLANGE_HEIGHT - r / 2) * Box(r, Y_MAX_LEDGE - Y_MIN + 2, r)
        cuts.append(box - tool)

    # open cavity above the webs
    cuts.append(prism(cavity_face(), WEB_HEIGHT, HEIGHT + 1))
    # cell seats
    seat = seat_tool(cone_start, cone_top_diameter)
    cuts += [seat.moved(Location((x, y, 0))) for x, y in cell_centres()]

    # wire channel on the floor face (-X side, mirrored to +X)
    for side, y_end in ((-1, channel_y_end[0]), (1, channel_y_end[1])):
        x0, x1 = CHANNEL_X
        leg = Pos(0, 0, -1) * extrude(Polygon((x0, Y_MIN - 5), (x1, Y_MIN - 5), (x1, y_end + 1), (x0, y_end + 1), align=None), CHANNEL_DEPTH + 1)
        rc = CHANNEL_CORNER_RADIUS
        corner = Polygon((x0, Y_MIN - 5), (CHANNEL_CORNER_X_END, Y_MIN - 5), (CHANNEL_CORNER_X_END, CHANNEL_CORNER_Y),
                            (x0, CHANNEL_CORNER_Y), align=None)
        round_ = Polygon((x1, CHANNEL_CORNER_Y), (x1 + rc, CHANNEL_CORNER_Y), (x1 + rc, CHANNEL_CORNER_Y + rc), (x1, CHANNEL_CORNER_Y + rc), align=None) \
            - Pos(x1 + rc, CHANNEL_CORNER_Y + rc) * Circle(rc)
        tool = leg + Pos(0, 0, -1) * extrude(corner, CHANNEL_DEPTH + 1) + Pos(0, 0, -1) * extrude(round_, CHANNEL_DEPTH + 1)
        if side > 0:
            tool = mirror(tool, Plane.YZ.offset(GRID_CENTRE_X))
        cuts.append(tool)

    # insert holes
    for side in (-1, 1):
        for k, (x, y) in enumerate(insert_positions(side)):
            if insert_holes is None:
                ztop = HEIGHT
                cuts.append(hole_z(x, y, INSERT_BORE_DIAMETER, -1, INSERT_BORE_DEPTH))
                step = (INSERT_BORE_DIAMETER - INSERT_HOLE_DIAMETER) / 2
                cuts.append(cone_z(x, y, INSERT_BORE_DIAMETER, INSERT_HOLE_DIAMETER, INSERT_BORE_DEPTH, INSERT_BORE_DEPTH + step))
                cuts.append(hole_z(x, y, INSERT_HOLE_DIAMETER, INSERT_BORE_DEPTH + step, ztop + 1))
                cuts.append(hole_z(x, y, INSERT_CBORE_DIAMETER, ztop - INSERT_CBORE_DEPTH, ztop + 1))
                c = INSERT_TOP_CHAMFER
                cuts.append(cone_z(x, y, INSERT_CBORE_DIAMETER, INSERT_CBORE_DIAMETER + 2 * c + 0.2, ztop - c, ztop + 0.1))
            else:
                cuts += insert_holes(x, y)
            # blind floor hole
            cuts.append(hole_z(x, y + FLOOR_HOLE_OFFSET_Y, FLOOR_HOLE_DIAMETER, -1, FLOOR_HOLE_DEPTH))
            # side cross hole with countersink
            if k in cross_hole_indices:
                xe = WALL_X_MIN if side < 0 else WALL_X_MAX
                xb = CROSS_HOLE_END_X if side < 0 else mirror_x(CROSS_HOLE_END_X)
                length = abs(xb - xe)
                rot = Rot(0, 90, 0) if side < 0 else Rot(0, -90, 0)
                yy = y + FLOOR_HOLE_OFFSET_Y
                cuts.append(Pos(xe + side * 1, yy, CROSS_HOLE_Z) * rot * Cylinder(CROSS_HOLE_DIAMETER / 2, length + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
                sink = (CROSS_HOLE_SINK_DIAMETER - CROSS_HOLE_DIAMETER) / 2
                cuts.append(Pos(xe + side * 0.1, yy, CROSS_HOLE_Z) * rot * Cone(CROSS_HOLE_SINK_DIAMETER / 2 + 0.1, CROSS_HOLE_DIAMETER / 2, sink + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN)))

    # +Y face holes
    for x in PLUS_Y_HOLES_X:
        cuts.append(Pos(x, Y_MAX_WALL + 1, PLUS_Y_HOLES_Z) * Rot(90, 0, 0) * Cylinder(PLUS_Y_HOLE_DIAMETER / 2, PLUS_Y_HOLES_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for x in PLUS_Y_LOW_HOLES_X:
        cuts.append(Pos(x, Y_MAX_LEDGE + 1, PLUS_Y_LOW_HOLES_Z) * Rot(90, 0, 0) * Cylinder(PLUS_Y_HOLE_DIAMETER / 2, PLUS_Y_LOW_HOLES_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # flange end holes near -Y
    for xe, rot in ((FLANGE_X_MIN, Rot(0, 90, 0)), (FLANGE_X_MAX, Rot(0, -90, 0))):
        s = 1 if xe < 0 else -1
        cuts.append(Pos(xe - s, FLANGE_HOLE_Y, FLANGE_HOLE_Z) * rot * Cylinder(FLANGE_HOLE_DIAMETER / 2, FLANGE_HOLE_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # lug holes
    for x, z in lugs:
        y0 = Y_MIN - LUG_LENGTH
        cuts.append(Pos(x, y0 - 1, z) * Rot(-90, 0, 0) * Cylinder(LUG_HOLE_DIAMETER / 2, LUG_HOLE_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    if extra_cuts:
        cuts += extra_cuts

    return body - Compound(children=cuts)


def notch_tool():
    """Pocket in the +Y face, x 9.25..186.25, up to z 20, R5 top corners."""
    x0, x1 = NOTCH_X
    rc = NOTCH_CORNER_RADIUS
    prof = Polygon((x0, -1), (x1, -1), (x1, NOTCH_TOP_Z), (x0, NOTCH_TOP_Z), align=None)
    for xc, sx in ((x0 + rc, -1), (x1 - rc, 1)):
        corner = Polygon((xc, NOTCH_TOP_Z - rc), (xc + sx * rc, NOTCH_TOP_Z - rc), (xc + sx * rc, NOTCH_TOP_Z), (xc, NOTCH_TOP_Z), align=None) \
            - Pos(xc, NOTCH_TOP_Z - rc) * Circle(rc)
        prof -= corner
    # Plane.XZ faces -Y: start 1 mm outside the +Y face and cut back to the notch floor
    return extrude(Plane.XZ.offset(-(Y_MAX_LEDGE + 1)) * prof, Y_MAX_LEDGE + 1 - NOTCH_BACK_Y)


def build() -> Part:
    part = build_cell_holder(extra_cuts=[notch_tool()])
    part.label = PART_NUMBER
    return part
