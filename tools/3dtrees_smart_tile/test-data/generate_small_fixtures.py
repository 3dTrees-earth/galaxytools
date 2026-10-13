from pathlib import Path
import json
import sys
import laspy
import numpy as np
from pyproj import CRS

root = Path(sys.argv[1])
root.mkdir(exist_ok=True)
h = laspy.LasHeader(point_format=3, version='1.2')
h.scales = [0.001, 0.001, 0.001]
h.offsets = [500000, 5400000, 0]
h.add_crs(CRS.from_epsg(32632))
h.add_extra_dim(laspy.ExtraBytesParams(name='PredInstance_SAT', type=np.uint32))
h.add_extra_dim(laspy.ExtraBytesParams(name='Amplitude', type=np.int16, no_data=[-1]))
c = laspy.LasData(h)
c.x = 500001 + np.arange(20) * 0.01
c.y = np.full(20, 5400001.0)
c.z = np.ones(20)
c.PredInstance_SAT = np.where(np.arange(20)%2==0, 7, 70000)
c.Amplitude = np.where(np.arange(20)%3==0, -1, 42)
c.write(root/'original_with_ids.laz')
c.write(root/'c00_r00.laz')
ph = h.copy()
ph.add_extra_dim(laspy.ExtraBytesParams(name='PredSpecies', type=np.uint16))
p = laspy.LasData(ph)
for name in c.point_format.dimension_names:
    p[name] = c[name]
p.x = c.x + 0.008
p.PredSpecies = np.where(c.PredInstance_SAT==7, 10, 20)
p.write(root/'species.laz')
bounds=dict(tile_length=10,tile_buffer=0,tiles=[dict(col=0,row=0,
    core=[[500000,500010],[5400000,5400010]],
    bounds=[[500000,500010],[5400000,5400010]])])
(root/'dense_tile_bounds.json').write_text(json.dumps(bounds,indent=2)+'\n')
