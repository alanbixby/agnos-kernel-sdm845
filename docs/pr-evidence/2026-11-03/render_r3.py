"""Before/after images from the 2026-11-03 camera RAW captures (S21 Ultra, Pro mode, ISO 50, 4 s, manual focus;
same framing and the same processing for every tile; the camera saw the screen upside down, so tiles are rotated 180 degrees). Each image: the comma logo screen and an all-black screen."""
import numpy as np, rawpy
from PIL import Image, ImageDraw, ImageFont

RAW = '/tmp/ab/cam/raw'
X0, X1, Y0, Y1 = 900, 1440, 400, 670   # half-size frame, around the comma's screen
SCALE = 2.0                             # brightened 2x so faint glow shows; identical for every tile
TW, TH = 440, 220
FONT = ImageFont.load_default(size=22)
SMALL = ImageFont.load_default(size=16)
SHOTS = {
  'stock':   ('20261103_051751.dng', '20261103_051803.dng'),
  'pr1':     ('20261103_051555.dng', '20261103_051607.dng'),
  'pr1_ibb': ('20261103_044502.dng', '20261103_052338.dng'),
  'off':     (None, '20261103_052353.dng'),
}

def tile(name):
  if name is None:
    return Image.new('RGB', (TW, TH), (0, 0, 0))
  with rawpy.imread(f'{RAW}/{name}') as r:
    lin = r.postprocess(gamma=(1, 1), no_auto_bright=True, use_camera_wb=True, output_bps=16, adjust_maximum_thr=0.0,
                        output_color=rawpy.ColorSpace.sRGB, half_size=True).astype(float) / 65535
  v = np.clip(lin[Y0:Y1, X0:X1] * SCALE, 0, 1)
  s = np.where(v <= 0.0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - 0.055)
  return Image.fromarray((s * 255).round().astype(np.uint8)).rotate(180).resize((TW, TH), Image.LANCZOS)

def panel(out, title, key, caption):
  logo, black = SHOTS[key]
  W = TW * 2 + 10
  img = Image.new('RGB', (W, 44 + 26 + TH + 34), (0, 0, 0))
  d = ImageDraw.Draw(img)
  d.text((4, 10), title, fill=(235, 235, 235), font=FONT)
  for i, (sub, name) in enumerate([('comma logo screen', logo), ('all-black screen', black)]):
    x = i * (TW + 10)
    d.text((x + 4, 46), sub, fill=(170, 170, 170), font=SMALL)
    img.paste(tile(name), (x, 70))
  d.text((4, 70 + TH + 8), caption, fill=(150, 150, 150), font=SMALL)
  img.save(out)

def strip(out, columns, caption):
  W = (TW + 10) * len(columns) - 10
  img = Image.new('RGB', (W, 44 + TH + 34), (0, 0, 0))
  d = ImageDraw.Draw(img)
  for i, (label, name) in enumerate(columns):
    x = i * (TW + 10)
    d.text((x + 4, 10), label, fill=(235, 235, 235), font=FONT)
    img.paste(tile(name), (x, 44))
  d.text((4, 44 + TH + 8), caption, fill=(150, 150, 150), font=SMALL)
  img.save(out)

CAP = 'Dark room. Same camera, exposure and processing for every photo, brightened 2x so faint glow shows.'
panel('stock.png', 'Before: stock', 'stock', CAP)
panel('pr1.png', 'With the panel fix (PR 1)', 'pr1', CAP)
panel('pr1-elvss.png', 'With the panel fix and -3.5 V (PR 2)', 'pr1_ibb', CAP)
strip('all-black-series.png', [('Stock', SHOTS['stock'][1]), ('Panel fix', SHOTS['pr1'][1]),
                               ('Panel fix and -3.5 V', SHOTS['pr1_ibb'][1]), ('Screen switched off', SHOTS['off'][1])],
      'All-black screen. ' + CAP)
