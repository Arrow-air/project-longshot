"""PW-BUS-006 Screw Terminal Positive - 6 mm terminal bar for the pack positive.

Same cross-section, corner radii and hole sizes as PW-BUS-005 (probed from
the Fusion reference solid); only the length and hole positions differ.
Component frame as PW-BUS-005: bar in the XZ plane, y = 0..6.
"""

from __future__ import annotations

from build123d import Part

from .pw_bus_005_screw_terminal_negative import build_terminal

PART_NUMBER = "PW-BUS-006-Screw_Terminal_Positive"

X_MIN = -96.55
X_MAX = -6.95
MOUNT_X = (-92.55, -10.95)
SMALL_HOLE_X = (-90.25, -65.25, -38.25, -13.25)  # 25 / 27 / 25 mm spacing


def build() -> Part:
    part = build_terminal(X_MIN, X_MAX, MOUNT_X, SMALL_HOLE_X)
    part.label = PART_NUMBER
    return part
