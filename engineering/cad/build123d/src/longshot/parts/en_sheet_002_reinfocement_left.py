"""EN-SHEET-002 Reinfocement Left - 1 mm bent aluminium side reinforcement.

"Reinfocement" (sic) is the spelling of the Fusion/CAD part number and is
kept verbatim in PART_NUMBER.

Probed from the Fusion reference solid: identical blank to EN-SHEET-001
(same frame x = -118.5..-54.5, y = 0..316, z = +/-38.85, same volume
28 401.7 mm^3, same bends and outline) - it is NOT a mirror image. Only the
cell-row hole pattern differs:

* web-B holes start one cell row later (y = 52.337 instead of 32.419) with
    the z sign alternation starting at +6.2 instead of -6.2;
* foot-tab holes at x = -74.75 / -97.75 (right: -63.25 / -86.25), i.e.
    shifted half a 23 mm cell pitch.
"""

from __future__ import annotations

from build123d import Part

from .en_sheet_001_reinfocement_right import CELL_HOLE_Z, CELL_PITCH_Y, WEB_B_HOLE_Y_FIRST, build_reinforcement

PART_NUMBER = "EN-SHEET-002-Reinfocement_Left"

WEB_B_HOLE_Y_FIRST_LEFT = WEB_B_HOLE_Y_FIRST + CELL_PITCH_Y / 2  # 52.337
WEB_B_HOLE_Z_FIRST_LEFT = CELL_HOLE_Z  # +6.2
TAB_HOLE_X_LEFT = (-74.75, -97.75)


def build() -> Part:
    part = build_reinforcement(
        web_b_hole_y_first=WEB_B_HOLE_Y_FIRST_LEFT,
        web_b_hole_z_first=WEB_B_HOLE_Z_FIRST_LEFT,
        tab_hole_x=TAB_HOLE_X_LEFT,
    )
    part.label = PART_NUMBER
    return part
