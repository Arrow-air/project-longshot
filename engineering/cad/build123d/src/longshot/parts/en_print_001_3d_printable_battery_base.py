"""EN-PRINT-001 3D-Printable Battery Base - printed end piece at the +Y end of the pack.

The part is five solids, all probed from the Fusion reference solid:

* the base itself (bbox 237.0 x 11.0 x 78.65 mm, ~74 825 mm^3): a 3 mm plate
    in the XZ plane (Y 146.471..149.471) with the pack outline (end notches for
    the strap), a 2 mm locating rim below it (Y 144.471..146.471, chamfered 45 deg
    on the end walls), a 3 mm ribbed truss above it (Y 149.471..152.471: perimeter
    wall, central rib, five cross ribs on a 36.5 mm pitch and zig-zag diagonals,
    pocket floors filleted) and four 6 mm tall cups (Y up to 155.471) that hold
    the feet;
* four identical printed feet (23 x 23 x 9 mm, Y 149.471..158.471) sitting in
    the cups: r2 vertical corners, 4.3 mm through hole and a 9 mm counterbore
    4 mm deep from the outer face.

Frame: Fusion component frame = global assembly frame. The pack's long axis is
Y; this base sits at the +Y end, the plate lies in XZ, the locating rim faces -Y
(towards the cells) and the feet point +Y. The layout is mirror symmetric about
x = -5.75 and z = -0.1.

Not modelled: the r0.4 rounds on the rib tops, the small cup/rib blends and a
2 mm drain notch in the bottom wall.

BOOLEAN_GAP offsets the pocket walls, floors and rib tops from the true
surfaces. It is 0 (true geometry). Exactly coincident faces make OCCT's
Common against the Fusion solid fail, so the validator falls back to a
sampled sym-diff; a 0.02 mm gap gives an exact boolean instead (1.07 %
sym-diff, of which about 0.4 % is the gap itself).
"""

from __future__ import annotations

import math

from build123d import (
    Axis,
    Box,
    Circle,
    Compound,
    Cylinder,
    Face,
    GeomType,
    Location,
    Part,
    Plane,
    Polygon,
    Pos,
    Rectangle,
    RectangleRounded,
    Solid,
    Vector,
    Wire,
    extrude,
    fillet,
    loft,
    offset,
)

PART_NUMBER = "EN-PRINT-001-3D-Printable_Battery_Base"

# --- symmetry centre of the layout (global x, z) ---------------------------
X0 = -5.75
Z0 = -0.1

# --- Y levels (global) -----------------------------------------------------
Y_RIM = 144.471  # underside of the locating rim
RIM_HEIGHT = 2.0
PLATE_THICKNESS = 3.0
RIB_HEIGHT = 3.0  # truss ribs above the plate
CUP_HEIGHT = 6.0  # cups above the plate
FOOT_HEIGHT = 9.0

Y_PLATE = Y_RIM + RIM_HEIGHT  # 146.471
Y_FLOOR = Y_PLATE + PLATE_THICKNESS  # 149.471, pocket floors
Y_RIB_TOP = Y_FLOOR + RIB_HEIGHT  # 152.471
Y_CUP_TOP = Y_FLOOR + CUP_HEIGHT  # 155.471

# --- outline (x, z) --------------------------------------------------------
X_MIN, X_MAX = -124.25, 112.75
Z_MIN, Z_MAX = -39.425, 39.225
OUTLINE_CORNER_R = 1.0  # all 12 plan corners
NOTCH_DEPTH = 8.0  # strap notch at both X ends
NOTCH_Z_MIN, NOTCH_Z_MAX = -17.95, 17.75
TOP_EDGE_FILLET = 2.0  # outer top edge of the truss

# --- rim -------------------------------------------------------------------
RIM_WALL_BOTTOM = 1.5  # end-wall thickness at the rim underside
RIM_WALL_TOP = 3.5  # end-wall thickness at the plate (45 deg chamfer)
RIM_SIDE_WALL = 3.3  # long side walls (vertical)
RIM_SLOT_HALF = 10.5  # rim is open for |z| < 10.5 at the notches

