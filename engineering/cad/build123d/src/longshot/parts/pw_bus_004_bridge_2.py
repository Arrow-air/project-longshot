"""PW-BUS-004 Bridge 2 - 0.2 mm copper bridge between the two pack halves.

Dimensions probed from the Fusion reference solid. Component frame: sheet in
the XY plane with its top face on z = 0.2, first cell of the right-hand group
at the origin, row 1 towards +Y. Two groups of 2 rows x 9 cells: the right
group (x >= 0) is on the Bridge 1 lattice, the left group is shifted +2.4 mm
in X (20.6 mm between the groups instead of 23). Same R7 cut-outs and joggled
weld tongues as Bridge 1. Along the -Y edge a flange is folded 90 deg down
(0.2 mm inner radius) into a plain 20 mm deep wall with R5 lower corners.
"""

from __future__ import annotations

from build123d import Part

from .pw_bus_003_bridge_1 import (
    CELL_PITCH,
    PAD_HALF_X,
    PAD_HALF_Y,
    ROW_PITCH,
    SHEET_TOP_Z,
    Busbar,
    build_busbar,
)

PART_NUMBER = "PW-BUS-004-Bridge_2"

GROUP_SHIFT_X = 2.4  # left group offset from the 23 mm lattice
ROWS = [
    (0.0, 0.0, 5),  # right group, row 0
    (CELL_PITCH / 2, ROW_PITCH, 4),  # right group, row 1
    (-4 * CELL_PITCH + GROUP_SHIFT_X, 0.0, 4),  # left group, row 0 (x = -89.6 ..)
    (-4.5 * CELL_PITCH + GROUP_SHIFT_X, ROW_PITCH, 5),  # left group, row 1 (x = -101.1 ..)
]
FLANGE_RUN = 5.8  # flat run from the row-0 pad edge to the bend line
BEND_LINE_Y = -PAD_HALF_Y - FLANGE_RUN  # -14.559
WALL_X = (-90.9, 84.3)
FLANGE_CORNER_RADIUS = 2.0  # inside corners where the flange leaves row 0
WALL_DEPTH = 20.0
WALL_CORNER_RADIUS = 5.0


def busbar() -> Busbar:
    left_row0_x = ROWS[2][0] - PAD_HALF_X  # -99.9
    right_row1_x = ROWS[1][0] + 3 * CELL_PITCH + PAD_HALF_X  # 90.8
    core = (left_row0_x, right_row1_x, -PAD_HALF_Y, ROW_PITCH + PAD_HALF_Y)
    flange = (WALL_X[0], WALL_X[1], BEND_LINE_Y, -PAD_HALF_Y)
    return Busbar(
        rows=ROWS,
        rects=[core, flange],
        ear=(ROWS[3][0] - PAD_HALF_X, ROW_PITCH, -1),
        top_z=SHEET_TOP_Z,
        radius_overrides={(x, -PAD_HALF_Y): FLANGE_CORNER_RADIUS for x in WALL_X},
        wall=(BEND_LINE_Y, -1, WALL_X[0], WALL_X[1], WALL_DEPTH, WALL_CORNER_RADIUS, (), 0.0, 0.0),
    )


def build() -> Part:
    part = build_busbar(busbar())
    part.label = PART_NUMBER
    return part
