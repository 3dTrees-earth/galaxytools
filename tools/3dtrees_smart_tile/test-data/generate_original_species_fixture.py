"""Create only species_original.laz; run with the SmartTile scientific runtime."""
import sys
from pathlib import Path

import laspy
import numpy as np
from point_cloud_metadata import (
    copy_single_source_header,
    extra_bytes_params_from_dimension_info,
    update_extra_dimensions,
)


def generate(destination: Path, fixtures: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "species_original.laz"
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    original = laspy.read(fixtures / "original_with_ids.laz")
    species = laspy.read(fixtures / "species.laz")
    assert len(original.points) == len(species.points) == 20
    np.testing.assert_array_equal(original.PredInstance_SAT, species.PredInstance_SAT)
    header = copy_single_source_header(original.header)
    info = species.point_format.dimension_by_name("PredSpecies")
    update_extra_dimensions(header, [extra_bytes_params_from_dimension_info(info, header=species.header)])
    output = laspy.LasData(header, laspy.ScaleAwarePointRecord.zeros(len(original.points), header=header))
    for name in original.points.array.dtype.names:
        output.points.array[name] = original.points.array[name]
    output.PredSpecies = np.asarray(species.PredSpecies)
    # Exclusive creation also protects an output created after the initial check.
    with target.open("xb") as handle:
        output.write(handle, do_compress=True)
    reread = laspy.read(target)
    for name in original.points.array.dtype.names:
        np.testing.assert_array_equal(reread.points.array[name], original.points.array[name])
    params = extra_bytes_params_from_dimension_info(reread.point_format.dimension_by_name("Amplitude"),
                                                    header=reread.header)
    np.testing.assert_array_equal(params.no_data, [-1])
    np.testing.assert_array_equal(reread.PredSpecies, species.PredSpecies)
    return target


if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        raise SystemExit("Usage: generate_original_species_fixture.py DESTINATION [FIXTURE_DIRECTORY]")
    print(generate(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) == 3 else Path(__file__).parent))
