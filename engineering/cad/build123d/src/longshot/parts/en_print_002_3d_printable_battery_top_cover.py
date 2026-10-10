"""EN-PRINT-002 3D-Printable Battery Top Cover - printed end cap at the -Y end of the pack.

The cover closes the -Y end of the 14S9P stack and carries the main PCB and the
ET60S connector. All dimensions were probed from the Fusion reference solid
(bbox 249.0 x 52.906 x 138.575 mm, 315 733 mm^3 over four solids). Frame: Fusion
component frame = global assembly frame; the layout is mirror symmetric about
x = -5.75 (X0) apart from a few small details.

Construction (four solids, as in the reference):

* main body - an end plate in XZ (outer face y = -172.529, 3 mm floor, r3 outer
    edge) with a skirt up to y = -134.571. The skirt outline steps out by 3 mm
    (O1 -> O2) through an S-shaped shoulder between y = -156.15 and -149.97, and
    a connector tower (z up to 93.65) rises above the top wall. Inside: a 6 mm
    central block with 5.7 deg end ramps and elliptical z run-outs, thick end
    blocks with the reinforcement-sheet slots, strap holes, fins and strap
    channels, a fuse box around the rectangular opening, square nut traps on the
    tie-rod holes, and the r9 floor round / rounded lip along the end walls. The
    tower has a sloped hood over the plate, the connector notch with its sloped
    channel floor, latch pockets and four M3 insert holes; the end walls carry four
    M4 insert holes. Outside: two strap mounds (intersection of an XY and a ZY
    silhouette) with a C-shaped strap slot, a shallow recess between them and a
    lip under the connector.
* two latches (7.7 x 11.48 x 3.5 mm) in the latch pockets on the tower roof;
* the latch pin (d 2.5 x 64 mm, 0.2 mm end chamfers).
"""

from __future__ import annotations

import math

from build123d import (
    Align,
    AngularDirection,
    Axis,
    Box,
    Circle,
    Compound,
    Cylinder,
    GeomType,
    chamfer,
    Edge,
    Face,
    Location,
    Part,
    Plane,
    Pos,
    Rectangle,
    RectangleRounded,
    Vector,
    Wire,
    extrude,
    fillet,
    mirror,
    offset,
)

PART_NUMBER = "EN-PRINT-002-3D-Printable_Battery_Top_Cover"

VALIDATION_NOTE = (
    "at the 2 % sym-diff limit: sampled 1.97 +/- 0.24 % (20k points) and 2.29 +/- 0.10 % "
    "(100k points). Differences: strap-mound corner rounds modelled as chamfers, r9 floor round "
    "and end-wall lip as stepped layers, simplified end-block notches, tower-roof insert bosses "
    "and small r0.5-r1 rounds not modelled."
)

X0 = -5.75  # mirror plane of the layout
ZC = -0.1  # centre of the end blocks / strap slots in z

# --- Y levels ----------------------------------------------------------------
Y_OUT = -172.529  # outer face of the end plate
Y_FLOOR = -169.529  # inner floor (3 mm plate)
Y_BLOCK = -166.529  # top of the 6 mm central block
SHOULDER = [(-156.15, 0.0), (-154.516, 0.485), (-153.409, 1.781), (-151.849, 2.766), (-149.971, 3.0)]  # (y, growth)
SHOULDER_LAYERS = 8
Y_LIP = -149.571  # inner step of the skirt
Y_TOWER_INNER_STEP = -152.026  # tower cavity switches to the upper profile here
Y_TOWER_TOP = -138.41  # top of the connector tower walls
Y_TOP = -134.571  # top of the skirt

# --- lower outer outline O1 (x, z) --------------------------------------------
O1_X = -127.25  # left end (right end mirrored about X0)
O1_Z_BOT = -44.925
O1_Z_TOP = 43.0
O1_R_BOT, O1_R_TOP = 2.5, 4.0
TOWER_X = -61.25  # tower side (lower)
TOWER_R_FOOT = 4.5
TOWER_R_SHOULDER = 7.5
TOWER_Z_TOP = 93.65
PLATE_EDGE_R = 3.0  # outer edge of the end plate

# --- upper outer outline O2 ------------------------------------------------------
O2_X = -130.25
O2_Z_TOP = 46.0
O2_R_BOT, O2_R_TOP = 5.5, 7.0
TOP_EDGE_R = 2.0


def _poly(pts: list[tuple[float, float, float]]) -> Face:
    """Closed polygon in local (u, v) = global (x, z) with per-vertex rounds."""
    clean = []
    for p in pts:
        if clean and abs(clean[-1][0] - p[0]) < 1e-9 and abs(clean[-1][1] - p[1]) < 1e-9:
            continue
        clean.append(p)
    if abs(clean[0][0] - clean[-1][0]) < 1e-9 and abs(clean[0][1] - clean[-1][1]) < 1e-9:
        clean.pop()
    # drop collinear points
    pts2 = []
    n = len(clean)
    for i, p in enumerate(clean):
        a, c = clean[i - 1], clean[(i + 1) % n]
        cross = (p[0] - a[0]) * (c[1] - p[1]) - (p[1] - a[1]) * (c[0] - p[0])
        if abs(cross) > 1e-9:
            pts2.append(p)
    face = Face(Wire.make_polygon([(x, z) for x, z, _ in pts2], close=True))
    by_r: dict[float, list] = {}
    for x, z, r in pts2:
        if r > 0:
            by_r.setdefault(r, []).append((x, z))
    for r, xy in sorted(by_r.items(), reverse=True):
        verts = [v for v in face.vertices() if any(abs(v.X - x) + abs(v.Y - z) < 1e-6 for x, z in xy)]
        face = fillet(verts, r)
    return face


def _sym(half: list[tuple[float, float, float]]) -> Face:
    """``half`` runs over the -X side from the top centre line to the bottom
    centre line; the +X side is its mirror image about x = X0."""
    right = [(2 * X0 - x, z, r) for x, z, r in reversed(half)]
    return _poly(half + right)


def _plane(y: float) -> Plane:
    return Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


def _prism(face: Face, y0: float, y1: float) -> Part:
    return extrude(_plane(y0) * face, amount=y1 - y0, dir=(0, 1, 0))


def _poly_xy(pts) -> Face:
    return Face(Wire.make_polygon([Vector(x, y) for x, y in pts], close=True))


