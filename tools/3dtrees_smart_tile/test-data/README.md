# SmartTile wrapper fixtures

All fixtures are small; the synthetic ones contain no private data.

| Fixture | Content |
| --- | --- |
| `mikro*`, `fm_version/mikro_segmented` | Real sample tile and its subsampled, segmented and merged views (two model versions). |
| `c00_r00_*` | RayCloudTools tree tables and QSM meshes before and after filtering. |
| `rct_merged_tile_00000` | A merged RayCloudTools prediction tile. |
| `tile_bounds_tindex.json` | Tile layout for the `mikro` merge tests. |
| `original_with_ids.laz` | 20 points, EPSG:32632, alternating IDs 7 and 70000, `Amplitude` with missing value -1. |
| `c00_r00.laz`, `dense_tile_bounds.json` | The same points as one dense tile inside a 10 m core. |
| `species.laz` | Species predictions shifted 8 mm in X (10 for ID 7, 20 for ID 70000), for nearest-point remap. |
| `species_original.laz` | The original points with species added, unshifted, for original-resolution remap. |
| `custom_original.laz`, `custom_species.laz` | As above with the custom ID field `CustomTreeId`. |
| `two_instance_dimensions.laz` | Adds `PredInstance_FM` (11 and 22) beside `PredInstance_SAT`. |

The `generate_*.py` scripts recreate the synthetic files; all but
`generate_small_fixtures.py` refuse to overwrite existing ones. Run them in the
SmartTile image (`PYTHONPATH=/src`) with the destination directory as the first
argument.
