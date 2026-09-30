"""PW-BUS-002 P Terminal - 0.2 mm copper positive end busbar with folded wall.

Dimensions probed from the Fusion reference solid. Component frame: sheet in
the XY plane with its top face on z = 0.2, first cell of row 0 at the origin,
row 1 towards +Y. Two rows of cells (5 + 4) with the same R7 cut-outs and
joggled weld tongues as Bridge 1, then the sheet runs on in +Y and is folded
90 deg down (0.2 mm inner radius) into a 15 mm deep terminal wall with four
3.5 mm holes and R5 lower corners.
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

PART_NUMBER = "PW-BUS-002-P_Terminal"

ROWS = [(0.0, 0.0, 5), (CELL_PITCH / 2, ROW_PITCH, 4)]  # (first cell x, y, count)
FLANGE_RUN = 14.8  # flat run from the row-1 pad edge to the bend line
BEND_LINE_Y = ROW_PITCH + PAD_HALF_Y + FLANGE_RUN  # 43.478
WALL_X = (CELL_PITCH / 2 - PAD_HALF_X, CELL_PITCH / 2 + 3 * CELL_PITCH + PAD_HALF_X)  # 1.2 .. 90.8
WALL_DEPTH = 15.0  # sheet top face to bottom of the wall
WALL_CORNER_RADIUS = 5.0
WALL_HOLE_DIAMETER = 3.5
WALL_HOLE_DEPTH = 9.0  # hole centres below the sheet top face
WALL_HOLE_X = (7.5, 32.5, 59.5, 84.5)


def busbar() -> Busbar:
    core = (WALL_X[0], WALL_X[1], -PAD_HALF_Y, BEND_LINE_Y)
    return Busbar(
        rows=ROWS,
        rects=[core],
        ear=(-PAD_HALF_X, 0.0, -1),
        top_z=SHEET_TOP_Z,
        wall=(BEND_LINE_Y, +1, WALL_X[0], WALL_X[1], WALL_DEPTH, WALL_CORNER_RADIUS,
                WALL_HOLE_X, WALL_HOLE_DEPTH, WALL_HOLE_DIAMETER),
    )


def build() -> Part:
    part = build_busbar(busbar())
    part.label = PART_NUMBER
    return part
