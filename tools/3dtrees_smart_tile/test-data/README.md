# SmartTile wrapper fixtures

The existing `mikro*` fixtures and RCT tables/meshes exercise spatial tiling,
prediction transfer, collection remap, product exports and attribute joins.
`fm_version/mikro_segmented` is another attribute view of the same original.

The 2.4 final-review fixtures are synthetic and contain no private dataset:

- `original_with_ids.laz`: 20 points in EPSG:32632; alternating instance IDs
  7 and 70000; `Amplitude` uses the declared missing sentinel -1.
- `c00_r00.laz`: the same points, named for the dense filter's tile layout.
- `dense_tile_bounds.json`: one 10 m core containing those points.
- `species.laz`: corresponding predictions shifted 8 mm in X, with species
  10 for instance 7 and 20 for instance 70000.

The synthetic cases cover required ID retention, high IDs, same-instance
attribute transfer, missing-value declarations through LAZ/COPC, source-order
index creation and the uint32 PLY declaration. Binary outputs are checked using
stable headers, collection identities and the SmartTile scientific test suite;
timestamps and compressed bytes are not reference expectations.

`generate_small_fixtures.py` regenerates the four synthetic files using laspy,
NumPy and pyproj from the SmartTile runtime. Run it with the destination directory
as its argument. Existing GFZ acceptance and ForestStructure consumer evidence
live in the SmartTile repository and are distinct from these small wrapper tests.

`custom_original.laz` and `custom_species.laz` are separate 20-point fixtures
with the same geometry and values, but use the custom instance field
`CustomTreeId`. `generate_custom_instance_fixtures.py` creates only these two
files and refuses to overwrite them; the earlier four fixtures stay unchanged.
The custom-field remap test verifies CLI selection and output fields. Its
alternating IDs and 8 mm prediction shift also make an unrestricted nearest
query borrow species from the wrong tree. Expected values are species 10 for
ID 7 and species 20 for ID 70000. The generator copies CRS declarations from
`original_with_ids.laz` beside it (or the optional second argument).

`species_original.laz` keeps all 20 coordinates and source fields from
`original_with_ids.laz`, including the `Amplitude = -1` missing-value declaration,
and adds the species values from `species.laz`. The earlier `species.laz` remains
deliberately shifted by 8 mm for sampled nearest-point tests; it is not an
original-resolution prediction fixture. The aligned fixture exercises original
COPC whole-instance output followed by same-instance remap to originals.

`generate_original_species_fixture.py DESTINATION [FIXTURE_DIRECTORY]` creates
only `species_original.laz` and refuses to overwrite it. Run it inside the
SmartTile scientific runtime, where laspy, NumPy and the canonical
`point_cloud_metadata` helper are available (`PYTHONPATH=/src` in the image).
The optional fixture directory defaults to the directory containing the script.

`two_instance_dimensions.laz` keeps all coordinates, `PredInstance_SAT` values
and `Amplitude` values/metadata from `original_with_ids.laz`. It adds
`PredInstance_FM`: ID 11 for the first ten points and ID 22 for the last ten.
This deliberately differs from SAT's alternating IDs 7 and 70000.

For a multi-dimension example, select whole-instance tiling, enter
`PredInstance_SAT,PredInstance_FM` in **Instance dimensions**, retain `Amplitude`,
and request original COPC plus 10 cm LAZ. The expected result is four separate
collections: one for each dimension/resolution pair. Each original collection
contains all 20 points; each output carries its own instance field and
`Amplitude`, including the declaration that -1 means missing.

`generate_two_instance_fixture.py DESTINATION [FIXTURE_DIRECTORY]` creates only
this fixture and refuses to overwrite it. Run with the SmartTile scientific
runtime and `PYTHONPATH=/src` (or point `PYTHONPATH` at the source checkout's
`src` directory). The optional fixture directory defaults to the script's
directory. Existing fixtures remain unchanged.
