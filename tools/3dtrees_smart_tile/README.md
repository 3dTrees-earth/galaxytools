# SmartTile 2.4 Galaxy wrapper

Candidate wrapper **2.4.0+galaxy4**, profile 24.2. It wraps the combined
SmartTile 2.4 CLI and keeps the existing tool ID `3dtrees_smart_tile`.
This checkout does not publish an image, install a ToolShed revision or update
production workflows. The declared `2.4.0` image must be built from the accepted
source and pinned with the coordinated release before deployment.

## Workflow mapping

| Workflow | Galaxy settings |
| --- | --- |
| Original → tiles → segmentation → merge → species → remap → visualization | Spatial tiling with coarse model inputs and fine targets; Filter/Merge with the matching tile bounds; Remap each final model collection to originals. |
| Labeled original → tiles → species → remap → visualization | Whole-instance tiling, the existing instance field and shared Output selections; same-instance Remap using the matching subsampled or original resolution. Whole-instance tiles already have unique ownership. |
| Already-dense buffered predictions → filter → species → remap | Filter / merge segmented tiles with High-resolution tiles left empty, plus their tile bounds and instance field. IDs are independent within each tile; cross-tile reconciliation is enabled by default. |
| Several segmentation attribute views → merged COPC → ForestStructure | Create merged file; add each version of the same originals as an Original collection; choose full resolution, COPC and source-order indexing. |

Both tiling modes use the same repeatable **Output** controls. Each entry selects
Subsampled (a voxel size) or Original resolution, plus LAZ, COPC LAZ or binary PLY.
Spatial outputs and the first instance dimension use `output_subsampled_res1` …
`output_subsampled_res6` in entry order. Further instance dimensions use
`output_instance_dim2_res1`, …, `output_instance_dim6_res6`. Whole-instance
workflows must rebind the former `output_instance_tiles` output.
Each resolution can occur once. Original resolution retains every point,
including duplicate coordinates; compatible source coordinate grids are preserved.

Whole-instance tiling accepts up to six comma-separated **Instance dimensions**,
for example `PredInstance_SAT,PredInstance_FM`. Two dimensions with Original
resolution and 10 cm produce four separate list collections, ordered by dimension
then Output entry. Each collection carries its own instance field; additional
attributes are optional. Ordinary spatial outputs contain geometry for inference.

All output-format selectors use the same options, in order: LAZ, COPC LAZ,
PLY (binary). Spatial tiles default to LAZ; merged products default to COPC LAZ.
Filtered prediction tiles remain LAZ, and enriched originals retain their input
LAS/LAZ encoding. Whole-instance PLY preserves scalar attributes and checks integer
values fit its 32-bit types; use LAZ/COPC for wider values or LAS metadata.

The four tasks are Tile and subsample, Filter / merge segmented tiles, Remap
predictions to originals, and Create merged file. Filter / merge accepts segmented
tiles and optional high-resolution targets. With targets, it transfers predictions
using a radius calculated as sqrt(3) × segmented input voxel size (10 cm → 17.32 cm).
Without targets, it skips prediction transfer and filters the supplied geometry.
Both use the merge backend and return `output_merge_tiles`, including RayCloudTools
with its required tree tables and optional meshes. The input-mode selector is removed.

Filter / merge returns only processed tiles and the required RayCloudTools
companions. Use Remap to enrich originals and Create merged file for combined
products. Segmented inputs must come from the same SmartTile run, and segmentation
must preserve their coordinates. IDs are always treated as independent within each
tile; disabling reconciliation keeps instances from different tiles separate.

Segmented files and their voxel size are grouped under `operation.segmented`.
Optional high-resolution targets and their voxel size are grouped under
`operation.targets`. Ownership, reconciliation and small-cluster reassignment
are under the collapsed `operation.advanced` section. Model and tile bounds remain
at `operation.*`. The target voxel size is recorded as the processed resolution
when targets are present; otherwise the segmented voxel size is used. Existing
candidate workflow bindings need updating.

In Remap, **Resolution of supplied predictions** means the current spacing of the
prediction files: for example 1 cm after transfer onto 1 cm geometry, or 10 cm when
using direct 10 cm predictions. It controls matching distance, not output density.
**Original resolution** matches retained source-point predictions within LAS
coordinate precision; every original point still requires a match. Remapped
outputs retain the original points. Same-instance mode preserves original tree IDs.

**Create merged file** has repeatable **Original collection** entries. Each accepts
a list collection or selected files. For example, add originals with SAT predictions
first and the same originals with ForestMamba predictions second. Names and point
order must match across entries, and shared attributes must agree. The prediction
attributes are combined before writing the chosen output formats. The uniform
repeat is `operation.original_collections`; it replaces the primary/further-version
split. Different original files belong together within one entry.

