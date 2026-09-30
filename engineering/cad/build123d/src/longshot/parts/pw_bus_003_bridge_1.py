"""PW-BUS-003 Bridge 1 - 0.2 mm copper series bridge over 4 rows of cells.

Dimensions probed from the Fusion reference solid. Component frame: sheet in
the XY plane with its top face on z = 0.2 (bottom on z = 0), cell (0, 0) of
the first row at the origin, rows stepping towards +Y. Each cell gets a
circular R7 cut-out with two 4 mm wide weld tongues (one per half, point
symmetric about the cell centre) that are joggled 1 mm down (towards the
cell) through two 45 deg bends with 0.2 mm inner radius.

This module also holds the shared sheet-metal builder used by all the
0.2 mm copper busbars (PW-BUS-001 .. 004): hex-packed cell pads, filleted
outline, weld tongues, locating ear and an optional 90 deg down-folded
terminal wall.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from build123d import (
    Axis,
    Box,
    Circle,
    Compound,
    Cylinder,
    Face,
    Line,
    Part,
    Plane,
    Pos,
    Rectangle,
    Sketch,
    ThreePointArc,
    Vector,
    Wire,
    extrude,
    fillet,
    make_face,
)

PART_NUMBER = "PW-BUS-003-Bridge_1"

# --- material ---------------------------------------------------------------
THICKNESS = 0.2  # single layer of 0.2 mm copper
BEND_RADIUS = 0.2  # inner bend radius of every bend (outer = 0.4)

# --- cell lattice (21700 cells, hex packed) --------------------------------
CELL_PITCH = 23.0
ROW_PITCH = CELL_PITCH * math.sin(math.radians(60))  # 19.9186
EDGE_INSET = 1.2  # outline sits 1.2 mm inside the half-pitch cell boundary
PAD_HALF_X = CELL_PITCH / 2 - EDGE_INSET  # 10.3
PAD_HALF_Y = ROW_PITCH / 2 - EDGE_INSET  # 8.7593

# --- outline -------------------------------------------------------------
CONVEX_RADIUS = 3.8
CONCAVE_RADIUS = 6.2
EAR_LENGTH = 4.0  # locating ear: pad edge to centre of its R1 end
EAR_WIDTH = 2.0

# --- per-cell cut-out and weld tongues ------------------------------------
CUTOUT_RADIUS = 7.0
TONGUE_WIDTH = 4.0
TONGUE_GAP = 0.5  # tongue inner edge from the cell centre line (x)
# root (first bend line) distance from the cell centre (y); equals
# sqrt(7^2 - 0.5^2) - 3 + 0.2*sqrt(2), i.e. a 3 mm flange setback on the R7 edge
TONGUE_ROOT = 4.264963
TONGUE_TIP = 3.817880  # tip, past the cell centre (y); root-to-tip 8.0828 in plan
TONGUE_TIP_RADIUS = 0.5
TONGUE_DROP = 1.0  # pad offset towards the cell
TONGUE_BEND_ANGLE = 45.0

# --- this part ---------------------------------------------------------------
SHEET_TOP_Z = THICKNESS
ROW_COUNTS = (5, 4, 5, 4)  # cells per row, rows 0..3 from y = 0 towards +Y
# even rows start at x = 0, odd rows at x = CELL_PITCH / 2; the odd-row pad
# span (x = 1.2 .. 90.8) runs as a solid core over the full height


@dataclass
class Busbar:
    """Description of one flat busbar in its component frame."""

    rows: list[tuple[float, float, int]]  # (x of first cell, y, cell count)
    rects: list[tuple[float, float, float, float]]  # extra outline rects (x0, x1, y0, y1)
    ear: tuple[float, float, int]  # (pad edge x, y, direction -1 / +1)
    top_z: float = SHEET_TOP_Z
    radius_overrides: dict[tuple[float, float], float] = field(default_factory=dict)
    # optional 90 deg down-folded wall: (bend line y, side -1/+1, x0, x1, depth,
    # corner radius, hole x list, hole depth below top, hole diameter)
    wall: tuple | None = None


def cell_centres(bar: Busbar) -> list[tuple[float, float]]:
    return [(x0 + i * CELL_PITCH, y) for x0, y, n in bar.rows for i in range(n)]


def _row_rect(x0: float, y: float, n: int) -> tuple[float, float, float, float]:
    return (x0 - PAD_HALF_X, x0 + (n - 1) * CELL_PITCH + PAD_HALF_X, y - PAD_HALF_Y, y + PAD_HALF_Y)


def _outline(bar: Busbar) -> Face:
    rects = [_row_rect(*r) for r in bar.rows] + list(bar.rects)
    sk = Sketch()
    for x0, x1, y0, y1 in rects:
        sk += Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)
    face = sk.faces()[0]

    def inside(x: float, y: float) -> bool:
        return any(x0 < x < x1 and y0 < y < y1 for x0, x1, y0, y1 in rects)

    skip_y = bar.wall[0] if bar.wall else None
    by_radius: dict[float, list[tuple[float, float]]] = {}
    for v in face.vertices():
        x, y = v.X, v.Y
        if skip_y is not None and abs(y - skip_y) < 1e-6:
            continue  # corners on the bend line stay sharp
        d = 1e-3
        n_in = sum(inside(x + sx * d, y + sy * d) for sx in (-1, 1) for sy in (-1, 1))
        if n_in not in (1, 3):
            continue  # collinear seam between touching rectangles
        r = CONVEX_RADIUS if n_in == 1 else CONCAVE_RADIUS
        for (ox, oy), orad in bar.radius_overrides.items():
            if abs(ox - x) < 1e-3 and abs(oy - y) < 1e-3:
                r = orad
        by_radius.setdefault(r, []).append((x, y))
    for r, pts in by_radius.items():
        verts = [v for v in face.vertices() if any(abs(v.X - x) < 1e-6 and abs(v.Y - y) < 1e-6 for x, y in pts)]
        face = face.fillet_2d(r, verts)

    ex, ey, edir = bar.ear
    ear = Pos(ex + edir * EAR_LENGTH / 2, ey) * Rectangle(EAR_LENGTH, EAR_WIDTH)
    ear += Pos(ex + edir * EAR_LENGTH, ey) * Circle(EAR_WIDTH / 2)
    return (Sketch() + face + ear).faces()[0]


def _cutout() -> Sketch:
    """Cell cut-out: R7 disc minus the two tongue roots (cell at origin)."""
    root_len = CUTOUT_RADIUS + 1.0 - TONGUE_ROOT
    cx = TONGUE_GAP + TONGUE_WIDTH / 2
    hole = Circle(CUTOUT_RADIUS)
    hole -= Pos(cx, -TONGUE_ROOT - root_len / 2) * Rectangle(TONGUE_WIDTH, root_len)
    hole -= Pos(-cx, TONGUE_ROOT + root_len / 2) * Rectangle(TONGUE_WIDTH, root_len)
    return hole


def _tongue() -> Part:
    """Weld tongue rooted at y = -TONGUE_ROOT, x = TONGUE_GAP..+WIDTH, top face at z = 0."""
    t, ri = THICKNESS, BEND_RADIUS
    ro = ri + t
    a = math.radians(TONGUE_BEND_ANGLE)
    s, c = math.sin(a), math.cos(a)
    # straight ramp length between the two bends (sheet mid-plane independent)
    ramp = (TONGUE_DROP - (ri + ro) * (1 - c)) / s
    y0 = -TONGUE_ROOT
    A = Vector(y0, -ro)  # first bend axis (below the sheet)
    B = Vector(y0 + (ro + ri) * s + ramp * c, -TONGUE_DROP + ri)  # second bend axis
    tip = TONGUE_TIP + 1.0  # overshoot, trimmed by the plan-view mask

    def P(v: Vector) -> tuple[float, float]:
        return (v.X, v.Y)

    def on(ctr: Vector, r: float, deg: float) -> Vector:
        return ctr + Vector(r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))

    th = TONGUE_BEND_ANGLE
    pts_top = [on(A, ro, 90), on(A, ro, 90 - th / 2), on(A, ro, 90 - th)]
    pts_top2 = [on(B, ri, 180 + 90 - th), on(B, ri, 270 - th / 2), on(B, ri, 270)]
    pts_bot2 = [on(B, ro, 270), on(B, ro, 270 - th / 2), on(B, ro, 180 + 90 - th)]
    pts_bot = [on(A, ri, 90 - th), on(A, ri, 90 - th / 2), on(A, ri, 90)]
    pl = Plane.YZ  # local (u, v) = (Y, Z)
    edges = [
        ThreePointArc(*[pl.from_local_coords(p) for p in pts_top]),
        Line(pl.from_local_coords(pts_top[2]), pl.from_local_coords(pts_top2[0])),
        ThreePointArc(*[pl.from_local_coords(p) for p in pts_top2]),
        Line(pl.from_local_coords(pts_top2[2]), pl.from_local_coords((tip, -TONGUE_DROP))),
        Line(pl.from_local_coords((tip, -TONGUE_DROP)), pl.from_local_coords((tip, -TONGUE_DROP - t))),
        Line(pl.from_local_coords((tip, -TONGUE_DROP - t)), pl.from_local_coords(pts_bot2[0])),
        ThreePointArc(*[pl.from_local_coords(p) for p in pts_bot2]),
        Line(pl.from_local_coords(pts_bot2[2]), pl.from_local_coords(pts_bot[0])),
        ThreePointArc(*[pl.from_local_coords(p) for p in pts_bot]),
        Line(pl.from_local_coords(pts_bot[2]), pl.from_local_coords(pts_top[0])),
    ]
    profile = make_face(Wire(edges))
    tongue = Pos(TONGUE_GAP, 0, 0) * extrude(profile, dir=(1, 0, 0), amount=TONGUE_WIDTH)
    # plan-view mask with the R0.5 tip corners
    ylo = y0 - 1.0
    mask = Pos(TONGUE_GAP + TONGUE_WIDTH / 2, (ylo + TONGUE_TIP) / 2) * Rectangle(TONGUE_WIDTH, TONGUE_TIP - ylo)
    mask_face = mask.faces()[0]
    tip_verts = [v for v in mask_face.vertices() if abs(v.Y - TONGUE_TIP) < 1e-6]
    mask_face = mask_face.fillet_2d(TONGUE_TIP_RADIUS, tip_verts)
    prism = Pos(0, 0, -5) * extrude(mask_face, 10)
    return tongue & prism


def _wall(bar: Busbar) -> Part:
    yb, side, x0, x1, depth, corner_r, holes_x, hole_z, hole_d = bar.wall
    t, ri = THICKNESS, BEND_RADIUS
    ro = ri + t
    axis_z = bar.top_z - ro
    width = x1 - x0
    # quarter-annulus bend (axis along X at y = yb, z = axis_z)
    ring = extrude(Plane.YZ.offset(x0) * (Circle(ro) - Circle(ri)), width)
    quad = Pos((x0 + x1) / 2, yb + side * ro / 2, axis_z + ro / 2) * Box(width, ro, ro)
    bend = Pos(0, yb, axis_z) * ring & quad
    # flat wall
    z_bot = bar.top_z - depth
    y_in = yb + side * ri
    wall = Pos((x0 + x1) / 2, y_in + side * t / 2, (axis_z + z_bot) / 2) * Box(width, t, axis_z - z_bot)
    wall = fillet(
        wall.edges().filter_by(Axis.Y).filter_by(lambda e: abs(e.center().Z - z_bot) < 1e-6),
        corner_r,
    )
    for hx in holes_x:
        wall -= Pos(hx, y_in + side * t / 2, bar.top_z - hole_z) * Cylinder(
            hole_d / 2, 1.0, rotation=(90, 0, 0)
        )
    return bend + wall


def build_busbar(bar: Busbar) -> Part:
    outline = Sketch() + _outline(bar)
    for x, y in cell_centres(bar):
        outline -= Pos(x, y) * _cutout()
    sheet = Pos(0, 0, bar.top_z - THICKNESS) * extrude(outline, THICKNESS)
    tongue = _tongue()
    tongues = []
    for x, y in cell_centres(bar):
        tongues.append(Pos(x, y, bar.top_z) * tongue)
        tongues.append(Pos(x, y, bar.top_z) * tongue.rotate(Axis.Z, 180))
    extra = tongues + ([_wall(bar)] if bar.wall else [])
    return Part(Compound([sheet.solids()[0].fuse(*extra).clean()]).wrapped)


def bridge_1_busbar(ear_side: int = -1) -> Busbar:
    """Bridge 1; ``ear_side=+1`` puts the locating ear on the +X end (the mirror part)."""
    rows = [
        (0.0 if r % 2 == 0 else CELL_PITCH / 2, r * ROW_PITCH, n) for r, n in enumerate(ROW_COUNTS)
    ]
    core = (CELL_PITCH / 2 - PAD_HALF_X, CELL_PITCH / 2 + 3 * CELL_PITCH + PAD_HALF_X, -PAD_HALF_Y, 3 * ROW_PITCH + PAD_HALF_Y)
    ear_x = -PAD_HALF_X if ear_side < 0 else 4 * CELL_PITCH + PAD_HALF_X
    return Busbar(rows=rows, rects=[core], ear=(ear_x, 0.0, ear_side))


def build() -> Part:
    part = build_busbar(bridge_1_busbar(ear_side=-1))
    part.label = PART_NUMBER
    return part
