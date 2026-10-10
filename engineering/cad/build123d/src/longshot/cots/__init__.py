"""Purchased (COTS) and PCB-derived parts.

These are not recreated: each wrapper module loads the reference geometry
that ``tools/extract_reference.py`` copied out of the Fusion export into
``reference/cots/`` (gzip-compressed STEP, component frame).

Every wrapper module defines ``PART_NUMBER``, ``REFERENCE_KEYS`` (the part
keys in ``placements.json`` it covers) and ``build(key=None)``.
"""

from __future__ import annotations

import importlib
from types import ModuleType

from build123d import Compound

from ..reference import load_cots, placements

MODULES = [
    "en_insert_001_ruthex_rx_m3x5_7",
    "en_insert_002_ruthex_rx_m4x8_1",
    "sl_pcb_002_sl_pcb_v3",
    "et60s_d06_0_00_d06_l_v1_s",
    "amt0450003db0000g",
    "fuse_smd_l10_0_w5_0_h3_8",
    "conn_th_430451612",
    "conn_smd_sm7b_ghs_tb_lf_sn",
    "vs_pcb_complete_bottom_left",
    "vs_pcb_complete_bottom_right",
    "vs_pcb_complete_top_left",
    "vs_pcb_complete_top_right",
    "tattu_4_0_30ah_clip",
    "el_fuse_001_amxl_200",
]


class ReferencePart:
    """Geometry wrapper around one or more committed reference STEPs."""

    def __init__(self, part_number: str, keys: list[str] | None = None, prefix: str | None = None):
        self.part_number = part_number
        if prefix is not None:
            keys = [k for k in placements()["parts"] if k.startswith(prefix)]
        self.keys = keys or [part_number]

    def available_keys(self) -> list[str]:
        """Keys that have committed geometry (some PCB artwork layers are skipped)."""
        return [k for k in self.keys if placements()["parts"][k].get("reference")]

    def build(self, key: str | None = None) -> Compound:
        """One reference body (``key``) or all of them as one labelled compound."""
        if key is not None:
            if key not in self.keys:
                raise KeyError(f"{key!r} is not part of {self.part_number}")
            shape = load_cots(key)
            shape.label = placements()["parts"][key]["label"]
            return shape
        children = [self.build(k) for k in self.available_keys()]
        if len(children) == 1:
            children[0].label = self.part_number
            return children[0]
        return Compound(children=children, label=self.part_number)


def load(module: str) -> ModuleType:
    return importlib.import_module(f"{__name__}.{module}")


def module_for_key(key: str) -> ModuleType:
    """Wrapper module that owns a placements.json part key."""
    for name in MODULES:
        mod = load(name)
        if key in mod.REFERENCE_KEYS:
            return mod
    raise KeyError(f"no COTS wrapper module for part key {key!r}")


def build(key: str) -> Compound:
    return module_for_key(key).build(key)
