"""PW-BUS-005 Screw Terminal Negative - 6 mm terminal bar for the pack negative.

Dimensions probed from the Fusion reference solid. Component frame: bar
lies in the XZ plane and is THICKNESS thick along +Y (y = 0..6); the two
mounting holes are countersunk from the y = 0 face; four smaller holes
run through along Y.
"""

from __future__ import annotations

import math

from build123d import Align, Axis, Box, Cone, Cylinder, Part, Pos, Rot, fillet

PART_NUMBER = "PW-BUS-005-Screw_Terminal_Negative"

THICKNESS = 6.0  # along Y
Z_BOTTOM = 13.675
HEIGHT = 14.6  # along Z
BOTTOM_CORNER_RADIUS = 5.0
TOP_CORNER_RADIUS = 2.0

X_MIN = -4.55
X_MAX = 96.55

# Countersunk mounting holes (countersink on the y = 0 face).
MOUNT_HOLE_DIAMETER = 3.5
MOUNT_COUNTERSINK_DIAMETER = 6.3
MOUNT_COUNTERSINK_ANGLE = 90.0  # included angle
MOUNT_Z = 24.275
MOUNT_X = (-0.55, 92.55)

# Plain through holes.
SMALL_HOLE_DIAMETER = 2.5
SMALL_HOLE_Z = 19.675
SMALL_HOLE_X = (5.5, 32.5, 59.5, 86.5)  # 27 mm pitch


def build_terminal(
    x_min: float,
    x_max: float,
    mount_x: tuple[float, ...],
    small_hole_x: tuple[float, ...],
) -> Part:
    """Terminal bar between ``x_min`` and ``x_max`` with the given holes."""
    bar = Pos(x_min, 0, Z_BOTTOM) * Box(
        x_max - x_min, THICKNESS, HEIGHT, align=(Align.MIN, Align.MIN, Align.MIN)
    )
    y_edges = bar.edges().filter_by(Axis.Y)
    bar = fillet(y_edges.filter_by_position(Axis.Z, Z_BOTTOM - 0.01, Z_BOTTOM + 0.01), BOTTOM_CORNER_RADIUS)
    y_edges = bar.edges().filter_by(Axis.Y)
    top = Z_BOTTOM + HEIGHT
    bar = fillet(y_edges.filter_by_position(Axis.Z, top - 0.01, top + 0.01), TOP_CORNER_RADIUS)

    # Tools are built along +Z, then rotated so +Z maps to +Y.
    to_y = Rot(-90, 0, 0)
    base = (Align.CENTER, Align.CENTER, Align.MIN)
    sink_depth = (MOUNT_COUNTERSINK_DIAMETER - MOUNT_HOLE_DIAMETER) / 2 / math.tan(
        math.radians(MOUNT_COUNTERSINK_ANGLE / 2)
    )
    for x in mount_x:
        bar -= Pos(x, 0, MOUNT_Z) * to_y * Cylinder(MOUNT_HOLE_DIAMETER / 2, THICKNESS, align=base)
        bar -= Pos(x, 0, MOUNT_Z) * to_y * Cone(
            MOUNT_COUNTERSINK_DIAMETER / 2, MOUNT_HOLE_DIAMETER / 2, sink_depth, align=base
        )
    for x in small_hole_x:
        bar -= Pos(x, 0, SMALL_HOLE_Z) * to_y * Cylinder(SMALL_HOLE_DIAMETER / 2, THICKNESS, align=base)
    return bar


def build() -> Part:
    part = build_terminal(X_MIN, X_MAX, MOUNT_X, SMALL_HOLE_X)
    part.label = PART_NUMBER
    return part
