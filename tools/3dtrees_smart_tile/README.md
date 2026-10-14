# SmartTile 2.4 Galaxy wrapper

Wrapper `2.4.0+galaxy0` (profile 24.2, tool ID `3dtrees_smart_tile`) for
[SmartTile](https://github.com/3dTrees-earth/3dtrees_Smart_Tile). It runs
`python /src/run.py` in `ghcr.io/3dtrees-earth/3dtrees_smart_tile:2.4.0`.
Publish and verify that image before installing this revision.

## Tasks

| Task | Use it for |
| --- | --- |
| Tile and subsample | Buffered spatial tiles, or whole-instance tiles that keep each tree of an existing ID field in one tile. Up to six **Output** entries, each a voxel size or Original resolution, as LAZ, COPC LAZ or binary PLY. |
| Filter / merge segmented tiles | Resolve buffer overlaps between segmented tiles of one tiling run, using its tile bounds JSON. With optional high-resolution tiles, predictions are first transferred onto that geometry (radius √3 × segmented voxel size). RayCloudTools needs both tree tables per tile; QSM meshes are optional. |
| Remap predictions to originals | Copy prediction attributes from one or more model collections, or one merged file, onto the original files. Can also write merged products. |
| Create merged file | Join several attribute versions of the same originals into one subsampled or full-resolution LAZ, COPC LAZ or PLY product. |

Typical chains:

1. Original → Tile (1 cm and 10 cm) → segmentation → Filter / merge → species → Remap.
2. Original with tree IDs → whole-instance Tile → species → same-instance Remap.
3. Several prediction versions of the same originals → Create merged file
   (full resolution, COPC LAZ, OriginalPointIndex) → ForestStructure.

## Outputs

- Spatial tiles and the first instance dimension: `output_subsampled_res1` …
  `output_subsampled_res6`, in Output entry order. Further instance dimensions:
  `output_instance_dim2_res1` … `output_instance_dim6_res6`.
- Filter / merge: `output_merge_tiles`, plus `output_tree_files` and
  `output_tree_meshes` for RayCloudTools.
- Remap: `output_originals_with_dims` in the input encoding, plus per-original
  RayCloudTools tables and meshes when a RayCloudTools collection is supplied.
- Products: `prod_merged_outputs` (LAZ/COPC, returned as `laz`) and
  `prod_merged_ply_outputs`.

Full-resolution products add `OriginalPointIndex` as the first ExtraByte
(uint64 in LAZ/COPC, uint32 in PLY, which fails on overflow). PLY cannot carry
LAS missing-value declarations; use COPC for ForestStructure.

## Migrating from 2.3

Parameter paths changed: segmented inputs are under `operation.segmented`,
high-resolution targets under `operation.targets`, ownership and reconciliation
under `operation.advanced`, and Create merged file uses the repeat
`operation.original_collections`. Whole-instance workflows must rebind the former
`output_instance_tiles` output. Rebind and re-test every production workflow step
on a non-production Galaxy before switching.

## Staging and resources

The tool writes dataset paths, names and datatypes to a JSON manifest.
`stage_inputs.py` checks the whole manifest, then symlinks each dataset into the
job directory under its Galaxy name with one extension taken from its datatype.
Duplicate names, path separators and control characters fail before any link is
created. Inputs are never modified.

`--workers` follows `GALAXY_SLOTS`. Memory and scratch disk are set by the Galaxy
destination; dense areas can exceed the tiler's point target.

## Testing

```bash
python -m pytest -q tools/3dtrees_smart_tile/test_stage_inputs.py
planemo lint tools/3dtrees_smart_tile/smart_tile.xml
planemo shed_lint --tools tools/3dtrees_smart_tile
planemo test --docker tools/3dtrees_smart_tile/smart_tile.xml
```

Run functional tests on a local or staging Galaxy only. The fixtures are
described in [test-data/README.md](test-data/README.md).