def _plane_zy() -> Plane:
    """Plane with local (u, v) = global (z, y), normal along -X."""
    return Plane(origin=(0, 0, 0), x_dir=(0, 0, 1), z_dir=(-1, 0, 0))


# ---------------------------------------------------------------------------
def outline_o1(d: float = 0.0) -> Face:
    """Lower outer outline; ``d`` (0..3) grows it towards O2 through the shoulder."""
    c45 = 131.028 + d * (140.383 - 131.028) / 3.0  # lower 45 deg tower line z = x + c45
    xt = TOWER_X - d
    half = [
        (X0, TOWER_Z_TOP, 0),
        (-46.753, TOWER_Z_TOP, 3.0),
        (-49.883, 90.52, 3.0),
        (-49.883, -49.883 + c45, 3.0),
        (xt, xt + c45, TOWER_R_SHOULDER),
    ] + ([
        (xt, O1_Z_TOP + d, TOWER_R_FOOT),
    ] if d < 0.5 else [  # O2-style 45 deg foot chamfer grows with d
        (xt, O1_Z_TOP + 4 * d, 6.5 * d / 3),
        (xt - 3 * d, O1_Z_TOP + d, 6.5 * d / 3),
    ]) + [
        (O1_X - d, O1_Z_TOP + d, O1_R_TOP + d),
        (O1_X - d, O1_Z_BOT, O1_R_BOT + d),
        (X0, O1_Z_BOT, 0),
    ]
    return _sym(half)


def outline_o2(tower: bool = True) -> Face:
    if not tower:
        half = [(X0, O2_Z_TOP, 0), (O2_X, O2_Z_TOP, O2_R_TOP), (O2_X, O1_Z_BOT, O2_R_BOT), (X0, O1_Z_BOT, 0)]
        return _sym(half)
    half = [
        (X0, TOWER_Z_TOP, 0),
        (-46.733, TOWER_Z_TOP, 3.0),
        (-64.25, -64.25 + 140.383, 8.0),
        (-64.25, -64.25 + 119.25, 6.5),
        (-73.25, O2_Z_TOP, 6.5),
        (O2_X, O2_Z_TOP, O2_R_TOP),
        (O2_X, O1_Z_BOT, O2_R_BOT),
        (X0, O1_Z_BOT, 0),
    ]
    return _sym(half)


def inner_upper() -> Face:
    """Skirt cavity above the lip (y > Y_LIP)."""
    half = [
        (X0, 80.15, 0),
        (-51.757, 80.15, 0),
        (-58.25, 73.657, 2.0),
        (-58.25, 39.525, 7.5),
        (-99.553, 39.525, 0),
        (-99.553, 42.525, 0),
        (-123.4, 42.525, 0),
        (-123.4, 39.525, 0),
        (-124.4, 39.525, 1.0),
        (-124.4, 17.6, 2.0),
        (-116.4, 17.6, 1.0),
        (-116.4, -17.8, 1.0),
        (-124.4, -17.8, 2.0),
        (-124.4, -39.725, 1.0),
        (-123.4, -39.725, 0),
        (-123.4, -42.525, 0),
        (-99.553, -42.525, 0),
        (-99.553, -39.725, 0),
        (X0, -39.725, 0),
    ]
    return _sym(half)


def _path_edges(start, segs):
    """Edges from ``start`` through segments ('L', p) or ('A', centre, p)."""
    edges, cur = [], start
    for seg in segs:
        if seg[0] == "L":
            p = seg[1]
            if abs(p[0] - cur[0]) + abs(p[1] - cur[1]) > 1e-9:
                edges.append(Edge.make_line(Vector(*cur), Vector(*p)))
        else:
            c, p = seg[1], seg[2]
            r = math.hypot(cur[0] - c[0], cur[1] - c[1])
            edges.append(_arc_c(c, r, cur, p))
        cur = p
    return edges, cur


def _sym_path(start, segs) -> Face:
    """Closed face from a -X half path (top centre -> bottom centre) mirrored about X0."""
    m = lambda p: (2 * X0 - p[0], p[1])
    e1, end = _path_edges(start, segs)
    pts = [start] + [s[-1] for s in segs]
    back = []
    for i in range(len(segs) - 1, -1, -1):
        seg = segs[i]
        target = m(pts[i])
        back.append(("L", target) if seg[0] == "L" else ("A", m(seg[1]), target))
    e2, _ = _path_edges(m(end), back)
    return Face(Wire(e1 + e2))


INNER_END_UPPER = [  # skirt cavity, -X end, upper S-curve into the end block (x, z)
    ("L", (-120.25, 31.949)), ("A", (-112.25, 31.949), (-114.75, 24.349)),
    ("A", (-117.25, 16.75), (-109.63, 19.185)), ("L", (-109.207, 18.307)),
]
INNER_END_LOWER = [
    ("L", (-109.207, -18.949)), ("L", (-109.63, -19.385)),
    ("A", (-117.25, -16.95), (-113.25, -23.878)), ("A", (-109.25, -30.806), (-117.25, -30.806)),
    ("L", (-117.25, -32.225)), ("L", (-119.664, -34.639)), ("A", (-118.25, -36.053), (-120.25, -36.053)),
    ("L", (-120.25, -39.725)),
]


def inner_lower() -> Face:
    """Skirt cavity below the lip, above the floor."""
    segs = [
        ("L", (-44.922, 80.0)), ("A", (-44.922, 75.5), (-48.104, 78.682)), ("L", (-56.932, 69.854)),
        ("A", (-53.75, 66.672), (-58.25, 66.672)), ("L", (-58.25, 47.025)), ("A", (-65.75, 47.025), (-65.75, 39.525)),
        ("L", (-120.25, 39.525)),
    ] + INNER_END_UPPER + INNER_END_LOWER + [("L", (X0, -39.725))]
    return _sym_path((X0, 80.0), segs)


