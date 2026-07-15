3Dtrees: CSP StandSegmentation
==============================

Galaxy wrapper for DTM generation, repeatable multi-segmentation forest
inventory, and optional Comparative Shortest Path tree segmentation.

The wrapper copies Galaxy's extensionless internal dataset to ``input.laz``,
the same pattern used by ``3dtrees_standardization/standard.xml``. This adds
temporary disk I/O and storage proportional to the compressed input size but
keeps the copy operation outside the R process's memory footprint.

The default interface exposes the input, repeatable instance/species dimension
mapping, non-tree IDs, CSP mode and seed source, AOI, 0.2 m DTM resolution, and
random seed. Algorithm controls are grouped under **Keep defaults** and
**Fine-tune** sections.

Inventory-only runs default to bounded 300 m spatial reads, a 5 m DTM buffer,
10 DTM workers, and 64 disk-backed instance partitions. DTM generation uses
spatial reads below 50 million points. For larger inputs it streams the source
in parallel, retains the minimum Z at each deterministic 0.1 m cell centre,
and runs CSF/TIN on that reduced surface in buffered 300 m tiles. These controls
are available under **Inventory memory settings**. CSP still reads the complete
cloud because its global voxel routing and point-cloud output must preserve
upstream behavior.

Run validation from the ``galaxytools`` repository::

    planemo lint tools/3dtrees_csp_stand_segmentation/3dtrees_csp_stand_segmentation.xml
    planemo test tools/3dtrees_csp_stand_segmentation/3dtrees_csp_stand_segmentation.xml --docker
    planemo shed_lint tools/3dtrees_csp_stand_segmentation
