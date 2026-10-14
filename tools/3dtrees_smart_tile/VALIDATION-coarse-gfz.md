# Simplified Filter / merge and coarse GFZ validation

Validated locally on 2026-10-14 with **2.4.0+galaxy4**.
The existing image remained `sha256:cc3e4b7245a480a78c4f06daf1494db5fba7b2d636e7e4e5cee9c47a48534a2e`; no image rebuild or publication occurred.
All 56 executable Python source files matched that image.

## Current wrapper

Filter / merge accepts segmented tiles with their voxel size and optional
high-resolution targets with their voxel size. Advanced ownership, reconciliation
and small-cluster controls are collapsed. It returns processed tiles and the
applicable RayCloudTools tables/meshes. Original enrichment and merged products
belong to Remap and Create merged file. Both tasks retain their previous behavior.

With targets, prediction transfer uses exactly the segmented voxel diagonal.
Without targets, the existing merge route filters the segmented geometry directly.
The recorded processed resolution follows the supplied geometry. IDs are always
independent within each input tile. Inputs must come from one SmartTile run and
segmentation must preserve coordinates; the wrapper does not automatically verify
that provenance contract.

## Completed checks

- Seven live Galaxy cases passed: indices **4, 5, 6, 8, 14, 22, 23**. They cover
  standard and RCT filtering with/without targets, optional small-cluster
  reassignment and multiple original attribute versions.
- **22** native command, staging, radius and output-filter cases passed. Ten
  Remap/Create cases had identical arguments, manifests and selected outputs
  before and after this wrapper change.
- Live form API checks verified four tasks, grouped resolutions, optional targets,
  collapsed Advanced controls and removal of merge's original/product controls.
  Planemo lint and diff whitespace checks passed.
- The actual Galaxy collection API smoke submitted **two list collections** to
  Create merged file and produced one job. Its **11,147 points**, coordinates,
  record order, source attributes, CRS and OriginalPointIndex passed exact checks.

The corrected tests 5 and 8 and the actual collection smoke close the execution
checks left pending in the historical
[optional-target record](VALIDATION-optional-targets.md). That record remains
unchanged as evidence of the earlier attempt.

## Reused GFZ segmentation results

Coarse-only filtering used existing SegmentAnyTree and ForestMamba predictions.
Each input collection contained **8,280,988 points**. SAT produced **2,479,599**
points with **102** final instance IDs; ForestMamba produced **2,479,643** points
with **114** final instance IDs. Independent checks confirmed source coordinates
and attributes were retained, each positive final ID belonged to one output tile,
and every positive core input sample retained positive output support within
**1 cm**, with zero unsupported samples.

The scientific run and boundary checks are documented in the SmartTile source
repository at `docs/validation/2026-10-14-coarse-gfz.md`. These checks establish
record provenance, coverage and ownership; the real GFZ predictions do not supply
independent biological tree ground truth or prove coarse-only and dense-first
results equivalent.

Machine-readable summary: [VALIDATION-coarse-gfz.json](VALIDATION-coarse-gfz.json).
Local artifacts: `/tmp/smarttile-coarse-gfz-20261014/wrapper` and
`/tmp/smarttile-coarse-gfz-20261014/collection-api/evidence.json`.
This evidence does not certify a published image or production rollout.