# --- strap mounds under the end plate (left one; right one mirrored) --------
MOUND_FILLET_R = 12.5  # concave run-out into the plate
MOUND_BULGE_R = 35.0
MOUND_BULGE_C_XY = (-88.627, -157.555)  # (x, y) centre of the r35 bulge, x profile
MOUND_BULGE_C_ZY = (-0.135, -157.554)  # (z, y) centre, z profile (upper side)
MOUND_ZC = -0.1685  # mound centre in z
MOUND_Y_BOT = -187.477
MOUND_X_OUT = -127.375  # outer run-out tangent point on the plate
MOUND_X_IN = -49.55  # inner run-out tangent point on the plate
MOUND_Z_HALF = 38.78  # run-out tangent points at MOUND_ZC +/- this
MOUND_ARM_R = 8.0  # bottom rounds of the strap arms
MOUND_CHAMFER_K = -32.21  # inner corner rounds as equal-area chamfers: x + |z - ZC| - slope * (y + 175.5) <= K
MOUND_CHAMFER_SLOPE = 1.862  # the rounds (r 8..10) grow with depth
SLOT_X = -109.2  # strap slot through the mound (open towards +X)
SLOT_Z = (-16.375, 15.925)
SLOT_Y = -176.529  # slot floor
SLOT_R = 2.0


def _arc_c(c, r, p0, p1):
    """Circular arc of centre c from p0 to p1 (the short way)."""
    a0 = math.degrees(math.atan2(p0[1] - c[1], p0[0] - c[0]))
    a1 = math.degrees(math.atan2(p1[1] - c[1], p1[0] - c[0]))
    d = (a1 - a0 + 180.0) % 360.0 - 180.0
    r0, r1 = math.hypot(p0[0] - c[0], p0[1] - c[1]), math.hypot(p1[0] - c[0], p1[1] - c[1])
    if abs(r0 - r1) > 1e-9 or abs(r0 - r) > 1e-6:  # probed points: pass exactly through them
        am = math.radians(a0 + d / 2)
        return Edge.make_three_point_arc(
            Vector(p0[0], p0[1]), Vector(c[0] + r * math.cos(am), c[1] + r * math.sin(am)), Vector(p1[0], p1[1])
        )
    pl = Plane.XY.move(Location((c[0], c[1], 0)))
    if d >= 0:
        arc = Edge.make_circle(r, pl, a0, a0 + d, AngularDirection.COUNTER_CLOCKWISE)
    else:
        arc = Edge.make_circle(r, pl, a0 + d, a0, AngularDirection.COUNTER_CLOCKWISE).reversed()
    return arc


def _chain_face(edges) -> Face:
    return Face(Wire(edges))


def _tangent_pt(c, r, towards):
    """Point on circle (c, r) in the direction of ``towards``."""
    dx, dy = towards[0] - c[0], towards[1] - c[1]
    d = math.hypot(dx, dy)
    return (c[0] + r * dx / d, c[1] + r * dy / d)


def mound_x_profile() -> Face:
    """Mound silhouette in the XY plane (u = x, v = y)."""
    cb = MOUND_BULGE_C_XY
    c1 = (MOUND_X_OUT, Y_OUT - MOUND_FILLET_R)
    t1 = _tangent_pt(c1, MOUND_FILLET_R, cb)
    p45 = (cb[0] - MOUND_BULGE_R / math.sqrt(2), cb[1] - MOUND_BULGE_R / math.sqrt(2))
    c3 = (-110.406, -181.03)  # r3 knee
    k0, k1 = (-112.528, -183.151), (-110.876, -183.993)
    s_end = (-88.548, MOUND_Y_BOT)  # 9 deg bottom slope reaches the flat
    f_end = (-72.994, MOUND_Y_BOT)
    c5 = (MOUND_X_IN, Y_OUT - MOUND_FILLET_R)
    t5 = (-60.277, -178.612)
    edges = [
        Edge.make_line(Vector(MOUND_X_OUT, Y_OUT + 1), Vector(MOUND_X_OUT, Y_OUT)),
        _arc_c(c1, MOUND_FILLET_R, (MOUND_X_OUT, Y_OUT), t1),
        _arc_c(cb, MOUND_BULGE_R, t1, p45),
        Edge.make_line(Vector(*p45), Vector(*k0)),
        _arc_c(c3, 3.0, k0, k1),
        Edge.make_line(Vector(*k1), Vector(*s_end)),
        Edge.make_line(Vector(*s_end), Vector(*f_end)),
        Edge.make_three_point_arc(Vector(*f_end), Vector(-64.557, -184.568), Vector(-62.126, -181.505)),
        Edge.make_line(Vector(-62.126, -181.505), Vector(*t5)),
        _arc_c(c5, MOUND_FILLET_R, t5, (MOUND_X_IN, Y_OUT)),
        Edge.make_line(Vector(MOUND_X_IN, Y_OUT), Vector(MOUND_X_IN, Y_OUT + 1)),
        Edge.make_line(Vector(MOUND_X_IN, Y_OUT + 1), Vector(MOUND_X_OUT, Y_OUT + 1)),
    ]
    return _chain_face(edges)


def mound_z_profile() -> Face:
    """Mound silhouette in the ZY plane (u = z, v = y), symmetric about MOUND_ZC."""
    zc = MOUND_ZC
    cb = (zc, MOUND_BULGE_C_ZY[1])
    top = []
    c1 = (zc + MOUND_Z_HALF, Y_OUT - MOUND_FILLET_R)
    t1 = _tangent_pt(c1, MOUND_FILLET_R, cb)
    p45 = (cb[0] + MOUND_BULGE_R / math.sqrt(2), cb[1] - MOUND_BULGE_R / math.sqrt(2))
    ca = (zc + 16.2425, -179.529)  # arm bottom round
    pa = (ca[0] + MOUND_ARM_R / math.sqrt(2), ca[1] - MOUND_ARM_R / math.sqrt(2))
    pb = (ca[0], ca[1] - MOUND_ARM_R)
    m = lambda p: (2 * zc - p[0], p[1])
    edges = [
        Edge.make_line(Vector(zc + MOUND_Z_HALF, Y_OUT + 1), Vector(zc + MOUND_Z_HALF, Y_OUT)),
        _arc_c(c1, MOUND_FILLET_R, (zc + MOUND_Z_HALF, Y_OUT), t1),
        _arc_c(cb, MOUND_BULGE_R, t1, p45),
        Edge.make_line(Vector(*p45), Vector(*pa)),
        _arc_c(ca, MOUND_ARM_R, pa, pb),
        Edge.make_line(Vector(*pb), Vector(*m(pb))),
        _arc_c(m(ca), MOUND_ARM_R, m(pb), m(pa)),
        Edge.make_line(Vector(*m(pa)), Vector(*m(p45))),
        _arc_c(cb, MOUND_BULGE_R, m(p45), m(t1)),
        _arc_c(m(c1), MOUND_FILLET_R, m(t1), m((zc + MOUND_Z_HALF, Y_OUT))),
        Edge.make_line(Vector(*m((zc + MOUND_Z_HALF, Y_OUT))), Vector(*m((zc + MOUND_Z_HALF, Y_OUT + 1)))),
        Edge.make_line(Vector(*m((zc + MOUND_Z_HALF, Y_OUT + 1))), Vector(zc + MOUND_Z_HALF, Y_OUT + 1)),
    ]
    return _chain_face(edges)