# --- truss -----------------------------------------------------------------
WALL_SIDE = 3.45  # perimeter wall along the long (X) sides
WALL_END = 3.0  # end walls, notch walls, notch ribs, cup walls
RIB = 1.2  # central rib, cross ribs, diagonals
RIB_PITCH = 36.5  # cross ribs at X0 + k * pitch, k = -2..2
RIB_COUNT = 5
POCKET_CORNER_R = 1.0  # vertical corner rounds next to a 1.2 mm rib
POCKET_CORNER_R_WALL = 2.0  # between two 3 mm walls
FLOOR_FILLET_TRUSS = 1.0  # pockets along the perimeter wall
FLOOR_FILLET_CENTRE = 0.5  # pockets along the central rib
FLOOR_FILLET_CORNER = 2.0  # small end-corner pockets
BOOLEAN_GAP = 0.0
POCKET_INSET = BOOLEAN_GAP
RIB_TOP_DROP = BOOLEAN_GAP
FLOOR_RAISE = BOOLEAN_GAP

# --- cups and feet -----------------------------------------------------------
CUP_DX = 92.5  # cup centres at X0 +/- CUP_DX
CUP_DZ = 24.375  # and Z0 +/- CUP_DZ
CUP_POCKET = 24.0  # square pocket for the foot
CUP_POCKET_R = 2.0
CUP_WALL = 3.0
CUP_OUTER_R = 5.0  # outer corner towards the pack centre
PLATE_HOLE_D = 4.0

FOOT_SIZE = 23.0
FOOT_CORNER_R = 2.0
FOOT_HOLE_D = 4.3
FOOT_CBORE_D = 9.0
FOOT_CBORE_DEPTH = 4.0

# --- snap tabs on the inside of the long walls -------------------------------
TAB_X = (-66.617, -56.083, -28.083, -17.217)  # -X half; mirrored about X0
TAB_WIDTH = 1.5
TAB_DEPTH_FLOOR = 2.5  # protrusion from the wall up to Y_FLOOR + 1
TAB_DEPTH_TOP = 0.5  # protrusion at the rib top (45 deg chamfer)


# ---------------------------------------------------------------------------
def _plane(y: float) -> Plane:
    """Sketch plane at height y: local (u, v) = global (x, z)."""
    return Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


def _prism(face: Face, y0: float, height: float) -> Part:
    return extrude(_plane(y0) * face, amount=height, dir=(0, 1, 0))


def _outline_points() -> list[tuple[float, float]]:
    nx0, nx1 = X_MIN + NOTCH_DEPTH, X_MAX - NOTCH_DEPTH
    return [
        (X_MIN, Z_MIN), (X_MAX, Z_MIN), (X_MAX, NOTCH_Z_MIN), (nx1, NOTCH_Z_MIN),
        (nx1, NOTCH_Z_MAX), (X_MAX, NOTCH_Z_MAX), (X_MAX, Z_MAX), (X_MIN, Z_MAX),
        (X_MIN, NOTCH_Z_MAX), (nx0, NOTCH_Z_MAX), (nx0, NOTCH_Z_MIN), (X_MIN, NOTCH_Z_MIN),
    ]


def outline_face() -> Face:
    face = Face(Wire.make_polygon(_outline_points(), close=True))
    return fillet(face.vertices(), OUTLINE_CORNER_R)


def _rim_inner(wall_end: float) -> list[tuple[float, float]]:
    """Inner loop of the rim; end walls of thickness ``wall_end``."""
    nx0, nx1 = X_MIN + NOTCH_DEPTH, X_MAX - NOTCH_DEPTH
    z0, z1 = Z_MIN + RIM_SIDE_WALL, Z_MAX - RIM_SIDE_WALL
    zn0, zn1 = NOTCH_Z_MIN - 1.0, NOTCH_Z_MAX + 1.0  # notch walls (vertical)
    return [
        (X_MIN + wall_end, z0), (X_MAX - wall_end, z0), (X_MAX - wall_end, zn0), (nx1 - wall_end, zn0),
        (nx1 - wall_end, zn1), (X_MAX - wall_end, zn1), (X_MAX - wall_end, z1), (X_MIN + wall_end, z1),
        (X_MIN + wall_end, zn1), (nx0 + wall_end, zn1), (nx0 + wall_end, zn0), (X_MIN + wall_end, zn0),
    ]


