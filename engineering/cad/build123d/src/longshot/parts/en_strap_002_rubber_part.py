"""EN-STRAP-002 Rubber Part - moulded rubber sleeve of the pack strap.

Dimensions probed from the Fusion reference solid (bbox 200 x 7 x 22 mm,
volume 19 530.5 mm^3). Component frame (unchanged from the STEP): strap
length along X centred on x = 0, profile centred on y = 0 / z = 0.

Constant cross-section (YZ) extruded along X: a lobed outline built from
tangent-ish arcs - R3.5 beads on the top/bottom edges (z = +/-11), R6.943
flanks and an R8 waist (y = +/-3.5 at z = 0). A 2 x 18 mm pocket runs the
full length for the 0.5 mm metal band EN-STRAP-001. In plan (XZ) the ends
are convex R41.083 arcs with apex at x = +/-100, and the two 5.5 mm slots
match the metal band (end-circle centres at |x| = 73 and 93).
"""

from __future__ import annotations

import math

from build123d import Box, BuildLine, BuildSketch, Part, Plane, Pos, ThreePointArc, extrude, make_face

from .en_strap_001_metal_piece import SLOT_WIDTH, SLOT_X_INNER, SLOT_X_OUTER, arc_ended_plate, slot

PART_NUMBER = "EN-STRAP-002-Rubber_Part"

LENGTH = 200.0
HEIGHT = 22.0  # along Z
THICKNESS = 7.0  # along Y (waist)
END_RADIUS = 41.083  # plan-view end arcs, apex at x = +/-LENGTH/2

# Cross-section arcs (y, z) in the YZ plane; mirrored in y and z.
BEAD_RADIUS = 3.5
BEAD_CENTER = (0.0, 7.5)
FLANK_RADIUS = 6.943
FLANK_CENTER = (-3.443, 3.861)  # for the +y flank; centre lies on the -y side
WAIST_RADIUS = 8.0
WAIST_CENTER = (-4.5, 0.0)  # for the +y waist

# Pocket for the metal band
POCKET_THICKNESS = 2.0
POCKET_HEIGHT = 18.0


def _circle_intersection(c0, r0, c1, r1, pick_max_y=True):
    dx, dy = c1[0] - c0[0], c1[1] - c0[1]
    d = math.hypot(dx, dy)
    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = math.sqrt(max(r0**2 - a**2, 0.0))
    mx, my = c0[0] + a * dx / d, c0[1] + a * dy / d
    pts = [(mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d)]
    return max(pts, key=lambda p: p[0])  # the +y (outer) intersection


def _mid(center, r, p0, p1):
    a0 = math.atan2(p0[1] - center[1], p0[0] - center[0])
    a1 = math.atan2(p1[1] - center[1], p1[0] - center[0])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    am = a0 + da / 2
    return (center[0] + r * math.cos(am), center[1] + r * math.sin(am))


def _profile_arcs():
    """Arcs (center, radius, start, end) for the +y half, top to bottom."""
    top = (BEAD_CENTER[0], BEAD_CENTER[1] + BEAD_RADIUS)
    p1 = _circle_intersection(BEAD_CENTER, BEAD_RADIUS, FLANK_CENTER, FLANK_RADIUS)
    p2 = _circle_intersection(FLANK_CENTER, FLANK_RADIUS, WAIST_CENTER, WAIST_RADIUS)
    arcs = [(BEAD_CENTER, BEAD_RADIUS, top, p1), (FLANK_CENTER, FLANK_RADIUS, p1, p2)]
    waist = (WAIST_CENTER, WAIST_RADIUS, p2, (p2[0], -p2[1]))
    lower = [((c[0], -c[1]), r, (e[0], -e[1]), (s[0], -s[1])) for c, r, s, e in reversed(arcs)]
    half = arcs + [waist] + lower
    other = [((-c[0], c[1]), r, (-e[0], e[1]), (-s[0], s[1])) for c, r, s, e in reversed(half)]
    return half + other


def build() -> Part:
    with BuildSketch(Plane.YZ.offset(-LENGTH / 2)) as sk:
        with BuildLine():
            for c, r, s, e in _profile_arcs():
                ThreePointArc(s, _mid(c, r, s, e), e)
        make_face()
    body = extrude(sk.sketch, LENGTH)
    body &= arc_ended_plate(LENGTH, HEIGHT, THICKNESS + 2, END_RADIUS, 0.0)
    body -= Box(LENGTH + 2, POCKET_THICKNESS, POCKET_HEIGHT)
    for s in (1, -1):
        body -= Pos(s * (SLOT_X_INNER + SLOT_X_OUTER) / 2, 0, 0) * slot(
            -(SLOT_X_OUTER - SLOT_X_INNER) / 2, (SLOT_X_OUTER - SLOT_X_INNER) / 2, SLOT_WIDTH, THICKNESS + 2, 0.0
        )
    body.label = PART_NUMBER
    return body
