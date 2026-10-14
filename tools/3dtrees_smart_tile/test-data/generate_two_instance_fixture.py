"""Create only two_instance_dimensions.laz using the SmartTile scientific runtime."""
import sys
from pathlib import Path

import laspy
import numpy as np
from point_cloud_metadata import copy_single_source_header, update_extra_dimensions


def generate(destination: Path, fixtures: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "two_instance_dimensions.laz"
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    source = laspy.read(fixtures / "original_with_ids.laz")
    if len(source.points) != 20:
        raise ValueError("Expected the existing 20-point original_with_ids fixture")
    header = copy_single_source_header(source.header)
    update_extra_dimensions(header, [laspy.ExtraBytesParams(name="PredInstance_FM", type=np.uint32)])
    output = laspy.LasData(header, laspy.ScaleAwarePointRecord.zeros(len(source.points), header=header))
    for name in source.points.array.dtype.names:
        output.points.array[name] = source.points.array[name]
    output.PredInstance_FM = np.where(np.arange(20) < 10, 11, 22)
    with target.open("xb") as handle:
        output.write(handle, do_compress=True)
    reread = laspy.read(target)
    for name in source.points.array.dtype.names:
        np.testing.assert_array_equal(reread.points.array[name], source.points.array[name])
    np.testing.assert_array_equal(reread.PredInstance_FM, output.PredInstance_FM)
    assert reread.header.parse_crs() == source.header.parse_crs()
    amplitude = next(struct for vlr in reread.header.vlrs
                     if vlr.user_id == "LASF_Spec" and vlr.record_id == 4
                     for struct in vlr.extra_bytes_structs if struct.name == b"Amplitude")
    np.testing.assert_array_equal(amplitude.no_data, [-1])
    return target


if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        raise SystemExit("Usage: generate_two_instance_fixture.py DESTINATION [FIXTURE_DIRECTORY]")
    print(generate(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) == 3 else Path(__file__).parent))