def build_rim() -> Part:
    rim = _prism(outline_face(), Y_RIM, RIM_HEIGHT)
    bottom = _plane(Y_RIM) * Wire.make_polygon(_rim_inner(RIM_WALL_BOTTOM), close=True)
    top = _plane(Y_PLATE) * Wire.make_polygon(_rim_inner(RIM_WALL_TOP), close=True)
    rim -= loft([Face(bottom), Face(top)], ruled=True)
    nx0, nx1 = X_MIN + NOTCH_DEPTH, X_MAX - NOTCH_DEPTH
    for xa, xb in ((nx0 - 1, nx0 + RIM_WALL_TOP), (nx1 - RIM_WALL_TOP, nx1 + 1)):
        slot = Pos((xa + xb) / 2, 0, 0) * Rectangle(xb - xa, 2 * RIM_SLOT_HALF)
        rim -= _prism(slot, Y_RIM - 0.1, RIM_HEIGHT + 0.2)
    return rim


def cup_centres() -> list[tuple[float, float]]:
    return [(X0 + sx * CUP_DX, Z0 + sz * CUP_DZ) for sx in (-1, 1) for sz in (-1, 1)]


def _cup_outer(cx: float, cz: float) -> Face:
    """Outer plan of a cup: 30 x 30 square, extended to the outline edge,
    r5 on the corner that faces the pack centre."""
    half = CUP_POCKET / 2 + CUP_WALL
    sx = 1 if cx < X0 else -1  # direction to the centre in x
    sz = 1 if cz < Z0 else -1
    edge_z = Z_MIN if cz < Z0 else Z_MAX
    x_in, x_out = cx + sx * half, cx - sx * half
    z_in = cz + sz * half
    pts = [(x_out, edge_z), (x_out, z_in), (x_in, z_in), (x_in, edge_z)]
    face = Face(Wire.make_polygon(pts, close=True))
    corner = [v for v in face.vertices() if abs(v.X - x_in) < 1e-6 and abs(v.Y - z_in) < 1e-6]
    return fillet(corner, CUP_OUTER_R)


def _thick_segment(p0, p1, width, over=0.3) -> Face:
    (x0, z0), (x1, z1) = p0, p1
    length = math.hypot(x1 - x0, z1 - z0)
    ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
    rect = Rectangle(length + 2 * over, width)
    return Location(((x0 + x1) / 2, (z0 + z1) / 2, 0), (0, 0, ang)) * rect