def build_mound() -> Part:
    fx = mound_x_profile()
    px = extrude(Plane.XY * fx, amount=100, both=True)  # along Z
    fz = mound_z_profile()
    # local (u, v) = (z, y) on a plane whose normal is X
    pz = extrude(_plane_zy() * fz, amount=200, both=True)
    mound = px & pz
    # inner (+X) corner chamfers: two leaning planes
    for sz in (1, -1):
        n = Vector(1, -MOUND_CHAMFER_SLOPE, sz).normalized()
        p0 = Vector(MOUND_CHAMFER_K, -175.5, MOUND_ZC)
        half = Plane(origin=p0, z_dir=n) * Box(400, 400, 200, align=(Align.CENTER, Align.CENTER, Align.MIN))
        mound -= half & (Pos(-60, (MOUND_Y_BOT + Y_OUT) / 2 - 1, 0) * Box(60, Y_OUT - MOUND_Y_BOT + 2, 100))
    slot = Pos((SLOT_X + 100) / 2 + 0.0, 0, 0) * RectangleRounded(100 - SLOT_X + 0.0, SLOT_Z[1] - SLOT_Z[0], SLOT_R)
    slot = Pos(SLOT_X + (100 - SLOT_X) / 2, (SLOT_Z[0] + SLOT_Z[1]) / 2) * RectangleRounded(100 - SLOT_X, SLOT_Z[1] - SLOT_Z[0], SLOT_R)
    mound -= _prism(slot, MOUND_Y_BOT - 1, SLOT_Y)
    return mound


# --- central block on the inside of the plate ---------------------------------
BLOCK_X_TOP = (-70.51, 59.01)  # flat top (Y_BLOCK)
BLOCK_X_FOOT = (-100.51, 89.01)  # ramps (5.7 deg) meet the floor
BLOCK_Z_TOP = (-24.829, 24.775)  # z sides run out into the floor as quarter ellipses
BLOCK_Z_FOOT = (-37.725, 37.275)
BLOCK_NOTCH_X = (17.009, 34.009)  # 2 mm deep U-notch in the top, r5 corners
BLOCK_NOTCH_Z = 4.775
BLOCK_NOTCH_DEPTH = 2.0
BLOCK_NOTCH_R = 5.0


def build_block() -> Part:
    h = Y_BLOCK - Y_FLOOR
    xy = _poly_xy([
        (BLOCK_X_FOOT[0], Y_FLOOR - 0.5), (BLOCK_X_FOOT[0], Y_FLOOR), (BLOCK_X_TOP[0], Y_BLOCK),
        (BLOCK_X_TOP[1], Y_BLOCK), (BLOCK_X_FOOT[1], Y_FLOOR), (BLOCK_X_FOOT[1], Y_FLOOR - 0.5),
    ])
    px = extrude(Plane.XY * xy, amount=60, both=True)
    # z sides: quarter ellipses (semi-axes run-out x block height), tangent to the floor
    def quarter(z_top, z_foot, n=12):
        a = z_foot - z_top
        return [Vector(z_top + a * (1 - math.cos(t)), Y_BLOCK - h * math.sin(t))
                for t in (i * math.pi / 2 / n for i in range(n + 1))]
    q1 = quarter(BLOCK_Z_TOP[1], BLOCK_Z_FOOT[1])
    q0 = quarter(BLOCK_Z_TOP[0], BLOCK_Z_FOOT[0])
    edges = [
        Edge.make_spline(q1),
        Edge.make_line(q1[-1], Vector(q1[-1].X, Y_FLOOR - 0.5)),
        Edge.make_line(Vector(q1[-1].X, Y_FLOOR - 0.5), Vector(q0[-1].X, Y_FLOOR - 0.5)),
        Edge.make_line(Vector(q0[-1].X, Y_FLOOR - 0.5), q0[-1]),
        Edge.make_spline(list(reversed(q0))),
        Edge.make_line(q0[0], q1[0]),
    ]
    pz = extrude(_plane_zy() * Face(Wire(edges)), amount=150, both=True)
    block = px & pz
    notch = _poly([
        (BLOCK_NOTCH_X[0], 40, 0), (BLOCK_NOTCH_X[0], BLOCK_NOTCH_Z, BLOCK_NOTCH_R),
        (BLOCK_NOTCH_X[1], BLOCK_NOTCH_Z, BLOCK_NOTCH_R), (BLOCK_NOTCH_X[1], 40, 0),
    ])
    block -= _prism(notch, Y_BLOCK - BLOCK_NOTCH_DEPTH, Y_BLOCK + 1)
    return block


