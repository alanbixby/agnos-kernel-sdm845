"""Mean RAW plane values in fixed half-res regions. Usage: measure.py DNG [DNG...]"""
import json, sys
import numpy as np, rawpy
REGIONS = {'left': (960, 1080, 465, 625), 'right': (1260, 1380, 465, 625), 'dark_bg': (300, 500, 300, 500)}
for path in sys.argv[1:]:
  raw = rawpy.imread(path).raw_image_visible.astype(float)
  planes = {'R': raw[0::2, 1::2], 'G': (raw[0::2, 0::2] + raw[1::2, 1::2]) / 2, 'B': raw[1::2, 0::2]}
  out = {n: {c: round(float(p[y0:y1, x0:x1].mean()), 2) for c, p in planes.items()} for n, (x0, x1, y0, y1) in REGIONS.items()}
  print(path.rsplit('/', 1)[1], json.dumps(out))
