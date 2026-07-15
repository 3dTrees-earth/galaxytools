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

Inventory-only runs default to bounded 25 m spatial reads, a 5 m DTM buffer,
and 64 disk-backed instance partitions. These controls are available under
**Inventory memory settings**. CSP still reads the complete cloud because its
global voxel routing and point-cloud output must preserve upstream behavior.

Run validation from the ``galaxytools`` repository::

    planemo lint tools/3dtrees_csp_stand_segmentation/3dtrees_csp_stand_segmentation.xml
    planemo test tools/3dtrees_csp_stand_segmentation/3dtrees_csp_stand_segmentation.xml --docker
    planemo shed_lint tools/3dtrees_csp_stand_segmentation
