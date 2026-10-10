#!/usr/bin/env python3
"""Validate every parametric custom part against its reference solid.

For each part in ``longshot.parts.PART_NUMBERS`` this builds the parametric
model and compares it with the solid extracted from Julius's Fusion STEP
(both in the Fusion component frame):

* bbox delta - largest absolute difference of the six bbox min/max values;
* volume delta - (model - reference) / reference;
* symmetric difference - volume(reference - model) + volume(model - reference),
    computed as V(ref) + V(model) - 2 V(ref & model), as a percentage of the
    reference volume. If the boolean fails on the Fusion B-spline geometry, it
    is estimated by classifying random points instead (noted in the results);
    such an estimate only passes if it is below the limit by two standard
    errors.

A part passes when bbox delta <= 0.2 mm, |volume delta| <= 1 % and the
symmetric difference is < 2 %. Results are written to
``validation/results.json`` and ``validation/results.md``.

The symmetric difference needs the reference solids in
``reference/.cache/custom`` (run ``tools/extract_reference.py`` first). Without
them, bbox and volume are still checked against the metrics stored in
``placements.json``.

Usage::

    python tools/validate_parts.py                 # all parts
    python tools/validate_parts.py PW-BUS-004-Bridge_2 EN-PC-001-Top_Plate
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common  # noqa: E402
from OCP.BRepClass3d import BRepClass3d_SolidClassifier  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.ShapeFix import ShapeFix_Shape  # noqa: E402
from OCP.TopAbs import TopAbs_IN  # noqa: E402
from OCP.gp import gp_Pnt  # noqa: E402
from OCP.TopTools import TopTools_ListOfShape  # noqa: E402

from longshot import parts as part_modules  # noqa: E402
from longshot.reference import BUILD123D_DIR, load_custom_reference, placements  # noqa: E402

VALIDATION_DIR = BUILD123D_DIR / "validation"
RESULTS_JSON = VALIDATION_DIR / "results.json"
RESULTS_MD = VALIDATION_DIR / "results.md"

SAMPLES = 20000  # points for the sampled sym-diff fallback
BBOX_TOL = 0.2  # mm
VOLUME_TOL = 1.0  # percent
SYMDIFF_TOL = 2.0  # percent


def bbox_values(shape) -> list[float]:
    bb = shape.bounding_box()
    return [bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z]


def solid_volume(shape) -> float:
    return sum(s.volume for s in shape.solids())


def fixed(solid):
    """ShapeFix'd copy of a solid; Fusion's B-spline faces otherwise make some
    booleans silently return an empty result."""
    fix = ShapeFix_Shape(solid.wrapped)
    fix.Perform()
    return fix.Shape()


def sampled_symdiff(ref, model, samples: int = SAMPLES) -> tuple[float, float]:
    """Symmetric difference estimated by classifying random points.

    Fallback for when the boolean fails. Returns (volume, standard error),
    both in mm^3. Points are drawn uniformly in the union of both bboxes.
    """
    lo = [min(a, b) for a, b in zip(bbox_values(ref)[:3], bbox_values(model)[:3])]
    hi = [max(a, b) for a, b in zip(bbox_values(ref)[3:], bbox_values(model)[3:])]
    box_volume = (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2])

    def inside(shape):
        classifiers = [BRepClass3d_SolidClassifier(s.wrapped) for s in shape.solids()]

        def test(point) -> bool:
            for classifier in classifiers:
                classifier.Perform(point, 1e-6)
                if classifier.State() == TopAbs_IN:
                    return True
            return False

        return test

    in_ref, in_model = inside(ref), inside(model)
    rng = random.Random(0)
    differ = 0
    for _ in range(samples):
        point = gp_Pnt(*(rng.uniform(a, b) for a, b in zip(lo, hi)))
        differ += in_ref(point) != in_model(point)
    frac = differ / samples
    return frac * box_volume, math.sqrt(max(frac, 1.0 / samples) * (1 - frac) / samples) * box_volume


def common_volume(a, b, fuzzy: float = 1e-3) -> float:
    """Volume of the intersection of two shapes.

    Uses OCCT's general fuse Common directly with a small fuzzy tolerance;
    two cuts through build123d's operators are much slower on coincident
    faces, and symdiff = V(a) + V(b) - 2 V(a & b) needs only one boolean.
    """
    op = BRepAlgoAPI_Common()
    args, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    for solid in a.solids():
        args.Append(fixed(solid))
    for solid in b.solids():
        tools.Append(fixed(solid))
    op.SetArguments(args)
    op.SetTools(tools)
    op.SetFuzzyValue(fuzzy)
    op.SetRunParallel(True)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("common failed")
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(op.Shape(), props)
    return props.Mass()


def validate(part_number: str) -> dict:
    ref_info = placements()["parts"][part_number]
    t0 = time.time()
    module = part_modules.load(part_number)
    model = module.build()
    build_s = time.time() - t0

    ref_bbox = ref_info["bbox"][0] + ref_info["bbox"][1]
    ref_volume = ref_info["volume"]
    model_volume = solid_volume(model)
    bbox_delta = max(abs(a - b) for a, b in zip(bbox_values(model), ref_bbox))
    volume_delta = 100.0 * (model_volume - ref_volume) / ref_volume

    symdiff = None
    symdiff_sigma = 0.0  # sampling error; 0 for the exact boolean result
    symdiff_note = ""
    try:
        ref = load_custom_reference(part_number)
        try:
            common = common_volume(ref, model)
        except RuntimeError:
            common = 0.0  # boolean not done -> use the sampled estimate below
        if common < 0.5 * min(solid_volume(ref), model_volume):
            # The boolean silently failed (bbox and volume already match).
            volume, error = sampled_symdiff(ref, model)
            symdiff = 100.0 * volume / ref_volume
            symdiff_sigma = 100.0 * error / ref_volume
            symdiff_note = (
                f"boolean failed; sym-diff estimated from {SAMPLES} random points, "
                f"+/-{symdiff_sigma:.2f} % (1 sigma)"
            )
        else:
            symdiff = max(0.0, 100.0 * (solid_volume(ref) + model_volume - 2.0 * common) / ref_volume)
    except FileNotFoundError:
        symdiff_note = "reference cache missing"

    ok = bbox_delta <= BBOX_TOL and abs(volume_delta) <= VOLUME_TOL
    if symdiff is None:
        status = "pass (bbox/volume only)" if ok else "approximate"
    else:
        # A sampled estimate only passes if it is below the limit by 2 sigma.
        status = "pass" if ok and symdiff + 2.0 * symdiff_sigma < SYMDIFF_TOL else "approximate"
    return {
        "part": part_number,
        "module": f"src/longshot/parts/{part_modules.module_name(part_number)}.py",
        "bbox_delta_mm": round(bbox_delta, 3),
        "volume_ref_mm3": round(ref_volume, 1),
        "volume_model_mm3": round(model_volume, 1),
        "volume_delta_pct": round(volume_delta, 3),
        "symdiff_pct": None if symdiff is None else round(symdiff, 3),
        "symdiff_note": symdiff_note,
        "status": status,
        "note": getattr(module, "VALIDATION_NOTE", "").strip(),
        "build_seconds": round(build_s, 1),
    }


def fmt(value, suffix="") -> str:
    return "n/a" if value is None else f"{value:.2f}{suffix}"


def write_markdown(results: dict) -> None:
    lines = [
        "# Part validation results",
        "",
        "Generated by `tools/validate_parts.py`. Each parametric part is compared with the",
        "matching solid from Julius's Fusion export `Longshot_Main_Assembly.step`.",
        f"Pass criteria: bbox delta <= {BBOX_TOL} mm, volume delta within +/-{VOLUME_TOL} %,",
        f"symmetric difference < {SYMDIFF_TOL} % of the reference volume.",
        "",
        "| Part number | bbox delta (mm) | Volume ref (mm³) | Volume delta | Sym. diff | Status | Notes |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for part in part_modules.PART_NUMBERS:
        r = results.get(part)
        if not r:
            lines.append(f"| `{part}` | | | | | not run | |")
            continue
        note = r["note"] or ""
        if r["symdiff_note"]:
            note = f"{note} ({r['symdiff_note']})".strip()
        lines.append(
            f"| [`{part}`](../{r['module']}) | {r['bbox_delta_mm']:.3f} | {r['volume_ref_mm3']:.0f} | "
            f"{r['volume_delta_pct']:+.2f} % | {fmt(r['symdiff_pct'], ' %')} | {r['status']} | "
            f"{note.replace('|', '/')} |"
        )
    RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("parts", nargs="*", help="part numbers to validate (default: all)")
    args = parser.parse_args()

    VALIDATION_DIR.mkdir(exist_ok=True)
    results = json.loads(RESULTS_JSON.read_text()) if RESULTS_JSON.exists() else {}
    for part in args.parts or part_modules.PART_NUMBERS:
        try:
            r = validate(part)
        except ModuleNotFoundError as exc:
            print(f"{part:45s} no module yet ({exc.name})")
            continue
        results[part] = r
        print(
            f"{part:45s} bbox {r['bbox_delta_mm']:7.3f} mm  vol {r['volume_delta_pct']:+7.3f} %  "
            f"symdiff {fmt(r['symdiff_pct'], ' %'):>9s}  {r['status']}",
            flush=True,
        )
    ordered = {p: results[p] for p in part_modules.PART_NUMBERS if p in results}
    RESULTS_JSON.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
    write_markdown(ordered)


if __name__ == "__main__":
    main()