# --- connector tower ------------------------------------------------------------
Y_TOWER_STEP = -141.41  # thick tower roof ends here; thin 3 mm walls above
HOOD_P0 = (-171.903, 78.858)  # (y, z) points of the sloped hood at the plate
HOOD_P1 = (-161.372, 92.484)
NOTCH_X = (-31.235, 19.735)  # connector notch through the roof
CHANNEL_X = (-34.235, 22.735)  # connector channel floor under the notch
# channel floor: top (notch floor) and bottom (cavity roof) as (y, z) polylines
CHANNEL_TOP = [
    (-172.014, 68.35), (-163.135, 68.35), (-158.113, 84.548), (-156.466, 86.65), (-156.28, 86.65),
    (-154.42, 84.996), (-154.274, 83.65), (-149.79, 83.65), (-149.79, 84.65), (-146.71, 84.65),
    (-146.21, 85.35), (-138.0, 85.35),
]
CHANNEL_BOTTOM = [
    (Y_FLOOR, 65.35), (-163.135, 65.35), (-159.77, 67.885), (-156.296, 80.0), (-148.241, 80.0),
    (-147.026, 80.15), (-141.41, 80.15), (-141.41, 82.9), (-138.0, 82.9),
]
BAR_X = (-33.49, 21.99)  # lip under the connector on the outer face
BAR_Z = (66.09, 72.387)
BAR_Y = -174.529
LATCH_NOTCH_X = (-39.234, -31.235)  # -X latch pocket (mirrored about X0)
LATCH_NOTCH_Y = (-160.8, -148.65)
LATCH_NOTCH_Z = 90.15
LATCH_PIN_POCKET = (-157.52, 87.814)  # deeper pocket around the pin: y below this, floor z
ROOF_CHAMFER = [(Y_FLOOR, 77.023), (-167.228, 80.0)]  # (y, z) roof-to-floor chamfer inside the tower
ROOF_CHAMFER_X = (-48.1, 36.6)
PIN_Y, PIN_Z = -159.369, 88.847
PIN_R = 1.25
PIN_X = (-38.234, 25.766)
PIN_CHAMFER = 0.2
LATCH_X = (-38.934, -31.234)
LATCH_Y = (-160.45, -148.97)
LATCH_Z = (90.15, 93.65)
LATCH_HOLE_R = 1.5
LATCH_HOLE_C = (-35.234, -154.71)  # (x, y)
INSERT_HOLES = [(-41.559, 83.7), (30.062, 83.7), (-63.714, 45.464), (52.214, 45.464)]
INSERT_HOLE_D = 4.0
INSERT_HOLE_BOTTOM = -148.11


def _yz_prism(pts_yz, x0, x1) -> Part:
    """Prism along X of a polygon given as (y, z) points."""
    face = Face(Wire.make_polygon([Vector(z, y) for y, z in pts_yz], close=True))
    return extrude(_plane_zy() * face, amount=x1 - x0, dir=(1, 0, 0)).moved(Location((x0, 0, 0)))


def inner_tower_top() -> Face:
    """Tower cavity above Y_TOWER_STEP (3 mm walls), down into the skirt cavity."""
    half = [
        (X0, 82.9, 0),
        (-30.735, 82.9, 0),
        (-34.485, 86.677, 0),
        (-34.485, 90.4, 1.0),
        (-45.409, 90.4, 1.0),
        (-61.0, 74.809, 4.75),
        (-61.0, 53.65, 11.252),
        (-68.654, 45.996, 1.0),
        (-68.654, 39.0, 0),
        (X0, 39.0, 0),
    ]
    return _sym(half)


def build_tower_cuts(body: Part) -> Part:
    body -= _prism(inner_tower_top(), Y_TOWER_STEP, Y_TOP + 1)
    # channel floor under the connector notch
    fill = [(y, z) for y, z in CHANNEL_BOTTOM] + [(-138.0, 95.0), (Y_FLOOR, 95.0)]
    body += _yz_prism(fill, CHANNEL_X[0], CHANNEL_X[1]) & _prism(outline_o2(), Y_OUT, Y_TOWER_TOP)
    notch = [(Y_OUT - 3, BAR_Z[1]), (CHANNEL_TOP[0][0], BAR_Z[1])] + CHANNEL_TOP + [(-138.0, 100.0), (Y_OUT - 3, 100.0)]
    body -= _yz_prism(notch, NOTCH_X[0], NOTCH_X[1])
    # sloped hood over the plate end of the tower
    k = (HOOD_P1[1] - HOOD_P0[1]) / (HOOD_P1[0] - HOOD_P0[0])
    ya, yb = Y_OUT - 3, HOOD_P1[0] + 5
    hood = [(ya, HOOD_P0[1] + k * (ya - HOOD_P0[0])), (yb, HOOD_P0[1] + k * (yb - HOOD_P0[0])), (yb, 120.0), (ya, 120.0)]
    body -= _yz_prism(hood, -80, 70)
    # latch pockets and insert holes
    for xa, xb in (LATCH_NOTCH_X, (2 * X0 - LATCH_NOTCH_X[1], 2 * X0 - LATCH_NOTCH_X[0])):
        body -= Pos((xa + xb) / 2, sum(LATCH_NOTCH_Y) / 2, (LATCH_NOTCH_Z + 100) / 2) * Box(
            xb - xa, LATCH_NOTCH_Y[1] - LATCH_NOTCH_Y[0], 100 - LATCH_NOTCH_Z
        )
        body -= Pos((xa + xb) / 2, (LATCH_NOTCH_Y[0] + LATCH_PIN_POCKET[0]) / 2, (LATCH_PIN_POCKET[1] + LATCH_NOTCH_Z) / 2 + 0.5) * Box(
            xb - xa, LATCH_PIN_POCKET[0] - LATCH_NOTCH_Y[0], LATCH_NOTCH_Z - LATCH_PIN_POCKET[1] + 1
        )
    (ya, za), (yb, zb) = ROOF_CHAMFER
    body -= _yz_prism([(ya - 0.01, za), (yb, zb + 0.01), (ya - 0.01, zb + 0.01)], *ROOF_CHAMFER_X)
    for x, z in INSERT_HOLES:
        body -= _prism(Pos(x, z) * Circle(INSERT_HOLE_D / 2), INSERT_HOLE_BOTTOM, Y_TOWER_STEP + 0.01)
    # lip under the connector
    body += Pos(sum(BAR_X) / 2, (BAR_Y + Y_OUT) / 2 + 0.25, sum(BAR_Z) / 2) * Box(
        BAR_X[1] - BAR_X[0], Y_OUT - BAR_Y + 0.5, BAR_Z[1] - BAR_Z[0]
    )
    return body


def build_latches() -> list[Part]:
    out = []
    for sgn in (1, -1):
        xa, xb = LATCH_X if sgn > 0 else (2 * X0 - LATCH_X[1], 2 * X0 - LATCH_X[0])
        latch = Pos((xa + xb) / 2, sum(LATCH_Y) / 2, sum(LATCH_Z) / 2) * Box(
            xb - xa, LATCH_Y[1] - LATCH_Y[0], LATCH_Z[1] - LATCH_Z[0]
        )
        hx = LATCH_HOLE_C[0] if sgn > 0 else 2 * X0 - LATCH_HOLE_C[0]
        latch -= Pos(hx, LATCH_HOLE_C[1], sum(LATCH_Z) / 2) * Cylinder(LATCH_HOLE_R, 10)
        out.append(latch)
    pin = Pos(sum(PIN_X) / 2, PIN_Y, PIN_Z) * Cylinder(PIN_R, PIN_X[1] - PIN_X[0], rotation=(0, 90, 0))
    pin = chamfer(pin.edges().filter_by(GeomType.CIRCLE), PIN_CHAMFER)
    out.append(pin)
    return out


