"""Rebuild the Longshot main assembly from the part modules and placements.

The Fusion tree stored in ``placements.json`` is rebuilt node by node as a
labelled build123d Compound hierarchy. Custom parts come from
``longshot.parts`` (parametric), purchased/PCB parts from ``longshot.cots``
(reference geometry). PCB artwork layers without committed geometry (copper,
silkscreen) are left out.

Usage (from engineering/cad/build123d)::

    PYTHONPATH=src python -m longshot.assembly             # check bbox, export everything
    PYTHONPATH=src python -m longshot.assembly --check     # build and check bbox only
    PYTHONPATH=src python -m longshot.assembly --no-step   # per-part STL/STEP only

Per-part exports go to ``exports/stl/<PART>.stl`` and ``exports/step/<PART>.step``;
the full assembly goes to ``exports/step/Longshot_Main_Assembly.step``.
"""

from __future__ import annotations

import argparse
import gzip
import shutil
import time
from pathlib import Path

from build123d import Compound, Location, Shape, export_step, export_stl

from . import cots, parts
from .reference import EXPORT_DIR, matrix_to_location, placements

STEP_DIR = EXPORT_DIR / "step"
STL_DIR = EXPORT_DIR / "stl"
# Not committed (about 75 MB, mostly vendor models); regenerate with this module.
ASSEMBLY_STEP = STEP_DIR / "Longshot_Main_Assembly.step"
BBOX_TOL = 0.5  # mm, rebuilt vs reference assembly bbox

_custom_cache: dict[str, Shape] = {}
_cots_cache: dict[str, Shape] = {}


def _relocate(shape: Shape, loc: Location, label: str) -> Shape:
    """Place ``shape`` at ``loc`` without deep-copying it (instances share geometry)."""
    kids = list(shape.children)
    if kids:
        out = Compound(children=[_relocate(k, k.location, k.label) for k in kids], label=label)
        out.color = shape.color
        out.location = loc
        return out
    out = type(shape)(shape.wrapped.Located(loc.wrapped))
    out.label = label
    out.color = shape.color
    return out


def part_shape(key: str) -> Shape | None:
    """Unplaced geometry for a part key, or None when no geometry is committed."""
    info = placements()["parts"][key]
    if info["kind"] == "custom":
        if key not in _custom_cache:
            _custom_cache[key] = parts.load(key).build()
        return _custom_cache[key]
    if not info.get("reference"):
        return None
    if key not in _cots_cache:
        _cots_cache[key] = cots.build(key)
    return _cots_cache[key]


def _build_node(entry: dict) -> Shape | None:
    loc = matrix_to_location(entry["location"])
    if "children" in entry:
        kids = [k for k in (_build_node(c) for c in entry["children"]) if k is not None]
        node = Compound(children=kids, label=entry["label"])
        node.location = loc
        return node
    shape = part_shape(entry["part"])
    if shape is None:
        return None
    return _relocate(shape, loc, entry["label"])


def build_assembly(verbose: bool = False) -> Compound:
    """The full ``Longshot_Main_Assembly`` compound."""
    if verbose:
        for key in parts.PART_NUMBERS:
            t0 = time.time()
            part_shape(key)
            print(f"  built {key} ({time.time() - t0:.1f} s)", flush=True)
    return _build_node(placements()["tree"])


def check_bbox(assembly: Compound) -> tuple[bool, list[float], list[float]]:
    bb = assembly.bounding_box()
    size = [bb.size.X, bb.size.Y, bb.size.Z]
    ref = placements()["source"]["size"]
    ok = all(abs(a - b) <= BBOX_TOL for a, b in zip(size, ref))
    return ok, size, ref


def export_parts() -> list[Path]:
    """One STL and one STEP per custom part number, in its own component frame.

    STLs are gzip-compressed: the repo spell check reads binary STL as text.
    """
    STL_DIR.mkdir(parents=True, exist_ok=True)
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for key in parts.PART_NUMBERS:
        shape = part_shape(key)
        plain = STL_DIR / f"{key}.stl"
        export_stl(shape, plain, tolerance=0.05, angular_tolerance=0.2)
        stl = STL_DIR / f"{key}.stl.gz"
        with plain.open("rb") as src, gzip.GzipFile(stl, "wb", mtime=0) as dst:
            shutil.copyfileobj(src, dst)
        plain.unlink()
        step = STEP_DIR / f"{key}.step"
        export_step(shape, step)
        written += [stl, step]
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Longshot main assembly.")
    parser.add_argument("--check", action="store_true", help="build and check the bbox only")
    parser.add_argument("--no-step", action="store_true", help="skip the assembly STEP export")
    parser.add_argument("--no-parts", action="store_true", help="skip the per-part STL/STEP exports")
    args = parser.parse_args()

    t0 = time.time()
    assembly = build_assembly(verbose=True)
    ok, size, ref = check_bbox(assembly)
    print(
        f"assembly bbox {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm "
        f"(reference {ref[0]:.2f} x {ref[1]:.2f} x {ref[2]:.2f}) -> {'OK' if ok else 'MISMATCH'}"
        f" [{time.time() - t0:.0f} s]",
        flush=True,
    )
    if args.check:
        raise SystemExit(0 if ok else 1)
    if not args.no_parts:
        for path in export_parts():
            print(f"  wrote {path.relative_to(EXPORT_DIR.parent)} ({path.stat().st_size / 1e6:.2f} MB)")
    if not args.no_step:
        ASSEMBLY_STEP.parent.mkdir(parents=True, exist_ok=True)
        export_step(assembly, ASSEMBLY_STEP)
        print(f"  wrote {ASSEMBLY_STEP.relative_to(EXPORT_DIR.parent)} ({ASSEMBLY_STEP.stat().st_size / 1e6:.1f} MB)")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