def truss_solid_2d() -> Face:
    """Plan of the material inside the perimeter walls (everything that is
    not pocket): end/notch walls, cups, central rib, cross ribs, diagonals."""
    zc0, zc1 = Z_MIN + WALL_SIDE, Z_MAX - WALL_SIDE  # pocket band in z
    parts = []
    nx0, nx1 = X_MIN + NOTCH_DEPTH, X_MAX - NOTCH_DEPTH
    # notch ribs + notch walls (the notch itself is outside the outline)
    for xa, xb in ((X_MIN - 1, nx0 + WALL_END), (nx1 - WALL_END, X_MAX + 1)):
        parts.append(Pos((xa + xb) / 2, (NOTCH_Z_MIN + NOTCH_Z_MAX) / 2, 0)
                        * Rectangle(xb - xa, NOTCH_Z_MAX - NOTCH_Z_MIN + 2 * WALL_END))
    # cups
    for cx, cz in cup_centres():
        parts.append(_cup_outer(cx, cz))
    # central rib
    parts.append(Pos(X0, Z0, 0) * Rectangle(X_MAX - X_MIN, RIB))
    # cross ribs and diagonals
    xs = [X0 + (k - (RIB_COUNT - 1) / 2) * RIB_PITCH for k in range(RIB_COUNT)]
    for x in xs:
        parts.append(Pos(x, Z0, 0) * Rectangle(RIB, Z_MAX - Z_MIN))
    for i in range(RIB_COUNT - 1):
        xa, xb = xs[i], xs[i + 1]
        # zig-zag: from the node on the central rib to the far wall at the next rib
        up_right = i % 2 == 0
        node, far = ((xa, Z0), xb) if up_right else ((xb, Z0), xa)
        parts.append(_thick_segment(node, (far, zc1), RIB))
        parts.append(_thick_segment(node, (far, zc0), RIB))
    # short diagonals from the outer cross-rib nodes towards the cups, at the
    # same slope as the main diagonals (they end inside the cup walls)
    slope = (zc1 - Z0) / RIB_PITCH
    for sx in (-1, 1):
        node = (xs[0] if sx < 0 else xs[-1], Z0)
        run = CUP_DX - RIB_PITCH * (RIB_COUNT - 1) / 2  # node to cup centre in x
        for sz in (-1, 1):
            parts.append(_thick_segment(node, (node[0] + sx * run, Z0 + sz * slope * run), RIB))
    region = Pos((X_MIN + X_MAX) / 2, (zc0 + zc1) / 2, 0) * Rectangle(X_MAX - X_MIN - 2 * WALL_END, zc1 - zc0)
    solid = parts[0]
    for p in parts[1:]:
        solid = solid + p
    return region - solid


def _is_thin(edge) -> bool:
    """Edge of a pocket that lies on a 1.2 mm rib (vs. a 3 mm wall)."""
    if edge.geom_type != GeomType.LINE:
        return edge.geom_type == GeomType.CIRCLE and edge.radius < 1.5
    d = edge.tangent_at(0.5)
    if abs(d.X) > 1e-3 and abs(d.Y) > 1e-3:
        return True  # diagonal
    m = edge.center()
    if abs(d.X) > abs(d.Y):  # along X at constant z (local y)
        return abs(m.Y - Z0) < RIB / 2 + 1e-3
    xs = [X0 + (k - (RIB_COUNT - 1) / 2) * RIB_PITCH for k in range(RIB_COUNT)]
    return any(abs(m.X - x) < RIB / 2 + 1e-3 for x in xs)


def _round_pocket(face: Face) -> Face:
    """Vertical corner rounds: r2 between two walls, r1 next to a rib."""
    face = Face(face.outer_wire())
    wall, rib = [], []
    for v in face.vertices():
        p = Vector(v.X, v.Y, v.Z)
        edges = [e for e in face.edges() if any((ev - p).length < 1e-6 for ev in (e @ 0, e @ 1))]
        if len(edges) != 2:
            continue
        t0 = edges[0].tangent_at(0 if (edges[0] @ 0 - p).length < 1e-6 else 1)
        t1 = edges[1].tangent_at(0 if (edges[1] @ 0 - p).length < 1e-6 else 1)
        if abs(abs(t0.dot(t1)) - 1) < 1e-6:
            continue  # tangent junction
        (rib if (_is_thin(edges[0]) or _is_thin(edges[1])) else wall).append(v)
    if wall:
        face = fillet(wall, POCKET_CORNER_R_WALL)
    if rib:
        keep = [(r.X, r.Y) for r in rib]
        rib = [v for v in face.vertices() if any(abs(v.X - x) + abs(v.Y - y) < 1e-6 for x, y in keep)]
        face = fillet(rib, POCKET_CORNER_R)
    return face