# --- outer recess, fuse opening -------------------------------------------------
RECESS_END_R = 30.0  # plan-view end arcs of the recess in the outer face
RECESS_X = (-53.586, 42.086)  # end arcs tangent to the outer face here
RECESS_FLAT_X = (-40.509, 29.009)
RECESS_DEPTH = 3.0  # to Y_FLOOR
RECESS_Z_PTS = [(15.775, 0.0), (14.257, 0.855), (8.415, 2.613), (2.275, 3.0),
                (-2.725, 3.0), (-8.864, 2.613), (-14.706, 0.855), (-16.225, 0.0)]  # (z, depth)
FUSE_HOLE_X = (-25.375, 13.875)
FUSE_HOLE_Z = (-39.673, -21.053)
FUSE_HOLE_R = 2.0
FUSE_LEDGE_Y = -159.529
FUSE_INNER_X = (-20.875, 9.375)
FUSE_INNER_Z = (-36.673, -25.553)
FUSE_BOX_X = (-27.375, 15.875)
FUSE_BOX_Z = (-39.725, -19.053)
FUSE_BOX_TOP = -157.529
SLOT_RUNOUT_C = (-51.814, -187.494)  # (x, y) r15 run-out of the strap slot into the recess
SLOT_RUNOUT_R = 15.0
SLOT_RUNOUT_X = -62.05  # where the run-out leaves the slot floor


def build_recess() -> Part:
    c0 = (RECESS_X[0], Y_OUT + RECESS_END_R)
    c1 = (RECESS_X[1], Y_OUT + RECESS_END_R)
    yb = Y_OUT + RECESS_DEPTH
    edges = [
        Edge.make_line(Vector(RECESS_X[0], Y_OUT - 1), Vector(RECESS_X[0], Y_OUT)),
        _arc_c(c0, RECESS_END_R, (RECESS_X[0], Y_OUT), (RECESS_FLAT_X[0], yb)),
        Edge.make_line(Vector(RECESS_FLAT_X[0], yb), Vector(RECESS_FLAT_X[1], yb)),
        _arc_c(c1, RECESS_END_R, (RECESS_FLAT_X[1], yb), (RECESS_X[1], Y_OUT)),
        Edge.make_line(Vector(RECESS_X[1], Y_OUT), Vector(RECESS_X[1], Y_OUT - 1)),
        Edge.make_line(Vector(RECESS_X[1], Y_OUT - 1), Vector(RECESS_X[0], Y_OUT - 1)),
    ]
    px = extrude(Plane.XY * Face(Wire(edges)), amount=50, both=True)
    pts = [Vector(z, Y_OUT + d) for z, d in RECESS_Z_PTS]
    zmax, zmin = RECESS_Z_PTS[0][0], RECESS_Z_PTS[-1][0]
    e2 = [
        Edge.make_spline(pts[:4]),
        Edge.make_line(pts[3], pts[4]),
        Edge.make_spline(pts[4:]),
        Edge.make_line(pts[-1], Vector(zmin, Y_OUT - 1)),
        Edge.make_line(Vector(zmin, Y_OUT - 1), Vector(zmax, Y_OUT - 1)),
        Edge.make_line(Vector(zmax, Y_OUT - 1), pts[0]),
    ]
    pz = extrude(_plane_zy() * Face(Wire(e2)), amount=100, both=True)
    return px & pz


def _rrect(x0, x1, z0, z1, r) -> Face:
    return Pos((x0 + x1) / 2, (z0 + z1) / 2) * RectangleRounded(x1 - x0, z1 - z0, r)


def build_fuse(body: Part) -> Part:
    box = _poly([
        (FUSE_BOX_X[0], FUSE_BOX_Z[0], 0), (FUSE_BOX_X[1], FUSE_BOX_Z[0], 0),
        (FUSE_BOX_X[1], FUSE_BOX_Z[1], 2.0), (FUSE_BOX_X[0], FUSE_BOX_Z[1], 2.0),
    ])
    body += _prism(box, Y_FLOOR - 0.5, FUSE_BOX_TOP)
    body -= _prism(_rrect(*FUSE_HOLE_X, *FUSE_HOLE_Z, FUSE_HOLE_R), Y_OUT - 1, FUSE_LEDGE_Y)
    body -= _prism(_rrect(*FUSE_INNER_X, *FUSE_INNER_Z, 0.5), FUSE_LEDGE_Y - 0.5, FUSE_BOX_TOP + 1)
    return body


# --- end blocks (left one; right one mirrored about X0) ----------------------------
SHEET_SLOT_X = (-116.4, -115.1)  # slot for the reinforcement sheet
SHEET_SLOT_Z = (-17.1, 16.9)
END_WALL_X = -120.25  # inner face of the end wall below the lip
END_FILLET_R = 9.0  # floor-to-end-wall round
END_FILLET_MASK_X = -109.5  # round runs along the end wall up to the end block face
END_FILLET_LAYERS = [(0.0, 0.5), (0.5, 1.2), (1.2, 2.0), (2.0, 3.0), (3.0, 4.5), (4.5, 6.5), (6.5, 9.0)]
END_LIP = [(-120.25, -156.271), (-120.341, -153.366), (-121.476, -150.68), (-122.75, -149.771)]  # (x, y)
END_LIP_LAYERS = 6
FIN_Z = [(14.25, 16.75), (-16.95, -14.45)]  # outer fins (2.5 mm)
# the lower fin flares into the floor on its -z side; (y, z) run-out curve
FIN_FLARE = [(-161.057, -16.95), (-162.378, -17.248), (-163.646, -17.722), (-164.839, -18.362),
                (-165.934, -19.157), (-166.913, -20.093), (-167.756, -21.152), (-168.446, -22.316),
                (-168.974, -23.563), (-169.529, -25.6)]
