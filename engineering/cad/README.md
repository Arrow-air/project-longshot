# CAD

Longshot CAD work lives here.

## Folders

- `build123d/` — Python/build123d parametric CAD source. It holds the Longshot main assembly model, its BOM, and the commands to rebuild them; see [`build123d/README.md`](build123d/README.md).
- `reference/` — imported vendor, measurement, or reference geometry.
- `build123d/exports/` — generated STEP/STL outputs for review, manufacturing, or downstream CAD use.

Generated exports should be reproducible from the source where practical. If an export is hand-edited or comes from another CAD package, document that in the nearest README.
