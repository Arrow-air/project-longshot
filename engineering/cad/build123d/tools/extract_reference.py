#!/usr/bin/env python3
"""Extract placements and reference geometry from the Fusion STEP export.

Reads Julius's ``Longshot_Main_Assembly.step`` and writes:

* ``src/longshot/placements.json`` - the full Fusion assembly tree (labels,
    relative locations, part keys), every item and leaf instance with its
    global 4x4 location matrix, and per-part reference metrics (bbox, volume,
    area) used by ``validate_parts.py``.
* ``reference/cots/<part>.step.gz`` - gzip-compressed reference STEP for each
    purchased / PCB-derived part (committed).
* ``reference/.cache/custom/<part>.step`` - reference solids for custom parts,
    used only to validate the parametric rebuilds (git-ignored).

Usage::

    python tools/extract_reference.py /path/to/Longshot_Main_Assembly.step
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path

from build123d import Compound, Location, export_step, import_step
from OCP.TopLoc import TopLoc_Location

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from longshot.reference import (  # noqa: E402
    BUILD123D_DIR,
    CACHE_DIR,
    COTS_DIR,
    PLACEMENTS_FILE,
    safe_name,
)

# Assembly nodes that only group other nodes (recursed into, never parts).
GROUP_PATTERNS = [
    r"^Longshot_Main_Assembly$",
    r"^Longshot_Cell_Assembly$",
    r"^PW-9P14S_Stack$",
    r"^PW-9P1S_Stack$",
    r"^Insert_Assembly$",
    r"^EN-INSERT-00\d-.*",
    r"^Strap_Assembly$",
    r"^SL_PCB-002-SL_PCB_V3$",
    r"^VS_PCB_COMPLETE_.*",
]

# Custom (Arrow-designed) part number prefixes; everything else is COTS/PCB.
CUSTOM_PREFIXES = ("PW-CELL-", "PW-BUS-", "EN-CELL-", "EN-SHEET-", "EN-PC-", "EN-PRINT-", "EN-STRAP-")

# PCB layer bodies are keyed by their board so the four different VS boards
# (and their layers) stay distinct.
PCB_PARENT = re.compile(r"^(SL_PCB-002-SL_PCB_V3|VS_PCB_COMPLETE_.*)$")
PCB_LAYER = re.compile(r"^(SL_PCB|VS_PCB)_")

# Insert solids carry vendor names; key them by Arrow's EN-INSERT part numbers.
LABEL_KEYS = {
    "RX-M4x8_1": "EN-INSERT-002-ruthex_RX-M4x8_1",
    "ruthex_RX-M3-5,7": "EN-INSERT-001-ruthex_RX-M3x5_7",
}

# Reference geometry left out of the repository to keep it small.
SKIP_REFERENCE = {
    r":SL_PCB_copper$": "copper artwork layer, about 18 MB as STEP; not needed for packaging",
    r":(SL|VS)_PCB_silkscreen": "cosmetic zero-thickness silkscreen artwork",
}

DIGITS = 9


def is_group(label: str) -> bool:
    return any(re.match(p, label) for p in GROUP_PATTERNS)


def part_key(label: str, parent_label: str | None) -> str:
    if label in LABEL_KEYS:
        return LABEL_KEYS[label]
    if parent_label and PCB_PARENT.match(parent_label) and PCB_LAYER.match(label):
        return f"{parent_label}:{label}"
    return label


def is_custom(key: str) -> bool:
    return key.startswith(CUSTOM_PREFIXES)


def skip_reason(key: str) -> str | None:
    for pattern, reason in SKIP_REFERENCE.items():
        if re.search(pattern, key):
            return reason
    return None


def mat(loc: Location) -> list[list[float]]:
    t = loc.wrapped.Transformation()
    rows = [[round(t.Value(r, c), DIGITS) + 0.0 for c in range(1, 5)] for r in range(1, 4)]
    return rows + [[0.0, 0.0, 0.0, 1.0]]


def bbox_list(shape) -> list[list[float]]:
    bb = shape.bounding_box()
    return [
        [round(bb.min.X, 4), round(bb.min.Y, 4), round(bb.min.Z, 4)],
        [round(bb.max.X, 4), round(bb.max.Y, 4), round(bb.max.Z, 4)],
    ]


def detach(node, keep_location: bool = True):
    """Rebuild a node (and its subtree) without the parent links.

    build123d's ``moved``/``copy`` deep-copy the whole assembly tree through
    the parent reference, which is very slow on this 47 MB model, so the OCCT
    shapes are re-wrapped directly instead.
    """
    kids = list(node.children)
    if kids:
        out = Compound(children=[detach(k) for k in kids], label=node.label)
        if keep_location:
            out.location = node.location
        return out
    loc = node.location.wrapped if keep_location else TopLoc_Location()
    out = type(node)(node.wrapped.Located(loc))
    out.label = node.label
    out.color = node.color
    return out


def local_copy(node):
    """Geometry of an item node in its own frame (children kept relative)."""
    return detach(node, keep_location=False)


def dump_json(data) -> str:
    """JSON with 2-space indent, keeping numeric arrays (vectors, matrix rows) on one line."""
    text = json.dumps(data, indent=2)
    number_list = re.compile(r"\[\s*(-?[\d.e+-]+(?:,\s*-?[\d.e+-]+)*)\s*\]")
    text = number_list.sub(lambda m: "[" + ", ".join(v.strip() for v in m.group(1).split(",")) + "]", text)
    return text + "\n"


def export_gz(shape, dest: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plain = Path(tmp) / "part.step"
        export_step(shape, plain)
        data = plain.read_bytes()
    # mtime=0 keeps the compressed output deterministic between runs.
    with gzip.GzipFile(dest, "wb", mtime=0) as fh:
        fh.write(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", type=Path, help="Fusion export Longshot_Main_Assembly.step")
    parser.add_argument("--no-geometry", action="store_true", help="only rewrite placements.json")
    args = parser.parse_args()

    print(f"loading {args.step} ...", flush=True)
    root = import_step(args.step)
    sha = hashlib.sha256(args.step.read_bytes()).hexdigest()

    parts: "OrderedDict[str, dict]" = OrderedDict()
    samples: dict[str, object] = {}
    items: list[dict] = []
    leaves: list[dict] = []
    warnings: list[str] = []

    def record_leaves(node, path: str, item_path: str, key: str) -> None:
        kids = list(node.children)
        if not kids:
            leaves.append(
                {
                    "path": path,
                    "label": node.label,
                    "part": key,
                    "item_path": item_path,
                    "location": mat(node.global_location),
                }
            )
        for kid in kids:
            record_leaves(kid, f"{path}/{kid.label}", item_path, key)

    def walk(node, path: str, parent_label: str | None) -> dict:
        entry: dict = {"label": node.label, "location": mat(node.location)}
        if is_group(node.label):
            entry["children"] = [walk(k, f"{path}/{k.label}", node.label) for k in node.children]
            return entry
        key = part_key(node.label, parent_label)
        entry["part"] = key
        items.append({"path": path, "part": key, "location": mat(node.global_location)})
        record_leaves(node, path, path, key)
        if key not in parts:
            local = local_copy(node)
            samples[key] = local
            parts[key] = {
                "label": node.label,
                "kind": "custom" if is_custom(key) else "cots",
                "count": 0,
                "bbox": bbox_list(local),
                "volume": round(local.volume, 4),
                "area": round(local.area, 4),
                "solids": len(local.solids()),
                "faces": len(local.faces()),
            }
        else:
            vol = round(local_copy(node).volume, 4) if not list(node.children) else parts[key]["volume"]
            if abs(vol - parts[key]["volume"]) > 1e-3 * max(1.0, abs(parts[key]["volume"])):
                warnings.append(f"{path}: volume {vol} differs from first {key} instance")
        parts[key]["count"] += 1
        return entry

    tree = walk(root, root.label, None)

    ref_bb = root.bounding_box()
    meta = {
        "source": {
            "file": args.step.name,
            "sha256": sha,
            "exported_by": "Autodesk Translation Framework (Fusion 360), STEP AP214",
            "bbox": bbox_list(root),
            "size": [round(ref_bb.size.X, 3), round(ref_bb.size.Y, 3), round(ref_bb.size.Z, 3)],
        },
        "units": "mm",
        "matrix_convention": "row-major 4x4, global = parent * local",
        "tree": tree,
        "items": items,
        "leaves": leaves,
        "parts": parts,
        "warnings": warnings,
    }

    if not args.no_geometry:
        COTS_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / "custom").mkdir(parents=True, exist_ok=True)
        for key, info in parts.items():
            shape = samples[key]
            if info["kind"] == "custom":
                dest = CACHE_DIR / "custom" / f"{safe_name(key)}.step"
                export_step(shape, dest)
                info["reference"] = None
                print(f"  custom ref  {dest.relative_to(BUILD123D_DIR)}", flush=True)
                continue
            reason = skip_reason(key)
            if reason:
                info["reference"] = None
                info["reference_note"] = f"not committed: {reason}"
                print(f"  skipped     {key}: {reason}", flush=True)
                continue
            dest = COTS_DIR / f"{safe_name(key)}.step.gz"
            export_gz(shape, dest)
            info["reference"] = dest.relative_to(BUILD123D_DIR).as_posix()
            print(f"  cots ref    {info['reference']} ({dest.stat().st_size / 1e6:.2f} MB)", flush=True)
    else:
        old = json.loads(PLACEMENTS_FILE.read_text()) if PLACEMENTS_FILE.exists() else {"parts": {}}
        for key, info in parts.items():
            prev = old["parts"].get(key, {})
            for field in ("reference", "reference_note"):
                if field in prev:
                    info[field] = prev[field]

    PLACEMENTS_FILE.write_text(dump_json(meta), encoding="utf-8")
    counts = Counter(i["part"] for i in items)
    print(f"wrote {PLACEMENTS_FILE.relative_to(BUILD123D_DIR)}: {len(items)} items, "
            f"{len(leaves)} leaves, {len(parts)} unique parts")
    for key, n in sorted(counts.items()):
        print(f"  {n:4d} x {key}")
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