FIN_ROUND_R = 3.5  # floor rounds of the upper fin (+z side) and of the strap channels
FIN_ROUND_X = (-109.25, -90.0)
FIN_TOP = [(-109.25, -158.087), (-107.303, -160.086), (-94.085, -161.181), (-81.072, -163.746),
            (-70.774, -166.382), (-70.509, -166.529)]  # (x, y) top edge
CENTRE_FIN_Z = (-3.45, 3.25)
CENTRE_FIN_TOP = [(-109.25, -158.436), (-107.686, -160.388), (-97.835, -163.038), (-88.25, -166.528)]
CHANNEL_Z = (-14.45, 14.25)  # strap channels between the fins: floor rises into the block
CHANNEL_FLOOR = [(-100.509, -169.529), (-95.81, -169.059)]  # 5.7 deg ramp, then r18 round
CHANNEL_FLOOR_C = (-97.601, -151.148)
CHANNEL_FLOOR_R = 18.0
CHANNEL_FLOOR_END = [(-89.516, -167.23), (-71.537, -166.616), (-70.509, -166.529)]
M4_HOLE_R = 2.25  # heat-set insert holes (M4) through the upper end walls, along X
M4_HOLE_Y = -143.471
M4_HOLE_Z = (27.263, -27.463)
STRAP_HOLE_R = 1.75  # two holes along X through the end wall
STRAP_HOLE_Y = -163.529
STRAP_HOLE_Z = (8.75, -8.95)
STRAP_HOLE_X = (-127.25, -111.05)
NUT_TRAP = 10.25  # square nut pocket (45 deg) around the tie-rod hole
NUT_TRAP_Y = -169.729
TIE_ROD_R = 3.25
TIE_ROD_X = -80.8
TIE_ROD_Z = -0.225


def build_end_block(body: Part) -> Part:
    def both(shape):
        return [shape, mirror(shape, Plane.YZ.offset(X0))]

    adds, cuts = [], []
    # r9 floor round along the end wall and its S-curves, as stepped offset bands
    cav = inner_lower()
    mask = _rrect(END_WALL_X - 1, END_FILLET_MASK_X, O1_Z_BOT, O2_Z_TOP, 0.1)
    near = cav & mask
    # extend the cavity past the long walls so the bands only follow the end wall
    cav = cav + _rrect(-130, -90, 39.0, 60.0, 0.1) + _rrect(-130, -90, -60.0, -39.2, 0.1)
    for h0, h1 in END_FILLET_LAYERS:
        hm = (h0 + h1) / 2
        d = END_FILLET_R - math.sqrt(END_FILLET_R ** 2 - (END_FILLET_R - hm) ** 2)
        band = near - offset(cav, -d)
        if band.faces():
            adds.append(_prism(band, Y_FLOOR + h0 - (0.01 if h0 == 0 else 0), Y_FLOOR + h1))
    # rounded top edge of the lower end wall / end block: the cavity grows by e(y)
    lip_mask = _rrect(-126.0, END_FILLET_MASK_X + 0.3, -39.725, 39.525, 0.1)
    ly = [p[1] for p in END_LIP] + [Y_LIP]
    le = [END_LIP[0][0] - p[0] for p in END_LIP] + [END_LIP[0][0] - END_LIP[-1][0]]
    for i in range(END_LIP_LAYERS):
        ya = ly[0] + i * (ly[-2] - ly[0]) / END_LIP_LAYERS
        yb = ly[0] + (i + 1) * (ly[-2] - ly[0]) / END_LIP_LAYERS
        ym = (ya + yb) / 2
        e = next(e0 + (e1 - e0) * (ym - y0) / (y1 - y0)
                    for y0, y1, e0, e1 in zip(ly[:-1], ly[1:], le[:-1], le[1:]) if y0 <= ym <= y1)
        if e > 0.02:
            grown = offset(cav, e) & lip_mask
            cuts.append(_prism(grown, ya, (yb if i < END_LIP_LAYERS - 1 else Y_LIP + 0.3)))
    fin = _poly_xy([(FIN_TOP[0][0], Y_FLOOR - 0.5)] + FIN_TOP + [(FIN_TOP[-1][0], Y_FLOOR - 0.5)])
    for z0, z1 in FIN_Z:
        adds.append(extrude(Plane.XY.offset(z0) * fin, amount=z1 - z0, dir=(0, 0, 1)))
    # lower fin flare
    fz = FIN_Z[1]
    pts = [Vector(z, y) for y, z in FIN_FLARE]
    flare = Face(Wire([
        Edge.make_spline(pts),
        Edge.make_line(pts[-1], Vector(pts[-1].X, Y_FLOOR - 0.5)),
        Edge.make_line(Vector(pts[-1].X, Y_FLOOR - 0.5), Vector(fz[1], Y_FLOOR - 0.5)),
        Edge.make_line(Vector(fz[1], Y_FLOOR - 0.5), Vector(fz[1], pts[0].Y)),
        Edge.make_line(Vector(fz[1], pts[0].Y), pts[0]),
    ]))
    flare_x = extrude(_plane_zy() * flare, amount=FIN_TOP[-1][0] - FIN_TOP[0][0], dir=(1, 0, 0)).moved(
        Location((FIN_TOP[0][0], 0, 0)))
    adds.append(flare_x & extrude(Plane.XY.offset(-40) * fin, amount=60, dir=(0, 0, 1)))
    # r3.5 floor rounds: +z side of the upper fin and both sides of the two strap channels
    r = FIN_ROUND_R
    for zw, sgn in ((FIN_Z[0][1], 1), (CENTRE_FIN_Z[1], 1), (FIN_Z[0][0], -1), (CENTRE_FIN_Z[0], -1), (FIN_Z[1][1], 1)):
        c = (zw + sgn * r, Y_FLOOR + r)
        rf = Face(Wire([
            Edge.make_line(Vector(zw, Y_FLOOR - 0.5), Vector(zw, c[1])),
            _arc_c(c, r, (zw, c[1]), (c[0], Y_FLOOR)),
            Edge.make_line(Vector(c[0], Y_FLOOR), Vector(c[0], Y_FLOOR - 0.5)),
            Edge.make_line(Vector(c[0], Y_FLOOR - 0.5), Vector(zw, Y_FLOOR - 0.5)),
        ]))
        adds.append(extrude(_plane_zy() * rf, amount=FIN_ROUND_X[1] - FIN_ROUND_X[0], dir=(1, 0, 0)).moved(
            Location((FIN_ROUND_X[0], 0, 0))))
    p = CHANNEL_FLOOR
    q = CHANNEL_FLOOR_END
    chf = Face(Wire([
        Edge.make_line(Vector(p[0][0], Y_FLOOR - 0.5), Vector(*p[0])),
        Edge.make_line(Vector(*p[0]), Vector(*p[1])),
        _arc_c(CHANNEL_FLOOR_C, CHANNEL_FLOOR_R, p[1], q[0]),
        Edge.make_line(Vector(*q[0]), Vector(*q[1])),
        Edge.make_line(Vector(*q[1]), Vector(*q[2])),
        Edge.make_line(Vector(*q[2]), Vector(q[2][0], Y_FLOOR - 0.5)),
        Edge.make_line(Vector(q[2][0], Y_FLOOR - 0.5), Vector(p[0][0], Y_FLOOR - 0.5)),
    ]))
    adds.append(extrude(Plane.XY.offset(CHANNEL_Z[0]) * chf, amount=CHANNEL_Z[1] - CHANNEL_Z[0], dir=(0, 0, 1)))
    cfin = _poly_xy([(CENTRE_FIN_TOP[0][0], Y_FLOOR - 0.5)] + CENTRE_FIN_TOP + [(CENTRE_FIN_TOP[-1][0], Y_FLOOR - 0.5)])
    adds.append(extrude(Plane.XY.offset(CENTRE_FIN_Z[0]) * cfin, amount=CENTRE_FIN_Z[1] - CENTRE_FIN_Z[0], dir=(0, 0, 1)))
    cuts.append(_prism(_rrect(*SHEET_SLOT_X, *SHEET_SLOT_Z, 0.3), Y_FLOOR, Y_LIP + 0.2))
    for z in STRAP_HOLE_Z:
        cuts.append(Pos(sum(STRAP_HOLE_X) / 2, STRAP_HOLE_Y, z)
                    * Cylinder(STRAP_HOLE_R, STRAP_HOLE_X[1] - STRAP_HOLE_X[0] + 1, rotation=(0, 90, 0)))
    cuts.append(_prism(Pos(TIE_ROD_X, TIE_ROD_Z) * (Rectangle(NUT_TRAP, NUT_TRAP).rotate(Axis.Z, 45)), NUT_TRAP_Y, Y_BLOCK + 0.5))
    cuts.append(_prism(Pos(TIE_ROD_X, TIE_ROD_Z) * Circle(TIE_ROD_R), MOUND_Y_BOT - 1, NUT_TRAP_Y + 0.01))
    for z in M4_HOLE_Z:
        cuts.append(Pos(O2_X + 3, M4_HOLE_Y, z) * Cylinder(M4_HOLE_R, 8.0, rotation=(0, 90, 0)))
    for a in adds:
        for sh in both(a):
            body += sh
    for c in cuts:
        for sh in both(c):
            body -= sh
    return body


