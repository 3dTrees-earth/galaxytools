# SmartTile v2.4 wrapper PR validation

Validated locally on 2026-10-15. Wrapper `2.4.0+galaxy4` targets the engine merged
in [SmartTile PR #3](https://github.com/3dTrees-earth/3dtrees_Smart_Tile/pull/3),
main commit `b2b84466158c528b75dffcbdfa4c04488261c06d`.

## Current checks

- 44 input-staging tests passed.
- Planemo XML/schema lint and ToolShed lint passed.
- Repository Flake8 checks passed. Import ordering and whitespace corrections
  preserve every script's import inventory and non-import AST; fixtures are unchanged.
- **All 24 live local Galaxy functional cases passed**, zero errors, failures
  or skips, against the immutable image below. They cover all four tasks,
  optional fine targets, RayCloudTools companions, whole-instance and
  multiple-dimension outputs, original-resolution remap and all output formats.
- Independent code review found no blocking wrapper defects. All 24 functional
  cases reference present test fixtures; no individual fixture exceeds 1 MB.

The engine's complete suite passed **1,016 tests and 94 subtests**, with zero
failures, errors or skips. All 57 embedded Python source files match accepted
source. The immutable image was reused without rebuilding it for this PR:
`sha256:41cd03e0f991669efdac8b0128ed53fc31fdae0f9f56528c48526b207ccbf018`.

The independent live Galaxy numeric replay passed on this wrapper and image:
four separate output collections, **4 SAT / 2 ForestMamba representatives at
10 cm**, and all **20 original points per instance dimension**. IDs, source
attributes, CRS and missing-value declarations were preserved. This closes the
voxel-boundary failure in the historical multiple-dimension record. See the
[engine evidence](https://github.com/3dTrees-earth/3dtrees_Smart_Tile/blob/b2b84466158c528b75dffcbdfa4c04488261c06d/docs/validation/2026-10-14-voxel-boundaries.md).

## Release dependency

The XML declares `ghcr.io/3dtrees-earth/3dtrees_smart_tile:2.4.0`. A registry read
on 2026-10-15 returned `manifest unknown`. The local Galaxy destination explicitly
overrides that reference with the candidate image above. Publish and verify the
accepted release image before merging/publishing this wrapper; this PR stays draft
while that dependency is open. Hosted functional tests cannot resolve the missing tag.

The coordinated SmartTile/RayCloudTools release still needs pinned image and wrapper
identities, updated workflow bindings, its end-to-end staging/visualization canary
and production verification under 3DT-1903. This PR does not deploy production.
Historical GFZ records are preserved; no fresh model inference is claimed here.

## Reproduction

```bash
python -m pytest -q tools/3dtrees_smart_tile/test_stage_inputs.py
flake8 tools/3dtrees_smart_tile
planemo lint tools/3dtrees_smart_tile/smart_tile.xml
planemo shed_lint --tools tools/3dtrees_smart_tile
```

For functional tests, use `planemo test` against an isolated local Galaxy with
an explicit candidate-image override. The standard published-image path becomes
usable once the declared release tag exists. Do not run against production Galaxy.
Local reports are under `/tmp/smarttile-wrapper-pr-20261015`; the accompanying
JSON records the wrapper/image identities and final check summary.
