#!/usr/bin/env python3
"""Generate BOM.md and BOM.csv for the Longshot main assembly.

Quantities are counted from ``src/longshot/placements.json`` (one pack) and
rolled up by BOM line (see ``longshot.catalog``). Validation status comes from
``validation/results.json`` written by ``tools/validate_parts.py``.

Usage::

    python tools/generate_bom.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from longshot import catalog  # noqa: E402
from longshot.reference import BUILD123D_DIR, placements, safe_name  # noqa: E402

BOM_MD = BUILD123D_DIR / "BOM.md"
BOM_CSV = BUILD123D_DIR / "BOM.csv"
RESULTS_JSON = BUILD123D_DIR / "validation" / "results.json"
PT1_BOM = "../../builds/PT1/BOM.md"

COLUMNS = [
    "Part number",
    "Description",
    "Qty",
    "Category",
    "Make/buy",
    "Material",
    "build123d source",
    "Reference / export",
    "Validation",
]


def validation_text(results: dict, part: str) -> str:
    r = results.get(part)
    if not r:
        return "not validated"
    sym = "n/a" if r["symdiff_pct"] is None else f"{r['symdiff_pct']:.2f} %"
    text = (
        f"{r['status']}: bbox Δ {r['bbox_delta_mm']:.3f} mm, vol Δ {r['volume_delta_pct']:+.2f} %, "
        f"sym-diff {sym}"
    )
    if r["status"] != "pass" and r.get("note"):
        text += f" ({r['note']})"
    return text


def main() -> None:
    meta = placements()
    results = json.loads(RESULTS_JSON.read_text()) if RESULTS_JSON.exists() else {}

    # Count instances per BOM line. PCB layer bodies are counted once per board.
    qty: Counter = Counter()
    per_key: dict[str, Counter] = defaultdict(Counter)
    boards_seen: set[str] = set()
    for item in meta["items"]:
        key = item["part"]
        line = catalog.bom_line(key)
        if line not in catalog.LINES:
            raise SystemExit(f"part key {key!r} (BOM line {line!r}) missing from longshot/catalog.py")
        if ":" in key:
            if line in boards_seen:
                continue
            boards_seen.add(line)
        qty[line] += 1
        per_key[line][key] += 1

    rows = []
    for line, info in catalog.LINES.items():
        if qty[line] == 0:
            raise SystemExit(f"BOM line {line!r} has no instances in placements.json")
        src = f"src/longshot/{info['source']}"
        sources = [src] + [f"src/longshot/{s}" for s in info.get("extra_sources", [])]
        if info["category"] in (catalog.CUSTOM, catalog.BUSBAR, catalog.CELL):
            refs = [f"exports/stl/{line}.stl", f"exports/step/{line}.step"]
            status = validation_text(results, line)
            for extra in per_key[line]:
                if extra != line:
                    status += f"; {extra}: " + validation_text(results, extra)
        else:
            keys = [k for k in meta["parts"] if catalog.bom_line(k) == line]
            refs = [meta["parts"][k]["reference"] for k in keys if meta["parts"][k].get("reference")]
            # For boards, point at the board body; the other layers sit next to it.
            board = [r for r in refs if r.endswith("_PCB.step.gz")]
            refs = board or refs[:1]
            status = "reference geometry (not recreated)"
        qty_text = str(qty[line])
        if len(per_key[line]) > 1 and ":" not in next(iter(per_key[line])):
            qty_text += " (" + " + ".join(f"{n} {k}" for k, n in per_key[line].items()) + ")"
        rows.append(
            {
                "Part number": line,
                "Description": info["description"],
                "Qty": qty[line],
                "Qty note": qty_text,
                "Category": info["category"],
                "Make/buy": info["make_buy"],
                "Material": info["material"],
                "sources": sources,
                "refs": refs,
                "Validation": status,
                "design": info.get("design"),
            }
        )

    # CSV
    with BOM_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(COLUMNS)
        for r in rows:
            writer.writerow(
                [
                    r["Part number"],
                    r["Description"],
                    r["Qty"],
                    r["Category"],
                    r["Make/buy"],
                    r["Material"],
                    "; ".join(r["sources"]),
                    "; ".join(r["refs"]),
                    r["Validation"],
                ]
            )

    # Markdown
    by_cat: Counter = Counter()
    lines_by_cat: Counter = Counter()
    for r in rows:
        by_cat[r["Category"]] += r["Qty"]
        lines_by_cat[r["Category"]] += 1
    total = sum(by_cat.values())
    src = meta["source"]
    size = " × ".join(f"{v:.1f}" for v in src["size"])

    md = [
        "# Longshot main assembly BOM",
        "",
        "Generated by `tools/generate_bom.py` from the Fusion assembly tree in",
        "[`src/longshot/placements.json`](src/longshot/placements.json). Quantities are per battery pack.",
        f"Source: Julius's Fusion export `{src['file']}` (assembly bbox {size} mm).",
        "",
        f"Purchase records and costs for the PT1 build are in the [PT1 BOM]({PT1_BOM}); this file",
        "lists what the CAD assembly contains and does not repeat supplier or cost data.",
        "",
        "## Summary",
        "",
        "| Category | BOM lines | Parts per pack |",
        "| --- | ---: | ---: |",
    ]
    for cat in (catalog.CELL, catalog.BUSBAR, catalog.CUSTOM, catalog.PCB, catalog.COTS):
        md.append(f"| {cat} | {lines_by_cat[cat]} | {by_cat[cat]} |")
    md += [f"| **Total** | **{len(rows)}** | **{total}** |", ""]
    md += [
        "## Notes",
        "",
        "- **Cells:** the Fusion model uses a vendor model named \"Molicel 21700 P45B\" as a placeholder for",
        "  `PW-CELL-001-21700`. The PT1 build uses 126 BAK 21700 65E cells; see the",
        f"  [PT1 BOM]({PT1_BOM}). The build123d cell is a simplified parametric 21700 cell sized from the",
        "  placeholder model.",
        "- **Bridge busbars:** the Fusion tree has 6 × `PW-BUS-003-Bridge_1` and 6 ×",
        "  `PW-BUS-003-Bridge_1_Mirror`. The \"Mirror\" component is not a geometric mirror: it has the",
        "  same outline and weld tongues, with the locating ear at the opposite end. Both are listed as one",
        "  line (12 per pack) because the PT1 copper order has a single `PW-BUS-003-Bridge_1` flat pattern.",
        "  Check with Julius before ordering if the two variants need separate flat patterns.",
        "- **PCBs:** PCB sub-layers in the Fusion export (board, copper/pads, soldermask, silkscreen) are",
        "  rolled up into their board. Populated components are listed as separate COTS lines. The",
        "  SL_PCB design lives in [`../../electronics/pcbs/SL_PCB/`](../../electronics/pcbs/SL_PCB/).",
        "- **Main fuse:** the CAD places an AMXL-200 fuse (`EL-FUSE-001-AMXL-200`); the",
        "  [SL_PCB README](../../electronics/pcbs/SL_PCB/README.md) describes an AMX-150 fuse.",
        "- **Spelling:** `Reinfocement` in the EN-SHEET part numbers is the CAD spelling and is kept so",
        "  the part numbers match Fusion.",
        "- **Material** is filled in only where the part number, name or a PT1 build record states it.",
        "",
        "## Parts",
        "",
        "| " + " | ".join(COLUMNS) + " |",
        "| --- | --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        src_links = ", ".join(f"[`{Path(s).name}`]({s})" for s in r["sources"])
        ref_links = ", ".join(f"[`{Path(s).name}`]({s})" for s in r["refs"])
        desc = r["Description"]
        if r["design"]:
            desc += f" ([design]({r['design']}))"
        md.append(
            f"| `{r['Part number']}` | {desc} | {r['Qty note']} | {r['Category']} | {r['Make/buy']} | "
            f"{r['Material']} | {src_links} | {ref_links} | {r['Validation']} |"
        )
    BOM_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {BOM_MD.name} and {BOM_CSV.name}: {len(rows)} lines, {total} parts per pack")
    for cat in by_cat:
        print(f"  {cat:18s} {lines_by_cat[cat]:3d} lines {by_cat[cat]:4d} parts")


if __name__ == "__main__":
    main()
