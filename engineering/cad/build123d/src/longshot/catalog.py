"""BOM metadata for every part in the Longshot main assembly.

Quantities are not stored here - ``tools/generate_bom.py`` counts them from
``placements.json``. ``PART_KEYS`` maps the part keys found in the Fusion
tree to the BOM line they roll up into (PCB layers into their board, the
mirrored bridge busbar into PW-BUS-003-Bridge_1).

Material is filled in only where the part number, part name or an Arrow
build record states it; otherwise it is left blank.
"""

from __future__ import annotations

CUSTOM = "custom mechanical"
BUSBAR = "busbar"
COTS = "COTS"
PCB = "PCB"
CELL = "cell"

COPPER_ORDER = "Copper, 0.2 mm sheet (PT1 copper order)"

# BOM line -> metadata. Order here is the BOM order.
LINES: dict[str, dict] = {
    # Cells
    "PW-CELL-001-21700": dict(
        description="21700 Li-ion cell. CAD placeholder model: Molicel 21700 P45B; PT1 uses BAK 21700 65E",
        category=CELL, make_buy="buy", material="",
        source="parts/pw_cell_001_21700.py",
    ),
    # Busbars
    "PW-BUS-001-N_Terminal": dict(
        description="Negative terminal busbar", category=BUSBAR, make_buy="make", material=COPPER_ORDER,
        source="parts/pw_bus_001_n_terminal.py",
    ),
    "PW-BUS-002-P_Terminal": dict(
        description="Positive terminal busbar", category=BUSBAR, make_buy="make", material=COPPER_ORDER,
        source="parts/pw_bus_002_p_terminal.py",
    ),
    "PW-BUS-003-Bridge_1": dict(
        description="Series bridge busbar between cell groups; qty includes the 6 instances of Fusion "
        "component PW-BUS-003-Bridge_1_Mirror (same outline and weld tongues, locating ear at the "
        "opposite end)",
        category=BUSBAR, make_buy="make", material=COPPER_ORDER,
        source="parts/pw_bus_003_bridge_1.py",
        extra_sources=["parts/pw_bus_003_bridge_1_mirror.py"],
    ),
    "PW-BUS-004-Bridge_2": dict(
        description="Series bridge busbar between the two cell-stack halves", category=BUSBAR,
        make_buy="make", material=COPPER_ORDER, source="parts/pw_bus_004_bridge_2.py",
    ),
    "PW-BUS-005-Screw_Terminal_Negative": dict(
        description="Negative screw terminal bar, 6 mm", category=BUSBAR, make_buy="make", material="",
        source="parts/pw_bus_005_screw_terminal_negative.py",
    ),
    "PW-BUS-006-Screw_Terminal_Positive": dict(
        description="Positive screw terminal bar, 6 mm", category=BUSBAR, make_buy="make", material="",
        source="parts/pw_bus_006_screw_terminal_positive.py",
    ),
    # Custom mechanical
    "EN-CELL-001-Upper_Cell_Holder": dict(
        description="Upper cell holder, 3D printed", category=CUSTOM, make_buy="make (3D print)", material="",
        source="parts/en_cell_001_upper_cell_holder.py",
    ),
    "EN-CELL-001-Bottom_Cell_Holder": dict(
        description="Bottom cell holder, 3D printed", category=CUSTOM, make_buy="make (3D print)", material="",
        source="parts/en_cell_001_bottom_cell_holder.py",
    ),
    "EN-PC-001-Top_Plate": dict(
        description="Top plate, 3 mm", category=CUSTOM, make_buy="make", material="Polycarbonate (PC)",
        source="parts/en_pc_001_top_plate.py",
    ),
    "EN-PC-002-Bottom_Plate": dict(
        description="Bottom plate, 3 mm", category=CUSTOM, make_buy="make", material="Polycarbonate (PC)",
        source="parts/en_pc_002_bottom_plate.py",
    ),
    "EN-SHEET-001-Reinfocement_Right": dict(
        description="Right reinforcement sheet (\"Reinfocement\" is the CAD part-number spelling)",
        category=CUSTOM, make_buy="make", material="Aluminium sheet",
        source="parts/en_sheet_001_reinfocement_right.py",
    ),
    "EN-SHEET-002-Reinfocement_Left": dict(
        description="Left reinforcement sheet (\"Reinfocement\" is the CAD part-number spelling)",
        category=CUSTOM, make_buy="make", material="Aluminium sheet",
        source="parts/en_sheet_002_reinfocement_left.py",
    ),
    "EN-PRINT-001-3D-Printable_Battery_Base": dict(
        description="Battery base, 3D printed", category=CUSTOM, make_buy="make (3D print)", material="",
        source="parts/en_print_001_3d_printable_battery_base.py",
    ),
    "EN-PRINT-002-3D-Printable_Battery_Top_Cover": dict(
        description="Battery top cover, 3D printed", category=CUSTOM, make_buy="make (3D print)", material="",
        source="parts/en_print_002_3d_printable_battery_top_cover.py",
    ),
    "EN-STRAP-001-Metal_piece": dict(
        description="Strap metal piece", category=CUSTOM, make_buy="make", material="Metal",
        source="parts/en_strap_001_metal_piece.py",
    ),
    "EN-STRAP-002-Rubber_Part": dict(
        description="Strap rubber part", category=CUSTOM, make_buy="make", material="Rubber",
        source="parts/en_strap_002_rubber_part.py",
    ),
    "EN-STRAP-003-Metal_End": dict(
        description="Strap metal end", category=CUSTOM, make_buy="make", material="Metal",
        source="parts/en_strap_003_metal_end.py",
    ),
    # PCBs (layers rolled up into the board)
    "SL_PCB-002-SL_PCB_V3": dict(
        description="SL_PCB V3 main battery PCB, bare board (components listed separately)",
        category=PCB, make_buy="make (PCB fab)", material="",
        source="cots/sl_pcb_002_sl_pcb_v3.py", design="../../electronics/pcbs/SL_PCB/",
    ),
    "VS_PCB_COMPLETE_TOP_LEFT": dict(
        description="Voltage-sense PCB, top left, bare board", category=PCB, make_buy="make (PCB fab)",
        material="", source="cots/vs_pcb_complete_top_left.py",
    ),
    "VS_PCB_COMPLETE_TOP_RIGHT": dict(
        description="Voltage-sense PCB, top right, bare board", category=PCB, make_buy="make (PCB fab)",
        material="", source="cots/vs_pcb_complete_top_right.py",
    ),
    "VS_PCB_COMPLETE_BOTTOM_LEFT": dict(
        description="Voltage-sense PCB, bottom left, bare board", category=PCB, make_buy="make (PCB fab)",
        material="", source="cots/vs_pcb_complete_bottom_left.py",
    ),
    "VS_PCB_COMPLETE_BOTTOM_RIGHT": dict(
        description="Voltage-sense PCB, bottom right, bare board", category=PCB, make_buy="make (PCB fab)",
        material="", source="cots/vs_pcb_complete_bottom_right.py",
    ),
    # COTS
    "ET60S-D06-0-00-D06-L-V1-S": dict(
        description="ET60S-D06 battery connector (on SL_PCB)", category=COTS, make_buy="buy", material="",
        source="cots/et60s_d06_0_00_d06_l_v1_s.py",
    ),
    "EL-FUSE-001-AMXL-200": dict(
        description="AMXL-200 fuse. The SL_PCB README specifies an AMX-150 fuse; the CAD uses AMXL-200",
        category=COTS, make_buy="buy", material="", source="cots/el_fuse_001_amxl_200.py",
    ),
    "FUSE-SMD_L10_0-W5_0-H3_8": dict(
        description="SMD fuse, 10.0 x 5.0 x 3.8 mm package per CAD name (on SL_PCB)", category=COTS,
        make_buy="buy", material="", source="cots/fuse_smd_l10_0_w5_0_h3_8.py",
    ),
    "AMT0450003DB0000G": dict(
        description="Component AMT0450003DB0000G (CAD model name, on SL_PCB)", category=COTS, make_buy="buy",
        material="", source="cots/amt0450003db0000g.py",
    ),
    "CONN-TH_430451612": dict(
        description="Through-hole connector 430451612 (CAD model name, on SL_PCB)", category=COTS,
        make_buy="buy", material="", source="cots/conn_th_430451612.py",
    ),
    "CONN-SMD_SM7B-GHS-TB-LF-SN": dict(
        description="JST SM7B-GHS-TB 7-pin SMD connector (4 on SL_PCB, 1 on each voltage-sense PCB)",
        category=COTS, make_buy="buy", material="", source="cots/conn_smd_sm7b_ghs_tb_lf_sn.py",
    ),
    "Tattu_4_0_30Ah_Clip": dict(
        description="Tattu 4.0 30Ah clip", category=COTS, make_buy="buy", material="",
        source="cots/tattu_4_0_30ah_clip.py",
    ),
    "EN-INSERT-001-ruthex_RX-M3x5_7": dict(
        description="ruthex RX-M3x5.7 heat-set insert, M3", category=COTS, make_buy="buy", material="",
        source="cots/en_insert_001_ruthex_rx_m3x5_7.py",
    ),
    "EN-INSERT-002-ruthex_RX-M4x8_1": dict(
        description="ruthex RX-M4x8.1 heat-set insert, M4", category=COTS, make_buy="buy", material="",
        source="cots/en_insert_002_ruthex_rx_m4x8_1.py",
    ),
}

# Fusion part keys that roll up into a different BOM line.
ROLLUP = {
    "PW-BUS-003-Bridge_1_Mirror": "PW-BUS-003-Bridge_1",
}


def bom_line(part_key: str) -> str:
    """BOM line for a part key from placements.json."""
    if part_key in ROLLUP:
        return ROLLUP[part_key]
    if ":" in part_key:  # PCB layer "BOARD:layer" -> board
        return part_key.split(":", 1)[0]
    return part_key
