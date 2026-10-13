# SmartTile 2.4 Galaxy wrapper

Candidate wrapper **2.4.0+galaxy1**, profile 24.2. It wraps the combined
SmartTile 2.4 CLI and keeps the existing tool ID `3dtrees_smart_tile`.
This checkout does not publish an image, install a ToolShed revision or update
production workflows. The declared `2.4.0` image must be built from the accepted
source and pinned with the coordinated release before deployment.

## Workflow mapping

| Workflow | Galaxy settings |
| --- | --- |
| Original → tiles → segmentation → merge → species → remap → visualization | Spatial tiling with coarse model inputs and fine targets; Filter/Merge with the matching tile bounds; Remap each final model collection to originals. |
| Labeled original → tiles → species → remap → visualization | Whole-instance tiling, the existing instance field and one resolution; same-instance Remap at that resolution. Whole-instance tiles already have unique ownership. |
| Already-dense buffered predictions → filter → species → remap | Filter with their tile bounds and instance field. Reconciliation is enabled by default and can be disabled for global identities. |
| Several segmentation attribute views → merged COPC → ForestStructure | Create prod-merged file; add each version of the same originals separately; choose full resolution, COPC and source-order indexing. |

Whole-instance mode produces one LAZ collection per run. The chosen instance
field is mandatory in every output, including values above 65535; additional
attributes are optional. Ordinary spatial outputs contain geometry for inference.
Use the CLI for multiple instance dimensions or resolutions in one invocation.

Standalone Filter accepts dense point predictions. Use the model-specific
Filter/Merge path for RayCloudTools, including its required tree tables and
optional meshes. Merge products require original files. Remap requires complete
coverage for non-RCT models; same-instance mode preserves original tree IDs.
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

```bash
python -m pytest -q tools/3dtrees_smart_tile/test_stage_inputs.py
planemo lint tools/3dtrees_smart_tile/smart_tile.xml
planemo shed_lint --tools tools/3dtrees_smart_tile
planemo test --docker tools/3dtrees_smart_tile/smart_tile.xml
```

For local candidate testing, configure an isolated Galaxy destination with the
exact candidate image ID. Never replace the published image tag with a local
candidate or run this suite against production Galaxy. The functional matrix
contains 18 cases across all five tasks, including RCT companions, additional
attribute versions, whole-instance tiles, same-instance species remap with default/custom ID names and
full-resolution COPC/PLY. See [fixtures](test-data/README.md) and the final
validation record alongside this README.

Workflow parameter names have changed since the 2.3 wrapper. Rebind every
affected production step and verify its formats on staging. A local test pass
does not certify the published release image, visualization canary, or the
coordinated RayCloudTools rollout.

References: [Galaxy XML schema](https://docs.galaxyproject.org/en/latest/dev/schema.html),
[IUC wrapper conventions](https://galaxy-iuc-standards.readthedocs.io/en/latest/best_practices/tool_xml.html).
