#!/usr/bin/env python3
"""Render a PNG preview of the rebuilt Longshot main assembly (VTK, off-screen).

Every placed body is tessellated once per part and coloured by BOM category.

Usage::

    python tools/render_preview.py [output.png] [--hide-covers]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import vtk
from build123d import Compound
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from longshot import catalog  # noqa: E402
from longshot.assembly import part_shape  # noqa: E402
from longshot.reference import BUILD123D_DIR, matrix_to_location, placements  # noqa: E402

COLOURS = {
    catalog.CELL: (0.20, 0.45, 0.80),
    catalog.BUSBAR: (0.85, 0.50, 0.25),
    catalog.CUSTOM: (0.80, 0.80, 0.78),
    catalog.PCB: (0.15, 0.55, 0.30),
    catalog.COTS: (0.25, 0.25, 0.28),
}
COVERS = ("EN-PRINT-002", "EN-PC-001", "EN-SHEET-00")


def to_polydata(shape, tolerance: float) -> vtk.vtkPolyData:
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()
    BRepMesh_IncrementalMesh(shape.wrapped, tolerance, False, 0.3, True)
    explorer = TopExp_Explorer(shape.wrapped, TopAbs_FACE)
    offset = 0
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        explorer.Next()
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            points.InsertNextPoint(p.X(), p.Y(), p.Z())
        reverse = face.Orientation() == TopAbs_REVERSED
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            if reverse:
                b, c = c, b
            polys.InsertNextCell(3)
            for n in (a, b, c):
                polys.InsertCellPoint(offset + n - 1)
        offset += tri.NbNodes()
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(polys)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.SetFeatureAngle(40)
    normals.Update()
    return normals.GetOutput()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output", nargs="?", type=Path, default=BUILD123D_DIR / "docs" / "preview.png")
    parser.add_argument("--hide-covers", action="store_true", help="hide top cover, top plate and side sheets")
    parser.add_argument("--size", default="1600x1200")
    args = parser.parse_args()

    meta = placements()
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)
    cache: dict[str, vtk.vtkPolyData | None] = {}
    for item in meta["items"]:
        key = item["part"]
        if args.hide_covers and key.startswith(COVERS):
            continue
        if key not in cache:
            shape = part_shape(key)
            if shape is None:
                cache[key] = None
            else:
                tol = 0.3 if meta["parts"][key]["kind"] == "custom" else 0.1
                cache[key] = to_polydata(shape if not shape.children else Compound(shape.solids()), tol)
        poly = cache[key]
        if poly is None:
            continue
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*COLOURS[catalog.LINES[catalog.bom_line(key)]["category"]])
        m = vtk.vtkMatrix4x4()
        loc = item["location"]
        for r in range(4):
            for c in range(4):
                m.SetElement(r, c, loc[r][c])
        actor.SetUserMatrix(m)
        renderer.AddActor(actor)

    width, height = (int(v) for v in args.size.split("x"))
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.AddRenderer(renderer)
    window.SetSize(width, height)
    camera = renderer.GetActiveCamera()
    camera.SetViewUp(0, 0, 1)
    camera.SetPosition(1, -1.2, 0.8)
    camera.SetFocalPoint(0, 0, 0)
    renderer.ResetCamera()
    camera.Zoom(1.3)
    light = vtk.vtkLight()
    light.SetLightTypeToCameraLight()
    renderer.AddLight(light)
    window.Render()

    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(window)
    grab.Update()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(args.output))
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()
    crop_to_content(args.output)
    print(f"wrote {args.output}")


def crop_to_content(path: Path, margin: int = 30) -> None:
    """Trim the white border around the rendered model."""
    img = Image.open(path).convert("RGB")
    bbox = ImageOps.invert(img).getbbox()
    if bbox:
        left, top, right, bottom = bbox
        img = img.crop(
            (max(left - margin, 0), max(top - margin, 0), min(right + margin, img.width), min(bottom + margin, img.height))
        )
    img.save(path, optimize=True)


if __name__ == "__main__":
    main()