def build_main() -> Part:
    lower = _prism(outline_o1(), Y_OUT, SHOULDER[0][0])
    lower = fillet([e for e in lower.edges() if abs(e.center().Y - Y_OUT) < 1e-6], PLATE_EDGE_R)
    body = lower
    # S-shaped outer shoulder between O1 and O2, as thin layers
    ys = [SHOULDER[0][0] + i * (SHOULDER[-1][0] - SHOULDER[0][0]) / SHOULDER_LAYERS for i in range(SHOULDER_LAYERS + 1)]
    for ya, yb in zip(ys[:-1], ys[1:]):
        ym = (ya + yb) / 2
        d = next(d0 + (d1 - d0) * (ym - y0) / (y1 - y0)
                    for (y0, d0), (y1, d1) in zip(SHOULDER[:-1], SHOULDER[1:]) if y0 <= ym <= y1)
        body += _prism(outline_o1(min(d, 2.9)), ya - 0.01, yb + 0.01)
    body += _prism(outline_o2(), SHOULDER[-1][0], Y_TOWER_TOP)
    top = _prism(outline_o2(tower=False), Y_TOWER_TOP - 1, Y_TOP)
    top = fillet([e for e in top.edges() if abs(e.center().Y - Y_TOP) < 1e-6], TOP_EDGE_R)
    body += top
    body -= _prism(inner_lower(), Y_FLOOR, Y_LIP)
    body -= _prism(inner_upper(), Y_LIP, Y_TOP + 1)
    tower_cav = inner_upper() & _rrect(-70.0, 60.0, 43.0, 100.0, 0.1)
    body -= _prism(tower_cav, Y_TOWER_INNER_STEP, Y_LIP + 0.5)
    return body


def build() -> Part:
    part = build_main()
    part += build_block()
    part = build_tower_cuts(part)
    m = build_mound()
    part += m
    part += mirror(m, Plane.YZ.offset(X0))
    c = SLOT_RUNOUT_C
    xe = c[0] - math.sqrt(SLOT_RUNOUT_R ** 2 - (Y_OUT - c[1]) ** 2)  # run-out meets the plate face
    run = Face(Wire([
        Edge.make_line(Vector(SLOT_RUNOUT_X, Y_OUT - 20), Vector(SLOT_RUNOUT_X, SLOT_Y)),
        _arc_c(c, SLOT_RUNOUT_R, (SLOT_RUNOUT_X, SLOT_Y), (xe, Y_OUT)),
        Edge.make_line(Vector(xe, Y_OUT), Vector(-40.0, Y_OUT)),
        Edge.make_line(Vector(-40.0, Y_OUT), Vector(-40.0, Y_OUT - 20)),
        Edge.make_line(Vector(-40.0, Y_OUT - 20), Vector(SLOT_RUNOUT_X, Y_OUT - 20)),
    ]))
    run = extrude(Plane.XY.offset(SLOT_Z[0]) * run, amount=SLOT_Z[1] - SLOT_Z[0], dir=(0, 0, 1))
    part -= run
    part -= mirror(run, Plane.YZ.offset(X0))
    part -= build_recess()
    part = build_fuse(part)
    part = build_end_block(part)
    solids = [part] + build_latches()
    out = Part(Compound([s for p in solids for s in p.solids()]).wrapped)
    out.label = PART_NUMBER
    return out
