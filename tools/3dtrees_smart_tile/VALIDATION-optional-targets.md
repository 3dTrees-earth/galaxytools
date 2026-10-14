# Optional transfer targets and repeatable original collections

Updated locally on 2026-10-14 with the active `2.4.0+galaxy4` wrapper.
The image remained `sha256:cc3e4b7245a480a78c4f06daf1494db5fba7b2d636e7e4e5cee9c47a48534a2e`; no executable-source or image changes were made.

## Behavior

Filter / merge accepts segmented tiles and optional high-resolution target tiles.
With targets, the transfer radius is sqrt(3) × segmented voxel size; 10 cm gives
about 17.32 cm. Without targets, `--segmented-remapped-folder` invokes the existing
ready-data merge route and skips prediction transfer. RCT companions,
reconciliation, recovery, optional originals and merged products remain available.

Optional original outputs use target voxel size when targets are supplied and
segmented voxel size otherwise. The target spacing is also recorded in merge
metadata. Remap's **Resolution of supplied predictions** refers to current prediction
spacing and controls matching distance; it does not resample the original output.
Original-resolution matching is supported by the standalone Remap task.

**Create merged file** uses one repeatable **Original collection** input. Entries
are attribute versions of the same originals (for example SAT then ForestMamba),
with matching filenames/point order and equal shared fields. Different original
files belong together within an entry.

## Completed checks

- Six targeted live Galaxy cases passed: transfer with originals/products,
  RCT with/without targets, direct filtering, originals/products without targets,
  and a single original entry (indices 4, 6, 7, 14, 22, 23).
- 19 native command/manifest/output-filter cases passed, including 10/20 cm radius
  calculations, all target/original/RCT combinations, and one/two/three original entries.
- Missing-original rejection, live form API checks, Planemo lint, diff whitespace
  checks and independent implementation review passed. The render record's hash
  matches the final XML. Earlier scientific-source tests were not rerun for this XML update.

## Pending execution checks

The initial eight-case run included two test-definition problems: an overly exact
textual float assertion (index 5, with the scientific job itself successful), and
embedded collection syntax unsupported for a multiple-data input (index 8).
Both definitions were corrected. Their rerun then blocked before SmartTile started:
the shared host was unable to launch Docker/runc processes. Galaxy remained responsive,
but the local one-worker runner could not progress. The test client was stopped.

A separate actual two-list-collection API smoke was prepared to check one merge job,
point inventory, all attributes, CRS and OriginalPointIndex. Its upload queued behind
the blocked runner; this execution remains pending. No passing result is claimed.
Rerun indices 5 and 8 and the collection API smoke when the local host recovers.
Original failure reports and retry scripts are preserved alongside passing evidence.

Artifacts: `/tmp/smarttile-optional-targets-20261014`.
The separate pre-existing voxel-boundary sampling limitation remains unchanged.
Workflow bindings must reflect the flattened merge inputs, optional
`operation.original_outputs` section and `operation.original_collections` repeat.
This is local wrapper evidence, not production rollout validation.
