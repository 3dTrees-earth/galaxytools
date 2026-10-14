"""Create two custom-ID fixtures without touching the existing wrapper fixtures."""
import sys
from copy import deepcopy
from pathlib import Path

import laspy
import numpy as np


def generate(destination, reference):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    outputs = [destination / name for name in ("custom_original.laz", "custom_species.laz")]
    if any(path.exists() for path in outputs):
        raise FileExistsError("Choose a destination without the custom instance fixtures")
    header = laspy.LasHeader(point_format=3, version="1.2")
    header.scales = [0.001, 0.001, 0.001]
    header.offsets = [500000, 5400000, 0]
    # Copy the synthetic fixture's CRS VLRs without requiring pyproj at generation.
    with laspy.open(reference) as reader:
        header.vlrs = deepcopy([vlr for vlr in reader.header.vlrs
                               if not (vlr.user_id == "LASF_Spec" and vlr.record_id == 4)])
    header.add_extra_dim(laspy.ExtraBytesParams(name="CustomTreeId", type=np.uint32))
    header.add_extra_dim(laspy.ExtraBytesParams(name="Amplitude", type=np.int16, no_data=[-1]))
    source = laspy.LasData(header)
    source.x = 500001 + np.arange(20) * 0.01
    source.y = np.full(20, 5400001.0)
    source.z = np.ones(20)
    source.CustomTreeId = np.where(np.arange(20) % 2 == 0, 7, 70000)
    source.Amplitude = np.where(np.arange(20) % 3 == 0, -1, 42)
    species_header = header.copy()
    species_header.add_extra_dim(laspy.ExtraBytesParams(name="PredSpecies", type=np.uint16))
    predictions = laspy.LasData(species_header)
    for name in source.point_format.dimension_names:
        predictions[name] = source[name]
    predictions.x = source.x + 0.008
    predictions.PredSpecies = np.where(source.CustomTreeId == 7, 10, 20)
    source.write(outputs[0])
    predictions.write(outputs[1])


if __name__ == "__main__":
    generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2
             else Path(__file__).with_name("original_with_ids.laz"))
