"""PW-BUS-001 N Terminal - 0.2 mm copper negative end busbar with folded wall.

Dimensions probed from the Fusion reference solid. Component frame (as
exported, not centred): sheet top face on z = 36.175, cells on the global
hex lattice (row A at y = -6.5 row pitches, row B at -5.5), the terminal wall
on the -Y side. Two rows of cells (5 + 4) with the same R7 cut-outs and
joggled weld tongues as Bridge 1; the sheet runs on in -Y and is folded
90 deg down (0.2 mm inner radius) into a 15 mm deep terminal wall with four
3.5 mm holes on a 27 mm pitch and R5 lower corners.
"""

from __future__ import annotations

from build123d import Part

from .pw_bus_003_bridge_1 import CELL_PITCH, PAD_HALF_X, PAD_HALF_Y, ROW_PITCH, Busbar, build_busbar

PART_NUMBER = "PW-BUS-001-N_Terminal"

SHEET_TOP_Z = 36.175
ROW_A = (-4.5 * CELL_PITCH, -6.5 * ROW_PITCH, 5)  # (first cell x, y, count) - wall side
ROW_B = (-4.0 * CELL_PITCH, -5.5 * ROW_PITCH, 4)
FLANGE_RUN = 14.8  # flat run from the row-A pad edge to the bend line
BEND_LINE_Y = ROW_A[1] - PAD_HALF_Y - FLANGE_RUN  # -153.030
# flange / wall span: row-B left pad edge .. row-A right pad edge
WALL_X = (ROW_B[0] - PAD_HALF_X, ROW_A[0] + 4 * CELL_PITCH + PAD_HALF_X)  # -102.3 .. -1.2
FLANGE_CORNER_RADIUS = 5.0  # inside corner between row A and the flange
WALL_DEPTH = 15.0
WALL_CORNER_RADIUS = 5.0
WALL_HOLE_DIAMETER = 3.5
WALL_HOLE_DEPTH = 9.0
WALL_HOLE_PITCH = 27.0
WALL_HOLE_X = tuple(-92.25 + i * WALL_HOLE_PITCH for i in range(4))


def busbar() -> Busbar:
    row_a_bottom = ROW_A[1] - PAD_HALF_Y
    core = (WALL_X[0], ROW_B[0] + 3 * CELL_PITCH + PAD_HALF_X, row_a_bottom, ROW_B[1] + PAD_HALF_Y)
    flange = (WALL_X[0], WALL_X[1], BEND_LINE_Y, row_a_bottom)
    return Busbar(
        rows=[ROW_A, ROW_B],
        rects=[core, flange],
        ear=(ROW_A[0] - PAD_HALF_X, ROW_A[1], -1),
        top_z=SHEET_TOP_Z,
        radius_overrides={(WALL_X[0], row_a_bottom): FLANGE_CORNER_RADIUS},
        wall=(BEND_LINE_Y, -1, WALL_X[0], WALL_X[1], WALL_DEPTH, WALL_CORNER_RADIUS,
                WALL_HOLE_X, WALL_HOLE_DEPTH, WALL_HOLE_DIAMETER),
    )


def build() -> Part:
    part = build_busbar(busbar())
    part.label = PART_NUMBER
    return part