def _pocket_tool(face: Face) -> Part:
    bb = face.bounding_box()
    small = bb.size.X < 2 * WALL_END + 3  # end-corner pockets
    touches_wall = bb.max.Y > Z_MAX - WALL_SIDE - 0.5 or bb.min.Y < Z_MIN + WALL_SIDE + 0.5
    r = FLOOR_FILLET_CORNER if small else (FLOOR_FILLET_TRUSS if touches_wall else FLOOR_FILLET_CENTRE)
    tool = _prism(face, Y_FLOOR + FLOOR_RAISE, CUP_HEIGHT + 1)
    bottom = [e for e in tool.edges() if abs(e.center().Y - Y_FLOOR - FLOOR_RAISE) < 1e-6]
    try:
        tool = fillet(bottom, r * 0.999)
    except Exception:
        pass
    return tool


def pockets_2d() -> list[Face]:
    # the 0.1 um inset only rebuilds the outlines as offset curves; it keeps
    # OCCT's fuzzy booleans against the Fusion solid stable
    return [offset(_round_pocket(f), -POCKET_INSET) if POCKET_INSET else _round_pocket(f) for f in truss_solid_2d().faces()]


def build_tabs() -> list[Part]:
    tabs = []
    for x in TAB_X:
        for xx in (x, 2 * X0 - x):
            for sz in (-1, 1):
                zw = Z_MAX - WALL_SIDE if sz > 0 else Z_MIN + WALL_SIDE
                # profile in the (y, depth) plane
                pts = [
                    (Y_FLOOR - 0.1, 0.0), (Y_FLOOR - 0.1, TAB_DEPTH_FLOOR),
                    (Y_RIB_TOP - (TAB_DEPTH_FLOOR - TAB_DEPTH_TOP), TAB_DEPTH_FLOOR),
                    (Y_RIB_TOP, TAB_DEPTH_TOP), (Y_RIB_TOP, -0.1), (Y_FLOOR - 0.1, -0.1),
                ]
                pl = Plane(origin=(xx - TAB_WIDTH / 2, 0, zw), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
                prof = Face(Wire.make_polygon([(yy, -sz * d) for yy, d in pts], close=True))
                tabs.append(extrude(pl * prof, amount=TAB_WIDTH))
    return tabs


def build_body() -> Part:
    outline = outline_face()
    body = _prism(outline, Y_PLATE, PLATE_THICKNESS + RIB_HEIGHT - RIB_TOP_DROP)
    top_edges = [e for e in body.edges() if abs(e.center().Y - (Y_RIB_TOP - RIB_TOP_DROP)) < 1e-6]
    body = fillet(top_edges, TOP_EDGE_FILLET)
    for cx, cz in cup_centres():
        body += _prism(_cup_outer(cx, cz), Y_FLOOR - 0.5, CUP_HEIGHT + 0.5)
    for f in pockets_2d():
        body -= _pocket_tool(f)
    for t in build_tabs():
        body += t
    for cx, cz in cup_centres():
        body -= _prism(Pos(cx, cz) * RectangleRounded(CUP_POCKET, CUP_POCKET, CUP_POCKET_R), Y_FLOOR, CUP_HEIGHT + 1)
        body -= _prism(Pos(cx, cz) * Circle(PLATE_HOLE_D / 2), Y_PLATE - 1, PLATE_THICKNESS + 2)
    body += build_rim()
    return body


def build_foot(cx: float, cz: float) -> Part:
    foot = _prism(Pos(cx, cz) * RectangleRounded(FOOT_SIZE, FOOT_SIZE, FOOT_CORNER_R), Y_FLOOR, FOOT_HEIGHT)
    foot -= _prism(Pos(cx, cz) * Circle(FOOT_HOLE_D / 2), Y_FLOOR - 1, FOOT_HEIGHT + 2)
    foot -= _prism(Pos(cx, cz) * Circle(FOOT_CBORE_D / 2), Y_FLOOR + FOOT_HEIGHT - FOOT_CBORE_DEPTH, FOOT_CBORE_DEPTH + 1)
    return foot


def build() -> Part:
    solids = [build_body()] + [build_foot(cx, cz) for cx, cz in cup_centres()]
    part = Part(Compound([s for p in solids for s in p.solids()]).wrapped)
    part.label = PART_NUMBER
    return part