For a custom ID field such as `CustomTreeId`, select that same Instance dimension
in whole-instance tiling and Remap. The remap default `PredInstance` retains
automatic recognition of `PredInstance*` and `treeID`. A custom name applies to
all collections in the run; use separate runs for different custom names.

Full-resolution LAZ/COPC writes `OriginalPointIndex` as uint64. Full-resolution
PLY writes uint32 and fails on overflow; disabling generation retains an
existing field. LAZ/COPC preserve compatible missing-value declarations. PLY
cannot represent LAS missing-value metadata and is not the ForestStructure
handoff. Joining attribute views requires matching names, coordinates, point
order and equal values for shared fields.

## Staging and resources

`smart_tile.xml` serializes dataset paths, names and types into JSON.
`stage_inputs.py` preflights that manifest and creates job-local symlinks without
shell interpolation. It normalizes a single physical extension, preserves COPC
and RCT companion names, and rejects duplicate names, traversal, control
characters and directory symlink escapes. Input files are never modified.

Only `--workers` is passed from `GALAXY_SLOTS` (fallback one worker); SmartTile
also respects CPU affinity and cgroup quotas. Job memory remains owned by the
Galaxy destination/container. Dense-cell point targets are not hard RAM bounds.
Operational reports remain in the job working directory rather than becoming
additional workflow output dependencies.

## Validation

All **24 current Galaxy functional cases** and **44 staging tests** pass,
alongside XML/schema lint, ToolShed lint and Python lint.
The latest PR validation uses the corrected image from merged
[SmartTile PR #3](https://github.com/3dTrees-earth/3dtrees_Smart_Tile/pull/3).
See [the current validation record](VALIDATION-v24-pr.md) for wrapper checks,
the corrected multiple-dimension voxel result and the unpublished image gate.
The dated records below preserve the earlier candidates and their results.

```bash
python -m pytest -q tools/3dtrees_smart_tile/test_stage_inputs.py
planemo lint tools/3dtrees_smart_tile/smart_tile.xml
planemo shed_lint --tools tools/3dtrees_smart_tile
planemo test --docker tools/3dtrees_smart_tile/smart_tile.xml
```

For local candidate testing, configure an isolated Galaxy destination with the
exact candidate image ID. Never replace the published image tag with a local
candidate or run this suite against production Galaxy. The frozen prior functional matrix
contains 18 cases across all five tasks, including RCT companions, additional
attribute versions, whole-instance tiles, same-instance species remap with
default/custom ID names and full-resolution COPC/PLY. All 18 cases pass against
the frozen `2.4.0+galaxy1` candidate, alongside 44 staging tests, 13 render variants and
nine independent numeric checks. See
[fixtures](test-data/README.md) and the final [validation record](VALIDATION.md).

The `+galaxy3` revision shares tile output controls, adds original-resolution
tiling/remapping, and supports whole-instance LAZ/COPC/PLY selections. All 21
Galaxy cases for that revision and the linked original-COPC → same-instance remap pass.
The source suite passes 553 tests; GFZ SAT/FM original-resolution round trips
retain 867,599 points per model with no species or probability mismatches.
See the [original-resolution validation record](VALIDATION-original-resolution.md); the
frozen `+galaxy1` release-candidate results remain separate.

The current `+galaxy4` multiple-dimension checks are recorded separately in
[the multiple-dimension validation record](VALIDATION-multiple-dimensions.md).

The previous unified Filter / merge revision passed four affected live Galaxy
cases and ten command/staging/output-filter variants. Its frozen record remains
[available here](VALIDATION-unified-filter-merge.md).

The simplified Filter / merge form passes **seven live Galaxy cases**, **22 native
command/staging/output-filter cases**, lint and live form checks. Ten Remap/Create
cases preserve their previous behavior exactly. The corrected tests 5 and 8 and
the actual two-list-collection API smoke now pass, closing the earlier host-related
execution gap. The collection smoke preserves all 11,147 points, attributes, CRS,
record order and OriginalPointIndex in one merge job.

Coarse-only GFZ SAT and ForestMamba checks each used 8,280,988 input points and
passed source-record, positive-core coverage and unique-ownership checks. The
existing image is unchanged. See the [current validation record](VALIDATION-coarse-gfz.md).
The [optional-target record](VALIDATION-optional-targets.md) remains historical;
its pending checks have been completed in the current record.

Workflow parameter names have changed since the 2.3 wrapper. Rebind every
affected production step and verify its formats on staging. A local test pass
does not certify the published release image, visualization canary, or the
coordinated RayCloudTools rollout.

References: [Galaxy XML schema](https://docs.galaxyproject.org/en/latest/dev/schema.html),
[IUC wrapper conventions](https://galaxy-iuc-standards.readthedocs.io/en/latest/best_practices/tool_xml.html).
