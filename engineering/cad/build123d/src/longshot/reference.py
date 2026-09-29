"""Paths and loaders for reference geometry and placement metadata."""

from __future__ import annotations

import gzip
import json
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from build123d import Compound, Location, import_step
from OCP.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf
from OCP.TopLoc import TopLoc_Location

PACKAGE_DIR = Path(__file__).resolve().parent
BUILD123D_DIR = PACKAGE_DIR.parents[1]
REFERENCE_DIR = BUILD123D_DIR / "reference"
COTS_DIR = REFERENCE_DIR / "cots"
# Custom-part reference solids are extracted here for validation only.
# The folder is git-ignored; run tools/extract_reference.py to fill it.
CACHE_DIR = REFERENCE_DIR / ".cache"
EXPORT_DIR = BUILD123D_DIR / "exports"
PLACEMENTS_FILE = PACKAGE_DIR / "placements.json"


def safe_name(key: str) -> str:
    """File-system safe name for a part key."""
    out = []
    for ch in key:
        out.append(ch if ch.isalnum() or ch in "-_" else "_")
    return "".join(out)


@lru_cache(maxsize=1)
def placements() -> dict:
    """Parsed ``placements.json``."""
    with PLACEMENTS_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def matrix_to_location(m: list[list[float]]) -> Location:
    """Convert a row-major 4x4 matrix (rigid transform) into a build123d Location.

    The frame is rebuilt from its origin, X and Z columns so the rotation is
    exactly orthonormal (OCCT rejects locations with any scaling).
    """
    origin = gp_Pnt(m[0][3], m[1][3], m[2][3])
    x_dir = gp_Dir(m[0][0], m[1][0], m[2][0])
    z_dir = gp_Dir(m[0][2], m[1][2], m[2][2])
    trsf = gp_Trsf()
    trsf.SetTransformation(gp_Ax3(origin, z_dir, x_dir))
    trsf.Invert()
    return Location(TopLoc_Location(trsf))


def _read_step(path: Path) -> Compound:
    if path.suffix == ".gz":
        with tempfile.TemporaryDirectory() as tmp:
            plain = Path(tmp) / path.stem
            with gzip.open(path, "rb") as src, plain.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            return import_step(plain)
    return import_step(path)


@lru_cache(maxsize=None)
def _load_cached(path: str) -> Compound:
    return _read_step(Path(path))


def load_cots(key: str) -> Compound:
    """Load the committed reference STEP for a purchased/PCB part key.

    Returned shapes are in the part's own (Fusion component) frame. A fresh
    copy is returned so callers can relocate it freely.
    """
    info = placements()["parts"][key]
    ref = info.get("reference")
    if not ref:
        raise FileNotFoundError(f"no committed reference geometry for {key!r}")
    shape = _load_cached(str(BUILD123D_DIR / ref))
    return shape.moved(Location())


def load_custom_reference(key: str) -> Compound:
    """Load an extracted custom-part reference solid (validation only)."""
    path = CACHE_DIR / "custom" / f"{safe_name(key)}.step"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing - run tools/extract_reference.py with the source STEP"
        )
    return _load_cached(str(path)).moved(Location())
