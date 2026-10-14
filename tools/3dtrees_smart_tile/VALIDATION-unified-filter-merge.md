# Unified Filter / merge task — local validation

Wrapper-only update to the active `2.4.0+galaxy4` candidate on 2026-10-14.
The executable image was unchanged: `sha256:cc3e4b7245a480a78c4f06daf1494db5fba7b2d636e7e4e5cee9c47a48534a2e`.

Galaxy exposes four tasks. **Filter / merge segmented tiles** has two input modes:

- **Segmented tiles + high-resolution tiles** transfers predictions using the existing merge command.
- **Already high-resolution segmented tiles** filters the existing dense predictions directly.

Both expose `output_merge_tiles`, with shared bounds, ownership and reconciliation
controls. The standalone Filter option and `output_filtered_tiles` port are removed.
Merge-specific inputs now live under `operation.input_mode`; existing workflow
steps must rebind those fields. The input mode defaults to prediction transfer.
RayCloudTools tables and meshes remain in that mode. The spatial tiling label is
**Buffered spatial tiles for downstream processing**.

Validation passed: four affected live Galaxy tests (indices 4, 5, 6, 14), covering
merge products, disabled reconciliation, RayCloudTools companions and dense filtering;
10 native command/staging/output-filter variants; missing-original rejection;
Planemo lint; live API verification of the four task options; independent review.
No scientific-source changes or image rebuild were made for this UI update.

Artifacts: `/tmp/smarttile-unified-filter-merge-20261014`.
The earlier multi-dimension sampling-boundary limitation remains documented in
`VALIDATION-multiple-dimensions.md`; this UI validation does not resolve it.
